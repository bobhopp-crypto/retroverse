#!/usr/bin/env python3
"""Rebuild DATA_INVENTORY.md from the RetroVerse project filesystem."""

from __future__ import annotations

import argparse
import os
from glob import glob
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCAN_ROOT = Path("/Users/bobhopp/Sites/retroverse")
INVENTORY_PATH = PROJECT_ROOT / "DATA_INVENTORY.md"
DATA_SOURCES_PATH = PROJECT_ROOT / "data" / "DATA_SOURCES.yaml"

DATA_EXTENSIONS = {".csv", ".json", ".yaml", ".yml"}
DATABASE_EXTENSIONS = {".db", ".sqlite", ".sqlite3"}
SCRIPT_EXTENSIONS = {".py", ".sh"}

EXCLUDED_DIRS = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "dist-pipeline",
    ".cache",
}

DATA_DOC_KEYWORDS = ("data", "dataset", "inventory", "sources", "billboard", "chart")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh RetroVerse DATA_INVENTORY.md.")
    parser.add_argument("--write", action="store_true", help="Write DATA_INVENTORY.md (default mode).")
    parser.add_argument("--stdout", action="store_true", help="Print inventory markdown to stdout.")
    return parser.parse_args()


def parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_simple_yaml(text: str) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    current_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            data[current_key] = {}
            continue
        if current_key and line.startswith("  ") and ":" in line:
            field, value = line.strip().split(":", 1)
            data[current_key][field.strip()] = parse_scalar(value.strip())
    return data


def load_data_sources() -> tuple[dict[str, dict[str, Any]], list[str]]:
    notes: list[str] = []
    if not DATA_SOURCES_PATH.exists():
        notes.append(f"Canonical source map not found: {DATA_SOURCES_PATH}")
        return {}, notes

    text = DATA_SOURCES_PATH.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        payload = yaml.safe_load(text)
        if isinstance(payload, dict):
            return payload, notes
        notes.append("DATA_SOURCES.yaml is not a mapping at the root.")
        return {}, notes
    except Exception:
        notes.append("PyYAML unavailable; using built-in simple YAML parser.")
        return parse_simple_yaml(text), notes


def is_glob_pattern(path_text: str) -> bool:
    return any(token in path_text for token in ("*", "?", "["))


def resolve_path(path_text: str) -> Path:
    candidate = Path(path_text).expanduser()
    if candidate.is_absolute():
        return candidate
    return (PROJECT_ROOT / path_text).resolve()


def expand_path(path_text: str) -> list[Path]:
    if is_glob_pattern(path_text):
        candidate = Path(path_text).expanduser()
        if candidate.is_absolute():
            return [Path(item) for item in sorted(glob(path_text))]
        return sorted(PROJECT_ROOT.glob(path_text))
    return [resolve_path(path_text)]


def relative_to_scan_root(path: Path, scan_root: Path) -> str:
    try:
        return path.resolve().relative_to(scan_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def iter_project_files(scan_root: Path) -> list[Path]:
    if not scan_root.exists():
        return []

    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(scan_root):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in EXCLUDED_DIRS and not name.startswith(".")
        )
        for filename in sorted(filenames):
            if filename == ".DS_Store":
                continue
            files.append(Path(dirpath) / filename)
    return files


def detect_file_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in DATABASE_EXTENSIONS:
        return "database"
    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".md":
        return "markdown"
    if suffix == ".py":
        return "python"
    if suffix == ".sh":
        return "shell"
    if suffix:
        return suffix.lstrip(".")
    return "file"


def is_data_doc(path: Path) -> bool:
    if path.suffix.lower() != ".md":
        return False
    lowered = path.as_posix().lower()
    return any(keyword in lowered for keyword in DATA_DOC_KEYWORDS)


