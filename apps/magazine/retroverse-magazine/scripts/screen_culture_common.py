#!/usr/bin/env python3
"""Shared helpers for screen/culture warehouse build and audits."""

from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from db_common import load_data_sources, resolve_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Repo root: retroverse-magazine -> magazine -> apps -> retroverse (parents[2])
RETROVERSE_ROOT = Path(os.environ["RETROVERSE_ROOT"]) if os.environ.get("RETROVERSE_ROOT") else PROJECT_ROOT.parents[2]
RAW_DATA_ROOT = RETROVERSE_ROOT / "data" / "raw"
SCREEN_CULTURE_ROOT = RAW_DATA_ROOT / "screen-culture"
# Actual warehouse: data/raw/screen-culture/screen-culture/warehouse/
WAREHOUSE_ROOT = SCREEN_CULTURE_ROOT / "screen-culture" / "warehouse"
MOVIES_ROOT = SCREEN_CULTURE_ROOT / "movies"
TELEVISION_ROOT = SCREEN_CULTURE_ROOT / "television"
REFERENCE_ROOT = SCREEN_CULTURE_ROOT / "reference"

DATA_SOURCES_PATH = PROJECT_ROOT / "data" / "DATA_SOURCES.yaml"
DEFAULT_YEAR_MASTER_PATH = RETROVERSE_ROOT / "data" / "derived" / "year-masters" / "retroverse_year_master_1958_2024.json"

TRUST_LEVELS = [
    "missing",
    "reference_derived",
    "direct_api",
    "licensed_or_official",
    "canonical_local",
]
TRUST_RANK = {level: index for index, level in enumerate(TRUST_LEVELS)}

MOVIE_MAJOR_FIELDS = [
    "source_ids.tmdb_id",
    "source_ids.imdb_id",
    "source_ids.omdb_imdb_id",
    "title",
    "original_title",
    "year",
    "release_date",
    "genres",
    "runtime_minutes",
    "country",
    "language",
    "director",
    "principal_cast",
    "studio",
    "box_office_domestic",
    "box_office_worldwide",
    "imdb_rating",
    "imdb_votes",
    "critic_scores.metacritic",
    "critic_scores.rotten_tomatoes",
    "awards_summary",
    "popularity_signals",
]

