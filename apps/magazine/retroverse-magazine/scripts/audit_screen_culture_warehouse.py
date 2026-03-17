#!/usr/bin/env python3
"""Audit coverage and quality for the screen/culture warehouse."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from screen_culture_common import WAREHOUSE_ROOT, get_nested, has_value, now_utc_iso, parse_year, read_json


DOCS_PATH = Path(__file__).resolve().parents[1] / "docs" / "SCREEN_CULTURE_WAREHOUSE_AUDIT.md"
MOVIES_MASTER_PATH = WAREHOUSE_ROOT / "movies_master.json"
TELEVISION_MASTER_PATH = WAREHOUSE_ROOT / "television_master.json"

MOVIE_THRESHOLDS = {
    "count": 15,
    "popularity": 10,
    "critic": 10,
}

TELEVISION_THRESHOLDS = {
    "count": 20,
    "network": 15,
    "popularity": 10,
    "critic": 8,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit screen/culture warehouse completeness.")
    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path, default={})
    if not isinstance(payload, dict):
        return []
    records = payload.get("records")
    if not isinstance(records, list):
        return []
    return [item for item in records if isinstance(item, dict)]


def movie_has_box_office(row: dict[str, Any]) -> bool:
    return has_value(row.get("box_office_domestic")) or has_value(row.get("box_office_worldwide"))


def movie_has_critic(row: dict[str, Any]) -> bool:
    critic = row.get("critic_scores")
    return (
        (isinstance(critic, dict) and (has_value(critic.get("metacritic")) or has_value(critic.get("rotten_tomatoes"))))
        or has_value(row.get("awards_summary"))
    )


def movie_has_ratings(row: dict[str, Any]) -> bool:
    return has_value(row.get("imdb_rating")) or has_value(row.get("imdb_votes"))


def movie_has_popularity(row: dict[str, Any]) -> bool:
    return isinstance(row.get("popularity_signals"), dict) and bool(row.get("popularity_signals"))


def tv_has_network(row: dict[str, Any]) -> bool:
    return has_value(row.get("network"))


def tv_has_popularity(row: dict[str, Any]) -> bool:
    viewership = row.get("viewership_signals")
    ratings = row.get("ratings_signals")
    return (isinstance(viewership, dict) and bool(viewership)) or (isinstance(ratings, dict) and bool(ratings))


def tv_has_critic(row: dict[str, Any]) -> bool:
    critic = row.get("critic_scores")
    return (isinstance(critic, dict) and bool(critic)) or has_value(row.get("awards_summary"))


def group_by_year(records: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in records:
        year = parse_year(row.get("year"))
        if year is None:
            continue
        grouped.setdefault(year, []).append(row)
    return grouped


def percent(part: int, whole: int) -> float:
    return round((part / whole) * 100, 2) if whole else 0.0


def field_sparsity(records: list[dict[str, Any]], fields: list[str]) -> dict[str, float]:
    output: dict[str, float] = {}
    total = len(records)
    for field in fields:
        missing = 0
        for row in records:
            if not has_value(get_nested(row, field)):
                missing += 1
        output[field] = percent(missing, total)
    return output


def evaluate_years(
    movie_by_year: dict[int, list[dict[str, Any]]],
    tv_by_year: dict[int, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[str]]:
    years = sorted(set(movie_by_year.keys()) | set(tv_by_year.keys()))
    rows: list[dict[str, Any]] = []
    weak_notes: list[str] = []

    for year in years:
        movies = movie_by_year.get(year, [])
        tv = tv_by_year.get(year, [])

        movie_count = len(movies)
        movie_box = sum(1 for row in movies if movie_has_box_office(row))
        movie_critic = sum(1 for row in movies if movie_has_critic(row))
        movie_rating = sum(1 for row in movies if movie_has_ratings(row))
        movie_pop = sum(1 for row in movies if movie_has_popularity(row))

        tv_count = len(tv)
        tv_network = sum(1 for row in tv if tv_has_network(row))
        tv_pop = sum(1 for row in tv if tv_has_popularity(row))
        tv_critic = sum(1 for row in tv if tv_has_critic(row))

        rows.append(
            {
                "year": year,
                "movies": {
                    "count": movie_count,
                    "with_box_office": movie_box,
                    "with_critic": movie_critic,
                    "with_ratings": movie_rating,
                    "with_popularity": movie_pop,
                },
                "television": {
                    "count": tv_count,
                    "with_network": tv_network,
                    "with_popularity": tv_pop,
                    "with_critic": tv_critic,
                },
            }
        )

        year_weak: list[str] = []
        if movie_count < MOVIE_THRESHOLDS["count"]:
            year_weak.append(f"movies count {movie_count} < {MOVIE_THRESHOLDS['count']}")
        if movie_pop < MOVIE_THRESHOLDS["popularity"]:
            year_weak.append(f"movie popularity {movie_pop} < {MOVIE_THRESHOLDS['popularity']}")
        if movie_critic < MOVIE_THRESHOLDS["critic"]:
            year_weak.append(f"movie critic/acclaim {movie_critic} < {MOVIE_THRESHOLDS['critic']}")

        if tv_count < TELEVISION_THRESHOLDS["count"]:
            year_weak.append(f"tv count {tv_count} < {TELEVISION_THRESHOLDS['count']}")
        if tv_network < TELEVISION_THRESHOLDS["network"]:
            year_weak.append(f"tv network {tv_network} < {TELEVISION_THRESHOLDS['network']}")
        if tv_pop < TELEVISION_THRESHOLDS["popularity"]:
            year_weak.append(f"tv popularity/viewership {tv_pop} < {TELEVISION_THRESHOLDS['popularity']}")
        if tv_critic < TELEVISION_THRESHOLDS["critic"]:
            year_weak.append(f"tv critic/acclaim {tv_critic} < {TELEVISION_THRESHOLDS['critic']}")

        if year_weak:
            weak_notes.append(f"{year}: " + "; ".join(year_weak))

    return rows, weak_notes


def render_markdown(
    year_rows: list[dict[str, Any]],
    weak_notes: list[str],
    movie_records: list[dict[str, Any]],
    tv_records: list[dict[str, Any]],
) -> str:
    movie_pop_total = sum(1 for row in movie_records if movie_has_popularity(row))
    movie_critic_total = sum(1 for row in movie_records if movie_has_critic(row))

    tv_network_total = sum(1 for row in tv_records if tv_has_network(row))
    tv_pop_total = sum(1 for row in tv_records if tv_has_popularity(row))
    tv_critic_total = sum(1 for row in tv_records if tv_has_critic(row))

    status = "HEALTHY" if not weak_notes else "INCOMPLETE"

    movie_sparsity = field_sparsity(
        movie_records,
        [
            "release_date",
            "genres",
            "runtime_minutes",
            "director",
            "box_office_worldwide",
            "imdb_rating",
            "critic_scores.metacritic",
            "critic_scores.rotten_tomatoes",
            "awards_summary",
        ],
    )
    tv_sparsity = field_sparsity(
        tv_records,
        [
            "premiere_date",
            "network",
            "genres",
            "seasons",
            "episodes",
            "viewership_signals",
            "ratings_signals",
            "critic_scores",
            "awards_summary",
        ],
    )

    lines: list[str] = []
    lines.append("# Screen & Culture Warehouse Audit")
    lines.append("")
    lines.append(f"Generated: {now_utc_iso()}")
    lines.append(f"Overall coverage status: {status}")
    lines.append("")

    lines.append("## Coverage Summary")
    lines.append("")
    lines.append(f"- Movies total: {len(movie_records)}")
    lines.append(f"- Movies with popularity metrics: {movie_pop_total} ({percent(movie_pop_total, len(movie_records))}%)")
    lines.append(f"- Movies with critic/acclaim metrics: {movie_critic_total} ({percent(movie_critic_total, len(movie_records))}%)")
    lines.append(f"- Television total: {len(tv_records)}")
    lines.append(f"- Television with network: {tv_network_total} ({percent(tv_network_total, len(tv_records))}%)")
    lines.append(f"- Television with popularity/viewership metrics: {tv_pop_total} ({percent(tv_pop_total, len(tv_records))}%)")
    lines.append(f"- Television with critic/acclaim metrics: {tv_critic_total} ({percent(tv_critic_total, len(tv_records))}%)")
    lines.append("")

    lines.append("## Per-Year Coverage")
    lines.append("")
    if year_rows:
        for row in year_rows:
            year = row["year"]
            movie = row["movies"]
            tv = row["television"]
            lines.append(f"### Year: {year}")
            lines.append("")
            lines.append(
                f"- Movies: {movie['count']} | box office: {movie['with_box_office']} | critic: {movie['with_critic']} | ratings: {movie['with_ratings']} | popularity: {movie['with_popularity']}"
            )
            lines.append(
                f"- Television: {tv['count']} | network: {tv['with_network']} | popularity/viewership: {tv['with_popularity']} | critic/acclaim: {tv['with_critic']}"
            )
            lines.append("")
    else:
        lines.append("No year-level records were found in warehouse outputs.")
        lines.append("")

    lines.append("## Weak Years")
    lines.append("")
    if weak_notes:
        for note in weak_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- No weak years detected against current thresholds.")
    lines.append("")

    lines.append("## Field-Level Sparsity")
    lines.append("")
    lines.append("### Movies")
    lines.append("")
    for field, missing_pct in movie_sparsity.items():
        lines.append(f"- {field}: {missing_pct}% missing")
    lines.append("")
    lines.append("### Television")
    lines.append("")
    for field, missing_pct in tv_sparsity.items():
        lines.append(f"- {field}: {missing_pct}% missing")
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    lines.append("- Add structured TMDb/OMDb/IMDb cache files to improve runtime, cast, ratings, and critic coverage.")
    lines.append("- Add stronger historical TV network/viewership references to improve television popularity signals.")
    lines.append("- Keep provenance and trust labels as-is; do not backfill unknown values with guessed data.")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def run_audit() -> dict[str, Any]:
    movie_records = load_records(MOVIES_MASTER_PATH)
    tv_records = load_records(TELEVISION_MASTER_PATH)

    movie_by_year = group_by_year(movie_records)
    tv_by_year = group_by_year(tv_records)
    year_rows, weak_notes = evaluate_years(movie_by_year, tv_by_year)

    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.write_text(render_markdown(year_rows, weak_notes, movie_records, tv_records), encoding="utf-8")

    return {
        "movie_records": movie_records,
        "tv_records": tv_records,
        "year_rows": year_rows,
        "weak_notes": weak_notes,
        "report_path": DOCS_PATH,
    }


def main() -> int:
    _args = parse_args()
    result = run_audit()

    movie_records = result["movie_records"]
    tv_records = result["tv_records"]
    weak_notes = result["weak_notes"]

    movie_pop_total = sum(1 for row in movie_records if movie_has_popularity(row))
    movie_critic_total = sum(1 for row in movie_records if movie_has_critic(row))

    tv_network_total = sum(1 for row in tv_records if tv_has_network(row))
    tv_pop_total = sum(1 for row in tv_records if tv_has_popularity(row))
    tv_critic_total = sum(1 for row in tv_records if tv_has_critic(row))

    print("## Screen & Culture Warehouse Audit")
    print(f"Movies total: {len(movie_records)}")
    print(f"Movies with popularity metrics: {movie_pop_total} ({percent(movie_pop_total, len(movie_records))}%)")
    print(f"Movies with critic/acclaim metrics: {movie_critic_total} ({percent(movie_critic_total, len(movie_records))}%)")
    print(f"Television total: {len(tv_records)}")
    print(f"Television with network: {tv_network_total} ({percent(tv_network_total, len(tv_records))}%)")
    print(f"Television with popularity/viewership: {tv_pop_total} ({percent(tv_pop_total, len(tv_records))}%)")
    print(f"Television with critic/acclaim: {tv_critic_total} ({percent(tv_critic_total, len(tv_records))}%)")
    print(f"Weak years flagged: {len(weak_notes)}")
    print(f"Report written: {result['report_path']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
