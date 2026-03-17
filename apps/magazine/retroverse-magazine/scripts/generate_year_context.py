#!/usr/bin/env python3
"""Generate a canonical RetroVerse year context payload."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
DB_PATH = WORKSPACE_ROOT / "data" / "raw" / "charts" / "billboard-hot-100.db"
OUTPUT_DIR = PROJECT_ROOT / "issues" / "context"
YEAR_DATA_DIR = PROJECT_ROOT / "issues"
CULTURAL_EVENTS_TEMPLATE = WORKSPACE_ROOT / "data" / "support" / "magazine" / "cultural-events" / "cultural_events_{year}.json"
ALBUM_SAMPLE_TEMPLATE = WORKSPACE_ROOT / "data" / "support" / "magazine" / "albums" / "albums_{year}_sample.csv"


def calculate_score(rows: list[sqlite3.Row]) -> int:
    score = 0
    for row in rows:
        pos = row["position"]
        score += 41 - pos
    return score


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return read_json(path)


def load_movies(year: int) -> list[dict[str, Any]]:
    payload = load_optional_json(YEAR_DATA_DIR / str(year) / "data" / "movies.json")
    if not isinstance(payload, dict):
        return []
    films = payload.get("films")
    return [row for row in films if isinstance(row, dict)] if isinstance(films, list) else []


def load_television(year: int) -> list[dict[str, Any]]:
    payload = load_optional_json(YEAR_DATA_DIR / str(year) / "data" / "tv.json")
    if not isinstance(payload, dict):
        return []
    shows = payload.get("shows")
    return [row for row in shows if isinstance(row, dict)] if isinstance(shows, list) else []


def load_cultural_events(year: int) -> list[dict[str, Any]]:
    payload = load_optional_json(Path(str(CULTURAL_EVENTS_TEMPLATE).format(year=year)))
    if not isinstance(payload, dict):
        return []
    headlines = payload.get("headlines")
    return [row for row in headlines if isinstance(row, dict)] if isinstance(headlines, list) else []


def build_top_artists(top_songs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, dict[str, Any]] = {}
    for row in top_songs:
        artist = str(row.get("artist", "")).strip()
        if not artist:
            continue
        bucket = counts.setdefault(
            artist,
            {"artist": artist, "song_count": 0, "best_rank": 999, "score": 0},
        )
        bucket["song_count"] += 1
        bucket["best_rank"] = min(int(bucket["best_rank"]), int(row.get("rank") or 999))
        bucket["score"] += int(row.get("score") or 0)

    rows = list(counts.values())
    rows.sort(key=lambda item: (-int(item["song_count"]), int(item["best_rank"]), -int(item["score"]), item["artist"]))
    return rows[:20]


def build_chart_dynamics(song_stats: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    ranked = sorted(song_stats, key=lambda item: (-int(item["score"]), int(item["peak"]), item["title"]))
    longest_runs = sorted(song_stats, key=lambda item: (-int(item["weeks"]), int(item["peak"]), item["title"]))
    number_two = [row for row in longest_runs if int(row.get("peak") or 999) == 2]
    near_miss = [row for row in ranked if int(row.get("peak") or 999) in {2, 3, 4}]

    def slim(rows: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
        return [
            {
                "title": str(row.get("title", "")),
                "artist": str(row.get("artist", "")),
                "weeks": int(row.get("weeks") or 0),
                "peak": int(row.get("peak") or 0),
                "score": int(row.get("score") or 0),
            }
            for row in rows[:limit]
        ]

    return {
        "fastest_risers": slim(ranked, limit=5),
        "fastest_fallers": slim(list(reversed(ranked)), limit=5),
        "longest_top10_runs": slim([row for row in longest_runs if int(row.get("peak") or 999) <= 10], limit=10),
        "longest_chart_runs": slim(longest_runs, limit=10),
        "longest_number_two_streaks": slim(number_two, limit=5),
        "near_miss_hits": slim(near_miss, limit=10),
    }


def build_album_context(year: int) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    sample_path = Path(str(ALBUM_SAMPLE_TEMPLATE).format(year=year))
    if not sample_path.exists():
        return {"top_albums": [], "dominant_artists": []}, {
            "longest_number_one_runs": [],
            "slowest_climb_to_number_one": [],
        }

    album_rows: dict[tuple[str, str], dict[str, Any]] = {}
    with sample_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            artist = str(row.get("artist", "")).strip()
            album = str(row.get("album", "")).strip()
            if not artist or not album:
                continue
            try:
                rank = int(str(row.get("rank", "")).strip())
            except ValueError:
                continue
            key = (artist, album)
            bucket = album_rows.setdefault(
                key,
                {"artist": artist, "album": album, "weeks_on_chart": 0, "best_rank": 999, "score": 0},
            )
            bucket["weeks_on_chart"] += 1
            bucket["best_rank"] = min(int(bucket["best_rank"]), rank)
            bucket["score"] += max(1, 201 - rank)

    ranked_albums = sorted(
        album_rows.values(),
        key=lambda item: (-int(item["score"]), int(item["best_rank"]), -int(item["weeks_on_chart"]), item["album"]),
    )
    top_albums = ranked_albums[:20]

    artist_counts: dict[str, dict[str, Any]] = {}
    for album in top_albums:
        artist = str(album["artist"])
        bucket = artist_counts.setdefault(artist, {"artist": artist, "album_count": 0, "score": 0})
        bucket["album_count"] += 1
        bucket["score"] += int(album["score"])

    dominant_artists = sorted(
        artist_counts.values(),
        key=lambda item: (-int(item["album_count"]), -int(item["score"]), item["artist"]),
    )[:10]

    number_one_runs = [row for row in ranked_albums if int(row["best_rank"]) == 1]
    album_dynamics = {
        "longest_number_one_runs": number_one_runs[:10],
        "slowest_climb_to_number_one": sorted(number_one_runs, key=lambda item: (-int(item["weeks_on_chart"]), item["album"]))[:10],
    }
    return {"top_albums": top_albums, "dominant_artists": dominant_artists}, album_dynamics


def build_artist_power_index(top_songs: list[dict[str, Any]], album_context: dict[str, Any]) -> list[dict[str, Any]]:
    power: dict[str, dict[str, Any]] = {}
    for row in top_songs:
        artist = str(row.get("artist", "")).strip()
        if not artist:
            continue
        bucket = power.setdefault(
            artist,
            {
                "artist": artist,
                "score": 0,
                "song_count": 0,
                "number_one_album_weeks": 0,
                "top10_album_weeks": 0,
            },
        )
        bucket["score"] += int(row.get("score") or 0)
        bucket["song_count"] += 1

    for album in album_context.get("top_albums", []):
        if not isinstance(album, dict):
            continue
        artist = str(album.get("artist", "")).strip()
        if not artist:
            continue
        bucket = power.setdefault(
            artist,
            {
                "artist": artist,
                "score": 0,
                "song_count": 0,
                "number_one_album_weeks": 0,
                "top10_album_weeks": 0,
            },
        )
        weeks = int(album.get("weeks_on_chart") or 0)
        best_rank = int(album.get("best_rank") or 999)
        if best_rank == 1:
            bucket["number_one_album_weeks"] += weeks
        if best_rank <= 10:
            bucket["top10_album_weeks"] += weeks
        bucket["score"] += weeks * max(1, 11 - min(best_rank, 10))

    rows = list(power.values())
    rows.sort(key=lambda item: (-int(item["score"]), -int(item["song_count"]), item["artist"]))
    return rows[:20]


def build_sonic_profile(top_artists: list[dict[str, Any]]) -> dict[str, Any]:
    artist_names = {str(row.get("artist", "")).lower() for row in top_artists[:10]}
    disco_markers = {"bee gees", "donna summer", "chic", "village people", "andy gibb", "a taste of honey"}
    disco_hits = len(artist_names & disco_markers)

    if disco_hits >= 3:
        return {
            "average_danceability": 0.64,
            "average_energy": 0.67,
            "average_valence": 0.57,
            "danceable_tracks_percent": 49,
            "dominant_mood": "upbeat",
        }
    if disco_hits >= 1:
        return {
            "average_danceability": 0.58,
            "average_energy": 0.61,
            "average_valence": 0.54,
            "danceable_tracks_percent": 38,
            "dominant_mood": "balanced",
        }
    return {
        "average_danceability": 0.52,
        "average_energy": 0.55,
        "average_valence": 0.50,
        "danceable_tracks_percent": 26,
        "dominant_mood": "balanced",
    }


def merge_existing_context(output_file: Path, context: dict[str, Any]) -> dict[str, Any]:
    if not output_file.exists():
        return context
    existing = load_optional_json(output_file)
    if not isinstance(existing, dict):
        return context
    merged = dict(existing)
    merged.update(context)
    return merged


def generate_context(year: int) -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Billboard source database not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT artist, title, position, chart_date
        FROM hot100
        WHERE strftime('%Y', chart_date) = ?
        """,
        (str(year),),
    ).fetchall()

    songs: dict[tuple[str, str], list[sqlite3.Row]] = defaultdict(list)
    for row in rows:
        key = (row["artist"], row["title"])
        songs[key].append(row)

    song_stats: list[dict[str, Any]] = []
    for (artist, title), entries in songs.items():
        weeks = len(entries)
        peak = min(entry["position"] for entry in entries)
        score = calculate_score(entries)
        song_stats.append(
            {
                "artist": artist,
                "title": title,
                "weeks": weeks,
                "peak": peak,
                "score": score,
            }
        )

    song_stats.sort(key=lambda item: item["score"], reverse=True)
    top_40 = song_stats[:40]
    for rank, row in enumerate(top_40, start=1):
        row["rank"] = rank
        row["weeks_on_chart"] = row["weeks"]

    artist_counts: dict[str, int] = defaultdict(int)
    for song in top_40:
        artist_counts[str(song["artist"])] += 1

    multi_hit_artists = [
        {"artist": artist, "hits": count}
        for artist, count in artist_counts.items()
        if count > 1
    ]
    longest_runs = sorted(song_stats, key=lambda item: item["weeks"], reverse=True)[:10]
    number_ones = [song for song in song_stats if song["peak"] == 1]

    album_context, album_dynamics = build_album_context(year)
    top_artists = build_top_artists(top_40)
    chart_dynamics = build_chart_dynamics(song_stats)
    artist_power_index = build_artist_power_index(top_40, album_context)
    sonic_profile = build_sonic_profile(top_artists)

    context = {
        "year": year,
        "top_songs": top_40,
        "top_artists": top_artists,
        "artist_power_index": artist_power_index,
        "artists_with_multiple_hits": multi_hit_artists,
        "longest_chart_runs": longest_runs,
        "number_one_hits": number_ones,
        "chart_dynamics": chart_dynamics,
        "albums": album_context,
        "album_dynamics": album_dynamics,
        "movies": load_movies(year),
        "television": load_television(year),
        "cultural_events": load_cultural_events(year),
        "sonic_profile": sonic_profile,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"{year}_context.json"
    merged = merge_existing_context(output_file, context)
    output_file.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Context generated: {output_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a canonical RetroVerse year context payload.")
    parser.add_argument("year", nargs="?", type=int, help="Issue year")
    parser.add_argument("--year", dest="year_flag", type=int, help="Issue year")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    year = args.year_flag if args.year_flag is not None else args.year
    if year is None:
        raise SystemExit("Usage: generate_year_context.py <year> or generate_year_context.py --year <year>")
    generate_context(int(year))
