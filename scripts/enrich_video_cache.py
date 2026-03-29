#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import ssl
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = REPO_ROOT / "raw-data" / "billboard-hot-100.db"
DEFAULT_CACHE_PATH = REPO_ROOT / "data" / "media" / "video_cache.json"
DEFAULT_DOTENV_PATH = REPO_ROOT / ".env"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
DEFAULT_LIMIT = 0
DEFAULT_CONFIDENCE = 0.75
DEFAULT_MIN_CONFIDENCE = 0.75
DEFAULT_SLEEP_SECONDS = 0.1
DEFAULT_CHECKPOINT_EVERY = 25


class YoutubeApiError(RuntimeError):
    pass


class YoutubeApiQuotaError(YoutubeApiError):
    pass


def normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def track_key(artist: str | None, title: str | None) -> str:
    artist_part = normalize_text(artist)
    title_part = normalize_text(title)
    if not artist_part or not title_part:
        return ""
    return artist_part + "__" + title_part


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def load_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def save_cache(path: Path, cache: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(sorted(cache.items())), indent=2) + "\n", encoding="utf-8")


def fetch_hot100_songs(db_path: Path) -> list[tuple[str, str]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT DISTINCT
              TRIM(p.name_display) AS artist,
              TRIM(w.title_display) AS title
            FROM event_entry AS ee
            JOIN event AS e ON e.event_id = ee.event_id
            JOIN work AS w ON w.work_id = ee.work_id
            JOIN person AS p ON p.person_id = w.primary_person_id
            WHERE e.source_system = 'RVA-HOT100'
              AND TRIM(COALESCE(p.name_display, '')) <> ''
              AND TRIM(COALESCE(w.title_display, '')) <> ''
            ORDER BY LOWER(p.name_display), LOWER(w.title_display)
            """,
        ).fetchall()
    finally:
        conn.close()

    songs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        artist = str(row["artist"]).strip()
        title = str(row["title"]).strip()
        key = track_key(artist, title)
        if not key or key in seen:
            continue
        seen.add(key)
        songs.append((artist, title))
    return songs


def needs_lookup(entry: dict[str, Any] | None, min_confidence: float, force_refresh: bool) -> bool:
    if force_refresh:
        return True
    if not entry:
        return True
    youtube_id = str(entry.get("youtube_id") or "").strip()
    if not youtube_id:
        return True
    try:
        confidence = float(entry.get("confidence") or 0.0)
    except (TypeError, ValueError):
        confidence = 0.0
    return confidence < min_confidence


def youtube_search_query(artist: str, title: str) -> str:
    return f"{artist} {title} official music video"


def build_ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def search_youtube_video_id(api_key: str, artist: str, title: str, timeout: float) -> str:
    params = {
        "part": "snippet",
        "type": "video",
        "maxResults": 1,
        "q": youtube_search_query(artist, title),
        "key": api_key,
    }
    url = YOUTUBE_SEARCH_URL + "?" + urlencode(params)
    request = Request(url, headers={"User-Agent": "retroverse-video-cache/1.0"})

    try:
        with urlopen(request, timeout=timeout, context=build_ssl_context()) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        lowered = body.lower()
        if exc.code in {403, 429} or "quota" in lowered:
            raise YoutubeApiQuotaError(f"HTTP {exc.code}: {body[:400]}") from exc
        raise YoutubeApiError(f"HTTP {exc.code}: {body[:400]}") from exc
    except URLError as exc:
        raise YoutubeApiError(f"Network error: {exc}") from exc

    items = payload.get("items") or []
    if not items:
        return ""

    item = items[0] or {}
    id_block = item.get("id") or {}
    return str(id_block.get("videoId") or "").strip()


def build_entry(youtube_id: str, confidence: float, today: str) -> dict[str, Any]:
    return {
        "youtube_id": youtube_id,
        "confidence": confidence,
        "last_updated": today,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enrich data/media/video_cache.json from Billboard Hot 100 songs via YouTube Data API v3."
    )
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Path to billboard-hot-100.db.")
    parser.add_argument("--output", default=str(DEFAULT_CACHE_PATH), help="Path to video_cache.json.")
    parser.add_argument("--dotenv", default=str(DEFAULT_DOTENV_PATH), help="Path to .env file.")
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Optional max songs to process this run. Default 0 processes all remaining candidates.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=DEFAULT_CONFIDENCE,
        help="Confidence score to assign to found YouTube matches.",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=DEFAULT_MIN_CONFIDENCE,
        help="Recheck entries at or below this confidence threshold.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Requery all discovered songs, including high-confidence cache entries.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=DEFAULT_SLEEP_SECONDS,
        help="Delay between YouTube API requests.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="HTTP timeout for YouTube API requests.",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=DEFAULT_CHECKPOINT_EVERY,
        help="Save the cache after this many processed cache updates.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).resolve()
    output_path = Path(args.output).resolve()
    dotenv_path = Path(args.dotenv).resolve()

    if not db_path.exists():
        raise SystemExit(f"Billboard DB not found: {db_path}")

    load_dotenv(dotenv_path)
    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(f"YOUTUBE_API_KEY is not set. Checked environment and {dotenv_path}")

    songs = fetch_hot100_songs(db_path)
    cache = load_cache(output_path)
    today = date.today().isoformat()

    candidates = [
        (artist, title)
        for artist, title in songs
        if needs_lookup(cache.get(track_key(artist, title)), args.min_confidence, args.force_refresh)
    ]

    limit = args.limit if args.limit and args.limit > 0 else len(candidates)
    queue = candidates[:limit]
    queue_total = len(queue)

    print("TOTAL_SONGS_DISCOVERED", len(songs))
    print("CACHE_ENTRIES_BEFORE", len(cache))
    print("LOOKUP_CANDIDATES", len(candidates))
    print("RUN_SIZE", queue_total)

    found = 0
    failed = 0
    unchanged = len(songs) - queue_total
    processed = 0
    dirty_updates = 0
    checkpoint_every = max(1, int(args.checkpoint_every))

    if not queue:
        print("NOTHING_TO_PROCESS")
        return 0

    try:
        for artist, title in queue:
            processed += 1
            key = track_key(artist, title)
            existing = cache.get(key)
            try:
                video_id = search_youtube_video_id(api_key, artist, title, args.timeout_seconds)
                if video_id:
                    cache[key] = build_entry(video_id, args.confidence, today)
                    found += 1
                    status = "FOUND"
                else:
                    cache[key] = build_entry("", 0.0, today)
                    failed += 1
                    status = "NO_MATCH"
            except YoutubeApiQuotaError as exc:
                save_cache(output_path, cache)
                print(f"STOPPED quota after {processed - 1} processed: {exc}", file=sys.stderr)
                return 1
            except YoutubeApiError as exc:
                fallback_id = str((existing or {}).get("youtube_id") or "").strip()
                fallback_confidence = 0.0
                if fallback_id:
                    try:
                        fallback_confidence = float((existing or {}).get("confidence") or 0.0)
                    except (TypeError, ValueError):
                        fallback_confidence = 0.0
                cache[key] = build_entry(fallback_id, fallback_confidence, today)
                failed += 1
                status = "FAILED"
                print(f"ERROR {artist} - {title}: {exc}", file=sys.stderr)

            dirty_updates += 1

            if dirty_updates >= checkpoint_every:
                save_cache(output_path, cache)
                dirty_updates = 0

            print(
                f"PROGRESS {processed} / {queue_total} | found={found} failed={failed} "
                f"unchanged={unchanged} {status} | {artist} - {title}"
            )

            if args.sleep_seconds > 0 and processed < queue_total:
                time.sleep(args.sleep_seconds)
    except KeyboardInterrupt:
        save_cache(output_path, cache)
        print(f"INTERRUPTED after {processed} / {queue_total}; cache saved to {output_path}", file=sys.stderr)
        return 130

    if dirty_updates:
        save_cache(output_path, cache)

    print("CACHE_ENTRIES_AFTER", len(cache))
    print("VIDEOS_FOUND", found)
    print("FAILED", failed)
    print("SKIPPED_OR_UNCHANGED", unchanged)
    print("DONE", output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
