#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import get_dataset_path
from lineage_hook import run_with_lineage


DEFAULT_DB_PATH = get_dataset_path("billboard_hot_100", fallback="data/raw/charts/billboard-hot-100.db")
DEFAULT_OUTPUT_DIR = get_dataset_path("year_master_dataset", fallback="data/derived/year-masters")

SYNONYMS = {
    "chart_date": ["chart_date", "issue_date", "date", "week_date"],
    "rank": ["rank", "position", "chart_position", "pos"],
    "title": ["title", "title_display", "song_title", "track_title"],
    "artist": ["artist", "artist_name", "performer", "name_display"],
}

CSV_COLUMNS = [
    "rv_rank",
    "title",
    "artist",
    "total_score",
    "weekly_score_top26",
    "peak_bonus",
    "peak_rank",
    "weeks_on_chart",
    "weeks_in_top_10",
    "weeks_in_top_40",
    "first_chart_date",
    "last_chart_date",
]


def _q(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _pick_column(columns: list[str], aliases: list[str]) -> str | None:
    lowered = {col.lower(): col for col in columns}
    for alias in aliases:
        if alias.lower() in lowered:
            return lowered[alias.lower()]
    return None


def _get_schema(conn: sqlite3.Connection) -> dict[str, list[str]]:
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]

    schema: dict[str, list[str]] = {}
    for table in tables:
        info = conn.execute(f"PRAGMA table_info({_q(table)})").fetchall()
        schema[table] = [row[1] for row in info]
    return schema


def _detect_event_join_strategy(schema: dict[str, list[str]]) -> dict[str, Any] | None:
    required_tables = {"event", "event_entry", "work"}
    if not required_tables.issubset(set(schema)):
        return None

    event_cols = schema["event"]
    entry_cols = schema["event_entry"]
    work_cols = schema["work"]

    date_col = _pick_column(event_cols, SYNONYMS["chart_date"])
    rank_col = _pick_column(entry_cols, SYNONYMS["rank"])
    title_col = _pick_column(work_cols, SYNONYMS["title"])

    event_id_col = _pick_column(event_cols, ["event_id"])
    entry_event_id_col = _pick_column(entry_cols, ["event_id"])
    work_id_col = _pick_column(work_cols, ["work_id"])
    entry_work_id_col = _pick_column(entry_cols, ["work_id"])

    if not all([date_col, rank_col, title_col, event_id_col, entry_event_id_col, work_id_col, entry_work_id_col]):
        return None

    artist_sources: list[str] = []
    joins: list[str] = []

    if "person" in schema:
        person_cols = schema["person"]
        person_id_col = _pick_column(person_cols, ["person_id"])
        person_name_col = _pick_column(person_cols, SYNONYMS["artist"])
        work_person_fk = _pick_column(work_cols, ["primary_person_id", "person_id", "artist_id"])
        if person_id_col and person_name_col and work_person_fk:
            joins.append(
                f'LEFT JOIN {_q("person")} p ON p.{_q(person_id_col)} = w.{_q(work_person_fk)}'
            )
            artist_sources.append(f"p.{_q(person_name_col)}")

    work_artist_col = _pick_column(work_cols, SYNONYMS["artist"])
    if work_artist_col:
        artist_sources.append(f"w.{_q(work_artist_col)}")

    if not artist_sources:
        return None

    artist_expr = artist_sources[0] if len(artist_sources) == 1 else f"COALESCE({', '.join(artist_sources)})"
    sql = f"""
        SELECT
            e.{_q(date_col)} AS chart_date,
            ee.{_q(rank_col)} AS rank,
            w.{_q(title_col)} AS title,
            {artist_expr} AS artist
        FROM {_q("event")} e
        JOIN {_q("event_entry")} ee ON ee.{_q(entry_event_id_col)} = e.{_q(event_id_col)}
        JOIN {_q("work")} w ON w.{_q(work_id_col)} = ee.{_q(entry_work_id_col)}
        {' '.join(joins)}
        WHERE e.{_q(date_col)} BETWEEN ? AND ?
          AND ee.{_q(rank_col)} BETWEEN 1 AND 100
        ORDER BY e.{_q(date_col)} ASC, ee.{_q(rank_col)} ASC
    """.strip()

    note = (
        "Detected event/event_entry/work strategy "
        f"(event.{date_col}, event_entry.{rank_col}, work.{title_col}, artist={artist_expr})."
    )
    return {
        "strategy": "event_join",
        "sql": sql,
        "extra_params": [],
        "note": note,
    }


