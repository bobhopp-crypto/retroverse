#!/usr/bin/env python3
"""Audit Billboard 200 coverage and schema from canonical source map."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from db_common import (
    connect_read_only,
    list_tables,
    load_data_sources,
    project_relative,
    resolve_path,
    sql_year_expression,
    table_columns,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_SOURCES_PATH = PROJECT_ROOT / "data" / "DATA_SOURCES.yaml"
YEARS_TO_CHECK = [1958, 1965, 1970, 1975, 1978, 1980]


def print_schema(conn: sqlite3.Connection, table: str) -> None:
    tables = list_tables(conn)
    print(f"\nSchema: {table}")
    if table not in tables:
        print("  (table missing)")
        return
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    for row in rows:
        print(f"  - {row['name']} ({row['type']})")


def pick_source_path() -> tuple[Path | None, str]:
    sources = load_data_sources(DATA_SOURCES_PATH)
    if not isinstance(sources, dict):
        return None, "No data source map loaded."

    if "billboard_200" in sources:
        path_text = str(sources["billboard_200"].get("path", "")).strip()
        if path_text:
            candidate = resolve_path(PROJECT_ROOT, path_text)
            if candidate.exists():
                return candidate, "Using billboard_200 source."
            # Keep looking for an in-repo canonical equivalent when the new path is missing.

    if "billboard_200_db" in sources:
        path_text = str(sources["billboard_200_db"].get("path", "")).strip()
        if path_text:
            candidate = resolve_path(PROJECT_ROOT, path_text)
            if candidate.exists():
                return candidate, "Primary billboard_200 path missing; using billboard_200_db."
    return None, "No usable Billboard 200 DB path found in source map."


def find_album_table(conn: sqlite3.Connection) -> tuple[str | None, str | None]:
    tables = list_tables(conn)
    table_candidates = ["albums", "billboard_200", "chart_positions"]
    date_candidates = ["date", "chart_week", "chart_date", "issue_date", "week", "year"]
    for table in table_candidates:
        if table not in tables:
            continue
        columns = table_columns(conn, table)
        for date_col in date_candidates:
            if date_col in columns:
                return table, date_col
    return None, None


def count_rows_by_year(conn: sqlite3.Connection, table: str, date_col: str) -> dict[int, int]:
    counts: dict[int, int] = {}
    expr = sql_year_expression(date_col)
    for year in YEARS_TO_CHECK:
        row = conn.execute(
            f"SELECT COUNT(*) AS c FROM {table} WHERE {expr} = ?",
            (str(year),),
        ).fetchone()
        counts[year] = int(row["c"]) if row else 0
    return counts


def main() -> int:
    print("## Billboard 200 DB Audit")
    db_path, reason = pick_source_path()
    if db_path is None:
        print(f"\nDatabase: (missing)\nStatus: {reason}")
        return 1

    print(f"\nDatabase: {project_relative(PROJECT_ROOT, db_path)}")
    print(f"Resolved path: {db_path}")
    print(f"Path selection: {reason}")

    try:
        conn = connect_read_only(db_path)
    except sqlite3.Error as exc:
        print(f"Status: could not open DB: {exc}")
        return 1

    tables = list_tables(conn)
    print("\nTables:")
    for table in tables:
        print(table)

    print_schema(conn, "albums")
    print_schema(conn, "acoustic_features")
    print_schema(conn, "songs")

    table_name, date_col = find_album_table(conn)
    print("\nRows by year:")
    if table_name is None or date_col is None:
        for year in YEARS_TO_CHECK:
            print(f"{year}: 0")
        print("\nNotes:")
        print("- Could not identify an album chart table with a usable date column.")
        conn.close()
        return 0

    counts = count_rows_by_year(conn, table_name, date_col)
    for year in YEARS_TO_CHECK:
        print(f"{year}: {counts.get(year, 0)}")

    expr = sql_year_expression(date_col)
    summary = conn.execute(
        f"SELECT MIN({expr}) AS min_year, MAX({expr}) AS max_year FROM {table_name}"
    ).fetchone()
    min_year = summary["min_year"] if summary else None
    max_year = summary["max_year"] if summary else None

    print("\nNotes:")
    print(f"- Using table `{table_name}` with date field `{date_col}`.")
    print(f"- Observed year range: {min_year} to {max_year}.")
    if counts.get(1978, 0):
        print("- 1978 album chart data is present.")
    else:
        print("- 1978 album chart data is missing or date parsing needs adjustment.")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
