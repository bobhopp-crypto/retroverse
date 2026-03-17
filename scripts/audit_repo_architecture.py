#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import os
import re
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "docs" / "REPO_ARCHITECTURE_AUDIT.md"
IGNORED_DIRS = {".git", "node_modules", "__pycache__"}
CANONICAL_DIRS = [
    "retroverse-data",
    "retroverse-magazine",
    "retroverse-hub",
    "retroverse-games",
    "scripts",
]
EXPERIMENTAL_TOKENS = [
    "test",
    "temp",
    "tmp",
    "sandbox",
    "draft",
    "old",
    "backup",
    "unused",
    "v1",
    "v2",
    "prototype",
]
ARTIFACT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".json", ".csv", ".pdf"}
EXPECTED_ARTIFACT_CONTAINERS = {
    "issues",
    "artifacts",
    "archive",
    "data",
    "raw-data",
    "public",
    "assets",
    "images",
    "output",
    "runs",
}
NON_ARTIFACT_JSON_NAMES = {
    "package.json",
    "package-lock.json",
    "pipeline.config.json",
    "tsconfig.json",
    "tsconfig.app.json",
    "tsconfig.node.json",
    "tsconfig.pipeline.json",
}
NON_ARTIFACT_PARENT_DIRS = {".vscode"}
DUPLICATE_PIPELINE_PATTERNS = {
    "generate_issue*": "generate_issue*",
    "build_issue*": "build_issue*",
    "create_issue*": "create_issue*",
}
SCRIPT_EXTENSIONS = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh"}
POSSIBLE_EQUIVALENTS = {
    "retroverse-data": ["data", "raw-data"],
    "retroverse-magazine": ["apps/magazine/retroverse-magazine"],
    "retroverse-hub": ["apps/web"],
    "retroverse-games": [],
    "scripts": ["pipelines/support-data/scripts", "pipelines/media-index/scripts"],
}


def rel_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def iter_walk():
    for current_root, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        yield Path(current_root), dirnames, sorted(filenames)


def build_tree_lines(root: Path, max_depth: int = 4) -> list[str]:
    lines = [f"{root.name}/"]

    def walk_dir(directory: Path, prefix: str, depth: int) -> None:
        if depth >= max_depth:
            return

        children = []
        for child in directory.iterdir():
            if child.name in IGNORED_DIRS:
                continue
            children.append(child)

        children.sort(key=lambda item: (not item.is_dir(), item.name.lower()))

        for index, child in enumerate(children):
            is_last = index == len(children) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if child.is_dir() and not child.is_symlink() else ""
            lines.append(f"{prefix}{connector}{child.name}{suffix}")

            if child.is_dir() and not child.is_symlink():
                extension = "    " if is_last else "│   "
                walk_dir(child, prefix + extension, depth + 1)

    walk_dir(root, "", 0)
    return lines


def canonical_validation() -> list[dict[str, str]]:
    rows = []
    for directory in CANONICAL_DIRS:
        path = REPO_ROOT / directory
        equivalents = [
            candidate
            for candidate in POSSIBLE_EQUIVALENTS.get(directory, [])
            if (REPO_ROOT / candidate).exists()
        ]
        rows.append(
            {
                "directory": directory,
                "status": "Present" if path.exists() else "Missing",
                "equivalents": ", ".join(equivalents) if equivalents else "—",
            }
        )
    return rows


def find_experimental_directories() -> list[dict[str, str]]:
    findings = []
    for current_root, dirnames, _ in iter_walk():
        for dirname in dirnames:
            lowered = dirname.lower()
            segments = {
                segment
                for segment in re.split(r"[^a-z0-9]+", lowered)
                if segment
            }
            matched = []
            for token in EXPERIMENTAL_TOKENS:
                if token in segments or f"{token}s" in segments:
                    matched.append(token)
            if not matched:
                continue
            findings.append(
                {
                    "path": rel_path(current_root / dirname),
                    "tokens": ", ".join(sorted(set(matched))),
                }
            )
    findings.sort(key=lambda item: item["path"])
    return findings


def looks_like_artifact(path: Path) -> bool:
    if path.suffix.lower() not in ARTIFACT_EXTENSIONS:
        return False
    lowered_name = path.name.lower()
    if lowered_name in NON_ARTIFACT_JSON_NAMES:
        return False
    if lowered_name.startswith("tsconfig.") and lowered_name.endswith(".json"):
        return False
    return True


def is_expected_artifact_location(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXPECTED_ARTIFACT_CONTAINERS)


def find_orphan_artifacts() -> list[dict[str, str]]:
    findings = []
    for current_root, _, filenames in iter_walk():
        for filename in filenames:
            path = current_root / filename
            if not looks_like_artifact(path):
                continue
            relative = path.relative_to(REPO_ROOT)
            if any(part in NON_ARTIFACT_PARENT_DIRS for part in relative.parts):
                continue
            if is_expected_artifact_location(relative):
                continue
            findings.append(
                {
                    "path": rel_path(path),
                    "size": str(path.stat().st_size),
                }
            )
    findings.sort(key=lambda item: item["path"])
    return findings


def detect_duplicate_pipelines() -> list[dict[str, object]]:
    groups: dict[str, list[str]] = {label: [] for label in DUPLICATE_PIPELINE_PATTERNS}
    for current_root, _, filenames in iter_walk():
        for filename in filenames:
            path = current_root / filename
            if path.suffix.lower() not in SCRIPT_EXTENSIONS:
                continue
            lowered = filename.lower()
            for label, pattern in DUPLICATE_PIPELINE_PATTERNS.items():
                if fnmatch.fnmatch(lowered, pattern.lower()):
                    groups[label].append(rel_path(path))

    findings = []
    for label, matches in groups.items():
        unique_matches = sorted(set(matches))
        if len(unique_matches) > 1:
            findings.append({"pattern": label, "matches": unique_matches})
    return findings


