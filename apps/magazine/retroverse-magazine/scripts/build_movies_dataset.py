#!/usr/bin/env python3
"""Build the RetroVerse movies master dataset with provenance and trust labels."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import Any

from screen_culture_common import (
    MOVIE_MAJOR_FIELDS,
    WAREHOUSE_ROOT,
    append_dict_signal,
    append_list_with_trust,
    as_float,
    as_int,
    blank_movie_record,
    canonical_key,
    collect_enrichment_files,
    coverage_years,
    ensure_screen_culture_dirs,
    finalize_record,
    infer_source_profile,
    issue_movie_files,
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


MOVIES_MASTER_PATH = WAREHOUSE_ROOT / "movies_master.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build movies master dataset for screen/culture warehouse.")
    parser.add_argument("--stdout", action="store_true", help="Print summary as JSON in addition to normal logs.")
    return parser.parse_args()


def split_list_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        parts = [part.strip() for part in value.replace("|", ",").split(",")]
        return [part for part in parts if part]
    return []


def normalize_movie_row(row: dict[str, Any]) -> dict[str, Any]:
    title = str(
        row.get("title")
        or row.get("name")
        or row.get("movie")
        or row.get("film")
        or row.get("movie_title")
        or ""
    ).strip()
    year = parse_year(row.get("year") or row.get("release_year") or row.get("release_date") or row.get("date"))
    if not title or year is None:
        return {}

    return {
        "title": title,
        "year": year,
        "original_title": row.get("original_title"),
        "release_date": row.get("release_date") or row.get("date"),
        "genres": split_list_value(row.get("genres") or row.get("genre")),
        "runtime_minutes": as_int(row.get("runtime_minutes") or row.get("runtime") or row.get("length")),
        "country": row.get("country") or row.get("countries"),
        "language": row.get("language") or row.get("languages"),
        "director": row.get("director"),
        "principal_cast": split_list_value(row.get("principal_cast") or row.get("cast") or row.get("actors")),
        "studio": row.get("studio") or row.get("production_company"),
        "box_office_domestic": as_int(
            row.get("box_office_domestic")
            or row.get("domestic_box_office")
            or row.get("boxoffice_domestic")
        ),
        "box_office_worldwide": as_int(
            row.get("box_office_worldwide")
            or row.get("worldwide_box_office")
            or row.get("box_office")
        ),
        "imdb_rating": as_float(row.get("imdb_rating") or row.get("rating") or row.get("vote_average")),
        "imdb_votes": as_int(row.get("imdb_votes") or row.get("votes") or row.get("vote_count")),
        "critic_metacritic": as_int(row.get("metacritic") or row.get("critic_metacritic")),
        "critic_rotten_tomatoes": as_int(row.get("rotten_tomatoes") or row.get("critic_rotten_tomatoes")),
        "awards_summary": row.get("awards_summary") or row.get("awards"),
        "tmdb_id": row.get("tmdb_id"),
        "imdb_id": row.get("imdb_id"),
        "omdb_imdb_id": row.get("omdb_imdb_id") or row.get("imdbID"),
        "popularity": as_float(row.get("popularity") or row.get("popularity_score")),
        "rank": as_int(row.get("rank") or row.get("box_office_rank")),
        "source_title_note": row.get("note") or row.get("summary"),
    }


def rows_from_json(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path, default=None)
    if payload is None:
        return []

    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]

    if isinstance(payload, dict):
        if isinstance(payload.get("films"), list):
            rows = []
            year = parse_year(payload.get("year"))
            for item in payload["films"]:
                if isinstance(item, dict):
                    row = dict(item)
                    if year is not None and "year" not in row:
                        row["year"] = year
                    rows.append(row)
                elif isinstance(item, str):
                    rows.append({"title": item, "year": year})
            return rows

        if isinstance(payload.get("movies"), list):
            return [row for row in payload["movies"] if isinstance(row, dict)]

        if isinstance(payload.get("results"), list):
            return [row for row in payload["results"] if isinstance(row, dict)]

        if isinstance(payload.get("data"), list):
            return [row for row in payload["data"] if isinstance(row, dict)]

        # Year keyed dictionary support.
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
            if not ({"title", "name", "movie", "film"} & column_set):
                continue
            if not ({"year", "release_date", "date"} & column_set):
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


def apply_movie_fields(
    record: dict[str, Any],
    field_trust: dict[str, str],
    normalized: dict[str, Any],
    source: dict[str, Any],
) -> None:
    set_field_with_trust(record, field_trust, "title", normalized.get("title"), source)
    set_field_with_trust(record, field_trust, "year", normalized.get("year"), source)
    set_field_with_trust(record, field_trust, "original_title", normalized.get("original_title"), source)
    set_field_with_trust(record, field_trust, "release_date", normalized.get("release_date"), source)
    append_list_with_trust(record, field_trust, "genres", normalized.get("genres") or [], source)
    set_field_with_trust(record, field_trust, "runtime_minutes", normalized.get("runtime_minutes"), source)
    set_field_with_trust(record, field_trust, "country", normalized.get("country"), source)
    set_field_with_trust(record, field_trust, "language", normalized.get("language"), source)
    set_field_with_trust(record, field_trust, "director", normalized.get("director"), source)
    append_list_with_trust(record, field_trust, "principal_cast", normalized.get("principal_cast") or [], source)
    set_field_with_trust(record, field_trust, "studio", normalized.get("studio"), source)
    set_field_with_trust(record, field_trust, "box_office_domestic", normalized.get("box_office_domestic"), source)
    set_field_with_trust(record, field_trust, "box_office_worldwide", normalized.get("box_office_worldwide"), source)
    set_field_with_trust(record, field_trust, "imdb_rating", normalized.get("imdb_rating"), source)
    set_field_with_trust(record, field_trust, "imdb_votes", normalized.get("imdb_votes"), source)
    set_field_with_trust(record, field_trust, "critic_scores.metacritic", normalized.get("critic_metacritic"), source)
    set_field_with_trust(
        record,
        field_trust,
        "critic_scores.rotten_tomatoes",
        normalized.get("critic_rotten_tomatoes"),
        source,
    )
    set_field_with_trust(record, field_trust, "awards_summary", normalized.get("awards_summary"), source)

    set_field_with_trust(record, field_trust, "source_ids.tmdb_id", normalized.get("tmdb_id"), source)
    set_field_with_trust(record, field_trust, "source_ids.imdb_id", normalized.get("imdb_id"), source)
    set_field_with_trust(record, field_trust, "source_ids.omdb_imdb_id", normalized.get("omdb_imdb_id"), source)

    append_dict_signal(record, field_trust, "popularity_signals", "popularity_score", normalized.get("popularity"), source)
    append_dict_signal(record, field_trust, "popularity_signals", "rank", normalized.get("rank"), source)
    append_dict_signal(record, field_trust, "popularity_signals", "note", normalized.get("source_title_note"), source)


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
        films = culture.get("films")
        if not isinstance(films, list):
            continue

        for index, item in enumerate(films, start=1):
            title = item.get("title") if isinstance(item, dict) else item
            if not str(title or "").strip():
                continue

            key = find_existing_key(records, str(title), year) or canonical_key(str(title), year)
            if key not in records:
                records[key] = blank_movie_record(str(title), year)
                field_trust_map[key] = {}

            source = provenance_entry(
                source_name="RetroVerse year master",
                source_type="json",
                trust_level="canonical_local",
                source_identifier=f"{source_path.as_posix()}#{year}.culture.films[{index}]",
            )
            normalized = normalize_movie_row({"title": title, "year": year})
            apply_movie_fields(records[key], field_trust_map[key], normalized, source)
            append_dict_signal(records[key], field_trust_map[key], "popularity_signals", "year_master_rank", index, source)
            append_dict_signal(records[key], field_trust_map[key], "popularity_signals", "source_year", year, source)
            source_counts[source["source_name"]] = source_counts.get(source["source_name"], 0) + 1

    notes.append(f"Loaded year-master movies from {source_path}")
    return notes


def ingest_issue_movies(
    records: dict[str, dict[str, Any]],
    field_trust_map: dict[str, dict[str, str]],
    source_counts: dict[str, int],
) -> list[str]:
    notes: list[str] = []
    files = issue_movie_files()
    if not files:
        notes.append("No issue-level movies.json files found.")
        return notes

    for path in files:
        payload = read_json(path, default={})
        if not isinstance(payload, dict):
            continue

        year = parse_year(payload.get("year") or path.parent.parent.name)
        chart_name = str(payload.get("chart_name", "")).strip()
        films = payload.get("films")
        if year is None or not isinstance(films, list):
            continue

        for index, film in enumerate(films, start=1):
            if isinstance(film, dict):
                title = str(film.get("title", "")).strip()
                rank = as_int(film.get("rank")) or index
                note = str(film.get("note", "")).strip()
            else:
                title = str(film).strip()
                rank = index
                note = ""
            if not title:
                continue

            key = find_existing_key(records, title, year) or canonical_key(title, year)
            if key not in records:
                records[key] = blank_movie_record(title, year)
                field_trust_map[key] = {}

            source = provenance_entry(
                source_name="RetroVerse issue movies",
                source_type="json",
                trust_level="reference_derived",
                source_identifier=f"{path.as_posix()}#films[{index}]",
            )
            normalized = normalize_movie_row({"title": title, "year": year, "rank": rank, "note": note})
            apply_movie_fields(records[key], field_trust_map[key], normalized, source)
            append_dict_signal(records[key], field_trust_map[key], "popularity_signals", "issue_rank", rank, source)
            append_dict_signal(records[key], field_trust_map[key], "popularity_signals", "issue_chart", chart_name, source)
            if note:
                append_dict_signal(records[key], field_trust_map[key], "popularity_signals", "issue_note", note, source)
            source_counts[source["source_name"]] = source_counts.get(source["source_name"], 0) + 1

        notes.append(f"Loaded issue movie source: {path}")

    return notes


def ingest_enrichment_files(
    records: dict[str, dict[str, Any]],
    field_trust_map: dict[str, dict[str, str]],
    source_counts: dict[str, int],
) -> list[str]:
    notes: list[str] = []
    files = collect_enrichment_files("movies")
    if not files:
        notes.append("No local movie enrichment files detected under raw-data/screen-culture.")
        return notes

    for path in files:
        # Issue files and year master are already ingested explicitly.
        if path.name in {"movies_master.json", "movies_by_year.json", "screen_culture_inventory.json"}:
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
            normalized = normalize_movie_row(row)
            title = normalized.get("title")
            year = normalized.get("year")
            if not title or year is None:
                continue

            key = find_existing_key(records, str(title), int(year)) or canonical_key(str(title), int(year))
            if key not in records:
                records[key] = blank_movie_record(str(title), int(year))
                field_trust_map[key] = {}

            source = dict(source_base)
            source["source_identifier"] = f"{path.as_posix()}#{index}"
            apply_movie_fields(records[key], field_trust_map[key], normalized, source)
            source_counts[source_name] = source_counts.get(source_name, 0) + 1
            loaded += 1

        notes.append(f"Loaded {loaded} rows from enrichment source: {path}")

    return notes


def build_movies_dataset(write_output: bool = True) -> dict[str, Any]:
    ensure_screen_culture_dirs()

    records: dict[str, dict[str, Any]] = {}
    field_trust_map: dict[str, dict[str, str]] = {}
    notes: list[str] = []
    source_counts: dict[str, int] = {}

    notes.extend(ingest_year_master(records, field_trust_map, source_counts))
    notes.extend(ingest_issue_movies(records, field_trust_map, source_counts))
    notes.extend(ingest_enrichment_files(records, field_trust_map, source_counts))

    finalized: list[dict[str, Any]] = []
    for key in sorted(records.keys()):
        record = records[key]
        if not record.get("title"):
            continue
        trust_state = field_trust_map.get(key, {})
        finalized.append(finalize_record(record, trust_state, MOVIE_MAJOR_FIELDS))

    finalized = sort_records(finalized)

    min_year, max_year = coverage_years(finalized)
    popularity_count = sum(1 for row in finalized if row.get("popularity_signals"))
    critic_count = sum(
        1
        for row in finalized
        if (row.get("critic_scores", {}).get("metacritic") is not None)
        or (row.get("critic_scores", {}).get("rotten_tomatoes") is not None)
        or bool(str(row.get("awards_summary") or "").strip())
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
            "with_popularity_signals": popularity_count,
            "with_critic_or_acclaim": critic_count,
            "popularity_percent": round((popularity_count / len(finalized)) * 100, 2) if finalized else 0.0,
            "critic_or_acclaim_percent": round((critic_count / len(finalized)) * 100, 2) if finalized else 0.0,
        },
        "source_counts": dict(sorted(source_counts.items())),
        "notes": notes,
        "records": finalized,
    }

    if write_output:
        write_json(MOVIES_MASTER_PATH, payload)

    return payload


def main() -> int:
    args = parse_args()
    payload = build_movies_dataset(write_output=True)

    print("Movies dataset build complete")
    print(f"Output: {MOVIES_MASTER_PATH}")
    print(f"Records: {payload['record_count']}")
    print(
        "Years covered: "
        f"{payload['year_range']['min']} to {payload['year_range']['max']}"
    )
    print(f"With popularity signals: {payload['metrics']['with_popularity_signals']}")
    print(f"With critic/acclaim signals: {payload['metrics']['with_critic_or_acclaim']}")

    if args.stdout:
        import json

        print(json.dumps(payload, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
