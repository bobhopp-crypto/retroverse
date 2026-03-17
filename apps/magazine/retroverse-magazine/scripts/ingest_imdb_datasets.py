#!/usr/bin/env python3
"""Download, parse, and apply IMDb bulk dataset enrichment to screen/culture warehouse."""

from __future__ import annotations

import argparse
import csv
import gzip
import shutil
import sqlite3
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from screen_culture_common import (
    TELEVISION_MAJOR_FIELDS,
    MOVIE_MAJOR_FIELDS,
    WAREHOUSE_ROOT,
    append_dict_signal,
    append_list_with_trust,
    build_by_year,
    coverage_years,
    finalize_record,
    has_value,
    now_utc_iso,
    parse_year,
    provenance_entry,
    read_json,
    set_field_with_trust,
    trust_distribution,
    write_json,
    write_sqlite_json_table,
    normalize_title,
    TRUST_RANK,
)


IMDB_BASE_URL = "https://datasets.imdbws.com"
IMDB_ROOT = Path("/Users/bobhopp/Sites/retroverse/data/raw/imdb")
SCREEN_CULTURE_REFERENCE_ROOT = Path("/Users/bobhopp/Sites/retroverse/data/raw/screen-culture/reference")
ENRICHMENT_PATH = SCREEN_CULTURE_REFERENCE_ROOT / "imdb_enrichment.json"

MOVIES_MASTER_PATH = WAREHOUSE_ROOT / "movies_master.json"
TELEVISION_MASTER_PATH = WAREHOUSE_ROOT / "television_master.json"
MOVIES_BY_YEAR_PATH = WAREHOUSE_ROOT / "movies_by_year.json"
TELEVISION_BY_YEAR_PATH = WAREHOUSE_ROOT / "television_by_year.json"
INVENTORY_PATH = WAREHOUSE_ROOT / "screen_culture_inventory.json"
SQLITE_PATH = WAREHOUSE_ROOT / "screen_culture.db"

REQUIRED_FILES = [
    "title.basics.tsv.gz",
    "title.ratings.tsv.gz",
    "title.akas.tsv.gz",
    "title.principals.tsv.gz",
    "name.basics.tsv.gz",
]

ALLOWED_IMDB_TYPES = {
    "movie",
    "short",
    "video",
    "tvmovie",
    "tvseries",
    "tvminiseries",
    "tvspecial",
}


@dataclass
class Candidate:
    tconst: str
    title: str
    year: int | None
    title_type: str
    runtime_minutes: int | None
    genres: list[str]
    imdb_rating: float | None = None
    imdb_votes: int | None = None
    movie_indices: set[int] = field(default_factory=set)
    tv_indices: set[int] = field(default_factory=set)


@dataclass
class IngestionSummary:
    basics_rows_processed: int = 0
    ratings_rows_processed: int = 0
    candidates_found: int = 0
    enrichment_rows_written: int = 0
    movie_matches_applied: int = 0
    tv_matches_applied: int = 0
    files_downloaded: int = 0
    files_decompressed: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest IMDb bulk datasets into RetroVerse screen/culture warehouse.")
    parser.add_argument("--force-download", action="store_true", help="Redownload IMDb .gz files even if present.")
    parser.add_argument("--force-decompress", action="store_true", help="Rebuild .tsv files from .gz even if present.")
    return parser.parse_args()


def ensure_directories() -> None:
    IMDB_ROOT.mkdir(parents=True, exist_ok=True)
    SCREEN_CULTURE_REFERENCE_ROOT.mkdir(parents=True, exist_ok=True)
    WAREHOUSE_ROOT.mkdir(parents=True, exist_ok=True)