TELEVISION_MAJOR_FIELDS = [
    "source_ids.tmdb_id",
    "source_ids.imdb_id",
    "title",
    "year",
    "premiere_date",
    "end_date",
    "genres",
    "type",
    "network",
    "seasons",
    "episodes",
    "principal_cast",
    "creators",
    "viewership_signals",
    "ratings_signals",
    "critic_scores",
    "awards_summary",
]


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_screen_culture_dirs() -> None:
    for path in (SCREEN_CULTURE_ROOT, MOVIES_ROOT, TELEVISION_ROOT, REFERENCE_ROOT, WAREHOUSE_ROOT):
        path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_year(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value)
    match = re.search(r"(19|20)\d{2}", text)
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def normalize_title(value: Any) -> str:
    title = str(value or "").strip().lower()
    if not title:
        return ""
    title = title.replace("&", " and ")
    title = re.sub(r"[^a-z0-9]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def tokens(value: Any) -> set[str]:
    normalized = normalize_title(value)
    if not normalized:
        return set()
    return {token for token in normalized.split(" ") if token}


def canonical_key(title: str, year: int | None) -> str:
    safe_title = normalize_title(title) or "untitled"
    safe_year = str(year) if year is not None else "unknown"
    return f"{safe_title}::{safe_year}"


def similar_title_match(a: str, b: str) -> bool:
    na = normalize_title(a)
    nb = normalize_title(b)
    if not na or not nb:
        return False
    if na == nb or na in nb or nb in na:
        return True
    ta = tokens(a)
    tb = tokens(b)
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / max(len(ta), len(tb))
    return overlap >= 0.7


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def get_nested(container: dict[str, Any], path: str) -> Any:
    node: Any = container
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def set_nested(container: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    node = container
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def dedupe_dicts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        token = json.dumps(item, sort_keys=True)
        if token in seen:
            continue
        seen.add(token)
        out.append(item)
    return out


def provenance_entry(
    source_name: str,
    source_type: str,
    trust_level: str,
    source_identifier: str | None = None,
    source_url: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    level = trust_level if trust_level in TRUST_RANK else "missing"
    entry: dict[str, Any] = {
        "source_name": source_name,
        "source_type": source_type,
        "source_identifier": source_identifier or "",
        "source_url": source_url or "",
        "trust_level": level,
    }
    if note:
        entry["note"] = note
    return entry


def register_provenance(record: dict[str, Any], field: str, entry: dict[str, Any]) -> None:
    provenance = record.setdefault("provenance", {})
    field_map = provenance.setdefault("fields", {})
    record_entries = provenance.setdefault("record", [])

    field_entries = field_map.setdefault(field, [])
    field_entries.append(entry)
    field_map[field] = dedupe_dicts(field_entries)

    record_entries.append(entry)
    provenance["record"] = dedupe_dicts(record_entries)


def stronger_or_equal(new_level: str, existing_level: str) -> bool:
    return TRUST_RANK.get(new_level, 0) >= TRUST_RANK.get(existing_level, 0)


def set_field_with_trust(
    record: dict[str, Any],
    field_trust: dict[str, str],
    field: str,
    value: Any,
    source: dict[str, Any],
) -> None:
    register_provenance(record, field, source)

    if not has_value(value):
        return

    current = get_nested(record, field)
    current_level = field_trust.get(field, "missing")
    new_level = str(source.get("trust_level", "missing"))

    if not has_value(current) or stronger_or_equal(new_level, current_level):
        set_nested(record, field, value)
        field_trust[field] = new_level


def append_list_with_trust(
    record: dict[str, Any],
    field_trust: dict[str, str],
    field: str,
    values: list[Any],
    source: dict[str, Any],
) -> None:
    register_provenance(record, field, source)
    if not values:
        return

    existing = get_nested(record, field)
    if not isinstance(existing, list):
        existing = []

    for value in values:
        if has_value(value) and value not in existing:
            existing.append(value)

    current_level = field_trust.get(field, "missing")
    new_level = str(source.get("trust_level", "missing"))
    if stronger_or_equal(new_level, current_level) or not get_nested(record, field):
        set_nested(record, field, existing)
        field_trust[field] = new_level


def append_dict_signal(
    record: dict[str, Any],
    field_trust: dict[str, str],
    field: str,
    key: str,
    value: Any,
    source: dict[str, Any],
) -> None:
    register_provenance(record, field, source)
    if not has_value(value):
        return

    payload = get_nested(record, field)
    if not isinstance(payload, dict):
        payload = {}

    current_level = field_trust.get(f"{field}.{key}", "missing")
    new_level = str(source.get("trust_level", "missing"))
    if key not in payload or stronger_or_equal(new_level, current_level):
        payload[key] = value
        set_nested(record, field, payload)
        field_trust[f"{field}.{key}"] = new_level


def resolve_data_source_path(key: str) -> Path | None:
    sources = load_data_sources(DATA_SOURCES_PATH)
    entry = sources.get(key) if isinstance(sources, dict) else None
    if not isinstance(entry, dict):
        return None
    path_text = str(entry.get("path", "")).strip()
    if not path_text:
        return None
    path = resolve_path(PROJECT_ROOT, path_text)
    return path if path.exists() else None


def year_master_path() -> Path | None:
    mapped = resolve_data_source_path("year_master_json")
    if mapped and mapped.exists():
        return mapped
    if DEFAULT_YEAR_MASTER_PATH.exists():
        return DEFAULT_YEAR_MASTER_PATH
    return None


def issue_movie_files() -> list[Path]:
    return sorted(PROJECT_ROOT.glob("issues/*/data/movies.json"))


def issue_television_files() -> list[Path]:
    return sorted(PROJECT_ROOT.glob("issues/*/data/tv.json"))


def infer_source_profile(path: Path) -> tuple[str, str, str]:
    name = path.name.lower()
    source_type = path.suffix.lower().lstrip(".") or "file"

    if "tmdb" in name:
        return "TMDb", source_type, "direct_api"
    if "omdb" in name:
        return "OMDb", source_type, "direct_api"
    if "imdb" in name:
        return "IMDb dataset", source_type, "licensed_or_official"
    if "official" in name:
        return path.stem, source_type, "licensed_or_official"
    if "year_master" in name:
        return "RetroVerse year master", source_type, "canonical_local"
    return path.stem, source_type, "reference_derived"


def collect_enrichment_files(target: str) -> list[Path]:
    # target in {"movies", "television"}
    if target not in {"movies", "television"}:
        return []

    candidates: list[Path] = []
    roots = [MOVIES_ROOT, TELEVISION_ROOT, REFERENCE_ROOT]
    keywords = {
        "movies": ["movie", "film", "tmdb", "omdb", "imdb", "boxoffice", "critic", "rating"],
        "television": ["tv", "television", "show", "tmdb", "imdb", "nielsen", "ratings", "viewership"],
    }[target]

    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".json", ".csv", ".db", ".sqlite", ".sqlite3"}:
                continue
            lower = path.name.lower()
            if any(keyword in lower for keyword in keywords):
                candidates.append(path)

    return candidates


def ensure_major_field_provenance(record: dict[str, Any], major_fields: list[str]) -> None:
    for field in major_fields:
        entries = record.get("provenance", {}).get("fields", {}).get(field, [])
        if entries:
            continue
        register_provenance(
            record,
            field,
            provenance_entry(
                source_name="unresolved",
                source_type="missing",
                trust_level="missing",
                note="Field not populated from available local sources.",
            ),
        )


def finalize_record(record: dict[str, Any], field_trust: dict[str, str], major_fields: list[str]) -> dict[str, Any]:
    ensure_major_field_provenance(record, major_fields)

    strongest = "missing"
    for field in major_fields:
        value = get_nested(record, field)
        if not has_value(value):
            continue
        level = field_trust.get(field, "missing")
        if stronger_or_equal(level, strongest):
            strongest = level
    record["trust_level"] = strongest

    filled = 0
    for field in major_fields:
        if has_value(get_nested(record, field)):
            filled += 1
    record["completeness_score"] = round((filled / len(major_fields)) * 100, 2) if major_fields else 0.0

    return record


def blank_movie_record(title: str, year: int | None) -> dict[str, Any]:
    return {
        "source_ids": {
            "tmdb_id": None,
            "imdb_id": None,
            "omdb_imdb_id": None,
        },
        "title": title,
        "original_title": None,
        "year": year,
        "release_date": None,
        "medium": "movie",
        "genres": [],
        "runtime_minutes": None,
        "country": None,
        "language": None,
        "director": None,
        "principal_cast": [],
        "studio": None,
        "box_office_domestic": None,
        "box_office_worldwide": None,
        "imdb_rating": None,
        "imdb_votes": None,
        "critic_scores": {
            "metacritic": None,
            "rotten_tomatoes": None,
        },
        "awards_summary": None,
        "popularity_signals": {},
        "provenance": {
            "record": [],
            "fields": {},
        },
        "trust_level": "missing",
        "completeness_score": 0.0,
    }


def blank_television_record(title: str, year: int | None) -> dict[str, Any]:
    return {
        "source_ids": {
            "tmdb_id": None,
            "imdb_id": None,
        },
        "title": title,
        "year": year,
        "premiere_date": None,
        "end_date": None,
        "medium": "television",
        "genres": [],
        "type": None,
        "network": None,
        "seasons": None,
        "episodes": None,
        "principal_cast": [],
        "creators": [],
        "viewership_signals": {},
        "ratings_signals": {},
        "critic_scores": {},
        "awards_summary": None,
        "provenance": {
            "record": [],
            "fields": {},
        },
        "trust_level": "missing",
        "completeness_score": 0.0,
    }


def sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda row: (
            parse_year(row.get("year")) or 0,
            normalize_title(row.get("title")),
        ),
    )


def build_by_year(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        year = parse_year(record.get("year"))
        if year is None:
            continue
        grouped.setdefault(str(year), []).append(record)

    for year in list(grouped.keys()):
        grouped[year] = sorted(grouped[year], key=lambda row: normalize_title(row.get("title")))
    return dict(sorted(grouped.items(), key=lambda item: int(item[0])))


def coverage_years(records: list[dict[str, Any]]) -> tuple[int | None, int | None]:
    years = [parse_year(record.get("year")) for record in records]
    numeric = sorted(year for year in years if year is not None)
    if not numeric:
        return None, None
    return numeric[0], numeric[-1]


def write_sqlite_json_table(conn: sqlite3.Connection, table: str, rows: list[dict[str, Any]]) -> None:
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.execute(
        f"""
        CREATE TABLE {table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            title TEXT,
            trust_level TEXT,
            completeness_score REAL,
            payload_json TEXT NOT NULL
        )
        """
    )

    for row in rows:
        conn.execute(
            f"INSERT INTO {table} (year, title, trust_level, completeness_score, payload_json) VALUES (?, ?, ?, ?, ?)",
            (
                parse_year(row.get("year")),
                str(row.get("title", "")),
                str(row.get("trust_level", "missing")),
                float(row.get("completeness_score", 0.0)),
                json.dumps(row, ensure_ascii=False),
            ),
        )


def trust_distribution(records: list[dict[str, Any]]) -> dict[str, int]:
    output = {level: 0 for level in TRUST_LEVELS}
    for row in records:
        level = str(row.get("trust_level", "missing"))
        if level not in output:
            level = "missing"
        output[level] += 1
    return output
