#!/usr/bin/env python3
"""
Populate data/media/video_cache.json via yt-dlp YouTube search.

Source: Billboard SQLite chart_positions (unique artist + title).
Matching: first result where both artist and title tokens appear in video title;
otherwise first search result. Only adds missing youtube_id; never overwrites.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = Path(
    "/Users/bobhopp/Sites/retroverse/archive/pipelines/retroverse-data/databases/source_billboard_hot_100.db"
)
DEFAULT_CACHE_PATH = REPO_ROOT / "data" / "media" / "video_cache.json"
DEFAULT_STATE_PATH = REPO_ROOT / "data" / "media" / "video_cache_ytdlp_state.json"
DEFAULT_CHECKPOINT_EVERY_ADDS = 25
DEFAULT_PROGRESS_EVERY = 25
DEFAULT_SLEEP_SECONDS = 0.1
DEFAULT_TIMEOUT_SECONDS = 60.0
DEFAULT_LIMIT = 0


def normalize_cache_part(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def normalize_match_text(value: str | None) -> str:
    raw = unicodedata.normalize("NFKD", str(value or ""))
    ascii_only = raw.encode("ascii", "ignore").decode("ascii")
    ascii_only = ascii_only.replace("&", " and ")
    ascii_only = re.sub(r"[^a-zA-Z0-9]+", " ", ascii_only)
    return re.sub(r"\s+", " ", ascii_only).strip().lower()


def track_key(artist: str | None, title: str | None) -> str:
    artist_part = normalize_cache_part(artist)
    title_part = normalize_cache_part(title)
    if not artist_part or not title_part:
        return ""
    return artist_part + "__" + title_part


def load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default
    return payload


def write_json_atomic(path: Path, payload: Any, *, sort_keys: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=str(path.parent),
        delete=False,
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=sort_keys)
        handle.write("\n")
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def load_cache(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json_file(path, {})
    return payload if isinstance(payload, dict) else {}


def save_cache(path: Path, cache: dict[str, dict[str, Any]]) -> None:
    write_json_atomic(path, dict(sorted(cache.items())), sort_keys=False)


def load_state(path: Path) -> dict[str, Any]:
    payload = load_json_file(path, {})
    return payload if isinstance(payload, dict) else {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    write_json_atomic(path, state, sort_keys=True)


def clear_state(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return


def db_signature(path: Path) -> str:
    try:
        st = path.stat()
    except OSError:
        return ""
    return f"{path.resolve()}|{int(st.st_mtime)}|{st.st_size}"


def load_billboard_unique_tracks(db_path: Path) -> tuple[list[dict[str, Any]], str]:
    if not db_path.exists():
        raise SystemExit(f"Billboard database not found: {db_path}")

    sig = db_signature(db_path)
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        cur = connection.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        if "hot100" not in tables:
            raise SystemExit(
                f"Table hot100 not found in {db_path}. Tables: {sorted(tables)[:20]}..."
            )

        cur.execute(
            """
            SELECT DISTINCT TRIM(artist) AS artist, TRIM(title) AS title
            FROM hot100
            WHERE artist IS NOT NULL
              AND title IS NOT NULL
              AND TRIM(artist) <> ''
              AND TRIM(title) <> ''
            ORDER BY artist COLLATE NOCASE, title COLLATE NOCASE
            """
        )
        rows = cur.fetchall()
    finally:
        connection.close()

    seen: set[str] = set()
    tracks: list[dict[str, Any]] = []
    for artist, title in rows:
        a = str(artist or "").strip()
        t = str(title or "").strip()
        key = track_key(a, t)
        if not key or key in seen:
            continue
        seen.add(key)
        tracks.append({"artist": a, "title": t, "key": key})

    return tracks, sig


def determine_resume_index(
    tracks: list[dict[str, Any]],
    state: dict[str, Any],
    signature: str,
    *,
    reset_state: bool,
) -> int:
    if reset_state or not state:
        return 0

    state_signature = str(state.get("db_signature") or "")
    if state_signature != signature:
        return 0

    next_track_key = str(state.get("next_track_key") or "").strip()
    if not next_track_key:
        return 0

    key_to_position = {track["key"]: position for position, track in enumerate(tracks)}
    return key_to_position.get(next_track_key, 0)


def build_resume_state(signature: str, next_track_key: str | None, today: str) -> dict[str, Any]:
    return {
        "db_signature": signature,
        "next_track_key": next_track_key or "",
        "updated_at": today,
    }


def youtube_search_query(artist: str, title: str) -> str:
    return f"{artist} {title}".strip()


def parse_ytdlp_output(raw_output: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for raw_line in raw_output.splitlines():
        line = raw_line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            entries.append(payload)
    return entries


def run_ytdlp_search(
    yt_dlp_bin: str,
    query: str,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    command = [
        yt_dlp_bin,
        f"ytsearch5:{query}",
        "--dump-json",
        "--skip-download",
        "--no-warnings",
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"yt-dlp not found: {yt_dlp_bin}") from exc
    except subprocess.TimeoutExpired:
        return []

    entries = parse_ytdlp_output(completed.stdout)
    if entries:
        return entries

    return []


def _phrase_tokens_appear_in_video(phrase: str, video_title: str) -> bool:
    """Relaxed: every significant token from phrase (len>1) must appear in normalized video title."""
    vt = normalize_match_text(video_title)
    if not vt:
        return False
    words = [w for w in normalize_match_text(phrase).split() if len(w) > 1]
    if not words:
        return False
    return all(w in vt for w in words)


def both_artist_and_title_in_video_title(artist: str, title: str, video_title: str) -> bool:
    return _phrase_tokens_appear_in_video(artist, video_title) and _phrase_tokens_appear_in_video(
        title, video_title
    )


def extract_video_id(candidate: dict[str, Any]) -> str:
    return str(candidate.get("id") or candidate.get("url") or "").strip()


def _title_has_preferred_keywords(video_title: str) -> bool:
    t = video_title.lower()
    return (
        "official video" in t
        or "official music video" in t
        or "hd" in t
        or "remastered" in t
    )


def pick_youtube_id(entries: list[dict[str, Any]], artist: str, title: str) -> str | None:
    for candidate in entries:
        if not isinstance(candidate, dict):
            continue
        vid = extract_video_id(candidate)
        if not vid:
            continue
        vtitle = str(candidate.get("title") or "")
        if both_artist_and_title_in_video_title(artist, title, vtitle) and _title_has_preferred_keywords(
            vtitle
        ):
            return vid
    for candidate in entries:
        if not isinstance(candidate, dict):
            continue
        vid = extract_video_id(candidate)
        if not vid:
            continue
        vtitle = str(candidate.get("title") or "")
        if both_artist_and_title_in_video_title(artist, title, vtitle):
            return vid
    if entries:
        first = entries[0]
        if isinstance(first, dict):
            return extract_video_id(first) or None
    return None


def build_cache_entry(youtube_id: str) -> dict[str, Any]:
    return {"youtube_id": youtube_id}


def cache_has_youtube_id(cache: dict[str, dict[str, Any]], key: str) -> bool:
    entry = cache.get(key)
    if not isinstance(entry, dict):
        return False
    yid = entry.get("youtube_id")
    return isinstance(yid, str) and bool(yid.strip())


def count_cache_with_id(cache: dict[str, dict[str, Any]]) -> int:
    n = 0
    for entry in cache.values():
        if isinstance(entry, dict):
            yid = entry.get("youtube_id")
            if isinstance(yid, str) and yid.strip():
                n += 1
    return n


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Populate video_cache.json from Billboard chart_positions via yt-dlp (ytsearch5)."
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help="Path to Billboard SQLite database (chart_positions).",
    )
    parser.add_argument("--cache", default=str(DEFAULT_CACHE_PATH), help="Path to video cache JSON.")
    parser.add_argument("--state", default=str(DEFAULT_STATE_PATH), help="Path to resume state JSON.")
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Optional max number of lookups this run (new attempts only). 0 = all remaining.",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=DEFAULT_CHECKPOINT_EVERY_ADDS,
        help="Write video_cache.json after this many new youtube_id additions.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=DEFAULT_PROGRESS_EVERY,
        help="Log progress every N tracks processed.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=DEFAULT_SLEEP_SECONDS,
        help="Delay between yt-dlp searches.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Timeout for each yt-dlp search command.",
    )
    parser.add_argument(
        "--yt-dlp-bin",
        default="yt-dlp",
        help="yt-dlp executable to use.",
    )
    parser.add_argument(
        "--reset-state",
        action="store_true",
        help="Ignore saved resume state and start from the beginning of the track list.",
    )
    return parser.parse_args()


def checkpoint(
    cache_path: Path,
    state_path: Path,
    cache: dict[str, dict[str, Any]],
    cache_dirty: bool,
    state_payload: dict[str, Any],
) -> None:
    if cache_dirty:
        save_cache(cache_path, cache)
    save_state(state_path, state_payload)


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).resolve()
    cache_path = Path(args.cache).resolve()
    state_path = Path(args.state).resolve()

    tracks, db_sig = load_billboard_unique_tracks(db_path)
    total_songs = len(tracks)
    cache = load_cache(cache_path)
    existing_with_id = count_cache_with_id(cache)
    state = load_state(state_path)
    today = date.today().isoformat()

    print(f"TOTAL_SONGS {total_songs}")
    print(f"EXISTING_CACHE_WITH_YOUTUBE_ID {existing_with_id}")

    resume_index = determine_resume_index(
        tracks,
        state,
        db_sig,
        reset_state=bool(args.reset_state),
    )

    pending_tracks: list[dict[str, Any]] = []
    for position in range(resume_index, len(tracks)):
        track = tracks[position]
        if cache_has_youtube_id(cache, track["key"]):
            continue
        pending_tracks.append(
            {
                "artist": track["artist"],
                "title": track["title"],
                "key": track["key"],
                "next_track_key": tracks[position + 1]["key"] if position + 1 < len(tracks) else None,
            }
        )

    total_pending = len(pending_tracks)
    if args.limit and args.limit > 0:
        pending_tracks = pending_tracks[: args.limit]

    total = len(pending_tracks)
    if total == 0:
        clear_state(state_path)
        print("NOTHING_TO_PROCESS")
        print("FINAL_ADDED 0")
        return 0

    processed = 0
    added = 0
    additions_since_checkpoint = 0
    cache_dirty = False
    checkpoint_every_adds = max(1, int(args.checkpoint_every))
    progress_every = max(1, int(args.progress_every))
    resume_key = ""
    track: dict[str, Any] | None = None

    try:
        for track in pending_tracks:
            query = youtube_search_query(track["artist"], track["title"])

            try:
                entries = run_ytdlp_search(
                    yt_dlp_bin=args.yt_dlp_bin,
                    query=query,
                    timeout_seconds=args.timeout_seconds,
                )
                yid = pick_youtube_id(entries, track["artist"], track["title"])
                if yid:
                    cache[track["key"]] = build_cache_entry(yid)
                    added += 1
                    cache_dirty = True
                    additions_since_checkpoint += 1
                    if additions_since_checkpoint >= checkpoint_every_adds:
                        resume_next = track["next_track_key"] or ""
                        state_payload = build_resume_state(db_sig, resume_next or None, today)
                        checkpoint(cache_path, state_path, cache, True, state_payload)
                        cache_dirty = False
                        additions_since_checkpoint = 0
            except (OSError, ValueError, TypeError) as exc:
                print(f"SKIP {track['key']}: {exc}", file=sys.stderr)

            processed += 1
            resume_key = track["next_track_key"] or ""

            if processed % progress_every == 0:
                print(f"PROGRESS processed={processed}/{total} added={added} (cumulative)")

            if args.sleep_seconds > 0 and processed < total:
                time.sleep(args.sleep_seconds)
    except KeyboardInterrupt:
        resume_at = (track or {}).get("key") or ""
        state_payload = build_resume_state(db_sig, resume_at or None, today)
        checkpoint(cache_path, state_path, cache, cache_dirty, state_payload)
        print("INTERRUPTED", file=sys.stderr)
        print(f"FINAL_ADDED {added}")
        return 130

    final_state = build_resume_state(db_sig, resume_key or None, today)
    has_more_after_run = total_pending > processed
    if has_more_after_run and resume_key:
        checkpoint(cache_path, state_path, cache, cache_dirty, final_state)
    else:
        if cache_dirty:
            save_cache(cache_path, cache)
        clear_state(state_path)

    print("DONE")
    print(f"FINAL_ADDED {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
