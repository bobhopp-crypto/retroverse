#!/usr/bin/env python3
"""Build the RetroVerse television master dataset with provenance and trust labels."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from screen_culture_common import (
    RETROVERSE_ROOT,
    TELEVISION_MAJOR_FIELDS,
    WAREHOUSE_ROOT,
    append_dict_signal,
    append_list_with_trust,
    as_float,
    as_int,
    blank_television_record,
    canonical_key,
    collect_enrichment_files,
    coverage_years,
    ensure_screen_culture_dirs,
    finalize_record,
    infer_source_profile,
    issue_television_files,
    normalize_title,
    now_utc_iso,
    parse_year,
    provenance_entry,
    read_json,
    set_field_with_trust,
    similar_title_match,
    sort_records,
    trust_distribution,
    write_json,
    year_master_path,
)


TELEVISION_MASTER_PATH = WAREHOUSE_ROOT / "television_master.json"
TV_LISTINGS_PATH = RETROVERSE_ROOT / "data" / "processed" / "tv_listings.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build television master dataset for screen/culture warehouse.")
    parser.add_argument("--stdout", action="store_true", help="Print summary payload as JSON.")
    return parser.parse_args()


def split_list_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        parts = [part.strip() for part in value.replace("|", ",").split(",")]
        return [part for part in parts if part]
    return []


def normalize_tv_row(row: dict[str, Any]) -> dict[str, Any]:
    title = str(
        row.get("title")
        or row.get("name")
        or row.get("show")
        or row.get("program")
        or row.get("series")
        or ""
    ).strip()
    year = parse_year(
        row.get("year")
        or row.get("premiere_year")
        or row.get("premiere_date")
        or row.get("date")
        or row.get("air_date")
    )
    if not title or year is None:
        return {}

    return {
        "title": title,
        "year": year,
        "premiere_date": row.get("premiere_date") or row.get("first_air_date"),
        "end_date": row.get("end_date") or row.get("last_air_date"),
        "genres": split_list_value(row.get("genres") or row.get("genre")),
        "type": row.get("type") or row.get("format") or row.get("kind"),
        "network": row.get("network") or row.get("channel"),
        "seasons": as_int(row.get("seasons") or row.get("season_count")),
        "episodes": as_int(row.get("episodes") or row.get("episode_count")),
        "principal_cast": split_list_value(row.get("principal_cast") or row.get("cast") or row.get("actors")),
        "creators": split_list_value(row.get("creators") or row.get("creator")),
        "viewership": as_float(row.get("viewership") or row.get("viewers") or row.get("audience")),
        "popularity": as_float(row.get("popularity") or row.get("popularity_score")),
        "rating": as_float(row.get("rating") or row.get("imdb_rating")),
        "votes": as_int(row.get("votes") or row.get("imdb_votes") or row.get("vote_count")),
        "metacritic": as_int(row.get("metacritic") or row.get("critic_metacritic")),
        "rotten_tomatoes": as_int(row.get("rotten_tomatoes") or row.get("critic_rotten_tomatoes")),
        "awards_summary": row.get("awards_summary") or row.get("awards"),
        "tmdb_id": row.get("tmdb_id"),
        "imdb_id": row.get("imdb_id"),
    }


def rows_from_json(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path, default=None)
    if payload is None:
        return []

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        if isinstance(payload.get("shows"), list):
            year = parse_year(payload.get("year"))
            rows: list[dict[str, Any]] = []
            for item in payload["shows"]:
                if isinstance(item, dict):
                    row = dict(item)
                    row.setdefault("year", year)
                    rows.append(row)
                elif isinstance(item, str):
                    rows.append({"title": item, "year": year})
            return rows

        for key in ("television", "tv", "results", "data"):
            if isinstance(payload.get(key), list):
                return [item for item in payload[key] if isinstance(item, dict)]

        rows: list[dict[str, Any]] = []
        for key, value in payload.items():
            year = parse_year(key)
            if year is None:
                continue
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        row = dict(item)
                        row.setdefault("year", year)
                        rows.append(row)
                    elif isinstance(item, str):
                        rows.append({"title": item, "year": year})
        if rows:
            return rows

    return []


def rows_from_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append({str(key): value for key, value in row.items()})
    return rows


def rows_from_sqlite(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        table_rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        for table_row in table_rows:
            table = str(table_row[0])
            columns = [str(col[1]) for col in conn.execute(f"PRAGMA table_info({table})").fetchall()]
            column_set = {column.lower() for column in columns}
            if not ({"title", "name", "show", "program", "series"} & column_set):
                continue
            if not ({"year", "premiere_date", "date", "air_date"} & column_set):
                continue

            selected = ", ".join(columns)
            query_rows = conn.execute(f"SELECT {selected} FROM {table}").fetchall()
            for query_row in query_rows:
                rows.append({key: query_row[key] for key in query_row.keys()})
    finally:
        conn.close()
    return rows


def find_existing_key(records: dict[str, dict[str, Any]], title: str, year: int | None) -> str | None:
    if not title or year is None:
        return None

    target = canonical_key(title, year)
    if target in records:
        return target

    for key, record in records.items():
        record_year = parse_year(record.get("year"))
        if record_year != year:
            continue
        if similar_title_match(title, record.get("title")):
            return key
    return None


def apply_television_fields(
    record: dict[str, Any],
    field_trust: dict[str, str],
    normalized: dict[str, Any],
    source: dict[str, Any],
) -> None:
    set_field_with_trust(record, field_trust, "title", normalized.get("title"), source)
    set_field_with_trust(record, field_trust, "year", normalized.get("year"), source)
    set_field_with_trust(record, field_trust, "premiere_date", normalized.get("premiere_date"), source)
    set_field_with_trust(record, field_trust, "end_date", normalized.get("end_date"), source)
    append_list_with_trust(record, field_trust, "genres", normalized.get("genres") or [], source)
    set_field_with_trust(record, field_trust, "type", normalized.get("type"), source)
    set_field_with_trust(record, field_trust, "network", normalized.get("network"), source)
    set_field_with_trust(record, field_trust, "seasons", normalized.get("seasons"), source)
    set_field_with_trust(record, field_trust, "episodes", normalized.get("episodes"), source)
    append_list_with_trust(record, field_trust, "principal_cast", normalized.get("principal_cast") or [], source)
    append_list_with_trust(record, field_trust, "creators", normalized.get("creators") or [], source)

    append_dict_signal(record, field_trust, "viewership_signals", "viewership", normalized.get("viewership"), source)
    append_dict_signal(record, field_trust, "viewership_signals", "popularity_score", normalized.get("popularity"), source)
    append_dict_signal(record, field_trust, "ratings_signals", "rating", normalized.get("rating"), source)
    append_dict_signal(record, field_trust, "ratings_signals", "votes", normalized.get("votes"), source)
    append_dict_signal(record, field_trust, "critic_scores", "metacritic", normalized.get("metacritic"), source)
    append_dict_signal(record, field_trust, "critic_scores", "rotten_tomatoes", normalized.get("rotten_tomatoes"), source)
    set_field_with_trust(record, field_trust, "awards_summary", normalized.get("awards_summary"), source)

    set_field_with_trust(record, field_trust, "source_ids.tmdb_id", normalized.get("tmdb_id"), source)
    set_field_with_trust(record, field_trust, "source_ids.imdb_id", normalized.get("imdb_id"), source)


def ingest_year_master(
    records: dict[str, dict[str, Any]],
    field_trust_map: dict[str, dict[str, str]],
    source_counts: dict[str, int],
) -> list[str]:
    notes: list[str] = []
    source_path = year_master_path()
    if source_path is None:
        notes.append("Year master JSON source not found.")
        return notes

    payload = read_json(source_path, default={})
    if not isinstance(payload, dict):
        notes.append(f"Year master JSON is not a dictionary: {source_path}")
        return notes

    for year_key, year_payload in payload.items():
        year = parse_year(year_key)
        if year is None or not isinstance(year_payload, dict):
            continue

        culture = year_payload.get("culture")
        if not isinstance(culture, dict):
            continue

        shows = culture.get("tv")
        if not isinstance(shows, list):
            continue

        for index, item in enumerate(shows, start=1):
            title = item.get("title") if isinstance(item, dict) else item
            if not str(title or "").strip():
                continue

            key = find_existing_key(records, str(title), year) or canonical_key(str(title), year)
            if key not in records:
                records[key] = blank_television_record(str(title), year)
                field_trust_map[key] = {}

            source = provenance_entry(
                source_name="RetroVerse year master",
                source_type="json",
                trust_level="canonical_local",
                source_identifier=f"{source_path.as_posix()}#{year}.culture.tv[{index}]",
            )
            normalized = normalize_tv_row({"title": title, "year": year})
            apply_television_fields(records[key], field_trust_map[key], normalized, source)
            append_dict_signal(records[key], field_trust_map[key], "viewership_signals", "year_master_rank", index, source)
            source_counts[source["source_name"]] = source_counts.get(source["source_name"], 0) + 1

    notes.append(f"Loaded year-master television from {source_path}")
    return notes


def ingest_issue_television(
    records: dict[str, dict[str, Any]],
    field_trust_map: dict[str, dict[str, str]],
    source_counts: dict[str, int],
) -> list[str]:
    notes: list[str] = []
    files = issue_television_files()
    if not files:
        notes.append("No issue-level tv.json files found.")
        return notes

    for path in files:
        payload = read_json(path, default={})
        if not isinstance(payload, dict):
            continue

        year = parse_year(payload.get("year") or path.parent.parent.name)
        shows = payload.get("shows")
        if year is None or not isinstance(shows, list):
            continue

        for index, show in enumerate(shows, start=1):
            if isinstance(show, dict):
                title = str(show.get("title", "")).strip()
                network = str(show.get("network", "")).strip()
                note = str(show.get("note", "")).strip()
            else:
                title = str(show).strip()
                network = ""
                note = ""
            if not title:
                continue

            key = find_existing_key(records, title, year) or canonical_key(title, year)
            if key not in records:
                records[key] = blank_television_record(title, year)
                field_trust_map[key] = {}

            source = provenance_entry(
                source_name="RetroVerse issue television",
                source_type="json",
                trust_level="reference_derived",
                source_identifier=f"{path.as_posix()}#shows[{index}]",
            )
            normalized = normalize_tv_row({"title": title, "year": year, "network": network})
            apply_television_fields(records[key], field_trust_map[key], normalized, source)
            append_dict_signal(records[key], field_trust_map[key], "viewership_signals", "issue_rank", index, source)
            if note:
                append_dict_signal(records[key], field_trust_map[key], "viewership_signals", "issue_note", note, source)
            source_counts[source["source_name"]] = source_counts.get(source["source_name"], 0) + 1

        notes.append(f"Loaded issue television source: {path}")

    return notes


def load_tv_listings_reference() -> list[dict[str, Any]]:
    if not TV_LISTINGS_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    with TV_LISTINGS_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append({str(key): value for key, value in row.items()})
    return rows


def ingest_tv_listings_reference(
    records: dict[str, dict[str, Any]],
    field_trust_map: dict[str, dict[str, str]],
    source_counts: dict[str, int],
) -> list[str]:
    rows = load_tv_listings_reference()
    if not rows:
        return ["TV listings reference file missing or empty."]

    by_year_programs: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        year = parse_year(row.get("date"))
        if year is None:
            continue
        by_year_programs[year].append(row)

    updates = 0
    for key, record in records.items():
        year = parse_year(record.get("year"))
        title = str(record.get("title", "")).strip()
        if year is None or not title:
            continue

        target = normalize_title(title)
        if not target:
            continue

        year_rows = by_year_programs.get(year, [])
        if not year_rows:
            continue

        matches = []
        network_counter: Counter[str] = Counter()
        for row in year_rows:
            program = str(row.get("program", "")).strip()
            if not program:
                continue
            normalized_program = normalize_title(program)
            if not normalized_program:
                continue

            if target in normalized_program or normalized_program in target:
                matches.append(row)
                network = str(row.get("network", "")).strip()
                if network:
                    network_counter[network.upper()] += 1

        if not matches:
            continue

        source = provenance_entry(
            source_name="Internet Archive TV listings",
            source_type="csv",
            trust_level="reference_derived",
            source_identifier=TV_LISTINGS_PATH.as_posix(),
            source_url="https://archive.org/",
        )
        append_dict_signal(record, field_trust_map[key], "viewership_signals", "tv_listing_mentions", len(matches), source)

        if network_counter:
            best_network = network_counter.most_common(1)[0][0]
            set_field_with_trust(record, field_trust_map[key], "network", best_network, source)

        source_counts[source["source_name"]] = source_counts.get(source["source_name"], 0) + 1
        updates += 1

    return [f"TV listings reference matched {updates} television records."]


def ingest_enrichment_files(
    records: dict[str, dict[str, Any]],
    field_trust_map: dict[str, dict[str, str]],
    source_counts: dict[str, int],
) -> list[str]:
    notes: list[str] = []
    files = collect_enrichment_files("television")
    if not files:
        notes.append("No local television enrichment files detected under raw-data/screen-culture.")
        return notes

    for path in files:
        if path.name in {"television_master.json", "television_by_year.json", "screen_culture_inventory.json"}:
            continue

        source_name, source_type, trust_level = infer_source_profile(path)
        source_base = provenance_entry(
            source_name=source_name,
            source_type=source_type,
            trust_level=trust_level,
            source_identifier=path.as_posix(),
        )

        rows: list[dict[str, Any]] = []
        try:
            if path.suffix.lower() == ".json":
                rows = rows_from_json(path)
            elif path.suffix.lower() == ".csv":
                rows = rows_from_csv(path)
            elif path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}:
                rows = rows_from_sqlite(path)
            else:
                continue
        except (OSError, csv.Error, sqlite3.Error):
            notes.append(f"Failed to read enrichment file: {path}")
            continue

        loaded = 0
        for index, row in enumerate(rows, start=1):
            normalized = normalize_tv_row(row)
            title = normalized.get("title")
            year = normalized.get("year")
            if not title or year is None:
                continue

            key = find_existing_key(records, str(title), int(year)) or canonical_key(str(title), int(year))
            if key not in records:
                records[key] = blank_television_record(str(title), int(year))
                field_trust_map[key] = {}

            source = dict(source_base)
            source["source_identifier"] = f"{path.as_posix()}#{index}"
            apply_television_fields(records[key], field_trust_map[key], normalized, source)
            source_counts[source_name] = source_counts.get(source_name, 0) + 1
            loaded += 1

        notes.append(f"Loaded {loaded} rows from enrichment source: {path}")

    return notes


def build_television_dataset(write_output: bool = True) -> dict[str, Any]:
    ensure_screen_culture_dirs()

    records: dict[str, dict[str, Any]] = {}
    field_trust_map: dict[str, dict[str, str]] = {}
    notes: list[str] = []
    source_counts: dict[str, int] = {}

    notes.extend(ingest_year_master(records, field_trust_map, source_counts))
    notes.extend(ingest_issue_television(records, field_trust_map, source_counts))
    notes.extend(ingest_tv_listings_reference(records, field_trust_map, source_counts))
    notes.extend(ingest_enrichment_files(records, field_trust_map, source_counts))

    finalized: list[dict[str, Any]] = []
    for key in sorted(records.keys()):
        record = records[key]
        if not record.get("title"):
            continue
        trust_state = field_trust_map.get(key, {})
        finalized.append(finalize_record(record, trust_state, TELEVISION_MAJOR_FIELDS))

    finalized = sort_records(finalized)

    min_year, max_year = coverage_years(finalized)
    with_network = sum(1 for row in finalized if str(row.get("network") or "").strip())
    with_popularity = sum(
        1
        for row in finalized
        if bool(row.get("viewership_signals")) or bool(row.get("ratings_signals"))
    )
    with_critic = sum(
        1
        for row in finalized
        if bool(row.get("critic_scores")) or bool(str(row.get("awards_summary") or "").strip())
    )

    payload = {
        "generated_at_utc": now_utc_iso(),
        "record_count": len(finalized),
        "year_range": {
            "min": min_year,
            "max": max_year,
        },
        "trust_distribution": trust_distribution(finalized),
        "metrics": {
            "with_network": with_network,
            "with_popularity_or_viewership": with_popularity,
            "with_critic_or_acclaim": with_critic,
            "network_percent": round((with_network / len(finalized)) * 100, 2) if finalized else 0.0,
            "popularity_percent": round((with_popularity / len(finalized)) * 100, 2) if finalized else 0.0,
            "critic_or_acclaim_percent": round((with_critic / len(finalized)) * 100, 2) if finalized else 0.0,
        },
        "source_counts": dict(sorted(source_counts.items())),
        "notes": notes,
        "records": finalized,
    }

    if write_output:
        write_json(TELEVISION_MASTER_PATH, payload)

    return payload


def main() -> int:
    args = parse_args()
    payload = build_television_dataset(write_output=True)

    print("Television dataset build complete")
    print(f"Output: {TELEVISION_MASTER_PATH}")
    print(f"Records: {payload['record_count']}")
    print(f"Years covered: {payload['year_range']['min']} to {payload['year_range']['max']}")
    print(f"With network: {payload['metrics']['with_network']}")
    print(f"With popularity/viewership: {payload['metrics']['with_popularity_or_viewership']}")
    print(f"With critic/acclaim: {payload['metrics']['with_critic_or_acclaim']}")

    if args.stdout:
        import json

        print(json.dumps(payload, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
