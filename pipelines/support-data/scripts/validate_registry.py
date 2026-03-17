#!/usr/bin/env python3
"""
Validate the Data Registry and discover unregistered dataset candidates.

Reads data/registry/DATA_REGISTRY.yaml, verifies registered paths exist,
scans data/raw and data/derived for unregistered files/directories, and
writes a suggestion report to docs/UNREGISTERED_DATASETS.md.

Does NOT modify the registry automatically.
"""

from __future__ import annotations

import argparse
import sys
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import REGISTRY_PATH, ROOT_DIR, load_registry


SCAN_ROOTS = ("data/raw", "data/derived")
REPORT_PATH = ROOT_DIR / "docs" / "UNREGISTERED_DATASETS.md"
BACKUP_RE = re.compile(r"\.bak(?:\.\d+)?$", re.IGNORECASE)
YEAR_END_CSV_RE = re.compile(r"retroverse_year_end_\d{4}\.csv$")
YEAR_END_TOP40_RE = re.compile(r"retroverse_year_end_\d{4}_top40\.csv$")


@dataclass
class Suggestion:
    dataset_id: str
    dataset_type: str
    path: str
    kind: str
    owner_pipeline: str
    consumers: list[str]
    inputs: list[str]
    basis: str
    ancestor_dataset_id: str | None
    description: str
    match_count: int = 1
    matched_paths: list[str] | None = None


@dataclass
class ValidationResult:
    missing_paths: list[str]
    orphan_scan_paths: list[str]
    suggestions: list[Suggestion]
    ignored_artifacts: list[str]


def _normalize_rel(path: Path | str) -> str:
    raw = str(path).replace("\\", "/").rstrip("/")
    return raw or "."


def _load_datasets() -> dict[str, dict[str, Any]]:
    if not REGISTRY_PATH.exists():
        print(f"[ERROR] Registry not found: {REGISTRY_PATH}")
        sys.exit(1)

    payload = load_registry()
    datasets = payload.get("datasets", {})
    if not isinstance(datasets, dict):
        return {}
    return {str(dataset_id): meta for dataset_id, meta in datasets.items() if isinstance(meta, dict)}


