#!/usr/bin/env python3
"""Enrich screen/culture warehouse records with OMDb critic/acclaim metadata."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from screen_culture_common import (
    MOVIE_MAJOR_FIELDS,
    TELEVISION_MAJOR_FIELDS,
    WAREHOUSE_ROOT,
    build_by_year,
    coverage_years,
    finalize_record,
    get_nested,
    has_value,
    now_utc_iso,
    provenance_entry,
    read_json,
    register_provenance,
    set_nested,
    trust_distribution,
    write_json,
    write_sqlite_json_table,
)


OMDB_BASE_URL = "http://www.omdbapi.com/"
DEFAULT_SLEEP_SECONDS = 0.2

MOVIES_MASTER_PATH = WAREHOUSE_ROOT / "movies_master.json"
TELEVISION_MASTER_PATH = WAREHOUSE_ROOT / "television_master.json"
MOVIES_BY_YEAR_PATH = WAREHOUSE_ROOT / "movies_by_year.json"
TELEVISION_BY_YEAR_PATH = WAREHOUSE_ROOT / "television_by_year.json"
INVENTORY_PATH = WAREHOUSE_ROOT / "screen_culture_inventory.json"
SQLITE_PATH = WAREHOUSE_ROOT / "screen_culture.db"

load_dotenv(dotenv_path=".env")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")


@dataclass
class EnrichmentCounts:
    movies_enriched_with_critic_scores: int = 0
    television_enriched_with_critic_scores: int = 0
    movies_with_box_office_values_added: int = 0
    awards_fields_added: int = 0
    omdb_calls: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enrich warehouse metadata with OMDb API.")
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS, help="Delay between OMDb requests.")
    parser.add_argument("--max-movies", type=int, default=0, help="Optional movie processing limit (0 = all).")
    parser.add_argument("--max-television", type=int, default=0, help="Optional TV processing limit (0 = all).")
    return parser.parse_args()


def parse_year(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value)
    for token in text.replace("/", "-").split("-"):
        token = token.strip()
        if len(token) == 4 and token.isdigit():
            return int(token)
    return None


def parse_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "N/A":
        return None
    text = text.replace(",", "")
    if text.endswith("%"):
        text = text[:-1]
    if "/" in text:
        text = text.split("/", 1)[0]
    try:
        return int(float(text))
    except ValueError:
        return None


def parse_box_office(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "N/A":
        return None
    text = text.replace("$", "").replace(",", "").strip()
    try:
        return int(text)
    except ValueError:
        return None


def derive_field_trust(record: dict[str, Any]) -> dict[str, str]:
    provenance_fields = record.get("provenance", {}).get("fields", {})
    if not isinstance(provenance_fields, dict):
        return {}

    trust_map: dict[str, str] = {}
    rank = {
        "missing": 0,
        "reference_derived": 1,
        "direct_api": 2,
        "licensed_or_official": 3,
        "canonical_local": 4,
    }
    for field_name, entries in provenance_fields.items():
        strongest = "missing"
        if isinstance(entries, list):
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                level = str(entry.get("trust_level", "missing"))
                if rank.get(level, 0) >= rank.get(strongest, 0):
                    strongest = level
        trust_map[field_name] = strongest
    return trust_map


def set_if_empty(
    record: dict[str, Any],
    field: str,
    value: Any,
    source: dict[str, Any],
    field_trust: dict[str, str],
) -> bool:
    register_provenance(record, field, source)
    if not has_value(value):
        return False
    current = get_nested(record, field)
    if has_value(current):
        return False
    set_nested(record, field, value)
    field_trust[field] = str(source.get("trust_level", "direct_api"))
    return True


def has_existing_critic_scores(record: dict[str, Any]) -> bool:
    critic = record.get("critic_scores")
    if not isinstance(critic, dict):
        return False

    return any(
        has_value(critic.get(field))
        for field in (
            "rotten_tomatoes",
            "metacritic",
            "metascore",
        )
    )


def omdb_request(api_key: str, params: dict[str, Any], sleep_seconds: float) -> dict[str, Any]:
    query = dict(params)
    query["apikey"] = api_key
    query["r"] = "json"

    url = f"{OMDB_BASE_URL}?{urllib.parse.urlencode(query)}"
    time.sleep(max(0.0, sleep_seconds))
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def extract_critic_fields(payload: dict[str, Any]) -> dict[str, int | None]:
    rotten = None
    metacritic = None

    ratings = payload.get("Ratings")
    if isinstance(ratings, list):
        for rating_row in ratings:
            if not isinstance(rating_row, dict):
                continue
            source = str(rating_row.get("Source", "")).strip().lower()
            value = rating_row.get("Value")
            if source == "rotten tomatoes":
                rotten = parse_int(value)
            elif source == "metacritic":
                metacritic = parse_int(value)

    metascore = parse_int(payload.get("Metascore"))

    if metacritic is None and metascore is not None:
        metacritic = metascore

    return {
        "rotten_tomatoes": rotten,
        "metacritic": metacritic,
        "metascore": metascore,
    }


def load_payload(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    if not isinstance(payload, dict):
        raise FileNotFoundError(f"Warehouse file unreadable: {path}")
    records = payload.get("records")
    if not isinstance(records, list):
        raise FileNotFoundError(f"Warehouse records missing in: {path}")
    payload["records"] = [row for row in records if isinstance(row, dict)]
    return payload


def enrich_record(
    record: dict[str, Any],
    medium: str,
    api_key: str,
    sleep_seconds: float,
    counts: EnrichmentCounts,
) -> bool:
    if has_existing_critic_scores(record):
        return False

    title = str(record.get("title") or "").strip()
    if not title:
        return False
    year = parse_year(record.get("year"))

    source_ids = record.setdefault("source_ids", {})
    imdb_id = str(source_ids.get("imdb_id") or source_ids.get("omdb_imdb_id") or "").strip()

    query_params: dict[str, Any]
    if imdb_id:
        query_params = {"i": imdb_id}
    else:
        query_params = {"t": title}
        if year is not None:
            query_params["y"] = year

    try:
        payload = omdb_request(api_key, query_params, sleep_seconds)
    except Exception:
        return False

    counts.omdb_calls += 1
    if str(payload.get("Response", "")).strip().lower() != "true":
        return False

    critic_fields = extract_critic_fields(payload)
    box_office = parse_box_office(payload.get("BoxOffice"))
    awards_summary = str(payload.get("Awards") or "").strip()
    if awards_summary.upper() == "N/A":
        awards_summary = ""

    source = provenance_entry(
        source_name="omdb_api",
        source_type="api",
        trust_level="direct_api",
        source_url="http://www.omdbapi.com/",
        source_identifier=imdb_id or f"{title}:{year or ''}",
    )
    field_trust = derive_field_trust(record)

    changed = False
    critic_added = False

    if set_if_empty(record, "critic_scores.rotten_tomatoes", critic_fields["rotten_tomatoes"], source, field_trust):
        changed = True
        critic_added = True
    if set_if_empty(record, "critic_scores.metacritic", critic_fields["metacritic"], source, field_trust):
        changed = True
        critic_added = True
    if set_if_empty(record, "critic_scores.metascore", critic_fields["metascore"], source, field_trust):
        changed = True
        critic_added = True

    if set_if_empty(record, "awards_summary", awards_summary, source, field_trust):
        counts.awards_fields_added += 1
        changed = True

    if medium == "movies":
        if set_if_empty(record, "box_office_domestic", box_office, source, field_trust):
            counts.movies_with_box_office_values_added += 1
            changed = True

    if imdb_id:
        # Preserve OMDb source identifier for title-based fallback only if not present.
        set_if_empty(record, "source_ids.omdb_imdb_id", imdb_id, source, field_trust)

    if medium == "movies":
        finalize_record(record, field_trust, MOVIE_MAJOR_FIELDS)
        if critic_added:
            counts.movies_enriched_with_critic_scores += 1
    else:
        finalize_record(record, field_trust, TELEVISION_MAJOR_FIELDS)
        if critic_added:
            counts.television_enriched_with_critic_scores += 1

    return changed


def refresh_payload_metrics(payload: dict[str, Any], medium: str) -> None:
    records = payload.get("records", [])
    if not isinstance(records, list):
        return

    payload["generated_at_utc"] = now_utc_iso()
    payload["record_count"] = len(records)
    min_year, max_year = coverage_years(records)
    payload["year_range"] = {"min": min_year, "max": max_year}
    payload["trust_distribution"] = trust_distribution(records)

    with_critic_or_acclaim = sum(
        1
        for row in records
        if (
            isinstance(row.get("critic_scores"), dict)
            and any(
                has_value(row.get("critic_scores", {}).get(field))
                for field in ("rotten_tomatoes", "metacritic", "metascore")
            )
        )
        or has_value(row.get("awards_summary"))
    )

    metrics = payload.setdefault("metrics", {})
    metrics["with_critic_or_acclaim"] = with_critic_or_acclaim
    metrics["critic_or_acclaim_percent"] = round((with_critic_or_acclaim / len(records)) * 100, 2) if records else 0.0

    if medium == "movies":
        with_box_office = sum(1 for row in records if has_value(row.get("box_office_domestic")) or has_value(row.get("box_office_worldwide")))
        metrics["with_box_office"] = with_box_office
        metrics["box_office_percent"] = round((with_box_office / len(records)) * 100, 2) if records else 0.0


def update_inventory(movies_payload: dict[str, Any], television_payload: dict[str, Any]) -> None:
    inventory = read_json(INVENTORY_PATH, default={})
    if not isinstance(inventory, dict):
        inventory = {}

    movies_records = movies_payload.get("records", [])
    television_records = television_payload.get("records", [])
    movies_by_year = build_by_year(movies_records if isinstance(movies_records, list) else [])
    tv_by_year = build_by_year(television_records if isinstance(television_records, list) else [])
    years = sorted({int(y) for y in list(movies_by_year.keys()) + list(tv_by_year.keys()) if str(y).isdigit()})

    inventory["generated_at_utc"] = now_utc_iso()
    inventory.setdefault("warehouse_version", "screen-culture-v1")
    inventory.setdefault(
        "paths",
        {
            "movies_master": str(MOVIES_MASTER_PATH),
            "television_master": str(TELEVISION_MASTER_PATH),
            "movies_by_year": str(MOVIES_BY_YEAR_PATH),
            "television_by_year": str(TELEVISION_BY_YEAR_PATH),
            "sqlite": str(SQLITE_PATH),
        },
    )
    inventory.setdefault(
        "source_layering",
        {
            "canonical_local": "RetroVerse internal datasets (authoritative local base)",
            "direct_api": "TMDb/OMDb style API enrichments when available",
            "licensed_or_official": "IMDb dataset files and other licensed/official structured sources",
            "reference_derived": "Reference tables and archive-derived metadata",
            "missing": "No available source populated the field",
        },
    )
    inventory.setdefault(
        "trust_hierarchy",
        ["missing", "reference_derived", "direct_api", "licensed_or_official", "canonical_local"],
    )

    inventory["movies"] = {
        "record_count": len(movies_records) if isinstance(movies_records, list) else 0,
        "year_range": movies_payload.get("year_range", {}),
        "years_indexed": len(movies_by_year),
        "trust_distribution": movies_payload.get("trust_distribution", {}),
        "source_counts": movies_payload.get("source_counts", {}),
        "metrics": movies_payload.get("metrics", {}),
    }
    inventory["television"] = {
        "record_count": len(television_records) if isinstance(television_records, list) else 0,
        "year_range": television_payload.get("year_range", {}),
        "years_indexed": len(tv_by_year),
        "trust_distribution": television_payload.get("trust_distribution", {}),
        "source_counts": television_payload.get("source_counts", {}),
        "metrics": television_payload.get("metrics", {}),
    }

    inventory["years_covered"] = years
    notes = inventory.setdefault("notes", [])
    note = "OMDb API enrichment applied using fill-empty-only merge behavior with direct_api provenance."
    if note not in notes:
        notes.append(note)

    write_json(INVENTORY_PATH, inventory)


def run(args: argparse.Namespace) -> EnrichmentCounts:
    api_key = str(OMDB_API_KEY or "").strip()
    if not api_key:
        raise RuntimeError("OMDB_API_KEY missing from .env")

    movies_payload = load_payload(MOVIES_MASTER_PATH)
    television_payload = load_payload(TELEVISION_MASTER_PATH)
    movies_records = movies_payload["records"]
    television_records = television_payload["records"]

    counts = EnrichmentCounts()

    movie_limit = args.max_movies if args.max_movies and args.max_movies > 0 else len(movies_records)
    tv_limit = args.max_television if args.max_television and args.max_television > 0 else len(television_records)

    movie_changed_records = 0
    tv_changed_records = 0

    for index, record in enumerate(movies_records):
        if index >= movie_limit:
            break
        if enrich_record(record, "movies", api_key, args.sleep, counts):
            movie_changed_records += 1

    for index, record in enumerate(television_records):
        if index >= tv_limit:
            break
        if enrich_record(record, "television", api_key, args.sleep, counts):
            tv_changed_records += 1

    refresh_payload_metrics(movies_payload, "movies")
    refresh_payload_metrics(television_payload, "television")

    movie_source_counts = movies_payload.setdefault("source_counts", {})
    movie_source_counts["omdb_api"] = int(movie_source_counts.get("omdb_api", 0)) + movie_changed_records

    tv_source_counts = television_payload.setdefault("source_counts", {})
    tv_source_counts["omdb_api"] = int(tv_source_counts.get("omdb_api", 0)) + tv_changed_records

    write_json(MOVIES_MASTER_PATH, movies_payload)
    write_json(TELEVISION_MASTER_PATH, television_payload)

    movies_by_year = build_by_year(movies_records)
    tv_by_year = build_by_year(television_records)
    write_json(MOVIES_BY_YEAR_PATH, movies_by_year)
    write_json(TELEVISION_BY_YEAR_PATH, tv_by_year)

    update_inventory(movies_payload, television_payload)

    conn = sqlite3.connect(SQLITE_PATH)
    try:
        write_sqlite_json_table(conn, "movies_master", movies_records)
        write_sqlite_json_table(conn, "television_master", television_records)
        conn.commit()
    finally:
        conn.close()

    return counts


def main() -> int:
    args = parse_args()
    try:
        counts = run(args)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: OMDb enrichment failed: {exc}")
        return 1

    print(f"Movies enriched with critic scores: {counts.movies_enriched_with_critic_scores}")
    print(f"TV enriched with critic scores: {counts.television_enriched_with_critic_scores}")
    print(f"Movies with box office values: {counts.movies_with_box_office_values_added}")
    print(f"Awards fields added: {counts.awards_fields_added}")
    print(f"OMDb API calls: {counts.omdb_calls}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
