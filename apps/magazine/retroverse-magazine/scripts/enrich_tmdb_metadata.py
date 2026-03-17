#!/usr/bin/env python3
"""Enrich screen/culture warehouse records with TMDb metadata."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import time
import urllib.parse
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from screen_culture_common import (
    MOVIE_MAJOR_FIELDS,
    TELEVISION_MAJOR_FIELDS,
    WAREHOUSE_ROOT,
    build_by_year,
    coverage_years,
    finalize_record,
    get_nested,
    has_value,
    normalize_title,
    now_utc_iso,
    provenance_entry,
    read_json,
    register_provenance,
    set_nested,
    trust_distribution,
    write_json,
    write_sqlite_json_table,
)


TMDB_BASE_URL = "https://api.themoviedb.org/3"
DEFAULT_SLEEP_SECONDS = 0.25

MOVIES_MASTER_PATH = WAREHOUSE_ROOT / "movies_master.json"
TELEVISION_MASTER_PATH = WAREHOUSE_ROOT / "television_master.json"
MOVIES_BY_YEAR_PATH = WAREHOUSE_ROOT / "movies_by_year.json"
TELEVISION_BY_YEAR_PATH = WAREHOUSE_ROOT / "television_by_year.json"
INVENTORY_PATH = WAREHOUSE_ROOT / "screen_culture_inventory.json"
SQLITE_PATH = WAREHOUSE_ROOT / "screen_culture.db"

load_dotenv(dotenv_path=".env")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


@dataclass
class EnrichmentCounts:
    movies_enriched: int = 0
    television_enriched: int = 0
    new_tmdb_ids_stored: int = 0
    network_metadata_added: int = 0
    genres_added: int = 0
    api_calls: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enrich warehouse metadata with TMDb API.")
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS, help="Delay between TMDb requests.")
    parser.add_argument("--max-movies", type=int, default=0, help="Optional movie processing limit (0 = all).")
    parser.add_argument("--max-television", type=int, default=0, help="Optional TV processing limit (0 = all).")
    return parser.parse_args()


def parse_year(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value)
    for token in text.replace("/", "-").split("-"):
        token = token.strip()
        if len(token) == 4 and token.isdigit():
            return int(token)
    return None


def title_similarity(a: str, b: str) -> float:
    na = normalize_title(a)
    nb = normalize_title(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    if na in nb or nb in na:
        return 0.92
    ta = set(na.split(" "))
    tb = set(nb.split(" "))
    overlap = len(ta & tb)
    union = len(ta | tb)
    if union == 0:
        return 0.0
    return overlap / union


def derive_field_trust(record: dict[str, Any]) -> dict[str, str]:
    provenance_fields = record.get("provenance", {}).get("fields", {})
    if not isinstance(provenance_fields, dict):
        return {}
    trust_map: dict[str, str] = {}
    rank = {
        "missing": 0,
        "reference_derived": 1,
        "direct_api": 2,
        "licensed_or_official": 3,
        "canonical_local": 4,
    }
    for field_name, entries in provenance_fields.items():
        strongest = "missing"
        if isinstance(entries, list):
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                level = str(entry.get("trust_level", "missing"))
                if rank.get(level, 0) >= rank.get(strongest, 0):
                    strongest = level
        trust_map[field_name] = strongest
    return trust_map


def set_if_empty(
    record: dict[str, Any],
    field: str,
    value: Any,
    source: dict[str, Any],
    field_trust: dict[str, str],
) -> bool:
    register_provenance(record, field, source)
    if not has_value(value):
        return False
    current = get_nested(record, field)
    if has_value(current):
        return False
    set_nested(record, field, value)
    field_trust[field] = str(source.get("trust_level", "direct_api"))
    return True


def list_if_empty(
    record: dict[str, Any],
    field: str,
    values: list[Any],
    source: dict[str, Any],
    field_trust: dict[str, str],
) -> bool:
    register_provenance(record, field, source)
    if not values:
        return False
    current = get_nested(record, field)
    if isinstance(current, list) and len(current) > 0:
        return False
    clean = [item for item in values if has_value(item)]
    if not clean:
        return False
    set_nested(record, field, clean)
    field_trust[field] = str(source.get("trust_level", "direct_api"))
    return True


class TMDbClient:
    def __init__(self, api_key: str, sleep_seconds: float) -> None:
        self.api_key = api_key
        self.sleep_seconds = max(0.0, sleep_seconds)
        self.calls = 0

    def _request_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = dict(params)
        query["api_key"] = self.api_key
        query_string = urllib.parse.urlencode(query)
        url = f"{TMDB_BASE_URL}{path}?{query_string}"
        time.sleep(self.sleep_seconds)
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError):
            # Some environments fail Python SSL trust-store verification.
            # Fall back to system curl for HTTPS transport.
            result = subprocess.run(
                ["curl", "-sfL", url],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return {}
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError:
                return {}
        self.calls += 1
        return payload if isinstance(payload, dict) else {}

    def find_by_imdb(self, imdb_id: str) -> dict[str, Any]:
        return self._request_json(f"/find/{urllib.parse.quote(imdb_id)}", {"external_source": "imdb_id"})

    def search_movie(self, title: str, year: int | None) -> dict[str, Any]:
        params: dict[str, Any] = {"query": title}
        if year is not None:
            params["year"] = year
        return self._request_json("/search/movie", params)

    def search_tv(self, title: str, year: int | None) -> dict[str, Any]:
        params: dict[str, Any] = {"query": title}
        if year is not None:
            params["first_air_date_year"] = year
        return self._request_json("/search/tv", params)

    def movie_details(self, movie_id: int) -> dict[str, Any]:
        return self._request_json(f"/movie/{movie_id}", {"append_to_response": "credits"})

    def tv_details(self, tv_id: int) -> dict[str, Any]:
        return self._request_json(f"/tv/{tv_id}", {"append_to_response": "credits"})


def pick_movie_candidate(results: list[dict[str, Any]], title: str, year: int | None) -> dict[str, Any] | None:
    best_row: dict[str, Any] | None = None
    best_score = -999.0
    for row in results:
        candidate_title = str(row.get("title") or row.get("original_title") or "").strip()
        if not candidate_title:
            continue
        score = title_similarity(title, candidate_title) * 100
        candidate_year = parse_year(row.get("release_date"))
        if year is not None and candidate_year is not None:
            score -= abs(year - candidate_year) * 5
        popularity = float(row.get("popularity") or 0.0)
        score += min(popularity, 50.0) * 0.1
        if score > best_score:
            best_score = score
            best_row = row
    return best_row


def pick_tv_candidate(results: list[dict[str, Any]], title: str, year: int | None) -> dict[str, Any] | None:
    best_row: dict[str, Any] | None = None
    best_score = -999.0
    for row in results:
        candidate_title = str(row.get("name") or row.get("original_name") or "").strip()
        if not candidate_title:
            continue
        score = title_similarity(title, candidate_title) * 100
        candidate_year = parse_year(row.get("first_air_date"))
        if year is not None and candidate_year is not None:
            score -= abs(year - candidate_year) * 5
        popularity = float(row.get("popularity") or 0.0)
        score += min(popularity, 50.0) * 0.1
        if score > best_score:
            best_score = score
            best_row = row
    return best_row


def load_payload(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    if not isinstance(payload, dict):
        raise FileNotFoundError(f"Warehouse file unreadable: {path}")
    records = payload.get("records")
    if not isinstance(records, list):
        raise FileNotFoundError(f"Warehouse records missing in: {path}")
    payload["records"] = [row for row in records if isinstance(row, dict)]
    return payload


def get_top_cast(details: dict[str, Any], limit: int = 5) -> list[str]:
    credits = details.get("credits")
    if not isinstance(credits, dict):
        return []
    cast = credits.get("cast")
    if not isinstance(cast, list):
        return []
    output: list[str] = []
    for row in cast[: limit * 2]:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name", "")).strip()
        if name and name not in output:
            output.append(name)
        if len(output) >= limit:
            break
    return output


def enrich_movie_record(record: dict[str, Any], client: TMDbClient, counts: EnrichmentCounts) -> bool:
    title = str(record.get("title", "")).strip()
    year = parse_year(record.get("year"))
    if not title:
        return False

    source = provenance_entry(
        source_name="tmdb_api",
        source_type="api",
        trust_level="direct_api",
        source_url="https://api.themoviedb.org/3",
    )
    field_trust = derive_field_trust(record)
    changed = False

    source_ids = record.setdefault("source_ids", {})
    existing_tmdb_id = source_ids.get("tmdb_id")
    tmdb_id: int | None = None

    if has_value(existing_tmdb_id):
        try:
            tmdb_id = int(existing_tmdb_id)
        except (TypeError, ValueError):
            tmdb_id = None

    imdb_id = str(source_ids.get("imdb_id") or source_ids.get("omdb_imdb_id") or "").strip()
    if tmdb_id is None and imdb_id:
        try:
            found = client.find_by_imdb(imdb_id)
            movie_results = found.get("movie_results", [])
            if isinstance(movie_results, list) and movie_results:
                tmdb_id = int(movie_results[0].get("id"))
        except Exception:
            tmdb_id = None

    if tmdb_id is None:
        try:
            search = client.search_movie(title, year)
            results = search.get("results", [])
            if isinstance(results, list):
                best = pick_movie_candidate(results, title, year)
                if best and has_value(best.get("id")):
                    tmdb_id = int(best.get("id"))
        except Exception:
            tmdb_id = None

    if tmdb_id is None:
        return False

    if set_if_empty(record, "source_ids.tmdb_id", tmdb_id, source, field_trust):
        counts.new_tmdb_ids_stored += 1
        changed = True

    try:
        details = client.movie_details(tmdb_id)
    except Exception:
        finalize_record(record, field_trust, MOVIE_MAJOR_FIELDS)
        return changed

    genres = []
    raw_genres = details.get("genres")
    if isinstance(raw_genres, list):
        genres = [str(item.get("name", "")).strip() for item in raw_genres if isinstance(item, dict)]
        genres = [item for item in genres if item]

    runtime = details.get("runtime")
    release_date = details.get("release_date")
    companies = details.get("production_companies")
    studio = None
    if isinstance(companies, list):
        for company in companies:
            if isinstance(company, dict):
                name = str(company.get("name", "")).strip()
                if name:
                    studio = name
                    break

    top_cast = get_top_cast(details, limit=5)

    changed |= set_if_empty(record, "runtime_minutes", runtime, source, field_trust)
    if list_if_empty(record, "genres", genres, source, field_trust):
        counts.genres_added += 1
        changed = True
    changed |= set_if_empty(record, "studio", studio, source, field_trust)
    changed |= set_if_empty(record, "release_date", release_date, source, field_trust)
    changed |= list_if_empty(record, "principal_cast", top_cast, source, field_trust)

    # Optional poster reference (do not enforce schema, store as signal if empty).
    poster_path = details.get("poster_path")
    if has_value(poster_path):
        popularity = record.setdefault("popularity_signals", {})
        if isinstance(popularity, dict) and not has_value(popularity.get("tmdb_poster_path")):
            register_provenance(record, "popularity_signals.tmdb_poster_path", source)
            popularity["tmdb_poster_path"] = str(poster_path)
            changed = True

    finalize_record(record, field_trust, MOVIE_MAJOR_FIELDS)
    return changed


def enrich_television_record(record: dict[str, Any], client: TMDbClient, counts: EnrichmentCounts) -> bool:
    title = str(record.get("title", "")).strip()
    year = parse_year(record.get("year"))
    if not title:
        return False

    source = provenance_entry(
        source_name="tmdb_api",
        source_type="api",
        trust_level="direct_api",
        source_url="https://api.themoviedb.org/3",
    )
    field_trust = derive_field_trust(record)
    changed = False

    source_ids = record.setdefault("source_ids", {})
    existing_tmdb_id = source_ids.get("tmdb_id")
    tmdb_id: int | None = None

    if has_value(existing_tmdb_id):
        try:
            tmdb_id = int(existing_tmdb_id)
        except (TypeError, ValueError):
            tmdb_id = None

    imdb_id = str(source_ids.get("imdb_id") or "").strip()
    if tmdb_id is None and imdb_id:
        try:
            found = client.find_by_imdb(imdb_id)
            tv_results = found.get("tv_results", [])
            if isinstance(tv_results, list) and tv_results:
                tmdb_id = int(tv_results[0].get("id"))
        except Exception:
            tmdb_id = None

    if tmdb_id is None:
        try:
            search = client.search_tv(title, year)
            results = search.get("results", [])
            if isinstance(results, list):
                best = pick_tv_candidate(results, title, year)
                if best and has_value(best.get("id")):
                    tmdb_id = int(best.get("id"))
        except Exception:
            tmdb_id = None

    if tmdb_id is None:
        return False

    if set_if_empty(record, "source_ids.tmdb_id", tmdb_id, source, field_trust):
        counts.new_tmdb_ids_stored += 1
        changed = True

    try:
        details = client.tv_details(tmdb_id)
    except Exception:
        finalize_record(record, field_trust, TELEVISION_MAJOR_FIELDS)
        return changed

    networks = details.get("networks")
    network_name = None
    if isinstance(networks, list):
        for network in networks:
            if isinstance(network, dict):
                name = str(network.get("name", "")).strip()
                if name:
                    network_name = name
                    break

    genres = []
    raw_genres = details.get("genres")
    if isinstance(raw_genres, list):
        genres = [str(item.get("name", "")).strip() for item in raw_genres if isinstance(item, dict)]
        genres = [item for item in genres if item]

    episode_runtime = details.get("episode_run_time")
    runtime = None
    if isinstance(episode_runtime, list) and episode_runtime:
        runtime = episode_runtime[0]

    creators = []
    raw_creators = details.get("created_by")
    if isinstance(raw_creators, list):
        creators = [str(item.get("name", "")).strip() for item in raw_creators if isinstance(item, dict)]
        creators = [item for item in creators if item]

    top_cast = get_top_cast(details, limit=5)
    seasons = details.get("number_of_seasons")
    episodes = details.get("number_of_episodes")
    first_air_date = details.get("first_air_date")

    if set_if_empty(record, "network", network_name, source, field_trust):
        counts.network_metadata_added += 1
        changed = True
    if list_if_empty(record, "genres", genres, source, field_trust):
        counts.genres_added += 1
        changed = True

    changed |= set_if_empty(record, "runtime_minutes", runtime, source, field_trust)
    changed |= set_if_empty(record, "seasons", seasons, source, field_trust)
    changed |= set_if_empty(record, "episodes", episodes, source, field_trust)
    changed |= list_if_empty(record, "creators", creators, source, field_trust)
    changed |= list_if_empty(record, "principal_cast", top_cast, source, field_trust)
    changed |= set_if_empty(record, "premiere_date", first_air_date, source, field_trust)

    # Optional poster reference
    poster_path = details.get("poster_path")
    if has_value(poster_path):
        viewership = record.setdefault("viewership_signals", {})
        if isinstance(viewership, dict) and not has_value(viewership.get("tmdb_poster_path")):
            register_provenance(record, "viewership_signals.tmdb_poster_path", source)
            viewership["tmdb_poster_path"] = str(poster_path)
            changed = True

    finalize_record(record, field_trust, TELEVISION_MAJOR_FIELDS)
    return changed


def refresh_payload_metrics(payload: dict[str, Any], medium: str) -> None:
    records = payload.get("records", [])
    if not isinstance(records, list):
        return
    payload["generated_at_utc"] = now_utc_iso()
    payload["record_count"] = len(records)
    min_year, max_year = coverage_years(records)
    payload["year_range"] = {"min": min_year, "max": max_year}
    payload["trust_distribution"] = trust_distribution(records)

    metrics = payload.setdefault("metrics", {})
    if medium == "movies":
        with_runtime = sum(1 for row in records if has_value(row.get("runtime_minutes")))
        with_genres = sum(1 for row in records if isinstance(row.get("genres"), list) and bool(row.get("genres")))
        with_tmdb_id = sum(1 for row in records if has_value(row.get("source_ids", {}).get("tmdb_id")))
        metrics["with_runtime"] = with_runtime
        metrics["with_genres"] = with_genres
        metrics["with_tmdb_id"] = with_tmdb_id
        metrics["runtime_percent"] = round((with_runtime / len(records)) * 100, 2) if records else 0.0
        metrics["genres_percent"] = round((with_genres / len(records)) * 100, 2) if records else 0.0
        metrics["tmdb_id_percent"] = round((with_tmdb_id / len(records)) * 100, 2) if records else 0.0
    else:
        with_network = sum(1 for row in records if has_value(row.get("network")))
        with_genres = sum(1 for row in records if isinstance(row.get("genres"), list) and bool(row.get("genres")))
        with_tmdb_id = sum(1 for row in records if has_value(row.get("source_ids", {}).get("tmdb_id")))
        metrics["with_network"] = with_network
        metrics["with_genres"] = with_genres
        metrics["with_tmdb_id"] = with_tmdb_id
        metrics["network_percent"] = round((with_network / len(records)) * 100, 2) if records else 0.0
        metrics["genres_percent"] = round((with_genres / len(records)) * 100, 2) if records else 0.0
        metrics["tmdb_id_percent"] = round((with_tmdb_id / len(records)) * 100, 2) if records else 0.0


def update_inventory(movies_payload: dict[str, Any], television_payload: dict[str, Any]) -> None:
    inventory = read_json(INVENTORY_PATH, default={})
    if not isinstance(inventory, dict):
        inventory = {}

    movies_records = movies_payload.get("records", [])
    television_records = television_payload.get("records", [])
    movies_by_year = build_by_year(movies_records if isinstance(movies_records, list) else [])
    tv_by_year = build_by_year(television_records if isinstance(television_records, list) else [])
    years = sorted({int(y) for y in list(movies_by_year.keys()) + list(tv_by_year.keys()) if str(y).isdigit()})

    inventory["generated_at_utc"] = now_utc_iso()
    inventory.setdefault("warehouse_version", "screen-culture-v1")
    inventory.setdefault(
        "paths",
        {
            "movies_master": str(MOVIES_MASTER_PATH),
            "television_master": str(TELEVISION_MASTER_PATH),
            "movies_by_year": str(MOVIES_BY_YEAR_PATH),
            "television_by_year": str(TELEVISION_BY_YEAR_PATH),
            "sqlite": str(SQLITE_PATH),
        },
    )
    inventory.setdefault(
        "source_layering",
        {
            "canonical_local": "RetroVerse internal datasets (authoritative local base)",
            "direct_api": "TMDb/OMDb style API enrichments when available",
            "licensed_or_official": "IMDb dataset files and other licensed/official structured sources",
            "reference_derived": "Reference tables and archive-derived metadata",
            "missing": "No available source populated the field",
        },
    )
    inventory.setdefault(
        "trust_hierarchy",
        ["missing", "reference_derived", "direct_api", "licensed_or_official", "canonical_local"],
    )
    inventory["movies"] = {
        "record_count": len(movies_records) if isinstance(movies_records, list) else 0,
        "year_range": movies_payload.get("year_range", {}),
        "years_indexed": len(movies_by_year),
        "trust_distribution": movies_payload.get("trust_distribution", {}),
        "source_counts": movies_payload.get("source_counts", {}),
        "metrics": movies_payload.get("metrics", {}),
    }
    inventory["television"] = {
        "record_count": len(television_records) if isinstance(television_records, list) else 0,
        "year_range": television_payload.get("year_range", {}),
        "years_indexed": len(tv_by_year),
        "trust_distribution": television_payload.get("trust_distribution", {}),
        "source_counts": television_payload.get("source_counts", {}),
        "metrics": television_payload.get("metrics", {}),
    }
    inventory["years_covered"] = years
    notes = inventory.setdefault("notes", [])
    note = "TMDb API enrichment applied using fill-empty-only merge behavior with direct_api provenance."
    if note not in notes:
        notes.append(note)
    write_json(INVENTORY_PATH, inventory)


def run(args: argparse.Namespace) -> EnrichmentCounts:
    api_key = str(TMDB_API_KEY or "").strip()
    if not api_key:
        raise RuntimeError("TMDB_API_KEY missing from .env")

    movies_payload = load_payload(MOVIES_MASTER_PATH)
    television_payload = load_payload(TELEVISION_MASTER_PATH)

    movies_records = movies_payload["records"]
    television_records = television_payload["records"]

    client = TMDbClient(api_key=api_key, sleep_seconds=args.sleep)
    counts = EnrichmentCounts()

    movie_limit = args.max_movies if args.max_movies and args.max_movies > 0 else len(movies_records)
    tv_limit = args.max_television if args.max_television and args.max_television > 0 else len(television_records)

    for index, record in enumerate(movies_records):
        if index >= movie_limit:
            break
        if enrich_movie_record(record, client, counts):
            counts.movies_enriched += 1

    for index, record in enumerate(television_records):
        if index >= tv_limit:
            break
        if enrich_television_record(record, client, counts):
            counts.television_enriched += 1

    refresh_payload_metrics(movies_payload, "movies")
    refresh_payload_metrics(television_payload, "television")

    movies_source_counts = movies_payload.setdefault("source_counts", {})
    movies_source_counts["tmdb_api"] = int(movies_source_counts.get("tmdb_api", 0)) + counts.movies_enriched
    tv_source_counts = television_payload.setdefault("source_counts", {})
    tv_source_counts["tmdb_api"] = int(tv_source_counts.get("tmdb_api", 0)) + counts.television_enriched

    write_json(MOVIES_MASTER_PATH, movies_payload)
    write_json(TELEVISION_MASTER_PATH, television_payload)

    movies_by_year = build_by_year(movies_records)
    tv_by_year = build_by_year(television_records)
    write_json(MOVIES_BY_YEAR_PATH, movies_by_year)
    write_json(TELEVISION_BY_YEAR_PATH, tv_by_year)

    update_inventory(movies_payload, television_payload)

    conn = sqlite3.connect(SQLITE_PATH)
    try:
        write_sqlite_json_table(conn, "movies_master", movies_records)
        write_sqlite_json_table(conn, "television_master", television_records)
        conn.commit()
    finally:
        conn.close()

    counts.api_calls = client.calls
    return counts


def main() -> int:
    args = parse_args()
    try:
        counts = run(args)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: TMDb enrichment failed: {exc}")
        return 1

    print(f"Movies enriched: {counts.movies_enriched}")
    print(f"TV shows enriched: {counts.television_enriched}")
    print(f"New TMDb IDs stored: {counts.new_tmdb_ids_stored}")
    print(f"Network metadata added: {counts.network_metadata_added}")
    print(f"Genres added: {counts.genres_added}")
    print(f"TMDb API calls: {counts.api_calls}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
