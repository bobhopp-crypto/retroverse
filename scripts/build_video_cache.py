#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "video_links_recovered.csv"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "media" / "video_cache.json"


def normalize_part(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def track_key(artist: str | None, title: str | None) -> str:
    artist_part = normalize_part(artist)
    title_part = normalize_part(title)
    if not artist_part or not title_part:
        return ""
    return artist_part + "__" + title_part


def youtube_id_from_url(url: str | None) -> str:
    raw = str(url or "").strip()
    if not raw:
        return ""

    try:
        parsed = urlparse(raw)
    except ValueError:
        return ""

    hostname = parsed.netloc.lower().replace("www.", "")
    if hostname == "youtu.be":
        return parsed.path.strip("/").split("/")[0]

    if hostname in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            return (parse_qs(parsed.query).get("v") or [""])[0]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/embed/", 1)[1].split("/")[0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/", 1)[1].split("/")[0]

    return ""


def load_existing_cache(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return payload if isinstance(payload, dict) else {}


def build_cache(input_path: Path, output_path: Path, confidence: float) -> tuple[int, int, int]:
    cache = load_existing_cache(output_path)
    today = date.today().isoformat()
    created = 0
    updated = 0
    skipped = 0

    with input_path.open(newline="", encoding="utf-8") as handle:
      reader = csv.DictReader(handle)
      for row in reader:
        artist = row.get("artist", "")
        title = row.get("title", "")
        youtube_url = row.get("youtube_url", "")
        key = track_key(artist, title)
        youtube_id = youtube_id_from_url(youtube_url)
        if not key or not youtube_id:
            skipped += 1
            continue

        existing = cache.get(key)
        entry = {
            "youtube_id": youtube_id,
            "confidence": confidence,
            "last_updated": today,
        }

        if not existing:
            cache[key] = entry
            created += 1
            continue

        existing_confidence = existing.get("confidence", 0)
        if existing.get("youtube_id") != youtube_id or float(existing_confidence) <= confidence:
            cache[key] = entry
            updated += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dict(sorted(cache.items())), indent=2) + "\n", encoding="utf-8")
    return created, updated, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a mergeable video cache from recovered CSV links.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to source CSV.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path to output JSON cache.")
    parser.add_argument("--confidence", type=float, default=1.0, help="Confidence score to assign to imported rows.")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists():
        raise SystemExit(f"Input CSV not found: {input_path}")

    created, updated, skipped = build_cache(input_path, output_path, args.confidence)
    total = len(load_existing_cache(output_path))
    print("WROTE", output_path)
    print("TOTAL_KEYS", total)
    print("CREATED", created)
    print("UPDATED", updated)
    print("SKIPPED", skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
