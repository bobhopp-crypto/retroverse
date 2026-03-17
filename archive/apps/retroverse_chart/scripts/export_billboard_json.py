#!/usr/bin/env python3
"""
Export Billboard Hot 100 chart data from SQLite to JSON.
Reads from event/event_entry/work/person schema.
Outputs: title, artist, year, peak, weeks, entry_week, peak_week, exit_week, weeks_at_peak, run.
"""

import json
import sqlite3
from pathlib import Path


def find_db() -> Path:
    """Locate billboard-hot-100.db or source_billboard_hot_100.db."""
    root = Path(__file__).resolve().parent.parent
    # root = retroverse_chart, root.parent = retroverse (repo root)
    candidates = [
        root.parent / "raw-data" / "billboard-hot-100.db",
        root.parent / "raw-data" / "source_billboard_hot_100.db",
        root / "raw-data" / "billboard-hot-100.db",
        root / "raw-data" / "source_billboard_hot_100.db",
        root.parent / "retroverse-1974" / "data" / "db" / "billboard-hot-100.db",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Billboard database not found. Tried: {[str(c) for c in candidates]}"
    )


def main() -> None:
    db_path = find_db()
    root = Path(__file__).resolve().parent.parent
    out_path = root / "public" / "data" / "billboard_hot_100.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT
            w.title_display AS title,
            COALESCE(p.name_display, '') AS artist,
            e.issue_date AS chart_date,
            ee.rank AS chart_position
        FROM event_entry ee
        JOIN event e ON e.event_id = ee.event_id
        JOIN work w ON w.work_id = ee.work_id
        LEFT JOIN person p ON p.person_id = w.primary_person_id
        ORDER BY w.work_id, e.issue_date
    """

    rows = conn.execute(sql).fetchall()
    conn.close()

    # Group by (title, artist), order entries by chart week, build run
    by_work: dict[tuple[str, str], list[tuple[str, int]]] = {}
    for r in rows:
        title = (r["title"] or "").strip()
        artist = (r["artist"] or "").strip()
        if not title or not artist:
            continue
        key = (title, artist)
        date_str = r["chart_date"] or ""
        rank = int(r["chart_position"]) if r["chart_position"] is not None else 999

        if key not in by_work:
            by_work[key] = []
        by_work[key].append((date_str, rank))

    out: list[dict] = []
    for (title, artist), entries in by_work.items():
        entries.sort(key=lambda x: x[0])
        run = [r for _, r in entries]
        if not run:
            continue

        peak = min(run)
        weeks = len(run)
        entry_week = 1
        exit_week = weeks
        peak_week = next((i + 1 for i, r in enumerate(run) if r == peak), 1)
        weeks_at_peak = sum(1 for r in run if r == peak)
        year = int(entries[0][0][:4]) if entries and len(entries[0][0]) >= 4 else 0

        out.append({
            "title": title,
            "artist": artist,
            "year": year,
            "peak": peak,
            "weeks": weeks,
            "entry_week": entry_week,
            "peak_week": peak_week,
            "exit_week": exit_week,
            "weeks_at_peak": weeks_at_peak,
            "run": run,
        })

    out.sort(key=lambda x: (-x["weeks"], x["peak"], x["year"]))

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(out)} records to {out_path}")


if __name__ == "__main__":
    main()