def download_file(url: str, destination: Path, force: bool) -> bool:
    if destination.exists() and destination.stat().st_size > 0 and not force:
        return False

    temp_path = destination.with_suffix(destination.suffix + ".part")
    if temp_path.exists():
        temp_path.unlink()

    request = urllib.request.Request(url, headers={"User-Agent": "RetroVerseIMDbIngest/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temp_path.open("wb") as output:
            shutil.copyfileobj(response, output)
    except urllib.error.URLError:
        # Some environments have Python SSL trust-store issues. Fall back to system curl.
        if temp_path.exists():
            temp_path.unlink()
        result = subprocess.run(
            ["curl", "-fL", "--retry", "3", "-o", str(temp_path), url],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip() or "curl download failed"
            raise RuntimeError(f"Failed downloading {url} via curl: {stderr}")

    temp_path.replace(destination)
    return True


def decompress_file(source_gz: Path, destination_tsv: Path, force: bool) -> bool:
    if destination_tsv.exists() and destination_tsv.stat().st_size > 0 and not force:
        return False

    with gzip.open(source_gz, "rb") as source_handle, destination_tsv.open("wb") as destination_handle:
        shutil.copyfileobj(source_handle, destination_handle)
    return True


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == "\\N":
        return None
    try:
        return int(text)
    except ValueError:
        return None


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == "\\N":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_genres(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text or text == "\\N":
        return []
    return [item.strip().lower() for item in text.split(",") if item.strip()]


def medium_from_imdb_type(title_type: str) -> str:
    lowered = (title_type or "").strip().lower()
    if lowered.startswith("tv"):
        return "television"
    if lowered in {"movie", "short", "video"}:
        return "movie"
    return lowered or "unknown"


def load_master(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    if not isinstance(payload, dict):
        raise FileNotFoundError(f"Invalid warehouse payload at {path}")
    records = payload.get("records")
    if not isinstance(records, list):
        raise FileNotFoundError(f"Missing records array in {path}")
    payload["records"] = [item for item in records if isinstance(item, dict)]
    return payload


def build_record_indexes(records: list[dict[str, Any]]) -> tuple[dict[tuple[str, int], list[int]], dict[str, list[int]]]:
    title_year_map: dict[tuple[str, int], list[int]] = {}
    imdb_id_map: dict[str, list[int]] = {}

    for index, record in enumerate(records):
        title = str(record.get("title", "")).strip()
        year = parse_year(record.get("year"))
        normalized = normalize_title(title)
        if normalized and year is not None:
            title_year_map.setdefault((normalized, year), []).append(index)

        imdb_id = str(record.get("source_ids", {}).get("imdb_id") or "").strip()
        if imdb_id:
            imdb_id_map.setdefault(imdb_id, []).append(index)

    return title_year_map, imdb_id_map


def derive_field_trust(record: dict[str, Any]) -> dict[str, str]:
    provenance_fields = record.get("provenance", {}).get("fields", {})
    if not isinstance(provenance_fields, dict):
        return {}

    trust_map: dict[str, str] = {}
    for field_name, entries in provenance_fields.items():
        if not isinstance(entries, list):
            continue
        strongest = "missing"
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            level = str(entry.get("trust_level", "missing"))
            if TRUST_RANK.get(level, 0) >= TRUST_RANK.get(strongest, 0):
                strongest = level
        trust_map[field_name] = strongest
    return trust_map


def best_candidate(existing: Candidate | None, incoming: Candidate) -> Candidate:
    if existing is None:
        return incoming

    existing_votes = existing.imdb_votes or -1
    incoming_votes = incoming.imdb_votes or -1
    if incoming_votes > existing_votes:
        return incoming
    if incoming_votes < existing_votes:
        return existing

    existing_rating = existing.imdb_rating or -1.0
    incoming_rating = incoming.imdb_rating or -1.0
    if incoming_rating > existing_rating:
        return incoming
    return existing


def collect_candidates(
    basics_path: Path,
    movie_title_year_map: dict[tuple[str, int], list[int]],
    movie_imdb_map: dict[str, list[int]],
    tv_title_year_map: dict[tuple[str, int], list[int]],
    tv_imdb_map: dict[str, list[int]],
    summary: IngestionSummary,
) -> dict[str, Candidate]:
    candidates: dict[str, Candidate] = {}

    with basics_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            summary.basics_rows_processed += 1

            tconst = str(row.get("tconst", "")).strip()
            if not tconst:
                continue

            title_type = str(row.get("titleType", "")).strip()
            lowered_type = title_type.lower()
            year = parse_year(row.get("startYear"))
            title = str(row.get("primaryTitle", "")).strip()
            normalized_title = normalize_title(title)

            direct_movie_indices = movie_imdb_map.get(tconst, [])
            direct_tv_indices = tv_imdb_map.get(tconst, [])

            title_year_movie_indices: list[int] = []
            title_year_tv_indices: list[int] = []
            if normalized_title and year is not None:
                title_year_movie_indices = movie_title_year_map.get((normalized_title, year), [])
                title_year_tv_indices = tv_title_year_map.get((normalized_title, year), [])

            has_any_match = bool(
                direct_movie_indices
                or direct_tv_indices
                or title_year_movie_indices
                or title_year_tv_indices
            )
            if not has_any_match:
                continue

            # Skip obviously unrelated types unless there is an explicit existing imdb id.
            has_direct_id_match = bool(direct_movie_indices or direct_tv_indices)
            if not has_direct_id_match and lowered_type not in ALLOWED_IMDB_TYPES:
                continue

            runtime_minutes = as_int(row.get("runtimeMinutes"))
            genres = parse_genres(row.get("genres"))

            candidate = candidates.get(tconst)
            if candidate is None:
                candidate = Candidate(
                    tconst=tconst,
                    title=title,
                    year=year,
                    title_type=title_type,
                    runtime_minutes=runtime_minutes,
                    genres=genres,
                )
                candidates[tconst] = candidate

            for idx in direct_movie_indices:
                candidate.movie_indices.add(idx)
            for idx in title_year_movie_indices:
                candidate.movie_indices.add(idx)

            for idx in direct_tv_indices:
                candidate.tv_indices.add(idx)
            for idx in title_year_tv_indices:
                candidate.tv_indices.add(idx)

    summary.candidates_found = len(candidates)
    return candidates


def attach_ratings(candidates: dict[str, Candidate], ratings_path: Path, summary: IngestionSummary) -> None:
    if not candidates:
        return

    candidate_ids = set(candidates.keys())
    with ratings_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            summary.ratings_rows_processed += 1
            tconst = str(row.get("tconst", "")).strip()
            if tconst not in candidate_ids:
                continue

            candidate = candidates[tconst]
            candidate.imdb_rating = as_float(row.get("averageRating"))
            candidate.imdb_votes = as_int(row.get("numVotes"))


def build_enrichment_payload(candidates: dict[str, Candidate]) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    for tconst in sorted(candidates.keys()):
        candidate = candidates[tconst]
        payload[tconst] = {
            "title": candidate.title,
            "year": candidate.year,
            "type": medium_from_imdb_type(candidate.title_type),
            "runtime": candidate.runtime_minutes,
            "genres": candidate.genres,
            "imdb_rating": candidate.imdb_rating,
            "imdb_votes": candidate.imdb_votes,
        }
    return payload


def apply_candidates_to_movies(
    movies_records: list[dict[str, Any]],
    candidates: dict[str, Candidate],
    summary: IngestionSummary,
) -> None:
    best_by_movie_index: dict[int, Candidate] = {}
    for candidate in candidates.values():
        for index in candidate.movie_indices:
            best_by_movie_index[index] = best_candidate(best_by_movie_index.get(index), candidate)

    source_url = f"{IMDB_BASE_URL}/"

    for index, candidate in best_by_movie_index.items():
        record = movies_records[index]
        before = (
            record.get("source_ids", {}).get("imdb_id"),
            record.get("imdb_rating"),
            record.get("imdb_votes"),
            record.get("runtime_minutes"),
            tuple(record.get("genres") or []),
        )

        source = provenance_entry(
            source_name="imdb_bulk_dataset",
            source_type="tsv",
            trust_level="licensed_or_official",
            source_identifier=candidate.tconst,
            source_url=source_url,
        )
        field_trust = derive_field_trust(record)

        set_field_with_trust(record, field_trust, "source_ids.imdb_id", candidate.tconst, source)
        set_field_with_trust(record, field_trust, "imdb_rating", candidate.imdb_rating, source)
        set_field_with_trust(record, field_trust, "imdb_votes", candidate.imdb_votes, source)
        set_field_with_trust(record, field_trust, "runtime_minutes", candidate.runtime_minutes, source)
        append_list_with_trust(record, field_trust, "genres", candidate.genres, source)

        finalize_record(record, field_trust, MOVIE_MAJOR_FIELDS)

        after = (
            record.get("source_ids", {}).get("imdb_id"),
            record.get("imdb_rating"),
            record.get("imdb_votes"),
            record.get("runtime_minutes"),
            tuple(record.get("genres") or []),
        )
        if before != after:
            summary.movie_matches_applied += 1


def apply_candidates_to_television(
    television_records: list[dict[str, Any]],
    candidates: dict[str, Candidate],
    summary: IngestionSummary,
) -> None:
    best_by_tv_index: dict[int, Candidate] = {}
    for candidate in candidates.values():
        for index in candidate.tv_indices:
            best_by_tv_index[index] = best_candidate(best_by_tv_index.get(index), candidate)

    source_url = f"{IMDB_BASE_URL}/"

    for index, candidate in best_by_tv_index.items():
        record = television_records[index]
        ratings_before = dict(record.get("ratings_signals") or {})
        before = (
            record.get("source_ids", {}).get("imdb_id"),
            record.get("imdb_rating"),
            record.get("imdb_votes"),
            record.get("runtime_minutes"),
            tuple(record.get("genres") or []),
            tuple(sorted(ratings_before.items())),
        )

        source = provenance_entry(
            source_name="imdb_bulk_dataset",
            source_type="tsv",
            trust_level="licensed_or_official",
            source_identifier=candidate.tconst,
            source_url=source_url,
        )
        field_trust = derive_field_trust(record)

        set_field_with_trust(record, field_trust, "source_ids.imdb_id", candidate.tconst, source)
        set_field_with_trust(record, field_trust, "imdb_rating", candidate.imdb_rating, source)
        set_field_with_trust(record, field_trust, "imdb_votes", candidate.imdb_votes, source)
        set_field_with_trust(record, field_trust, "runtime_minutes", candidate.runtime_minutes, source)
        set_field_with_trust(record, field_trust, "type", candidate.title_type, source)
        append_list_with_trust(record, field_trust, "genres", candidate.genres, source)
        append_dict_signal(record, field_trust, "ratings_signals", "imdb_rating", candidate.imdb_rating, source)
        append_dict_signal(record, field_trust, "ratings_signals", "imdb_votes", candidate.imdb_votes, source)

        finalize_record(record, field_trust, TELEVISION_MAJOR_FIELDS)

        ratings_after = dict(record.get("ratings_signals") or {})
        after = (
            record.get("source_ids", {}).get("imdb_id"),
            record.get("imdb_rating"),
            record.get("imdb_votes"),
            record.get("runtime_minutes"),
            tuple(record.get("genres") or []),
            tuple(sorted(ratings_after.items())),
        )
        if before != after:
            summary.tv_matches_applied += 1


def recalc_movies_payload(payload: dict[str, Any], records: list[dict[str, Any]], summary: IngestionSummary) -> None:
    payload["records"] = records
    payload["generated_at_utc"] = now_utc_iso()
    payload["record_count"] = len(records)
    min_year, max_year = coverage_years(records)
    payload["year_range"] = {"min": min_year, "max": max_year}
    payload["trust_distribution"] = trust_distribution(records)

    with_popularity = sum(1 for row in records if isinstance(row.get("popularity_signals"), dict) and bool(row.get("popularity_signals")))
    with_critic_or_acclaim = sum(
        1
        for row in records
        if (
            (row.get("critic_scores", {}).get("metacritic") is not None)
            or (row.get("critic_scores", {}).get("rotten_tomatoes") is not None)
            or has_value(row.get("awards_summary"))
        )
    )
    with_imdb = sum(1 for row in records if has_value(row.get("imdb_rating")) or has_value(row.get("imdb_votes")))

    metrics = payload.setdefault("metrics", {})
    metrics["with_popularity_signals"] = with_popularity
    metrics["with_critic_or_acclaim"] = with_critic_or_acclaim
    metrics["with_imdb_metrics"] = with_imdb
    metrics["popularity_percent"] = round((with_popularity / len(records)) * 100, 2) if records else 0.0
    metrics["critic_or_acclaim_percent"] = round((with_critic_or_acclaim / len(records)) * 100, 2) if records else 0.0
    metrics["imdb_metrics_percent"] = round((with_imdb / len(records)) * 100, 2) if records else 0.0

    source_counts = payload.setdefault("source_counts", {})
    source_counts["imdb_bulk_dataset"] = int(source_counts.get("imdb_bulk_dataset", 0)) + summary.movie_matches_applied

    notes = payload.setdefault("notes", [])
    note = (
        f"IMDb bulk dataset ingest {now_utc_iso()}: matched {summary.movie_matches_applied} movie records."
    )
    if note not in notes:
        notes.append(note)


def recalc_tv_payload(payload: dict[str, Any], records: list[dict[str, Any]], summary: IngestionSummary) -> None:
    payload["records"] = records
    payload["generated_at_utc"] = now_utc_iso()
    payload["record_count"] = len(records)
    min_year, max_year = coverage_years(records)
    payload["year_range"] = {"min": min_year, "max": max_year}
    payload["trust_distribution"] = trust_distribution(records)

    with_network = sum(1 for row in records if has_value(row.get("network")))
    with_popularity = sum(
        1
        for row in records
        if (
            isinstance(row.get("viewership_signals"), dict)
            and bool(row.get("viewership_signals"))
        )
        or (
            isinstance(row.get("ratings_signals"), dict)
            and bool(row.get("ratings_signals"))
        )
    )
    with_critic = sum(
        1
        for row in records
        if (isinstance(row.get("critic_scores"), dict) and bool(row.get("critic_scores")))
        or has_value(row.get("awards_summary"))
    )
    with_imdb = sum(1 for row in records if has_value(row.get("imdb_rating")) or has_value(row.get("imdb_votes")))

    metrics = payload.setdefault("metrics", {})
    metrics["with_network"] = with_network
    metrics["with_popularity_or_viewership"] = with_popularity
    metrics["with_critic_or_acclaim"] = with_critic
    metrics["with_imdb_metrics"] = with_imdb
    metrics["network_percent"] = round((with_network / len(records)) * 100, 2) if records else 0.0
    metrics["popularity_percent"] = round((with_popularity / len(records)) * 100, 2) if records else 0.0
    metrics["critic_or_acclaim_percent"] = round((with_critic / len(records)) * 100, 2) if records else 0.0
    metrics["imdb_metrics_percent"] = round((with_imdb / len(records)) * 100, 2) if records else 0.0

    source_counts = payload.setdefault("source_counts", {})
    source_counts["imdb_bulk_dataset"] = int(source_counts.get("imdb_bulk_dataset", 0)) + summary.tv_matches_applied

    notes = payload.setdefault("notes", [])
    note = (
        f"IMDb bulk dataset ingest {now_utc_iso()}: matched {summary.tv_matches_applied} television records."
    )
    if note not in notes:
        notes.append(note)


def update_inventory(
    movies_payload: dict[str, Any],
    tv_payload: dict[str, Any],
    movies_by_year: dict[str, list[dict[str, Any]]],
    tv_by_year: dict[str, list[dict[str, Any]]],
) -> None:
    inventory = read_json(INVENTORY_PATH, default={})
    if not isinstance(inventory, dict):
        inventory = {}

    movie_records = movies_payload.get("records", []) if isinstance(movies_payload.get("records"), list) else []
    tv_records = tv_payload.get("records", []) if isinstance(tv_payload.get("records"), list) else []

    years = sorted({int(year) for year in list(movies_by_year.keys()) + list(tv_by_year.keys()) if str(year).isdigit()})

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
        "record_count": len(movie_records),
        "year_range": movies_payload.get("year_range", {}),
        "years_indexed": len(movies_by_year),
        "trust_distribution": movies_payload.get("trust_distribution", {}),
        "source_counts": movies_payload.get("source_counts", {}),
        "metrics": movies_payload.get("metrics", {}),
    }
    inventory["television"] = {
        "record_count": len(tv_records),
        "year_range": tv_payload.get("year_range", {}),
        "years_indexed": len(tv_by_year),
        "trust_distribution": tv_payload.get("trust_distribution", {}),
        "source_counts": tv_payload.get("source_counts", {}),
        "metrics": tv_payload.get("metrics", {}),
    }
    inventory["years_covered"] = years

    notes = inventory.setdefault("notes", [])
    note = "IMDb bulk dataset enrichment applied; ratings, votes, IDs, runtime, and genres merged with provenance."
    if note not in notes:
        notes.append(note)

    write_json(INVENTORY_PATH, inventory)


def run(force_download: bool, force_decompress: bool) -> IngestionSummary:
    ensure_directories()
    summary = IngestionSummary()

    # Step 1/2: download required gzip bundles.
    for filename in REQUIRED_FILES:
        gz_path = IMDB_ROOT / filename
        url = f"{IMDB_BASE_URL}/{filename}"
        try:
            downloaded = download_file(url, gz_path, force_download)
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Failed downloading {url}: {exc}") from exc
        if downloaded:
            summary.files_downloaded += 1

    # Step 3: decompress .gz to .tsv.
    for filename in REQUIRED_FILES:
        gz_path = IMDB_ROOT / filename
        tsv_path = IMDB_ROOT / filename[:-3] if filename.endswith(".gz") else IMDB_ROOT / f"{filename}.tsv"
        decompressed = decompress_file(gz_path, tsv_path, force_decompress)
        if decompressed:
            summary.files_decompressed += 1

    # Paths used for parsing.
    basics_path = IMDB_ROOT / "title.basics.tsv"
    ratings_path = IMDB_ROOT / "title.ratings.tsv"

    if not basics_path.exists() or not ratings_path.exists():
        raise FileNotFoundError("IMDb TSV files are missing after download/decompression.")

    movies_payload = load_master(MOVIES_MASTER_PATH)
    television_payload = load_master(TELEVISION_MASTER_PATH)

    movies_records = movies_payload["records"]
    television_records = television_payload["records"]

    movie_title_year_map, movie_imdb_map = build_record_indexes(movies_records)
    tv_title_year_map, tv_imdb_map = build_record_indexes(television_records)

    candidates = collect_candidates(
        basics_path,
        movie_title_year_map,
        movie_imdb_map,
        tv_title_year_map,
        tv_imdb_map,
        summary,
    )

    attach_ratings(candidates, ratings_path, summary)

    enrichment_payload = build_enrichment_payload(candidates)
    write_json(ENRICHMENT_PATH, enrichment_payload)
    summary.enrichment_rows_written = len(enrichment_payload)

    apply_candidates_to_movies(movies_records, candidates, summary)
    apply_candidates_to_television(television_records, candidates, summary)

    recalc_movies_payload(movies_payload, movies_records, summary)
    recalc_tv_payload(television_payload, television_records, summary)

    write_json(MOVIES_MASTER_PATH, movies_payload)
    write_json(TELEVISION_MASTER_PATH, television_payload)

    movies_by_year = build_by_year(movies_records)
    tv_by_year = build_by_year(television_records)
    write_json(MOVIES_BY_YEAR_PATH, movies_by_year)
    write_json(TELEVISION_BY_YEAR_PATH, tv_by_year)

    update_inventory(movies_payload, television_payload, movies_by_year, tv_by_year)

    conn = sqlite3.connect(SQLITE_PATH)
    try:
        write_sqlite_json_table(conn, "movies_master", movies_records)
        write_sqlite_json_table(conn, "television_master", television_records)
        conn.commit()
    finally:
        conn.close()

    return summary


def main() -> int:
    args = parse_args()

    try:
        summary = run(force_download=args.force_download, force_decompress=args.force_decompress)
    except (RuntimeError, FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"IMDb titles processed: {summary.basics_rows_processed}")
    print(f"IMDb ratings rows processed: {summary.ratings_rows_processed}")
    print(f"IMDb enrichment rows written: {summary.enrichment_rows_written}")
    print(f"Matches applied to movies_master: {summary.movie_matches_applied}")
    print(f"Matches applied to television_master: {summary.tv_matches_applied}")
    print(f"Files downloaded: {summary.files_downloaded}")
    print(f"Files decompressed: {summary.files_decompressed}")
    print(f"IMDb enrichment file: {ENRICHMENT_PATH}")
    print(f"Warehouse SQLite updated: {SQLITE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
