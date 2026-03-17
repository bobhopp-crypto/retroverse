#!/usr/bin/env python3
"""Build unified screen/culture warehouse outputs for RetroVerse."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Any

from build_movies_dataset import build_movies_dataset
from build_television_dataset import build_television_dataset
from screen_culture_common import (
    TRUST_LEVELS,
    WAREHOUSE_ROOT,
    build_by_year,
    coverage_years,
    ensure_screen_culture_dirs,
    now_utc_iso,
    trust_distribution,
    write_json,
    write_sqlite_json_table,
)


MOVIES_MASTER_PATH = WAREHOUSE_ROOT / "movies_master.json"
TELEVISION_MASTER_PATH = WAREHOUSE_ROOT / "television_master.json"
MOVIES_BY_YEAR_PATH = WAREHOUSE_ROOT / "movies_by_year.json"
TELEVISION_BY_YEAR_PATH = WAREHOUSE_ROOT / "television_by_year.json"
INVENTORY_PATH = WAREHOUSE_ROOT / "screen_culture_inventory.json"
SQLITE_PATH = WAREHOUSE_ROOT / "screen_culture.db"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build unified screen/culture warehouse artifacts.")
    parser.add_argument("--no-sqlite", action="store_true", help="Skip SQLite export.")
    return parser.parse_args()


def union_years(movie_by_year: dict[str, Any], tv_by_year: dict[str, Any]) -> list[int]:
    years = set()
    for key in movie_by_year.keys():
        if str(key).isdigit():
            years.add(int(key))
    for key in tv_by_year.keys():
        if str(key).isdigit():
            years.add(int(key))
    return sorted(years)


def build_inventory(
    movies_payload: dict[str, Any],
    television_payload: dict[str, Any],
    movies_by_year: dict[str, list[dict[str, Any]]],
    television_by_year: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    movie_records = movies_payload.get("records", []) if isinstance(movies_payload, dict) else []
    tv_records = television_payload.get("records", []) if isinstance(television_payload, dict) else []

    movie_min, movie_max = coverage_years(movie_records)
    tv_min, tv_max = coverage_years(tv_records)
    years = union_years(movies_by_year, television_by_year)

    return {
        "generated_at_utc": now_utc_iso(),
        "warehouse_version": "screen-culture-v1",
        "paths": {
            "movies_master": str(MOVIES_MASTER_PATH),
            "television_master": str(TELEVISION_MASTER_PATH),
            "movies_by_year": str(MOVIES_BY_YEAR_PATH),
            "television_by_year": str(TELEVISION_BY_YEAR_PATH),
            "sqlite": str(SQLITE_PATH),
        },
        "source_layering": {
            "canonical_local": "RetroVerse internal datasets (authoritative local base)",
            "direct_api": "TMDb/OMDb style API enrichments when available",
            "licensed_or_official": "IMDb dataset files and other licensed/official structured sources",
            "reference_derived": "Reference tables and archive-derived metadata",
            "missing": "No available source populated the field",
        },
        "trust_hierarchy": TRUST_LEVELS,
        "movies": {
            "record_count": len(movie_records),
            "year_range": {"min": movie_min, "max": movie_max},
            "years_indexed": len(movies_by_year),
            "trust_distribution": movies_payload.get("trust_distribution", trust_distribution(movie_records)),
            "source_counts": movies_payload.get("source_counts", {}),
            "metrics": movies_payload.get("metrics", {}),
        },
        "television": {
            "record_count": len(tv_records),
            "year_range": {"min": tv_min, "max": tv_max},
            "years_indexed": len(television_by_year),
            "trust_distribution": television_payload.get("trust_distribution", trust_distribution(tv_records)),
            "source_counts": television_payload.get("source_counts", {}),
            "metrics": television_payload.get("metrics", {}),
        },
        "years_covered": years,
        "notes": [
            "Warehouse preserves field-level provenance and trust labels.",
            "Stronger trust levels are not overwritten by weaker source layers.",
            "Sparse fields are retained as null/empty values with missing provenance entries.",
        ],
    }


def write_sqlite(movies: list[dict[str, Any]], television: list[dict[str, Any]]) -> None:
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        write_sqlite_json_table(conn, "movies_master", movies)
        write_sqlite_json_table(conn, "television_master", television)
        conn.commit()
    finally:
        conn.close()


def build_screen_culture_warehouse(write_sqlite_output: bool = True) -> dict[str, Any]:
    ensure_screen_culture_dirs()

    movies_payload = build_movies_dataset(write_output=True)
    television_payload = build_television_dataset(write_output=True)

    movies_records = movies_payload.get("records", []) if isinstance(movies_payload, dict) else []
    television_records = television_payload.get("records", []) if isinstance(television_payload, dict) else []

    movies_by_year = build_by_year(movies_records)
    television_by_year = build_by_year(television_records)

    write_json(MOVIES_BY_YEAR_PATH, movies_by_year)
    write_json(TELEVISION_BY_YEAR_PATH, television_by_year)

    if write_sqlite_output:
        write_sqlite(movies_records, television_records)

    inventory = build_inventory(
        movies_payload,
        television_payload,
        movies_by_year,
        television_by_year,
    )
    write_json(INVENTORY_PATH, inventory)

    return {
        "movies_payload": movies_payload,
        "television_payload": television_payload,
        "movies_by_year_count": len(movies_by_year),
        "television_by_year_count": len(television_by_year),
        "inventory": inventory,
        "sqlite_written": write_sqlite_output,
    }


def main() -> int:
    args = parse_args()
    result = build_screen_culture_warehouse(write_sqlite_output=not args.no_sqlite)

    movies_payload = result["movies_payload"]
    television_payload = result["television_payload"]
    inventory = result["inventory"]

    print("Screen/culture warehouse build complete")
    print(f"Movies master: {MOVIES_MASTER_PATH}")
    print(f"Television master: {TELEVISION_MASTER_PATH}")
    print(f"Movies by year: {MOVIES_BY_YEAR_PATH}")
    print(f"Television by year: {TELEVISION_BY_YEAR_PATH}")
    print(f"Inventory: {INVENTORY_PATH}")
    if result["sqlite_written"]:
        print(f"SQLite: {SQLITE_PATH}")

    print(f"Movies records: {movies_payload.get('record_count', 0)}")
    print(f"Television records: {television_payload.get('record_count', 0)}")

    years = inventory.get("years_covered", [])
    if years:
        print(f"Years covered: {years[0]} to {years[-1]} ({len(years)} years)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