def guess_purpose(path: Path) -> str:
    lowered = path.as_posix().lower()
    name = path.name.lower()

    if "billboard-hot-100.db" in lowered:
        return "Primary Billboard Hot 100 SQLite dataset."
    if "billboard-200-albums-charts.db" in lowered:
        return "Billboard 200 album chart history database."
    if "retroverse_year_master" in lowered:
        return "Consolidated year master JSON for multi-year issue context."
    if name.startswith("year_end_top_40_"):
        return "Year-end Top 40 song export by year."
    if name.startswith("cultural_events_"):
        return "Cultural events, film, and TV context by year."
    if "/artifacts/output/billboard/" in lowered:
        return "Derived Billboard analytics and summary outputs."
    if "/retroverse-magazine/issues/context/" in lowered:
        return "Generated issue context artifact."
    if "/retroverse-magazine/issues/" in lowered and "/art/" not in lowered:
        return "Issue-specific source or generated page content."
    if "/retroverse-magazine/prompts/" in lowered:
        return "Prompt template used for editorial or art generation."
    if "/retroverse-magazine/art_library/" in lowered or "/retroverse-magazine/art-library/" in lowered:
        return "Shared RetroVerse magazine artwork asset."
    if "/retroverse-magazine/issues/" in lowered and "/art/" in lowered:
        return "Issue-level artwork asset."
    if path.suffix.lower() == ".py":
        return "Python automation script."
    if path.suffix.lower() == ".sh":
        return "Shell automation script."
    if path.suffix.lower() in {".json", ".csv", ".yaml", ".yml"}:
        return "Structured project dataset or configuration."
    if path.suffix.lower() in DATABASE_EXTENSIONS:
        return "SQLite or database artifact."
    if path.suffix.lower() == ".md":
        return "Project documentation."
    return "Project file."


def make_row(path: Path, scan_root: Path) -> tuple[str, str, str, str]:
    rel_path = relative_to_scan_root(path, scan_root)
    return (path.name, rel_path, detect_file_type(path), guess_purpose(path))


def unique_sorted(paths: list[Path], scan_root: Path) -> list[Path]:
    seen: dict[str, Path] = {}
    for path in paths:
        seen[relative_to_scan_root(path, scan_root)] = path
    return [seen[key] for key in sorted(seen.keys())]


def format_table(rows: list[tuple[str, str, str, str]]) -> list[str]:
    if not rows:
        return ["_None found._", ""]
    lines = [
        "| File | Relative Path | Type | Purpose |",
        "|---|---|---|---|",
    ]
    for file_name, rel_path, file_type, purpose in rows:
        safe_purpose = purpose.replace("|", "\\|")
        lines.append(f"| `{file_name}` | `{rel_path}` | `{file_type}` | {safe_purpose} |")
    lines.append("")
    return lines


def collect_categories(scan_root: Path) -> dict[str, list[Path]]:
    all_files = iter_project_files(scan_root)

    data_files: list[Path] = []
    databases: list[Path] = []
    scripts: list[Path] = []
    generated_issues: list[Path] = []
    artwork_library: list[Path] = []
    prompt_templates: list[Path] = []

    for path in all_files:
        rel = relative_to_scan_root(path, scan_root)
        rel_lower = rel.lower()
        suffix = path.suffix.lower()
        parts = Path(rel).parts

        if suffix in DATA_EXTENSIONS or is_data_doc(path):
            data_files.append(path)
        if suffix in DATABASE_EXTENSIONS:
            databases.append(path)
        if suffix in SCRIPT_EXTENSIONS:
            scripts.append(path)

        if rel_lower.startswith("retroverse-magazine/issues/") and "/art/" not in rel_lower:
            generated_issues.append(path)
        if rel_lower.startswith("retroverse-magazine/art_library/") or rel_lower.startswith("retroverse-magazine/art-library/"):
            artwork_library.append(path)
        if rel_lower.startswith("retroverse-magazine/issues/") and "/art/" in rel_lower:
            artwork_library.append(path)

        if rel_lower.startswith("retroverse-magazine/prompts/"):
            prompt_templates.append(path)
        elif "prompt" in path.name.lower() and "retroverse-magazine" in parts:
            prompt_templates.append(path)

    return {
        "data_files": unique_sorted(data_files, scan_root),
        "databases": unique_sorted(databases, scan_root),
        "scripts": unique_sorted(scripts, scan_root),
        "generated_issues": unique_sorted(generated_issues, scan_root),
        "artwork_library": unique_sorted(artwork_library, scan_root),
        "prompt_templates": unique_sorted(prompt_templates, scan_root),
    }


def canonical_source_statuses(
    sources: dict[str, dict[str, Any]],
    scan_root: Path,
) -> tuple[list[tuple[str, str, str, str, str, str]], list[str]]:
    rows: list[tuple[str, str, str, str, str, str]] = []
    missing_required: list[str] = []

    for key in sorted(sources.keys()):
        entry = sources.get(key, {})
        path_text = str(entry.get("path", "")).strip()
        source_type = str(entry.get("type", "unknown"))
        required = bool(entry.get("required", False))
        description = str(entry.get("description", "")).strip() or "No description provided."

        if not path_text:
            status = "missing path in config"
            if required:
                missing_required.append(key)
            rows.append((key, "", status, source_type, str(required).lower(), description))
            continue

        matches = expand_path(path_text)
        if is_glob_pattern(path_text):
            status = f"{len(matches)} match(es)"
            if required and not matches:
                missing_required.append(key)
        else:
            target = matches[0]
            if source_type == "directory":
                exists = target.is_dir()
            else:
                exists = target.exists()
            status = f"exists ({relative_to_scan_root(target, scan_root)})" if exists else "missing"
            if required and not exists:
                missing_required.append(key)

        rows.append((key, path_text, status, source_type, str(required).lower(), description))

    return rows, missing_required


