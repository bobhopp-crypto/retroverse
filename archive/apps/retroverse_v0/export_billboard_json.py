#!/usr/bin/env python3
"""
Export Billboard Hot 100 chart data from SQLite to JSON.
Reads from event/event_entry/work/person schema, aggregates per song,
outputs: title, artist, year, chart_position, weeks_on_chart.
"""

import json
import sqlite3
from pathlib import Path


def find_db() -> Path:
    """Locate billboard-hot-100.db or source_billboard_hot_100.db."""
    candidates = [
        Path(__file__).resolve().parent.parent / "raw-data" / "billboard-hot-100.db",
        Path(__file__).resolve().parent.parent / "raw-data" / "source_billboard_hot_100.db",
        Path(__file__).resolve().parent / "billboard-hot-100.db",
        Path(__file__).resolve().parent / "source_billboard_hot_100.db",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Billboard database not found. Tried: {[str(c) for c in candidates]}"
    )


def main() -> None:
    db_path = find_db()
    out_path = Path(__file__).resolve().parent / "public" / "data" / "billboard_hot_100.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT
            w.title_display AS title,
            COALESCE(p.name_display, '') AS artist,
            e.issue_date AS chart_date,
            ee.rank AS chart_position,
            ee.weeks_on_chart AS weeks_on_chart
        FROM event_entry ee
        JOIN event e ON e.event_id = ee.event_id
        JOIN work w ON w.work_id = ee.work_id
        LEFT JOIN person p ON p.person_id = w.primary_person_id
        ORDER BY ee.work_id, e.issue_date
    """

    rows = conn.execute(sql).fetchall()
    conn.close()

    # Aggregate per (title, artist): peak position, total weeks, year of peak
    by_work: dict[tuple[str, str], dict] = {}
    for r in rows:
        title = (r["title"] or "").strip()
        artist = (r["artist"] or "").strip()
        if not title or not artist:
            continue
        key = (title, artist)
        date_str = r["chart_date"] or ""
        rank = int(r["chart_position"]) if r["chart_position"] is not None else 999
        weeks = int(r["weeks_on_chart"]) if r["weeks_on_chart"] is not None else 0

        if key not in by_work:
            by_work[key] = {
                "title": title,
                "artist": artist,
                "year": int(date_str[:4]) if len(date_str) >= 4 else 0,
                "chart_position": rank,
                "weeks_on_chart": weeks,
            }
        else:
            rec = by_work[key]
            if rank < rec["chart_position"]:
                rec["chart_position"] = rank
                rec["year"] = int(date_str[:4]) if len(date_str) >= 4 else rec["year"]
            if weeks > rec["weeks_on_chart"]:
                rec["weeks_on_chart"] = weeks

    out = [rec for rec in by_work.values()]
    out.sort(key=lambda x: (-x["weeks_on_chart"], x["chart_position"], x["year"]))

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(out)} records to {out_path}")


if __name__ == "__main__":
    main()
