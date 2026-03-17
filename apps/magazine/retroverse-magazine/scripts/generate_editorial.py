#!/usr/bin/env python3
"""Generate editorial payloads for a RetroVerse issue year."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class EditorialBuildError(Exception):
    """Raised when editorial generation inputs are missing or malformed."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EditorialBuildError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EditorialBuildError(f"Invalid JSON in {path}: {exc}") from exc


def top_titles(entries: list[dict[str, Any]], key: str, limit: int) -> list[str]:
    items: list[str] = []
    for entry in entries[:limit]:
        value = entry.get(key)
        if value:
            items.append(str(value))
    return items


def generate_feature_story(
    year: str,
    chart_entries: list[dict[str, Any]],
    films: list[dict[str, Any]],
    shows: list[dict[str, Any]],
) -> dict[str, Any]:
    songs = top_titles(chart_entries, "title", 3)
    artists = top_titles(chart_entries, "artist", 3)
    film_titles = top_titles(films, "title", 3)
    tv_titles = top_titles(shows, "title", 2)

    lead_song = songs[0] if songs else "the current radio leaders"
    lead_artist = artists[0] if artists else "the chart leaders"
    second_artist = artists[1] if len(artists) > 1 else "major crossover acts"
    lead_film = film_titles[0] if film_titles else "the season's big theatrical releases"
    second_film = film_titles[1] if len(film_titles) > 1 else "event cinema"
    lead_tv = tv_titles[0] if tv_titles else "prime-time television"

    paragraphs = [
        (
            f"{year} feels like a hinge year, where radio hits such as {lead_song} carry club energy "
            "into everyday streets, cabs, and corner stores."
        ),
        (
            f"Artists including {lead_artist} and {second_artist} are proving that polished production can "
            "still feel immediate, social, and physical."
        ),
        (
            f"At the multiplex, {lead_film} and {second_film} confirm that theatrical scale matters, even as "
            f"{lead_tv} keeps families tied to weekly television habits."
        ),
        (
            "The result is a culture that moves on multiple tracks at once: dance floor urgency, screen-sized "
            "spectacle, and living-room ritual."
        ),
    ]

    return {
        "headline": f"{year} in Motion: Dance Floors, Marquees, and Living Rooms",
        "deck": "A short field report on how music, movies, and television are shaping one shared year.",
        "byline": "By A.J. Hunter",
        "paragraphs": paragraphs,
        "sidebar_facts": [
            f"Radio momentum: {', '.join(songs[:3])}" if songs else "Radio momentum: chart leaders hold steady.",
            f"Box office pressure: {', '.join(film_titles[:3])}" if film_titles else "Box office pressure remains high.",
            f"TV watch-list: {', '.join(tv_titles[:2])}" if tv_titles else "TV watch-list remains appointment viewing.",
        ],
        "quote": "1978 is less a conclusion than a high-speed midpoint.",
    }


def generate_collage(chart_entries: list[dict[str, Any]], films: list[dict[str, Any]], shows: list[dict[str, Any]]) -> dict[str, Any]:
    song = chart_entries[0]["title"] if chart_entries else "Top 40 single"
    film = films[0]["title"] if films else "major release"
    show = shows[0]["title"] if shows else "prime-time show"
    tiles = [
        f"Record-store listening booth card for {song}",
        f"Movie ticket stub: late show for {film}",
        "Subway token and folded transit map corner",
        "Arcade score sheet tucked into jacket pocket",
        f"TV listing clipping with {show} circled in pen",
        "Neon diner receipt with coffee refill marks",
        "Department-store fashion swatch and disco shoe sketch",
        "FM station request slip from a weekend countdown",
        "Polaroid-style street snapshot outside a cinema queue",
    ]
    return {"tiles": tiles}


def generate_comic(chart_entries: list[dict[str, Any]], films: list[dict[str, Any]], shows: list[dict[str, Any]]) -> dict[str, Any]:
    song = chart_entries[1]["title"] if len(chart_entries) > 1 else "the latest dance hit"
    film = films[1]["title"] if len(films) > 1 else "the biggest movie in town"
    show = shows[1]["title"] if len(shows) > 1 else "tonight's top TV show"

    panels = [
        {"title": "Panel 1", "scene": "Friday night starts at the record counter as friends compare new 45s.", "caption": "The plan forms before sunset."},
        {"title": "Panel 2", "scene": f"The DJ drops {song} and the room locks into tempo.", "caption": "One song can reset the whole mood."},
        {"title": "Panel 3", "scene": f"By midnight, the line wraps around the block for {film}.", "caption": "Cinema becomes a group event."},
        {"title": "Panel 4", "scene": "Saturday afternoon drifts toward the arcade and a pocket of quarters.", "caption": "Competition is neighborhood theater."},
        {"title": "Panel 5", "scene": f"At home, everyone argues playfully over whether to watch {show}.", "caption": "TV still sets the weekly rhythm."},
        {"title": "Panel 6", "scene": "Sunday closes with notes, flyers, and tickets spread on a kitchen table.", "caption": "A year gets archived one weekend at a time."},
    ]
    return {"panels": panels}


def build_editorial_payload(year: str, charts: dict[str, Any], movies: dict[str, Any], tv: dict[str, Any]) -> dict[str, Any]:
    chart_entries = charts.get("entries", []) if isinstance(charts, dict) else []
    films = movies.get("films", []) if isinstance(movies, dict) else []
    shows = tv.get("shows", []) if isinstance(tv, dict) else []

    if not isinstance(chart_entries, list) or not chart_entries:
        raise EditorialBuildError("charts.json must include a non-empty 'entries' list.")
    if not isinstance(films, list) or not films:
        raise EditorialBuildError("movies.json must include a non-empty 'films' list.")
    if not isinstance(shows, list) or not shows:
        raise EditorialBuildError("tv.json must include a non-empty 'shows' list.")

    return {
        "feature_story": generate_feature_story(year, chart_entries, films, shows),
        "collage": generate_collage(chart_entries, films, shows),
        "comic": generate_comic(chart_entries, films, shows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RetroVerse editorial data.")
    parser.add_argument("--year", default="1978", help="Issue year to generate (default: 1978)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    year = str(args.year)
    data_dir = root / "issues" / year / "data"

    charts_path = data_dir / "charts.json"
    movies_path = data_dir / "movies.json"
    tv_path = data_dir / "tv.json"
    output_path = data_dir / "editorial.json"

    try:
        charts = load_json(charts_path)
        movies = load_json(movies_path)
        tv = load_json(tv_path)
        editorial = build_editorial_payload(year, charts, movies, tv)
    except EditorialBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    output_path.write_text(json.dumps(editorial, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote editorial data: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