def _detect_hot100_chart_ids(conn: sqlite3.Connection, schema: dict[str, list[str]]) -> list[Any]:
    if "charts" not in schema:
        return []

    chart_cols = schema["charts"]
    chart_id_col = _pick_column(chart_cols, ["chart_id", "id"])
    chart_key_col = _pick_column(chart_cols, ["chart_key", "key", "slug"])
    chart_name_col = _pick_column(chart_cols, ["chart_name", "name", "label"])

    if not chart_id_col or (not chart_key_col and not chart_name_col):
        return []

    predicates: list[str] = []
    params: list[str] = []
    if chart_key_col:
        predicates.append(f"LOWER({_q(chart_key_col)}) LIKE ?")
        params.extend(["%hot100%", "%hot_100%", "%hot-100%"])
        predicates.append(f"LOWER({_q(chart_key_col)}) = ?")
        params.append("billboard_hot100")
    if chart_name_col:
        predicates.append(f"LOWER({_q(chart_name_col)}) LIKE ?")
        params.extend(["%hot 100%", "%hot100%"])

    if not predicates:
        return []

    sql = f'SELECT {_q(chart_id_col)} FROM {_q("charts")} WHERE ' + " OR ".join(predicates)
    return [row[0] for row in conn.execute(sql, params).fetchall() if row[0] is not None]


