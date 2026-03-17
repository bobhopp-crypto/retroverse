#!/usr/bin/env python3
"""Audit movies, television, and cultural event dataset coverage."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from glob import glob
from pathlib import Path
from typing import Any

from db_common import connect_read_only, list_tables, load_data_sources, project_relative, resolve_path, sql_year_expression, table_columns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_SOURCES_PATH = PROJECT_ROOT / "data" / "DATA_SOURCES.yaml"
AUDIT_REPORT_PATH = PROJECT_ROOT / "docs" / "SCREEN_CULTURE_DATA_AUDIT.md"

DATASETS = ("movies", "television", "cultural_events")
THRESHOLDS = {
    "movies": 10,
    "television": 15,
    "cultural_events": 8,
}

KEYWORDS = {
    "movies": ("movie", "movies", "film", "films", "cinema"),
    "television": ("television", "tv", "show", "shows", "series"),
    "cultural_events": ("culture", "cultural", "event", "events", "headline", "headlines"),
}

CATEGORY_KEYS = {
    "movies": ("movies", "films"),
    "television": ("television", "tv", "shows", "series"),
    "cultural_events": ("cultural_events", "events", "headlines", "culture"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit screen/culture dataset coverage.")
    parser.add_argument("--year", type=int, help="Optional single-year focus (example: 1978).")
    return parser.parse_args()


def empty_counts() -> dict[str, dict[str, int]]:
    return {dataset: {} for dataset in DATASETS}


def parse_year(value: Any) -> str | None:
    if value is None:
        return None
    match = re.search(r"(19|20)\d{2}", str(value))
    if not match:
        return None
    return match.group(0)


def infer_year_from_path(path: Path) -> str | None:
    return parse_year(path.name)


def add_count(counts: dict[str, dict[str, int]], dataset: str, year: str | None, amount: int) -> None:
    if dataset not in DATASETS or year is None:
        return
    if amount <= 0:
        return
    counts[dataset][year] = counts[dataset].get(year, 0) + amount


def merge_counts_max(target: dict[str, dict[str, int]], incoming: dict[str, dict[str, int]]) -> None:
    for dataset in DATASETS:
        for year, amount in incoming[dataset].items():
            target[dataset][year] = max(target[dataset].get(year, 0), int(amount))


def detect_dataset_hints(text: str) -> set[str]:
    lowered = text.lower()
    hints = set()
    for dataset, keywords in KEYWORDS.items():
        if any(word in lowered for word in keywords):
            hints.add(dataset)
    if "year_master" in lowered:
        hints.update(DATASETS)
    return hints


def resolve_entry_paths(path_text: str, source_type: str) -> list[Path]:
    expanded = Path(path_text).expanduser()
    if any(token in path_text for token in ("*", "?", "[")) or source_type.endswith("_glob"):
        if expanded.is_absolute():
            return [Path(item) for item in sorted(glob(str(expanded)))]
        return sorted(PROJECT_ROOT.glob(path_text))

    resolved = resolve_path(PROJECT_ROOT, path_text)
    if resolved.is_file():
        return [resolved]

    if resolved.is_dir():
        candidates: list[Path] = []
        for candidate in sorted(resolved.rglob("*")):
            if not candidate.is_file() or candidate.suffix.lower() not in {".json", ".csv", ".db", ".sqlite", ".sqlite3"}:
                continue
            name = candidate.name.lower()
            if any(word in name for keywords in KEYWORDS.values() for word in keywords):
                candidates.append(candidate)
        return candidates

    return []


def discover_sources(sources: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    discovered: list[dict[str, Any]] = []
    notes: list[str] = []

    for key in sorted(sources.keys()):
        entry = sources.get(key)
        if not isinstance(entry, dict):
            continue

        path_text = str(entry.get("path", "")).strip()
        if not path_text:
            continue

        source_type = str(entry.get("type", "file")).strip().lower()
        description = str(entry.get("description", "")).strip()
        hints = detect_dataset_hints(f"{key} {description} {path_text}")

        if not hints:
            continue

        paths = resolve_entry_paths(path_text, source_type)
        if not paths:
            notes.append(f"No matching files for source `{key}` at `{path_text}`.")
            continue

        for path in paths:
            discovered.append(
                {
                    "key": key,
                    "type": source_type,
                    "path": path,
                    "hints": set(hints),
                }
            )

    return discovered, notes


def count_list_items(value: Any) -> int:
    if not isinstance(value, list):
        return 0
    return sum(1 for item in value if str(item).strip())


def extract_counts_from_record(record: dict[str, Any], hints: set[str]) -> dict[str, int]:
    counts = {dataset: 0 for dataset in DATASETS}
    blocks: list[dict[str, Any]] = [record]

    culture_block = record.get("culture")
    if isinstance(culture_block, dict):
        blocks.append(culture_block)

    for block in blocks:
        if not isinstance(block, dict):
            continue
        for dataset, keys in CATEGORY_KEYS.items():
            if hints and dataset not in hints:
                continue
            best = 0
            for key in keys:
                value = block.get(key)
                candidate_count = count_list_items(value)
                if candidate_count > best:
                    best = candidate_count
            counts[dataset] = max(counts[dataset], best)

    return counts


def parse_json_counts(path: Path, hints: set[str]) -> dict[str, dict[str, int]]:
    counts = empty_counts()
    payload = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(payload, dict):
        root_year = parse_year(payload.get("year"))
        if root_year:
            extracted = extract_counts_from_record(payload, hints)
            for dataset, amount in extracted.items():
                add_count(counts, dataset, root_year, amount)

        for key, value in payload.items():
            year = parse_year(key)
            if year is None or not isinstance(value, dict):
                continue
            extracted = extract_counts_from_record(value, hints)
            for dataset, amount in extracted.items():
                add_count(counts, dataset, year, amount)

        if all(not bucket for bucket in counts.values()):
            inferred_year = infer_year_from_path(path)
            if inferred_year:
                extracted = extract_counts_from_record(payload, hints)
                for dataset, amount in extracted.items():
                    add_count(counts, dataset, inferred_year, amount)

    elif isinstance(payload, list):
        row_level_counted = False
        for row in payload:
            if not isinstance(row, dict):
                continue
            year = parse_year(row.get("year") or row.get("date") or row.get("chart_date") or row.get("issue_date"))
            if year is None:
                continue
            extracted = extract_counts_from_record(row, hints)
            for dataset, amount in extracted.items():
                add_count(counts, dataset, year, amount)
            row_level_counted = True

        if not row_level_counted:
            inferred_year = infer_year_from_path(path)
            if inferred_year:
                amount = count_list_items(payload)
                if hints:
                    for dataset in hints:
                        add_count(counts, dataset, inferred_year, amount)

    return counts


def infer_csv_dataset(path: Path, headers: list[str], hints: set[str]) -> str | None:
    haystack = f"{path.name.lower()} {' '.join(headers)}"
    if any(token in haystack for token in KEYWORDS["movies"]):
        return "movies"
    if any(token in haystack for token in KEYWORDS["television"]):
        return "television"
    if any(token in haystack for token in KEYWORDS["cultural_events"]):
        return "cultural_events"
    if len(hints) == 1:
        return next(iter(hints))
    return None


def parse_csv_counts(path: Path, hints: set[str]) -> tuple[dict[str, dict[str, int]], list[str]]:
    counts = empty_counts()
    notes: list[str] = []

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = [str(header or "").strip().lower() for header in (reader.fieldnames or [])]
        dataset = infer_csv_dataset(path, headers, hints)
        if dataset is None:
            notes.append(f"CSV skipped (could not infer dataset): {project_relative(PROJECT_ROOT, path)}")
            return counts, notes

        year_fields = [field for field in ("year", "date", "chart_date", "issue_date", "week", "chart_week") if field in headers]
        if not year_fields:
            notes.append(f"CSV skipped (no year-like column): {project_relative(PROJECT_ROOT, path)}")
            return counts, notes

        for row in reader:
            year = None
            for field in year_fields:
                year = parse_year(row.get(field))
                if year:
                    break
            if year:
                add_count(counts, dataset, year, 1)

    return counts, notes


def infer_sqlite_dataset(table: str, columns: list[str], hints: set[str]) -> str | None:
    haystack = f"{table.lower()} {' '.join(columns).lower()}"
    if any(token in haystack for token in KEYWORDS["movies"]):
        return "movies"
    if any(token in haystack for token in KEYWORDS["television"]):
        return "television"
    if any(token in haystack for token in KEYWORDS["cultural_events"]):
        return "cultural_events"
    if len(hints) == 1:
        return next(iter(hints))
    return None


def parse_sqlite_counts(path: Path, hints: set[str]) -> tuple[dict[str, dict[str, int]], list[str]]:
    counts = empty_counts()
    notes: list[str] = []

    with connect_read_only(path) as conn:
        for table in list_tables(conn):
            columns = table_columns(conn, table)
            dataset = infer_sqlite_dataset(table, columns, hints)
            if dataset is None:
                continue

            date_col = next(
                (
                    column
                    for column in ("year", "date", "chart_date", "issue_date", "chart_week", "week")
                    if column in columns
                ),
                None,
            )
            if date_col is None:
                continue

            year_expr = sql_year_expression(date_col)
            rows = conn.execute(
                f"""
                SELECT y, COUNT(*) AS c
                FROM (
                    SELECT {year_expr} AS y
                    FROM {table}
                )
                WHERE y GLOB '[12][0-9][0-9][0-9]'
                GROUP BY y
                ORDER BY y
                """
            ).fetchall()

            for row in rows:
                add_count(counts, dataset, str(row[0]), int(row[1]))

    if all(not bucket for bucket in counts.values()):
        notes.append(f"No screen/culture rows detected in DB: {project_relative(PROJECT_ROOT, path)}")

    return counts, notes


def parse_source(path: Path, hints: set[str]) -> tuple[dict[str, dict[str, int]], list[str]]:
    notes: list[str] = []
    counts = empty_counts()

    if not path.exists():
        notes.append(f"Missing source file: {project_relative(PROJECT_ROOT, path)}")
        return counts, notes

    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            counts = parse_json_counts(path, hints)
        elif suffix == ".csv":
            counts, extra = parse_csv_counts(path, hints)
            notes.extend(extra)
        elif suffix in {".db", ".sqlite", ".sqlite3"}:
            counts, extra = parse_sqlite_counts(path, hints)
            notes.extend(extra)
        else:
            notes.append(f"Unsupported source type skipped: {project_relative(PROJECT_ROOT, path)}")
    except (json.JSONDecodeError, csv.Error, OSError, sqlite3.Error) as exc:
        notes.append(f"Failed to parse {project_relative(PROJECT_ROOT, path)}: {exc}")

    return counts, notes


def evaluate_coverage(
    counts: dict[str, dict[str, int]],
    year_filter: int | None,
) -> tuple[dict[str, dict[str, str]], str, list[str]]:
    years = sorted(
        {
            year
            for dataset in DATASETS
            for year in counts[dataset]
            if re.fullmatch(r"(19|20)\d{2}", year)
        },
        key=int,
    )

    if year_filter is not None:
        year_text = str(year_filter)
        years = [year_text]

    statuses: dict[str, dict[str, str]] = {}
    warnings: list[str] = []
    overall = "OK"

    for year in years:
        statuses[year] = {}
        low: list[str] = []
        for dataset in DATASETS:
            current = counts[dataset].get(year, 0)
            status = "OK" if current >= THRESHOLDS[dataset] else "LOW"
            statuses[year][dataset] = status
            if status == "LOW":
                low.append(dataset)

        if low:
            overall = "INCOMPLETE"
            warnings.append(f"Year {year}: below threshold for {', '.join(low)}")

    if not years:
        overall = "INCOMPLETE"
        warnings.append("No year-tagged movie/television/cultural entries were detected.")

    return statuses, overall, warnings


def render_console(counts: dict[str, dict[str, int]], statuses: dict[str, dict[str, str]], overall: str) -> str:
    years = sorted(statuses.keys(), key=lambda value: int(value) if value.isdigit() else value)
    labels = {
        "movies": "Movies dataset",
        "television": "Television dataset",
        "cultural_events": "Cultural events dataset",
    }

    lines: list[str] = ["## Screen & Culture Dataset Audit", ""]
    for dataset in DATASETS:
        lines.append(f"{labels[dataset]}:")
        if not years:
            lines.append("No year-tagged entries found.")
        else:
            for year in years:
                lines.append(
                    f"{year}: {counts[dataset].get(year, 0)} entries ({statuses[year].get(dataset, 'LOW')})"
                )
        lines.append("")

    lines.append(f"Overall coverage status: {overall}")
    return "\n".join(lines)


def render_markdown(
    discovered_sources: list[dict[str, Any]],
    parse_notes: list[str],
    counts: dict[str, dict[str, int]],
    statuses: dict[str, dict[str, str]],
    overall: str,
    warnings: list[str],
) -> str:
    years = sorted(statuses.keys(), key=lambda value: int(value) if value.isdigit() else value)

    lines: list[str] = [
        "# Screen & Culture Data Audit",
        "",
        f"Overall coverage status: {overall}",
        "",
        "## Thresholds",
        "",
        f"- Movies: >= {THRESHOLDS['movies']}",
        f"- Television: >= {THRESHOLDS['television']}",
        f"- Cultural events: >= {THRESHOLDS['cultural_events']}",
        "",
        "## Source Detection",
        "",
    ]

    if discovered_sources:
        for source in discovered_sources:
            rel_path = project_relative(PROJECT_ROOT, source["path"])
            hinted = ", ".join(sorted(source["hints"]))
            lines.append(f"- `{source['key']}` ({source['type']}): `{rel_path}` [targets: {hinted}]")
    else:
        lines.append("- No relevant screen/culture sources were discovered from DATA_SOURCES.yaml.")

    lines.extend(["", "## Per-Year Counts", ""])
    if years:
        for year in years:
            movie_count = counts["movies"].get(year, 0)
            television_count = counts["television"].get(year, 0)
            event_count = counts["cultural_events"].get(year, 0)

            lines.append(f"### Year: {year}")
            lines.append("")
            lines.append(f"- Movies: {movie_count} ({statuses[year]['movies']})")
            lines.append(f"- Television: {television_count} ({statuses[year]['television']})")
            lines.append(f"- Cultural events: {event_count} ({statuses[year]['cultural_events']})")
            lines.append("")

            if all(statuses[year][dataset] == "OK" for dataset in DATASETS):
                lines.append("Recommendation: Coverage is adequate for editorial planning.")
            else:
                low = [dataset for dataset in DATASETS if statuses[year][dataset] != "OK"]
                lines.append(f"Recommendation: Expand {', '.join(low)} for this year.")
            lines.append("")
    else:
        lines.append("No year-tagged entries were found.")
        lines.append("")

    lines.append("## Coverage Warnings")
    lines.append("")
    if warnings:
        for item in warnings:
            lines.append(f"- {item}")
    else:
        lines.append("- No threshold warnings detected.")
    lines.append("")

    lines.append("## Dataset Gaps")
    lines.append("")
    if overall == "OK":
        lines.append("- No major gaps detected for evaluated years.")
    else:
        lines.append("- Coverage remains incomplete for at least one required category/year.")
    lines.append("")

    if parse_notes:
        lines.append("## Parsing Notes")
        lines.append("")
        for note in parse_notes:
            lines.append(f"- {note}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def run(year_filter: int | None) -> tuple[str, dict[str, dict[str, int]], dict[str, dict[str, str]], list[str], list[dict[str, Any]]]:
    sources = load_data_sources(DATA_SOURCES_PATH)
    discovered_sources, notes = discover_sources(sources)

    merged_counts = empty_counts()
    for source in discovered_sources:
        local_counts, local_notes = parse_source(source["path"], source["hints"])
        merge_counts_max(merged_counts, local_counts)
        notes.extend(local_notes)

    statuses, overall, warnings = evaluate_coverage(merged_counts, year_filter)

    AUDIT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_REPORT_PATH.write_text(
        render_markdown(discovered_sources, notes, merged_counts, statuses, overall, warnings),
        encoding="utf-8",
    )

    return overall, merged_counts, statuses, notes, discovered_sources


def main() -> int:
    args = parse_args()
    overall, counts, statuses, _notes, _sources = run(args.year)

    print(render_console(counts, statuses, overall))
    print(f"Audit report written: {project_relative(PROJECT_ROOT, AUDIT_REPORT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
