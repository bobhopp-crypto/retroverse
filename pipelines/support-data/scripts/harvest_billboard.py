#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import get_dataset_path
from lineage_hook import run_with_lineage
from pipeline_common import (
    PROCESSED_DIR,
    ROOT_DIR,
    SQLITE_PATH,
    backup_if_exists,
    deterministic_sort,
    ensure_directories,
    log_pipeline,
    safe_write_csv,
    write_sqlite_table,
)


OUTPUT_PATH = PROCESSED_DIR / "billboard_hot100.csv"
RAW_DB_PATH = get_dataset_path("billboard_hot_100", fallback="data/raw/charts/billboard-hot-100.db")

SQL_EVENT_QUERY = """
SELECT
  e.issue_date AS chart_date,
  ee.rank AS rank,
  w.title_display AS title,
  COALESCE(p.name_display, '') AS artist,
  COALESCE(ee.weeks_on_chart, 0) AS weeks_on_chart,
  COALESCE(ee.peak_pos, ee.rank) AS peak_position
FROM event_entry ee
JOIN event e ON e.event_id = ee.event_id
JOIN work w ON w.work_id = ee.work_id
LEFT JOIN person p ON p.person_id = w.primary_person_id
WHERE e.issue_date >= '1958-01-01'
ORDER BY e.issue_date, ee.rank;
"""

SQL_CHART_POSITIONS_FALLBACK = """
SELECT
  cp.issue_date AS chart_date,
  cp.rank AS rank,
  cp.title AS title,
  cp.artist AS artist,
  NULL AS weeks_on_chart,
  cp.rank AS peak_position
FROM chart_positions cp
JOIN charts c ON c.chart_id = cp.chart_id
WHERE cp.issue_date >= '1958-01-01'
ORDER BY cp.issue_date, cp.rank;
"""


def load_billboard_from_sqlite(db_path: Path) -> pd.DataFrame:
    db_uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(db_uri, uri=True) as connection:
        try:
            return pd.read_sql_query(SQL_EVENT_QUERY, connection)
        except Exception:  # noqa: BLE001
            return pd.read_sql_query(SQL_CHART_POSITIONS_FALLBACK, connection)


def main() -> None:
    ensure_directories()
    if not RAW_DB_PATH.exists():
        raise FileNotFoundError(f"Missing canonical Billboard source DB: {RAW_DB_PATH}")

    source_df = load_billboard_from_sqlite(RAW_DB_PATH)

    for col in ("chart_date", "title", "artist"):
        if col in source_df.columns:
            source_df[col] = source_df[col].fillna("").astype(str).str.strip()

    for col in ("rank", "weeks_on_chart", "peak_position"):
        if col in source_df.columns:
            source_df[col] = pd.to_numeric(source_df[col], errors="coerce")

    source_df = source_df[
        ["chart_date", "rank", "title", "artist", "weeks_on_chart", "peak_position"]
    ]
    before = len(source_df)
    combined = source_df.drop_duplicates(
        subset=["chart_date", "rank", "title", "artist"],
        keep="first",
    )
    duplicates_removed = before - len(combined)

    combined = deterministic_sort(combined, ["chart_date", "rank", "title", "artist"])
    safe_write_csv(combined, OUTPUT_PATH)

    backup_if_exists(SQLITE_PATH)
    write_sqlite_table(combined, "billboard_hot100")

    records_collected = len(source_df)
    log_pipeline(
        script_name="harvest_billboard.py",
        records_collected=records_collected,
        errors=0,
        duplicates_removed=duplicates_removed,
        message=f"output_rows={len(combined)} source_db_exists={RAW_DB_PATH.exists()}",
    )
    print(f"records_collected: {records_collected}")
    print(f"total_rows: {len(combined)}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