def _detect_single_table_strategy(conn: sqlite3.Connection, schema: dict[str, list[str]]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None

    for table, columns in schema.items():
        mapping = {key: _pick_column(columns, aliases) for key, aliases in SYNONYMS.items()}
        if not all(mapping[k] for k in ["chart_date", "rank", "title", "artist"]):
            continue

        score = sum(1 for value in mapping.values() if value is not None)
        lowered_table = table.lower()
        if "hot100" in lowered_table or "hot_100" in lowered_table or "hot-100" in lowered_table:
            score += 2

        candidate = {"table": table, "mapping": mapping, "score": score}
        if best is None or candidate["score"] > best["score"]:
            best = candidate

    if best is None:
        return None

    table = best["table"]
    mapping = best["mapping"]
    columns = schema[table]

    where_clauses = [
        f'{_q(mapping["chart_date"])} BETWEEN ? AND ?',
        f'{_q(mapping["rank"])} BETWEEN 1 AND 100',
    ]
    extra_params: list[Any] = []

    chart_id_col = _pick_column(columns, ["chart_id"])
    if chart_id_col:
        hot100_ids = _detect_hot100_chart_ids(conn, schema)
        if hot100_ids:
            placeholders = ", ".join("?" for _ in hot100_ids)
            where_clauses.append(f"{_q(chart_id_col)} IN ({placeholders})")
            extra_params.extend(hot100_ids)

    sql = f"""
        SELECT
            {_q(mapping["chart_date"])} AS chart_date,
            {_q(mapping["rank"])} AS rank,
            {_q(mapping["title"])} AS title,
            {_q(mapping["artist"])} AS artist
        FROM {_q(table)}
        WHERE {' AND '.join(where_clauses)}
        ORDER BY {_q(mapping["chart_date"])} ASC, {_q(mapping["rank"])} ASC
    """.strip()

    note = f"Detected single-table strategy on {table} with mapping {mapping}."
    if chart_id_col and extra_params:
        note += f" Filtered to Hot 100 chart IDs: {extra_params}."

    return {
        "strategy": "single_table",
        "sql": sql,
        "extra_params": extra_params,
        "note": note,
    }


def _detect_query_strategy(conn: sqlite3.Connection) -> dict[str, Any]:
    schema = _get_schema(conn)

    strategy = _detect_event_join_strategy(schema)
    if strategy is None:
        strategy = _detect_single_table_strategy(conn, schema)

    if strategy is None:
        raise RuntimeError(
            "Could not detect a usable schema for chart_date/rank/title/artist. "
            f"Available tables: {schema}"
        )

    return strategy


def _weekly_tier_bonus(rank: int) -> int:
    if rank <= 5:
        return 25
    if rank <= 10:
        return 15
    if rank <= 20:
        return 8
    if rank <= 40:
        return 3
    return 0


def _weekly_score(rank: int) -> float:
    base_points = (101 - rank) ** 1.4
    return base_points + _weekly_tier_bonus(rank)


def _peak_bonus(peak_rank: int) -> int:
    if peak_rank == 1:
        return 120
    if peak_rank <= 3:
        return 75
    if peak_rank <= 5:
        return 40
    if peak_rank <= 10:
        return 15
    return 0


def _fetch_year_rows(conn: sqlite3.Connection, strategy: dict[str, Any], year: int) -> list[sqlite3.Row]:
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    params: list[Any] = [start_date, end_date, *strategy.get("extra_params", [])]
    return conn.execute(strategy["sql"], params).fetchall()


def _build_rankings(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)

    for row in rows:
        chart_date = str(row["chart_date"]).strip()
        title = str(row["title"]).strip()
        artist = str(row["artist"]).strip()
        rank = int(row["rank"])

        if not chart_date or not title or not artist:
            continue
        grouped[(title, artist)].append((chart_date, rank))

    ranked: list[dict[str, Any]] = []
    for (title, artist), entries in grouped.items():
        entries.sort(key=lambda item: item[0])
        ranks = [rank for _, rank in entries]
        weekly_scores = sorted((_weekly_score(rank) for rank in ranks), reverse=True)

        peak_rank = min(ranks)
        weekly_score_top26 = sum(weekly_scores[:26])
        peak_bonus = _peak_bonus(peak_rank)
        total_score = weekly_score_top26 + peak_bonus

        ranked.append(
            {
                "title": title,
                "artist": artist,
                "peak_rank": peak_rank,
                "weeks_on_chart": len(ranks),
                "weeks_in_top_10": sum(1 for rank in ranks if rank <= 10),
                "weeks_in_top_40": sum(1 for rank in ranks if rank <= 40),
                "first_chart_date": entries[0][0],
                "last_chart_date": entries[-1][0],
                "weekly_score_top26": weekly_score_top26,
                "peak_bonus": peak_bonus,
                "total_score": total_score,
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["total_score"],
            item["peak_rank"],
            -item["weeks_in_top_10"],
            -item["weeks_in_top_40"],
            item["title"].lower(),
            item["artist"].lower(),
        )
    )

    top_100 = ranked[:100]
    for idx, row in enumerate(top_100, start=1):
        row["rv_rank"] = idx
    return top_100


def _format_rows_for_csv(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for row in rows:
        out = dict(row)
        out["total_score"] = f"{out['total_score']:.4f}"
        out["weekly_score_top26"] = f"{out['weekly_score_top26']:.4f}"
        formatted.append(out)
    return formatted


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in CSV_COLUMNS})


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RetroVerse year-end rankings from Billboard weekly chart data.")
    parser.add_argument("--year", type=int, required=True, help="Target year, for example 1974")
    parser.add_argument(
        "--db_path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write CSV outputs (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    db_path = Path(args.db_path)
    output_dir = Path(args.output_dir)

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        strategy = _detect_query_strategy(conn)
        rows = _fetch_year_rows(conn, strategy, args.year)
    finally:
        conn.close()

    if not rows:
        raise RuntimeError(f"No chart rows found for year {args.year}.")

    ranked_rows = _build_rankings(rows)
    if not ranked_rows:
        raise RuntimeError(f"No valid title/artist rows found for year {args.year}.")

    full_rows = _format_rows_for_csv(ranked_rows)
    top40_rows = full_rows[:40]

    full_path = output_dir / f"retroverse_year_end_{args.year}.csv"
    top40_path = output_dir / f"retroverse_year_end_{args.year}_top40.csv"

    _write_csv(full_path, full_rows)
    _write_csv(top40_path, top40_rows)

    print(f"Strategy: {strategy['strategy']}")
    print(f"Note: {strategy['note']}")
    print(f"Wrote {len(full_rows)} rows: {full_path}")
    print(f"Wrote {len(top40_rows)} rows: {top40_path}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
