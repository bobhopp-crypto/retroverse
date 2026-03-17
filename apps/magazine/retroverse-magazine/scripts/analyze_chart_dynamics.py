#!/usr/bin/env python3
"""Analyze weekly chart movement patterns and append dynamics to year context."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from db_common import (
    connect_read_only,
    list_tables,
    load_data_sources,
    resolve_path,
    sql_year_expression,
    table_columns,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_SOURCES_PATH = PROJECT_ROOT / "data" / "DATA_SOURCES.yaml"
CONTEXT_DIR = PROJECT_ROOT / "issues" / "context"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze chart dynamics for one year.")
    parser.add_argument("--year", type=int, required=True, help="Issue year to analyze.")
    return parser.parse_args()


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def date_sort_key(value: str) -> tuple[int, str]:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if digits:
        try:
            return (int(digits[:8]), str(value))
        except ValueError:
            pass
    return (0, str(value))


def normalize_name(value: str) -> str:
    return " ".join(str(value).strip().split()).lower()


def pick_source_path(sources: dict[str, dict[str, Any]], primary_key: str, fallback_key: str | None = None) -> Path | None:
    entry = sources.get(primary_key, {})
    if (not isinstance(entry, dict) or not entry) and fallback_key:
        entry = sources.get(fallback_key, {})
    if not isinstance(entry, dict):
        return None
    path_text = str(entry.get("path", "")).strip()
    if not path_text:
        return None
    path = resolve_path(PROJECT_ROOT, path_text)
    return path if path.exists() else None


def choose_column(columns: list[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def load_hot100_rows(conn: sqlite3.Connection, year: int) -> list[dict[str, Any]]:
    tables = set(list_tables(conn))

    # Canonical RetroVerse model.
    if {"event", "event_entry", "work", "person"}.issubset(tables):
        rows = conn.execute(
            """
            SELECT
                e.issue_date AS chart_date,
                ee.rank AS rank,
                ee.last_week AS previous_rank,
                ee.work_id AS song_id,
                COALESCE(p.name_display, '') AS artist,
                COALESCE(w.title_display, ee.work_id) AS title,
                ee.weeks_on_chart AS weeks_on_chart
            FROM event_entry ee
            JOIN event e ON e.event_id = ee.event_id
            LEFT JOIN work w ON w.work_id = ee.work_id
            LEFT JOIN person p ON p.person_id = w.primary_person_id
            WHERE substr(e.issue_date, 1, 4) = ?
            ORDER BY e.issue_date, ee.rank
            """,
            (str(year),),
        ).fetchall()
        return [dict(row) for row in rows]

    table_candidates = [name for name in ["chart_positions", "hot100"] if name in tables]
    for table_name in table_candidates:
        columns = table_columns(conn, table_name)
        date_col = choose_column(columns, ["chart_date", "issue_date", "chart_week", "week", "date", "year"])
        rank_col = choose_column(columns, ["rank", "position", "chart_position"])
        title_col = choose_column(columns, ["title", "song", "track"])
        artist_col = choose_column(columns, ["artist", "artist_name"])
        prev_col = choose_column(columns, ["previous_rank", "last_week", "prev_rank"])
        song_id_col = choose_column(columns, ["song_id", "work_id", "mbid", "id"])
        weeks_col = choose_column(columns, ["weeks_on_chart"])

        if not all([date_col, rank_col, title_col, artist_col]):
            continue

        select_prev = f", {prev_col} AS previous_rank" if prev_col else ", NULL AS previous_rank"
        select_song_id = f", {song_id_col} AS song_id" if song_id_col else ", '' AS song_id"
        select_weeks = f", {weeks_col} AS weeks_on_chart" if weeks_col else ", NULL AS weeks_on_chart"

        query = f"""
            SELECT
                {date_col} AS chart_date,
                {rank_col} AS rank
                {select_prev}
                {select_song_id}
                , {artist_col} AS artist
                , {title_col} AS title
                {select_weeks}
            FROM {table_name}
            WHERE {sql_year_expression(date_col)} = ?
            ORDER BY {date_col}, {rank_col}
        """
        rows = conn.execute(query, (str(year),)).fetchall()
        return [dict(row) for row in rows]

    return []


def load_album_rows(conn: sqlite3.Connection, year: int) -> list[dict[str, Any]]:
    tables = set(list_tables(conn))
    if "albums" not in tables:
        return []

    columns = table_columns(conn, "albums")
    date_col = choose_column(columns, ["date", "chart_week", "chart_date", "issue_date", "week", "year"])
    rank_col = choose_column(columns, ["rank", "position", "chart_position"])
    title_col = choose_column(columns, ["album", "title", "name"])
    artist_col = choose_column(columns, ["artist", "artist_name"])
    prev_col = choose_column(columns, ["previous_rank", "last_week", "prev_rank"])
    album_id_col = choose_column(columns, ["album_id", "id"])
    weeks_col = choose_column(columns, ["weeks_on_chart", "length"])

    if not all([date_col, rank_col, title_col, artist_col]):
        return []

    select_prev = f", {prev_col} AS previous_rank" if prev_col else ", NULL AS previous_rank"
    select_album_id = f", {album_id_col} AS album_id" if album_id_col else ", '' AS album_id"
    select_weeks = f", {weeks_col} AS weeks_on_chart" if weeks_col else ", NULL AS weeks_on_chart"

    query = f"""
        SELECT
            {date_col} AS chart_date,
            {rank_col} AS rank
            {select_prev}
            {select_album_id}
            , {artist_col} AS artist
            , {title_col} AS title
            {select_weeks}
        FROM albums
        WHERE {sql_year_expression(date_col)} = ?
        ORDER BY {date_col}, {rank_col}
    """
    rows = [dict(row) for row in conn.execute(query, (str(year),)).fetchall()]
    for row in rows:
        row["album_group_id"] = f"{normalize_name(row.get('title', ''))}::{normalize_name(row.get('artist', ''))}"
    return rows


def build_timelines(rows: list[dict[str, Any]], entity_id_field: str = "song_id") -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        rank = as_int(row.get("rank"))
        if rank is None or rank <= 0:
            continue

        date_text = str(row.get("chart_date", "")).strip()
        if not date_text:
            continue

        title = str(row.get("title", "")).strip()
        artist = str(row.get("artist", "")).strip()
        raw_id = str(row.get(entity_id_field, "")).strip()
        if not raw_id:
            raw_id = f"{normalize_name(title)}::{normalize_name(artist)}"

        normalized = {
            "chart_date": date_text,
            "rank": rank,
            "previous_rank": as_int(row.get("previous_rank")),
            "id": raw_id,
            "title": title,
            "artist": artist,
            "weeks_on_chart": as_int(row.get("weeks_on_chart")),
        }
        grouped.setdefault(raw_id, []).append(normalized)

    for key in grouped:
        grouped[key].sort(key=lambda item: date_sort_key(item["chart_date"]))
    return grouped


def consecutive_max(flags: list[bool]) -> int:
    best = 0
    current = 0
    for flag in flags:
        if flag:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def summarize_timelines(timelines: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for entity_id, timeline in timelines.items():
        if not timeline:
            continue

        title = timeline[0].get("title", "")
        artist = timeline[0].get("artist", "")
        ranks = [int(item["rank"]) for item in timeline]
        weeks_field_max = max((item.get("weeks_on_chart") or 0) for item in timeline)
        total_weeks = weeks_field_max if weeks_field_max > 0 else len(timeline)

        largest_jump = 0
        largest_jump_date = ""
        largest_drop = 0
        largest_drop_date = ""
        uptrend_flags: list[bool] = []

        for index, item in enumerate(timeline):
            rank = int(item["rank"])
            prev_rank = item.get("previous_rank")
            if prev_rank is None and index > 0:
                prev_rank = timeline[index - 1]["rank"]

            if prev_rank is None:
                uptrend_flags.append(False)
                continue

            jump = int(prev_rank) - rank
            drop = rank - int(prev_rank)
            if jump > largest_jump:
                largest_jump = jump
                largest_jump_date = str(item["chart_date"])
            if drop > largest_drop:
                largest_drop = drop
                largest_drop_date = str(item["chart_date"])
            uptrend_flags.append(jump > 0)

        weeks_to_top10: int | None = None
        for idx, rank in enumerate(ranks, start=1):
            if rank <= 10:
                weeks_to_top10 = idx
                break

        weeks_in_top10 = sum(1 for rank in ranks if rank <= 10)
        weeks_at_rank2 = sum(1 for rank in ranks if rank == 2)
        peak_rank = min(ranks)
        peak_41_45 = any(41 <= rank <= 45 for rank in ranks)
        ever_top40 = any(rank <= 40 for rank in ranks)

        summaries.append(
            {
                "id": entity_id,
                "title": title,
                "artist": artist,
                "peak_rank": peak_rank,
                "weeks_on_chart": total_weeks,
                "weeks_in_top10": weeks_in_top10,
                "weeks_at_rank2": weeks_at_rank2,
                "weeks_to_top10": weeks_to_top10,
                "largest_single_week_jump": largest_jump,
                "largest_single_week_jump_date": largest_jump_date,
                "largest_single_week_drop": largest_drop,
                "largest_single_week_drop_date": largest_drop_date,
                "longest_upward_streak": consecutive_max(uptrend_flags),
                "near_miss": peak_41_45 and not ever_top40,
            }
        )
    return summaries


def compact_song_row(row: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    payload = {"title": row.get("title", ""), "artist": row.get("artist", "")}
    payload.update(extra)
    return payload


def top_rows(rows: list[dict[str, Any]], metric: str, limit: int, require_positive: bool = False) -> list[dict[str, Any]]:
    filtered = rows
    if require_positive:
        filtered = [row for row in rows if as_int(row.get(metric)) and int(row.get(metric, 0)) > 0]
    return sorted(
        filtered,
        key=lambda row: (
            -(as_int(row.get(metric)) or 0),
            as_int(row.get("peak_rank")) or 9999,
            str(row.get("title", "")).lower(),
        ),
    )[:limit]


def build_chart_dynamics(song_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    fastest_risers_rows = top_rows(song_summaries, "largest_single_week_jump", limit=5, require_positive=True)
    fastest_fallers_rows = top_rows(song_summaries, "largest_single_week_drop", limit=5, require_positive=True)
    slow_burn_rows = sorted(
        [row for row in song_summaries if row.get("weeks_to_top10") is not None],
        key=lambda row: (-(int(row["weeks_to_top10"])), as_int(row.get("peak_rank")) or 9999, str(row.get("title", "")).lower()),
    )[:5]
    longest_top10_rows = top_rows(song_summaries, "weeks_in_top10", limit=5, require_positive=True)
    longest_chart_rows = top_rows(song_summaries, "weeks_on_chart", limit=5, require_positive=True)
    near_miss_rows = sorted(
        [row for row in song_summaries if row.get("near_miss")],
        key=lambda row: (as_int(row.get("peak_rank")) or 9999, -(as_int(row.get("weeks_on_chart")) or 0), str(row.get("title", "")).lower()),
    )[:10]
    number_two_rows = sorted(
        [row for row in song_summaries if (as_int(row.get("peak_rank")) == 2 and (as_int(row.get("weeks_at_rank2")) or 0) > 0)],
        key=lambda row: (-(as_int(row.get("weeks_at_rank2")) or 0), -(as_int(row.get("weeks_on_chart")) or 0), str(row.get("title", "")).lower()),
    )[:10]

    return {
        "fastest_risers": [
            compact_song_row(
                row,
                {
                    "largest_single_week_jump": int(row.get("largest_single_week_jump", 0)),
                    "jump_week": row.get("largest_single_week_jump_date", ""),
                    "peak_rank": as_int(row.get("peak_rank")),
                },
            )
            for row in fastest_risers_rows
        ],
        "fastest_fallers": [
            compact_song_row(
                row,
                {
                    "largest_single_week_drop": int(row.get("largest_single_week_drop", 0)),
                    "drop_week": row.get("largest_single_week_drop_date", ""),
                    "peak_rank": as_int(row.get("peak_rank")),
                },
            )
            for row in fastest_fallers_rows
        ],
        "slow_burn_hits": [
            compact_song_row(
                row,
                {
                    "weeks_to_top10": int(row.get("weeks_to_top10", 0)),
                    "peak_rank": as_int(row.get("peak_rank")),
                },
            )
            for row in slow_burn_rows
        ],
        "longest_top10_runs": [
            compact_song_row(
                row,
                {
                    "weeks_in_top10": int(row.get("weeks_in_top10", 0)),
                    "peak_rank": as_int(row.get("peak_rank")),
                },
            )
            for row in longest_top10_rows
        ],
        "longest_chart_runs": [
            compact_song_row(
                row,
                {
                    "weeks_on_chart": int(row.get("weeks_on_chart", 0)),
                    "peak_rank": as_int(row.get("peak_rank")),
                },
            )
            for row in longest_chart_rows
        ],
        "largest_single_week_jump": [
            compact_song_row(
                row,
                {
                    "value": int(row.get("largest_single_week_jump", 0)),
                    "week": row.get("largest_single_week_jump_date", ""),
                },
            )
            for row in fastest_risers_rows
        ],
        "largest_single_week_drop": [
            compact_song_row(
                row,
                {
                    "value": int(row.get("largest_single_week_drop", 0)),
                    "week": row.get("largest_single_week_drop_date", ""),
                },
            )
            for row in fastest_fallers_rows
        ],
        "near_miss_hits": [
            compact_song_row(
                row,
                {
                    "peak_rank": as_int(row.get("peak_rank")),
                    "weeks_on_chart": int(row.get("weeks_on_chart", 0)),
                },
            )
            for row in near_miss_rows
        ],
        "longest_number_two_streaks": [
            compact_song_row(
                row,
                {
                    "weeks_at_rank2": int(row.get("weeks_at_rank2", 0)),
                    "weeks_on_chart": int(row.get("weeks_on_chart", 0)),
                },
            )
            for row in number_two_rows
        ],
    }


def build_album_dynamics(album_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    # weeks_at_number_one is not in generic summary; derive here.
    for row in album_summaries:
        if "weeks_at_number_one" not in row:
            row["weeks_at_number_one"] = int(row.get("weeks_at_rank1", 0) or 0)

    number_one_rows = sorted(
        [row for row in album_summaries if as_int(row.get("peak_rank")) == 1 and (as_int(row.get("weeks_at_number_one")) or 0) > 0],
        key=lambda row: (-(as_int(row.get("weeks_at_number_one")) or 0), -(as_int(row.get("weeks_on_chart")) or 0), str(row.get("title", "")).lower()),
    )[:10]

    top10_rows = sorted(
        [row for row in album_summaries if (as_int(row.get("weeks_in_top10")) or 0) > 0],
        key=lambda row: (-(as_int(row.get("weeks_in_top10")) or 0), as_int(row.get("peak_rank")) or 9999, str(row.get("title", "")).lower()),
    )[:10]

    slowest_to_no1_rows = sorted(
        [row for row in album_summaries if row.get("weeks_to_number_one") is not None],
        key=lambda row: (-(int(row["weeks_to_number_one"])), str(row.get("title", "")).lower()),
    )[:10]

    return {
        "longest_number_one_runs": [
            {
                "album": row.get("title", ""),
                "artist": row.get("artist", ""),
                "weeks_at_number_one": int(row.get("weeks_at_number_one", 0)),
                "weeks_on_chart": int(row.get("weeks_on_chart", 0)),
            }
            for row in number_one_rows
        ],
        "longest_top10_runs": [
            {
                "album": row.get("title", ""),
                "artist": row.get("artist", ""),
                "weeks_in_top10": int(row.get("weeks_in_top10", 0)),
                "peak_rank": as_int(row.get("peak_rank")),
            }
            for row in top10_rows
        ],
        "slowest_climb_to_number_one": [
            {
                "album": row.get("title", ""),
                "artist": row.get("artist", ""),
                "weeks_to_number_one": int(row.get("weeks_to_number_one", 0)),
                "weeks_at_number_one": int(row.get("weeks_at_number_one", 0)),
            }
            for row in slowest_to_no1_rows
        ],
    }


def enrich_album_summary_metrics(album_timelines: dict[str, list[dict[str, Any]]], summaries: list[dict[str, Any]]) -> None:
    by_id = {row["id"]: row for row in summaries}
    for album_id, timeline in album_timelines.items():
        summary = by_id.get(album_id)
        if not summary:
            continue
        ranks = [int(item["rank"]) for item in timeline]
        summary["weeks_at_number_one"] = sum(1 for rank in ranks if rank == 1)
        weeks_to_number_one: int | None = None
        for idx, rank in enumerate(ranks, start=1):
            if rank == 1:
                weeks_to_number_one = idx
                break
        summary["weeks_to_number_one"] = weeks_to_number_one


def run(year: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, int]]:
    sources = load_data_sources(DATA_SOURCES_PATH)
    hot100_path = pick_source_path(sources, "billboard_hot_100", "billboard_hot_100_db")
    b200_path = pick_source_path(sources, "billboard_200", "billboard_200_db")

    if hot100_path is None:
        raise FileNotFoundError("Could not resolve canonical Hot100 DB path from DATA_SOURCES.yaml")
    if b200_path is None:
        raise FileNotFoundError("Could not resolve canonical Billboard 200 DB path from DATA_SOURCES.yaml")

    with connect_read_only(hot100_path) as hot_conn:
        hot_rows = load_hot100_rows(hot_conn, year)
    hot_timelines = build_timelines(hot_rows, entity_id_field="song_id")
    hot_summaries = summarize_timelines(hot_timelines)

    with connect_read_only(b200_path) as album_conn:
        album_rows = load_album_rows(album_conn, year)
    album_timelines = build_timelines(album_rows, entity_id_field="album_group_id")
    album_summaries = summarize_timelines(album_timelines)
    enrich_album_summary_metrics(album_timelines, album_summaries)

    dynamics = build_chart_dynamics(hot_summaries)
    album_dynamics = build_album_dynamics(album_summaries)
    counts = {
        "hot100_rows": len(hot_rows),
        "hot100_entities": len(hot_timelines),
        "album_rows": len(album_rows),
        "album_entities": len(album_timelines),
    }
    return dynamics, album_dynamics, counts


def main() -> int:
    args = parse_args()
    year = int(args.year)

    context_path = CONTEXT_DIR / f"{year}_context.json"
    if not context_path.exists():
        raise SystemExit(f"Context file missing: {context_path}. Run generate_year_context first.")

    try:
        context_payload = json.loads(context_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid context JSON: {context_path} ({exc})")

    if not isinstance(context_payload, dict):
        raise SystemExit(f"Context file root must be a JSON object: {context_path}")

    dynamics, album_dynamics, counts = run(year)
    context_payload["chart_dynamics"] = dynamics
    context_payload["album_dynamics"] = album_dynamics

    context_path.write_text(json.dumps(context_payload, indent=2) + "\n", encoding="utf-8")

    print("Chart dynamics analysis complete")
    print(f"Context file: {context_path}")
    print(f"Hot100 rows analyzed: {counts['hot100_rows']} ({counts['hot100_entities']} songs)")
    print(f"Album rows analyzed: {counts['album_rows']} ({counts['album_entities']} albums)")
    print(f"fastest_risers: {len(dynamics['fastest_risers'])}")
    print(f"near_miss_hits: {len(dynamics['near_miss_hits'])}")
    print(f"album longest_number_one_runs: {len(album_dynamics['longest_number_one_runs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