def project_structure_rows(scan_root: Path) -> list[tuple[str, str, str]]:
    candidates = [
        ("Magazine workspace", scan_root / "retroverse-magazine"),
        ("Raw datasets", scan_root / "raw-data"),
        ("RetroVerse output", scan_root / "retroverse-output"),
        ("Billboard analytics", scan_root / "artifacts" / "output" / "billboard"),
        ("Public data bundles", scan_root / "public" / "data"),
    ]
    rows: list[tuple[str, str, str]] = []
    for label, path in candidates:
        status = "exists" if path.exists() else "missing"
        rows.append((label, relative_to_scan_root(path, scan_root), status))
    return rows


def render_inventory_markdown(
    scan_root: Path,
    sources: dict[str, dict[str, Any]],
    source_notes: list[str],
    categories: dict[str, list[Path]],
) -> str:
    lines: list[str] = ["# RetroVerse Data Inventory", ""]

    lines.append("## Project Structure")
    lines.append("")
    lines.append("| Area | Relative Path | Status |")
    lines.append("|---|---|---|")
    for label, rel_path, status in project_structure_rows(scan_root):
        lines.append(f"| {label} | `{rel_path}` | {status} |")
    lines.append("")

    lines.append("## Canonical Data Sources")
    lines.append("")
    if sources:
        source_rows, missing_required = canonical_source_statuses(sources, scan_root)
        lines.append("| Source Key | Config Path | Status | Type | Required | Description |")
        lines.append("|---|---|---|---|---|---|")
        for key, path_text, status, source_type, required, description in source_rows:
            safe_desc = description.replace("|", "\\|")
            lines.append(
                f"| `{key}` | `{path_text}` | {status} | `{source_type}` | `{required}` | {safe_desc} |"
            )
        lines.append("")
        if missing_required:
            lines.append("Required canonical sources currently missing:")
            for key in missing_required:
                lines.append(f"- `{key}`")
            lines.append("")
    else:
        lines.append("_No canonical data source map found._")
        lines.append("")

    lines.append("## Data Files")
    lines.append("")
    lines.extend(format_table([make_row(path, scan_root) for path in categories["data_files"]]))

    lines.append("## Databases")
    lines.append("")
    lines.extend(format_table([make_row(path, scan_root) for path in categories["databases"]]))

    lines.append("## Scripts")
    lines.append("")
    lines.extend(format_table([make_row(path, scan_root) for path in categories["scripts"]]))

    lines.append("## Generated Issues")
    lines.append("")
    lines.extend(format_table([make_row(path, scan_root) for path in categories["generated_issues"]]))

    lines.append("## Artwork Library")
    lines.append("")
    lines.extend(format_table([make_row(path, scan_root) for path in categories["artwork_library"]]))

    lines.append("## Prompt Templates")
    lines.append("")
    lines.extend(format_table([make_row(path, scan_root) for path in categories["prompt_templates"]]))

    lines.append("## Observations")
    lines.append("")
    lines.append(f"- Scan root: `{scan_root.as_posix()}`")
    lines.append(
        "- File counts: "
        f"data={len(categories['data_files'])}, "
        f"db={len(categories['databases'])}, "
        f"scripts={len(categories['scripts'])}, "
        f"issues={len(categories['generated_issues'])}, "
        f"art={len(categories['artwork_library'])}, "
        f"prompts={len(categories['prompt_templates'])}"
    )
    lines.append(
        "- Excluded directories during scan: "
        + ", ".join(sorted(EXCLUDED_DIRS))
    )
    if source_notes:
        lines.append("- Source map notes:")
        for note in source_notes:
            lines.append(f"  - {note}")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    mode = "stdout" if args.stdout else "write"

    scan_root = DEFAULT_SCAN_ROOT if DEFAULT_SCAN_ROOT.exists() else PROJECT_ROOT.parent
    sources, source_notes = load_data_sources()
    categories = collect_categories(scan_root)
    markdown = render_inventory_markdown(scan_root, sources, source_notes, categories)

    if mode == "stdout":
        print(markdown)
        return 0

    INVENTORY_PATH.write_text(markdown + "\n", encoding="utf-8")
    print(f"Wrote data inventory: {INVENTORY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