def _registry_path_map(datasets: dict[str, dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for dataset_id, meta in datasets.items():
        path = _normalize_rel(meta.get("path", ""))
        if path and path != ".":
            mapping[path] = dataset_id
    return mapping


def _path_is_covered(registered_paths: set[str], candidate: str) -> bool:
    for registered_path in registered_paths:
        if candidate == registered_path or candidate.startswith(f"{registered_path}/"):
            return True
        if registered_path.startswith(f"{candidate}/"):
            return True
    return False


def _is_ignored_artifact(path: Path) -> bool:
    name = path.name
    if name.startswith("."):
        return True
    if name in {".DS_Store"}:
        return True
    if name.endswith(("-wal", "-shm", "-journal")):
        return True
    if BACKUP_RE.search(name):
        return True
    return False


def _nearest_registered_ancestor(path_rel: str, path_map: dict[str, str]) -> tuple[str | None, dict[str, Any] | None]:
    best_path: str | None = None
    best_dataset_id: str | None = None
    for registered_path, dataset_id in path_map.items():
        if path_rel == registered_path or path_rel.startswith(f"{registered_path}/"):
            if best_path is None or len(registered_path) > len(best_path):
                best_path = registered_path
                best_dataset_id = dataset_id
    if best_dataset_id is None:
        return None, None
    datasets = _load_datasets()
    return best_dataset_id, datasets.get(best_dataset_id)


def _guess_owner_for_path(path_rel: str) -> str:
    if path_rel.startswith("data/raw/charts/"):
        return "pipelines/support-data"
    if path_rel.startswith("data/raw/media/"):
        return "pipelines/media-index"
    if path_rel.startswith("data/raw/imdb/") or path_rel.startswith("data/raw/screen-culture/"):
        return "apps/magazine"
    if path_rel.startswith("data/derived/cards/"):
        return "pipelines/cards-1974"
    if path_rel.startswith("data/derived/media-index/"):
        return "pipelines/media-index"
    if path_rel.startswith("data/derived/culture/") or path_rel.startswith("data/derived/year-masters/"):
        return "pipelines/support-data"
    return "TODO_OWNER"


def _default_consumers(owner_pipeline: str) -> list[str]:
    if owner_pipeline == "pipelines/support-data":
        return ["apps/web", "apps/magazine", "pipelines/support-data"]
    if owner_pipeline == "pipelines/media-index":
        return ["apps/web", "pipelines/media-index"]
    if owner_pipeline == "pipelines/cards-1974":
        return ["apps/web", "pipelines/cards-1974"]
    if owner_pipeline == "apps/magazine":
        return ["apps/magazine"]
    return ["TODO_CONSUMER"]


def _sanitize_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return token


def _suggest_dataset_id(path_or_template: str, kind: str) -> str:
    rel_path = Path(path_or_template)
    parts = list(rel_path.parts)
    base_parts = parts[2:] if len(parts) >= 3 and parts[0] == "data" else parts

    tokens: list[str] = []
    if parts[:2] == ["data", "raw"]:
        tokens.append("raw")
    elif parts[:2] == ["data", "derived"]:
        tokens.append("derived")

    if rel_path.suffix:
        for part in base_parts[:-1]:
            token = _sanitize_token(part)
            if token:
                tokens.append(token)
        stem_token = _sanitize_token(rel_path.stem)
        if stem_token:
            tokens.append(stem_token)
        suffix_token = _sanitize_token(rel_path.suffix.lstrip("."))
        if suffix_token:
            tokens.append(suffix_token)
    else:
        for part in base_parts:
            token = _sanitize_token(part)
            if token:
                tokens.append(token)
        if kind == "directory":
            tokens.append("dir")
        elif kind == "file_family":
            tokens.append("family")

    return "_".join(token for token in tokens if token) or "unregistered_dataset"


def _suggest_description(path_or_template: str, kind: str, basis: str, match_count: int = 1) -> str:
    if kind == "file_family":
        return f"TODO: describe unregistered file family at {path_or_template} ({match_count} matching files discovered)."
    if kind == "directory":
        return f"TODO: describe unregistered directory dataset at {path_or_template}."
    return f"TODO: describe unregistered file dataset at {path_or_template}."


def _make_suggestion(
    *,
    path: str,
    kind: str,
    dataset_type: str,
    basis: str,
    ancestor_dataset_id: str | None,
    ancestor_meta: dict[str, Any] | None,
    matched_paths: list[str] | None = None,
) -> Suggestion:
    owner_pipeline = str((ancestor_meta or {}).get("owner_pipeline", "")).strip() or _guess_owner_for_path(path)
    consumers = list((ancestor_meta or {}).get("consumers", []) or _default_consumers(owner_pipeline))
    inputs = list((ancestor_meta or {}).get("inputs", [])) if dataset_type == "derived" else []
    match_count = len(matched_paths or [path])

    return Suggestion(
        dataset_id=_suggest_dataset_id(path, kind),
        dataset_type=dataset_type,
        path=path,
        kind=kind,
        owner_pipeline=owner_pipeline,
        consumers=consumers,
        inputs=inputs,
        basis=basis,
        ancestor_dataset_id=ancestor_dataset_id,
        description=_suggest_description(path, kind, basis, match_count),
        match_count=match_count,
        matched_paths=matched_paths,
    )


def _family_suggestion_for_year_masters(
    parent_rel: str,
    paths: list[str],
    ancestor_dataset_id: str | None,
    ancestor_meta: dict[str, Any] | None,
) -> list[Suggestion]:
    yearly = sorted(path for path in paths if YEAR_END_CSV_RE.search(Path(path).name))
    yearly_top40 = sorted(path for path in paths if YEAR_END_TOP40_RE.search(Path(path).name))
    suggestions: list[Suggestion] = []

    if yearly:
        suggestions.append(
            Suggestion(
                dataset_id="year_masters_retroverse_year_end_year_csv_family",
                dataset_type="derived",
                path=f"{parent_rel}/retroverse_year_end_YYYY.csv",
                kind="file_family",
                owner_pipeline=str((ancestor_meta or {}).get("owner_pipeline", "")).strip() or "pipelines/support-data",
                consumers=list((ancestor_meta or {}).get("consumers", []) or _default_consumers("pipelines/support-data")),
                inputs=list((ancestor_meta or {}).get("inputs", [])),
                basis=f"grouped from {len(yearly)} matching files under {parent_rel}",
                ancestor_dataset_id=ancestor_dataset_id,
                description=_suggest_description(
                    f"{parent_rel}/retroverse_year_end_YYYY.csv",
                    "file_family",
                    "year-masters family",
                    len(yearly),
                ),
                match_count=len(yearly),
                matched_paths=yearly,
            )
        )

    if yearly_top40:
        suggestions.append(
            Suggestion(
                dataset_id="year_masters_retroverse_year_end_year_top40_csv_family",
                dataset_type="derived",
                path=f"{parent_rel}/retroverse_year_end_YYYY_top40.csv",
                kind="file_family",
                owner_pipeline=str((ancestor_meta or {}).get("owner_pipeline", "")).strip() or "pipelines/support-data",
                consumers=list((ancestor_meta or {}).get("consumers", []) or _default_consumers("pipelines/support-data")),
                inputs=list((ancestor_meta or {}).get("inputs", [])),
                basis=f"grouped from {len(yearly_top40)} matching files under {parent_rel}",
                ancestor_dataset_id=ancestor_dataset_id,
                description=_suggest_description(
                    f"{parent_rel}/retroverse_year_end_YYYY_top40.csv",
                    "file_family",
                    "year-masters family",
                    len(yearly_top40),
                ),
                match_count=len(yearly_top40),
                matched_paths=yearly_top40,
            )
        )

    return suggestions


def _discover_registered_dir_children(
    datasets: dict[str, dict[str, Any]],
    path_map: dict[str, str],
) -> tuple[list[Suggestion], list[str]]:
    suggestions: dict[str, Suggestion] = {}
    ignored_artifacts: list[str] = []

    for registered_path, dataset_id in sorted(path_map.items(), key=lambda item: item[0]):
        if not any(registered_path == root or registered_path.startswith(f"{root}/") for root in SCAN_ROOTS):
            continue
        full_path = ROOT_DIR / registered_path
        if not full_path.exists() or not full_path.is_dir():
            continue

        meta = datasets.get(dataset_id, {})
        dataset_type = "raw" if registered_path.startswith("data/raw/") else "derived"
        year_master_children: list[str] = []

        for child in sorted(full_path.iterdir()):
            child_rel = _normalize_rel(child.relative_to(ROOT_DIR))
            if _is_ignored_artifact(child):
                ignored_artifacts.append(child_rel)
                continue
            if child_rel in path_map:
                continue

            if registered_path == "data/derived/year-masters" and child.is_file():
                if YEAR_END_CSV_RE.search(child.name) or YEAR_END_TOP40_RE.search(child.name):
                    year_master_children.append(child_rel)
                    continue

            suggestion = _make_suggestion(
                path=child_rel,
                kind="directory" if child.is_dir() else "file",
                dataset_type=dataset_type,
                basis=f"unregistered child of registered dataset `{dataset_id}`",
                ancestor_dataset_id=dataset_id,
                ancestor_meta=meta,
            )
            suggestions[child_rel] = suggestion

        if year_master_children:
            for suggestion in _family_suggestion_for_year_masters(
                "data/derived/year-masters",
                year_master_children,
                dataset_id,
                meta,
            ):
                suggestions[suggestion.path] = suggestion

    return sorted(suggestions.values(), key=lambda item: item.path), sorted(set(ignored_artifacts))


def _discover_orphan_scan_paths(path_map: dict[str, str]) -> list[str]:
    registered_paths = set(path_map.keys())
    discovered: list[str] = []

    for scan_root in SCAN_ROOTS:
        full_root = ROOT_DIR / scan_root
        if not full_root.exists():
            continue

        for child in sorted(full_root.iterdir()):
            child_rel = _normalize_rel(child.relative_to(ROOT_DIR))
            if _is_ignored_artifact(child):
                continue
            if child_rel in registered_paths:
                continue
            if any(path.startswith(f"{child_rel}/") for path in registered_paths):
                continue
            if not _path_is_covered(registered_paths, child_rel):
                discovered.append(child_rel)

    return sorted(discovered)


def validate_registry() -> ValidationResult:
    """Validate registered paths and discover unregistered dataset candidates."""
    datasets = _load_datasets()
    path_map = _registry_path_map(datasets)

    missing_paths: list[str] = []
    for dataset_id, meta in sorted(datasets.items()):
        path = _normalize_rel(meta.get("path", ""))
        if not path or path == ".":
            missing_paths.append(f"{dataset_id}: no path defined")
            continue
        full_path = ROOT_DIR / path
        if not full_path.exists():
            missing_paths.append(f"{dataset_id}: {path}")

    orphan_scan_paths = _discover_orphan_scan_paths(path_map)
    suggestions, ignored_artifacts = _discover_registered_dir_children(datasets, path_map)

    for orphan in orphan_scan_paths:
        ancestor_dataset_id, ancestor_meta = _nearest_registered_ancestor(orphan, path_map)
        suggestions.append(
            _make_suggestion(
                path=orphan,
                kind="directory" if (ROOT_DIR / orphan).is_dir() else "file",
                dataset_type="raw" if orphan.startswith("data/raw/") else "derived",
                basis="orphan path under scan root with no registered container",
                ancestor_dataset_id=ancestor_dataset_id,
                ancestor_meta=ancestor_meta,
            )
        )

    suggestions.sort(key=lambda item: (item.path, item.dataset_id))
    return ValidationResult(
        missing_paths=missing_paths,
        orphan_scan_paths=orphan_scan_paths,
        suggestions=suggestions,
        ignored_artifacts=ignored_artifacts,
    )


def _yaml_block(suggestion: Suggestion) -> str:
    lines = [
        f"{suggestion.dataset_id}:",
        f"  type: {suggestion.dataset_type}",
        f"  path: {suggestion.path}",
        f"  description: {suggestion.description}",
        f"  owner_pipeline: {suggestion.owner_pipeline}",
    ]
    if suggestion.inputs:
        lines.append("  inputs:")
        for dataset_id in suggestion.inputs:
            lines.append(f"    - {dataset_id}")
    lines.append("  consumers:")
    for consumer in suggestion.consumers or ["TODO_CONSUMER"]:
        lines.append(f"    - {consumer}")
    return "\n".join(lines)


def write_unregistered_report(result: ValidationResult, report_out: Path) -> None:
    report_out.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Unregistered Datasets",
        "",
        f"Generated from `{REGISTRY_PATH.relative_to(ROOT_DIR)}` by `pipelines/support-data/scripts/validate_registry.py`.",
        "",
        "This report is advisory only. It does not modify the registry automatically.",
        "",
        "## Summary",
        "",
        f"- Missing registered paths: {len(result.missing_paths)}",
        f"- Orphan top-level scan paths: {len(result.orphan_scan_paths)}",
        f"- Suggested registry entries: {len(result.suggestions)}",
        f"- Ignored transient or backup artifacts: {len(result.ignored_artifacts)}",
        "",
        "Discovery scans `data/raw` and `data/derived`, ignores obvious transient artifacts, and suggests entries for unregistered child directories or files beneath registered dataset roots.",
        "",
    ]

    if result.missing_paths:
        lines.extend(["## Missing Registered Paths", ""])
        for item in result.missing_paths:
            lines.append(f"- {item}")
        lines.append("")

    if result.orphan_scan_paths:
        lines.extend(["## Orphan Top-Level Scan Paths", ""])
        for item in result.orphan_scan_paths:
            lines.append(f"- `{item}`")
        lines.append("")

    lines.extend([
        "## Suggested Entries",
        "",
        "| Suggested ID | Kind | Suggested Path | Basis |",
        "|---|---|---|---|",
    ])
    for suggestion in result.suggestions:
        lines.append(
            f"| `{suggestion.dataset_id}` | `{suggestion.kind}` | `{suggestion.path}` | {suggestion.basis} |"
        )
    lines.append("")

    if result.ignored_artifacts:
        lines.extend([
            "## Ignored Artifacts",
            "",
            "These were discovered during the scan but intentionally excluded from suggestions because they appear to be hidden, backup, or transient files:",
            "",
        ])
        for artifact in result.ignored_artifacts[:50]:
            lines.append(f"- `{artifact}`")
        if len(result.ignored_artifacts) > 50:
            lines.append(f"- ... {len(result.ignored_artifacts) - 50} more")
        lines.append("")

    lines.extend([
        "## Suggested YAML Entries",
        "",
        "These entries are suggestions only. Review the path granularity, owners, descriptions, inputs, and consumers before copying them into `DATA_REGISTRY.yaml`.",
        "",
    ])

    for suggestion in result.suggestions:
        lines.append(f"### `{suggestion.dataset_id}`")
        lines.append("")
        lines.append(f"- Kind: `{suggestion.kind}`")
        lines.append(f"- Suggested path: `{suggestion.path}`")
        lines.append(f"- Basis: {suggestion.basis}")
        if suggestion.ancestor_dataset_id:
            lines.append(f"- Nearest registered dataset: `{suggestion.ancestor_dataset_id}`")
        if suggestion.match_count > 1:
            lines.append(f"- Matching paths grouped: {suggestion.match_count}")
        lines.append("")
        if suggestion.matched_paths and suggestion.match_count > 1:
            lines.append("Matched paths:")
            for path in suggestion.matched_paths[:12]:
                lines.append(f"- `{path}`")
            if len(suggestion.matched_paths) > 12:
                lines.append(f"- ... {len(suggestion.matched_paths) - 12} more")
            lines.append("")
        lines.append("```yaml")
        lines.append(_yaml_block(suggestion))
        lines.append("```")
        lines.append("")

    report_out.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate DATA_REGISTRY.yaml and suggest missing registry entries.")
    parser.add_argument(
        "--report-out",
        type=Path,
        default=REPORT_PATH,
        help="Markdown path for the unregistered dataset suggestion report",
    )
    return parser.parse_args()


def main() -> None:
    """Run validation, discovery, and report generation."""
    args = parse_args()

    print("Validating Data Registry...")
    print(f"Registry: {REGISTRY_PATH}")
    print(f"Repo root: {ROOT_DIR}")
    print()

    result = validate_registry()
    write_unregistered_report(result, args.report_out)

    if result.missing_paths:
        print("[MISSING] Registered paths that do not exist:")
        for item in result.missing_paths:
            print(f"  - {item}")
        print()

    if result.orphan_scan_paths:
        print("[ORPHAN] Top-level paths under data/raw or data/derived with no registered container:")
        for item in result.orphan_scan_paths:
            print(f"  - {item}")
        print()

    if result.suggestions:
        print("[SUGGESTIONS] Unregistered dataset candidates discovered:")
        for suggestion in result.suggestions:
            detail = f"{suggestion.path} -> {suggestion.dataset_id}"
            if suggestion.match_count > 1:
                detail += f" ({suggestion.match_count} matches)"
            print(f"  - {detail}")
        print()
    else:
        print("[SUGGESTIONS] No unregistered dataset candidates discovered.")
        print()

    print(f"Suggestion report written to: {args.report_out}")

    if result.missing_paths:
        sys.exit(1)


if __name__ == "__main__":
    main()
