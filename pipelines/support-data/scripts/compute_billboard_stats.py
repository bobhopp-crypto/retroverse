#!/usr/bin/env python3
"""Compute Billboard capability outputs from raw-data/billboard-hot-100.db.

Outputs (JSON):
  - artifacts/output/billboard/year_stats.json
  - artifacts/output/billboard/artist_totals.json
  - artifacts/output/billboard/top_songs_by_year.json
  - artifacts/output/billboard/weeks_at_number_one.json

The script reads from raw-data only and writes derived files into artifacts.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SOURCE_SYSTEM = "RVA-HOT100"
ROOT_DIR = Path(__file__).resolve().parents[3]
LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import get_dataset_path
from lineage_hook import run_with_lineage


DEFAULT_DB_PATH = get_dataset_path("billboard_hot_100", fallback="data/raw/charts/billboard-hot-100.db")
DEFAULT_OUT_DIR = get_dataset_path("media_index", fallback="data/derived/media-index") / "output" / "billboard"


@dataclass
class YearAccumulator:
    chart_rows: int = 0
    songs: set[str] = field(default_factory=set)
    weeks: set[str] = field(default_factory=set)
    first_week: str | None = None
    last_week: str | None = None


@dataclass
class DecadeAccumulator:
    chart_rows: int = 0
    songs: set[str] = field(default_factory=set)
    weeks: set[str] = field(default_factory=set)


@dataclass
class SongYearAccumulator:
    year: int
    song_id: str
    title: str
    artist: str
    chart_weeks: int = 0
    best_rank: int = 1000
    weeks_at_peak: int = 0


@dataclass
class ArtistAccumulator:
    artist: str
    chart_rows: int = 0
    distinct_songs: set[str] = field(default_factory=set)
    best_rank: int = 1000
    weeks_at_number_one: int = 0
    first_year: int | None = None
    last_year: int | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute Billboard derived stats from SQLite")
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help=f"Path to billboard-hot-100.db (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help=f"Directory for derived output JSON files (default: {DEFAULT_OUT_DIR})",
    )
    return parser.parse_args()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row

    year_acc: dict[int, YearAccumulator] = defaultdict(YearAccumulator)
    decade_acc: dict[int, DecadeAccumulator] = defaultdict(DecadeAccumulator)
    song_year_acc: dict[tuple[int, str], SongYearAccumulator] = {}
    artist_acc: dict[str, ArtistAccumulator] = {}
    weeks_at_number_one: dict[tuple[str, str, str], int] = defaultdict(int)

    query = """
      SELECT e.issue_date AS issue_date,
             ee.work_id AS work_id,
             ee.rank AS rank,
             w.title_display AS title,
             COALESCE(NULLIF(TRIM(p.name_display), ''), 'Unknown Artist') AS artist
        FROM event_entry ee
        JOIN event e ON ee.event_id = e.event_id
        JOIN work w ON ee.work_id = w.work_id
   LEFT JOIN person p ON w.primary_person_id = p.person_id
       WHERE e.source_system = ?
       ORDER BY e.issue_date ASC, ee.rank ASC
    """

    for row in connection.execute(query, (SOURCE_SYSTEM,)):
        issue_date = str(row["issue_date"] or "").strip()
        if len(issue_date) != 10:
            continue
        try:
            year = int(issue_date[0:4])
        except ValueError:
            continue
        decade = (year // 10) * 10

        song_id = str(row["work_id"] or "").strip()
        if not song_id:
            continue

        try:
            rank = int(row["rank"])
        except (TypeError, ValueError):
            continue
        if rank < 1 or rank > 100:
            continue

        title = str(row["title"] or "Unknown Title").strip() or "Unknown Title"
        artist = str(row["artist"] or "Unknown Artist").strip() or "Unknown Artist"

        y = year_acc[year]
        y.chart_rows += 1
        y.songs.add(song_id)
        y.weeks.add(issue_date)
        if y.first_week is None or issue_date < y.first_week:
            y.first_week = issue_date
        if y.last_week is None or issue_date > y.last_week:
            y.last_week = issue_date

        d = decade_acc[decade]
        d.chart_rows += 1
        d.songs.add(song_id)
        d.weeks.add(issue_date)

        key = (year, song_id)
        song_year = song_year_acc.get(key)
        if song_year is None:
            song_year = SongYearAccumulator(
                year=year,
                song_id=song_id,
                title=title,
                artist=artist,
            )
            song_year_acc[key] = song_year
        song_year.chart_weeks += 1
        if rank < song_year.best_rank:
            song_year.best_rank = rank
            song_year.weeks_at_peak = 1
        elif rank == song_year.best_rank:
            song_year.weeks_at_peak += 1

        artist_row = artist_acc.get(artist)
        if artist_row is None:
            artist_row = ArtistAccumulator(artist=artist)
            artist_acc[artist] = artist_row
        artist_row.chart_rows += 1
        artist_row.distinct_songs.add(song_id)
        artist_row.best_rank = min(artist_row.best_rank, rank)
        artist_row.first_year = year if artist_row.first_year is None else min(artist_row.first_year, year)
        artist_row.last_year = year if artist_row.last_year is None else max(artist_row.last_year, year)

        if rank == 1:
            artist_row.weeks_at_number_one += 1
            weeks_at_number_one[(song_id, title, artist)] += 1

    connection.close()

    top_songs_grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    number_one_counts: dict[int, int] = defaultdict(int)

    for song in song_year_acc.values():
        top_songs_grouped[song.year].append(
            {
                "song_id": song.song_id,
                "title": song.title,
                "artist": song.artist,
                "best_rank": song.best_rank,
                "chart_weeks": song.chart_weeks,
                "weeks_at_peak": song.weeks_at_peak,
            }
        )
        if song.best_rank == 1:
            number_one_counts[song.year] += 1

    for year, rows in top_songs_grouped.items():
        rows.sort(
            key=lambda item: (
                item["best_rank"],
                -item["weeks_at_peak"],
                -item["chart_weeks"],
                item["artist"],
                item["title"],
            )
        )

    year_stats = []
    for year in sorted(year_acc.keys()):
        summary = year_acc[year]
        year_stats.append(
            {
                "year": year,
                "chart_rows": summary.chart_rows,
                "songs_charted": len(summary.songs),
                "week_count": len(summary.weeks),
                "first_week": summary.first_week,
                "last_week": summary.last_week,
                "number_one_song_count": number_one_counts.get(year, 0),
            }
        )

    decade_stats = []
    for decade in sorted(decade_acc.keys()):
        summary = decade_acc[decade]
        decade_stats.append(
            {
                "decade": decade,
                "chart_rows": summary.chart_rows,
                "songs_charted": len(summary.songs),
                "week_count": len(summary.weeks),
            }
        )

    top_songs_by_year = []
    for year in sorted(top_songs_grouped.keys()):
        top_songs_by_year.append(
            {
                "year": year,
                "top_songs": top_songs_grouped[year][:40],
            }
        )

    artist_totals = []
    for artist in artist_acc.values():
        artist_totals.append(
            {
                "artist": artist.artist,
                "chart_rows": artist.chart_rows,
                "distinct_songs": len(artist.distinct_songs),
                "best_rank": artist.best_rank if artist.best_rank <= 100 else None,
                "weeks_at_number_one": artist.weeks_at_number_one,
                "first_year": artist.first_year,
                "last_year": artist.last_year,
            }
        )
    artist_totals.sort(
        key=lambda item: (
            -item["weeks_at_number_one"],
            -item["chart_rows"],
            item["artist"],
        )
    )

    weeks_at_number_one_payload = [
        {
            "song_id": song_id,
            "title": title,
            "artist": artist,
            "weeks_at_number_one": weeks,
        }
        for (song_id, title, artist), weeks in weeks_at_number_one.items()
    ]
    weeks_at_number_one_payload.sort(
        key=lambda item: (-item["weeks_at_number_one"], item["artist"], item["title"])
    )

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    metadata = {
        "generated_at": generated_at,
        "source_db": str(db_path),
        "source_system": SOURCE_SYSTEM,
    }

    write_json(
        out_dir / "year_stats.json",
        {
            "meta": metadata,
            "year_stats": year_stats,
            "decade_stats": decade_stats,
        },
    )
    write_json(
        out_dir / "artist_totals.json",
        {
            "meta": metadata,
            "artist_totals": artist_totals,
        },
    )
    write_json(
        out_dir / "top_songs_by_year.json",
        {
            "meta": metadata,
            "top_songs_by_year": top_songs_by_year,
        },
    )
    write_json(
        out_dir / "weeks_at_number_one.json",
        {
            "meta": metadata,
            "weeks_at_number_one": weeks_at_number_one_payload,
        },
    )

    print(f"[billboard-stats] wrote outputs to {out_dir}")
    print(f"[billboard-stats] years={len(year_stats)} decades={len(decade_stats)} artists={len(artist_totals)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