def markdown_inventory() -> list[dict[str, str]]:
    findings = []
    for current_root, _, filenames in iter_walk():
        for filename in filenames:
            if not filename.lower().endswith(".md"):
                continue
            path = current_root / filename
            stat = path.stat()
            findings.append(
                {
                    "path": rel_path(path),
                    "size": str(stat.st_size),
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )
    findings.sort(key=lambda item: item["path"])
    return findings


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    table = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        table.append("| " + " | ".join(row) + " |")
    return "\n".join(table)


def render_report() -> str:
    tree_lines = build_tree_lines(REPO_ROOT, max_depth=4)
    canonical_rows = canonical_validation()
    experimental_rows = find_experimental_directories()
    orphan_rows = find_orphan_artifacts()
    duplicate_rows = detect_duplicate_pipelines()
    markdown_rows = markdown_inventory()

    platform_state_path = REPO_ROOT / "RETROVERSE_PLATFORM_STATE.md"
    requested_magazine_state = REPO_ROOT / "retroverse-magazine" / "PROJECT_STATE.md"
    migrated_magazine_state = (
        REPO_ROOT / "apps" / "magazine" / "retroverse-magazine" / "PROJECT_STATE.md"
    )

    lines: list[str] = []
    lines.append("# Repository Architecture Audit")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Repository root: `{REPO_ROOT}`")
    lines.append("")
    lines.append(
        "Observed root layout uses the migrated `apps/`, `data/`, `pipelines/`, and `archive/` structure."
    )
    lines.append("")
    lines.append("## Repository Tree")
    lines.append("")
    lines.append("```text")
    lines.extend(tree_lines)
    lines.append("```")
    lines.append("")
    lines.append("## Canonical Directory Validation")
    lines.append("")
    lines.append(
        format_table(
            ["Directory", "Status", "Observed Equivalent(s)"],
            [
                [row["directory"], row["status"], row["equivalents"]]
                for row in canonical_rows
            ],
        )
    )
    lines.append("")
    missing = [row["directory"] for row in canonical_rows if row["status"] == "Missing"]
    if missing:
        lines.append(f"Missing canonical directories: {', '.join(missing)}")
    else:
        lines.append("All requested canonical directories are present.")
    lines.append("")
    lines.append("## Experimental Directories")
    lines.append("")
    if experimental_rows:
        lines.append(
            format_table(
                ["Path", "Matched Token(s)"],
                [[row["path"], row["tokens"]] for row in experimental_rows],
            )
        )
    else:
        lines.append("No experimental-style directories detected.")
    lines.append("")
    lines.append("## Orphan Artifacts")
    lines.append("")
    lines.append(
        "Artifact heuristic checks `png`, `jpg`, `jpeg`, `json`, `csv`, and `pdf` files outside expected artifact containers"
        f" ({', '.join(sorted(EXPECTED_ARTIFACT_CONTAINERS))})."
    )
    lines.append("")
    if orphan_rows:
        lines.append(
            format_table(
                ["Path", "Size (bytes)"],
                [[row["path"], row["size"]] for row in orphan_rows],
            )
        )
    else:
        lines.append("No orphan artifacts detected by the configured heuristic.")
    lines.append("")
    lines.append("## Duplicate Pipelines")
    lines.append("")
    if duplicate_rows:
        for row in duplicate_rows:
            lines.append(f"### {row['pattern']}")
            lines.append("")
            for match in row["matches"]:
                lines.append(f"- `{match}`")
            lines.append("")
    else:
        lines.append("No duplicate pipeline families detected for the configured patterns.")
        lines.append("")
    lines.append("## Markdown Inventory")
    lines.append("")
    lines.append(f"Total Markdown files: `{len(markdown_rows)}`")
    lines.append("")
    lines.append(
        format_table(
            ["Path", "Size (bytes)", "Last Modified"],
            [[row["path"], row["size"], row["modified"]] for row in markdown_rows],
        )
    )
    lines.append("")
    lines.append("## Platform State File Check")
    lines.append("")
    if platform_state_path.exists():
        lines.append(f"- PASS: `RETROVERSE_PLATFORM_STATE.md` found at `{rel_path(platform_state_path)}`")
    else:
        lines.append("- FAIL: `RETROVERSE_PLATFORM_STATE.md` is missing from the repository root.")
    lines.append("")
    lines.append("## Magazine State File Check")
    lines.append("")
    if requested_magazine_state.exists():
        lines.append(
            f"- PASS: requested file found at `{rel_path(requested_magazine_state)}`"
        )
    else:
        lines.append(
            "- FAIL: requested path `retroverse-magazine/PROJECT_STATE.md` is missing."
        )
        if migrated_magazine_state.exists():
            lines.append(
                f"- NOTE: migrated equivalent found at `{rel_path(migrated_magazine_state)}`"
            )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Missing canonical directories: `{len(missing)}`")
    lines.append(f"- Experimental directories flagged: `{len(experimental_rows)}`")
    lines.append(f"- Orphan artifacts flagged: `{len(orphan_rows)}`")
    lines.append(f"- Duplicate pipeline families: `{len(duplicate_rows)}`")
    lines.append(f"- Markdown files inventoried: `{len(markdown_rows)}`")
    lines.append(
        "- Root appears to be a migrated RetroVerse layout rather than the older flat module layout."
    )
    lines.append(
        "- Requested magazine state path is absent, but a migrated equivalent exists under `apps/magazine/retroverse-magazine/PROJECT_STATE.md`."
        if migrated_magazine_state.exists() and not requested_magazine_state.exists()
        else "- Requested magazine state path is present."
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = render_report()
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Generated report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
