#!/usr/bin/env python3
"""Audit Billboard Hot 100 coverage and schema from canonical source map."""

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


def find_hot100_table(conn: sqlite3.Connection) -> tuple[str | None, str | None]:
    tables = list_tables(conn)
    candidates = ["chart_positions", "hot100"]
    date_candidates = ["issue_date", "chart_date", "chart_week", "week", "date", "year"]
    for table in candidates:
        if table not in tables:
            continue
        columns = table_columns(conn, table)
        for date_col in date_candidates:
            if date_col in columns:
                return table, date_col
    # As a fallback, choose first table with rank+title+artist and some date-like column.
    for table in tables:
        columns = table_columns(conn, table)
        if not {"rank", "title", "artist"}.issubset(set(columns)):
            continue
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


def has_event_entry_model(conn: sqlite3.Connection) -> bool:
    tables = set(list_tables(conn))
    if not {"event", "event_entry"}.issubset(tables):
        return False
    event_cols = set(table_columns(conn, "event"))
    entry_cols = set(table_columns(conn, "event_entry"))
    return {"event_id", "issue_date"}.issubset(event_cols) and {"event_id", "rank"}.issubset(entry_cols)


def count_rows_by_year_event_model(conn: sqlite3.Connection) -> dict[int, int]:
    counts: dict[int, int] = {}
    for year in YEARS_TO_CHECK:
        row = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM event_entry ee
            JOIN event e ON e.event_id = ee.event_id
            WHERE substr(e.issue_date, 1, 4) = ?
            """,
            (str(year),),
        ).fetchone()
        counts[year] = int(row["c"]) if row else 0
    return counts


def diagnose_coverage(
    counts: dict[int, int],
    table_name: str | None,
    date_col: str | None,
    model_name: str,
    db_path: Path,
    conn: sqlite3.Connection,
) -> list[str]:
    notes: list[str] = []
    if model_name == "event_entry":
        row = conn.execute(
            """
            SELECT MIN(substr(issue_date, 1, 4)) AS min_year, MAX(substr(issue_date, 1, 4)) AS max_year
            FROM event
            """
        ).fetchone()
        min_year = row["min_year"] if row else None
        max_year = row["max_year"] if row else None
        notes.append("Using event/event_entry model with `event.issue_date`.")
        notes.append(f"Observed year range in model: {min_year} to {max_year}.")
        if counts.get(1978, 0) > 0:
            notes.append("1978 rows are present.")
            return notes
        notes.append("1978 rows are zero.")
        notes.append("Diagnosis:")
        notes.append("wrong table: unlikely; event/event_entry model is present.")
        notes.append("wrong date field: unlikely; using event.issue_date.")
        notes.append(f"wrong DB path: verify canonical path points to complete DB: {db_path}.")
        notes.append("missing data: possible if the DB is partial.")
        notes.append("SQL query issue: unlikely if other years return non-zero.")
        return notes

    if table_name is None or date_col is None:
        notes.append("Could not find a usable chart table/date field pair.")
        notes.append("Possible issue: wrong table or unexpected schema.")
        return notes

    expr = sql_year_expression(date_col)
    row = conn.execute(
        f"SELECT MIN({expr}) AS min_year, MAX({expr}) AS max_year, COUNT(*) AS c FROM {table_name}"
    ).fetchone()
    min_year = row["min_year"] if row else None
    max_year = row["max_year"] if row else None

    notes.append(f"Using table `{table_name}` with date field `{date_col}`.")
    notes.append(f"Observed year range in table: {min_year} to {max_year}.")

    if counts.get(1978, 0) > 0:
        notes.append("1978 rows are present.")
        return notes

    notes.append("1978 rows are zero.")
    notes.append("Diagnosis:")
    notes.append("wrong table: less likely if selected table has rank/title/artist/date fields.")
    notes.append("wrong date field: check if another date-like column exists in the same table.")
    notes.append(f"wrong DB path: verify canonical source points to the full historical DB, not a partial snapshot: {db_path}.")
    notes.append("missing data: likely if year range does not include 1978.")
    notes.append("SQL query issue: unlikely if other years return non-zero using same year-expression logic.")
    return notes


def main() -> int:
    sources = load_data_sources(DATA_SOURCES_PATH)
    source = sources.get("billboard_hot_100", {}) if isinstance(sources, dict) else {}
    if not isinstance(source, dict) or not source:
        source = sources.get("billboard_hot_100_db", {}) if isinstance(sources, dict) else {}
    path_text = str(source.get("path", "")).strip()

    print("## Hot100 DB Audit")
    if not path_text:
        print("\nDatabase: (missing path in DATA_SOURCES.yaml)")
        return 1

    db_path = resolve_path(PROJECT_ROOT, path_text)
    print(f"\nDatabase: {project_relative(PROJECT_ROOT, db_path)}")
    print(f"Resolved path: {db_path}")

    if not db_path.exists():
        print("Status: missing file")
        return 1

    try:
        conn = connect_read_only(db_path)
    except sqlite3.Error as exc:
        print(f"Status: could not open DB: {exc}")
        return 1

    tables = list_tables(conn)
    print("\nTables:")
    for table in tables:
        print(table)

    print_schema(conn, "charts")
    print_schema(conn, "chart_positions")
    print_schema(conn, "songs")

    model_name = "table"
    table_name: str | None
    date_col: str | None
    counts: dict[int, int]

    if has_event_entry_model(conn):
        model_name = "event_entry"
        table_name = "event_entry"
        date_col = "issue_date"
        counts = count_rows_by_year_event_model(conn)
    else:
        table_name, date_col = find_hot100_table(conn)
        counts = count_rows_by_year(conn, table_name, date_col) if table_name and date_col else {}

    print("\nRows by year:")
    if table_name is None or date_col is None:
        for year in YEARS_TO_CHECK:
            print(f"{year}: 0")
        notes = diagnose_coverage({}, table_name, date_col, model_name, db_path, conn)
    else:
        for year in YEARS_TO_CHECK:
            print(f"{year}: {counts.get(year, 0)}")
        notes = diagnose_coverage(counts, table_name, date_col, model_name, db_path, conn)

    print("\nNotes:")
    for note in notes:
        print(f"- {note}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
