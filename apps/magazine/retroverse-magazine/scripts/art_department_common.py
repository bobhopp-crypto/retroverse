#!/usr/bin/env python3
"""Shared helpers for the RetroVerse Art Department registry and assets."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_APPS_ROOT = PROJECT_ROOT.parent.parent
WEB_PUBLIC_ROOT = REPO_APPS_ROOT / "web" / "public"
CANONICAL_REGISTRY_PATH = PROJECT_ROOT / "data" / "retroverse_artists.json"
PUBLIC_ART_DEPARTMENT_ROOT = PROJECT_ROOT / "public" / "art-department"
PUBLIC_REGISTRY_CACHE_PATH = PUBLIC_ART_DEPARTMENT_ROOT / "registry.json"
PORTRAITS_ROOT = PUBLIC_ART_DEPARTMENT_ROOT / "portraits"
REFERENCE_ROOT = PUBLIC_ART_DEPARTMENT_ROOT / "reference"
TYPE_SAMPLES_ROOT = PUBLIC_ART_DEPARTMENT_ROOT / "type-samples"
WEB_PUBLIC_ART_DEPARTMENT_PATH = WEB_PUBLIC_ROOT / "art-department"
LOGS_ROOT = PROJECT_ROOT / "logs"

REQUIRED_FIELDS = [
    "id",
    "display_name",
    "public_credit",
    "internal_influence",
    "department",
    "era_fit",
    "origin_region",
    "bio",
    "personality",
    "style_traits",
    "best_use",
    "avoid_use",
    "signature_notes",
    "self_portrait_prompt",
    "reference_scene_prompts",
    "self_portrait_path",
    "reference_images",
    "published_examples",
]


def utc_timestamp() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_art_department_directories() -> None:
    for path in (PUBLIC_ART_DEPARTMENT_ROOT, PORTRAITS_ROOT, REFERENCE_ROOT, TYPE_SAMPLES_ROOT, LOGS_ROOT):
        path.mkdir(parents=True, exist_ok=True)


def load_registry() -> dict[str, Any]:
    payload = json.loads(CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{CANONICAL_REGISTRY_PATH} must contain a JSON object.")
    artists = payload.get("artists")
    if not isinstance(artists, list):
        raise ValueError(f"{CANONICAL_REGISTRY_PATH} must contain artists[].")
    return payload


def save_registry(payload: dict[str, Any]) -> None:
    CANONICAL_REGISTRY_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def validate_registry(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    artists = payload.get("artists")
    if not isinstance(artists, list):
        return ["Registry must include artists[] as a list."]

    seen_ids: set[str] = set()
    for index, artist in enumerate(artists):
        if not isinstance(artist, dict):
            errors.append(f"Artist at index {index} is not an object.")
            continue

        artist_id = str(artist.get("id") or "").strip()
        if not artist_id:
            errors.append(f"Artist at index {index} is missing id.")
        elif artist_id in seen_ids:
            errors.append(f"Duplicate artist id: {artist_id}")
        else:
            seen_ids.add(artist_id)

        for field in REQUIRED_FIELDS:
            if field not in artist:
                errors.append(f"{artist_id or f'index {index}'} missing required field: {field}")

        for list_field in ("era_fit", "style_traits", "best_use", "avoid_use", "reference_scene_prompts", "reference_images", "published_examples"):
            value = artist.get(list_field)
            if not isinstance(value, list):
                errors.append(f"{artist_id or f'index {index}'} field {list_field} must be a list.")

        for string_field in (
            "display_name",
            "public_credit",
            "internal_influence",
            "department",
            "origin_region",
            "bio",
            "personality",
            "signature_notes",
            "self_portrait_prompt",
            "self_portrait_path",
        ):
            value = artist.get(string_field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{artist_id or f'index {index}'} field {string_field} must be a non-empty string.")

    return errors


def slugify(text: str, limit: int = 72) -> str:
    compact = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    compact = re.sub(r"-{2,}", "-", compact)
    if not compact:
        return "item"
    return compact[:limit].strip("-") or "item"


def prompt_slug(prompt: str, word_limit: int = 7) -> str:
    words = re.findall(r"[a-z0-9]+", prompt.lower())
    return slugify("-".join(words[:word_limit]))


def is_typography_specialist(artist: dict[str, Any]) -> bool:
    return str(artist.get("department") or "").strip().lower() == "type & lettering"


def illustration_artists(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [artist for artist in payload.get("artists", []) if isinstance(artist, dict) and not is_typography_specialist(artist)]


def find_artist(payload: dict[str, Any], artist_id: str) -> dict[str, Any] | None:
    for artist in payload.get("artists", []):
        if isinstance(artist, dict) and artist.get("id") == artist_id:
            return artist
    return None


def write_public_registry_cache(payload: dict[str, Any]) -> None:
    ensure_art_department_directories()
    cache_payload = {
        "version": payload.get("version", 1),
        "built_at": utc_timestamp(),
        "artists": payload.get("artists", []),
    }
    PUBLIC_REGISTRY_CACHE_PATH.write_text(json.dumps(cache_payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def ensure_web_public_bridge() -> str:
    ensure_art_department_directories()
    WEB_PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)

    if WEB_PUBLIC_ART_DEPARTMENT_PATH.is_symlink():
        current = os.readlink(WEB_PUBLIC_ART_DEPARTMENT_PATH)
        expected = os.path.relpath(PUBLIC_ART_DEPARTMENT_ROOT, start=WEB_PUBLIC_ART_DEPARTMENT_PATH.parent)
        if current == expected:
            return "symlink_ok"
        raise RuntimeError(
            f"Existing art-department symlink points to {current}, expected {expected}: {WEB_PUBLIC_ART_DEPARTMENT_PATH}"
        )

    if WEB_PUBLIC_ART_DEPARTMENT_PATH.exists():
        return "exists_without_symlink"

    relative_target = os.path.relpath(PUBLIC_ART_DEPARTMENT_ROOT, start=WEB_PUBLIC_ART_DEPARTMENT_PATH.parent)
    WEB_PUBLIC_ART_DEPARTMENT_PATH.symlink_to(relative_target, target_is_directory=True)
    return "symlink_created"


def append_log(log_name: str, message: str) -> None:
    ensure_art_department_directories()
    log_path = LOGS_ROOT / log_name
    timestamped = f"[{utc_timestamp()}] {message}"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(timestamped + "\n")

