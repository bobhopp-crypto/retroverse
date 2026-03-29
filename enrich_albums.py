#!/usr/bin/env python3
import csv
import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests


BASE_URL = "https://musicbrainz.org/ws/2"
USER_AGENT = "RetroVerse/1.0 (local script)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
}
CACHE_FILE = "mb_cache.json"
EXTRA_FIELDS = [
    "release_group_mbid",
    "release_mbid",
    "release_title",
    "top_tracks",
    "track_count",
    "match_score",
    "match_status",
]


def normalize_text(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def cache_key(artist: str, album: str, year: Any) -> str:
    return f"{normalize_text(artist)}|{normalize_text(album)}|{str(year or '').strip()}"


def load_cache(path: str) -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def save_cache(path: str, cache: Dict[str, Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(cache, handle, ensure_ascii=True, indent=2, sort_keys=True)


def mb_get(path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None
    finally:
        time.sleep(1)


def search_release_groups(album: str, artist: str, year: Optional[int]) -> List[Dict[str, Any]]:
    queries = []
    base = [f'releasegroup:"{album}"', f'artist:"{artist}"']
    if year is not None:
        queries.append(base + [f"firstreleasedate:{year}"])
    queries.append(base)

    for parts in queries:
        data = mb_get(
            "/release-group",
            {
                "fmt": "json",
                "limit": 50,
                "query": " AND ".join(parts),
            },
        )
        if data and data.get("release-groups"):
            return data["release-groups"]
    return []


def extract_artist_name(release_group: Dict[str, Any]) -> str:
    names = []
    for item in release_group.get("artist-credit", []):
        if isinstance(item, dict):
            artist = item.get("artist", {})
            if isinstance(artist, dict) and artist.get("name"):
                names.append(artist["name"])
    return " ".join(names).strip()


def parse_release_group_year(release_group: Dict[str, Any]) -> Optional[int]:
    first_date = (release_group.get("first-release-date") or "").strip()
    if len(first_date) >= 4 and first_date[:4].isdigit():
        return int(first_date[:4])
    return None


def parse_release_year(value: Any) -> Optional[int]:
    text = str(value or "").strip()
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    return None


def score_release_group(
    candidate: Dict[str, Any],
    album: str,
    artist: str,
    year: Optional[int],
) -> Tuple[int, int, int, int, bool, bool]:
    album_norm = normalize_text(album)
    title_norm = normalize_text(candidate.get("title", ""))
    artist_norm = normalize_text(artist)
    candidate_artist_norm = normalize_text(extract_artist_name(candidate))

    title_exact = album_norm == title_norm and bool(album_norm)
    artist_exact = artist_norm == candidate_artist_norm and bool(artist_norm)

    if title_exact:
        title_score = 60
    else:
        album_tokens = set(album_norm.split())
        title_tokens = set(title_norm.split())
        overlap = 0.0
        if album_tokens:
            overlap = len(album_tokens & title_tokens) / float(len(album_tokens))
        if album_norm and (album_norm in title_norm or title_norm in album_norm):
            title_score = 40
        elif overlap >= 0.75:
            title_score = 35
        elif overlap >= 0.5:
            title_score = 25
        elif overlap > 0.0:
            title_score = 10
        else:
            title_score = 0

    if artist_exact:
        artist_score = 30
    elif artist_norm and (
        artist_norm in candidate_artist_norm or candidate_artist_norm in artist_norm
    ):
        artist_score = 20
    else:
        artist_tokens = set(artist_norm.split())
        candidate_tokens = set(candidate_artist_norm.split())
        if artist_tokens:
            overlap = len(artist_tokens & candidate_tokens) / float(len(artist_tokens))
            if overlap >= 0.5:
                artist_score = 10
            elif overlap > 0.0:
                artist_score = 5
            else:
                artist_score = 0
        else:
            artist_score = 0

    candidate_year = parse_release_group_year(candidate)
    if year is None or candidate_year is None:
        year_score = 0
    elif candidate_year == year:
        year_score = 10
    elif abs(candidate_year - year) <= 1:
        year_score = 5
    else:
        year_score = 0

    total = max(0, min(100, title_score + artist_score + year_score))
    return total, title_score, artist_score, year_score, title_exact, artist_exact


def pick_best_release_group(
    groups: List[Dict[str, Any]],
    album: str,
    artist: str,
    year: Optional[int],
) -> Tuple[Optional[Dict[str, Any]], int, str]:
    ranked = rank_release_groups(groups, album, artist, year)
    if not ranked:
        return None, 0, "no_match"

    best = ranked[0]
    best_score, _, _, best_year_score, best_title_exact, best_artist_exact = score_release_group(
        best, album, artist, year
    )

    if best is None or best_score < 40:
        return None, 0, "no_match"
    if best_score >= 95 and best_title_exact and best_artist_exact and best_year_score == 10:
        return best, best_score, "exact"
    if best_score >= 70:
        return best, best_score, "good"
    return best, best_score, "fuzzy"


def summarize_release_structure(release_data: Dict[str, Any]) -> Tuple[int, int]:
    media = release_data.get("media", [])
    if not isinstance(media, list):
        return 0, 0

    total_tracks = 0
    for medium in media:
        if not isinstance(medium, dict):
            continue
        medium_track_count = safe_int(medium.get("track-count"))
        if medium_track_count is not None and medium_track_count > 0:
            total_tracks += medium_track_count
            continue
        tracks = medium.get("tracks", [])
        if isinstance(tracks, list):
            total_tracks += len(tracks)
    return total_tracks, len(media)


def track_range_distance(track_count: int) -> int:
    if 10 <= track_count <= 15:
        return 0
    if track_count < 10:
        return 10 - track_count
    return track_count - 15


def year_distance(release_year: Optional[int], input_year: Optional[int]) -> int:
    if input_year is None or release_year is None:
        return 9999
    return abs(release_year - input_year)


def fetch_all_releases(release_group_mbid: str) -> List[Dict[str, Any]]:
    all_releases: List[Dict[str, Any]] = []
    limit = 100
    offset = 0

    while True:
        data = mb_get(
            "/release",
            {
                "fmt": "json",
                "limit": limit,
                "offset": offset,
                "release-group": release_group_mbid,
                "inc": "media",
            },
        )
        if not data:
            break

        releases = data.get("releases", [])
        if not releases:
            break
        all_releases.extend(releases)

        release_count = safe_int(data.get("release-count"))
        offset += len(releases)
        if release_count is not None:
            if offset >= release_count:
                break
        elif len(releases) < limit:
            break

    return all_releases


def rank_release_groups(
    groups: List[Dict[str, Any]],
    album: str,
    artist: str,
    year: Optional[int],
) -> List[Dict[str, Any]]:
    scored: List[Tuple[Tuple[int, int, int, int], Dict[str, Any]]] = []
    for group in groups:
        total, title_score, artist_score, year_score, _, _ = score_release_group(
            group, album, artist, year
        )
        scored.append(((title_score, artist_score, year_score, total), group))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [group for _, group in scored]


def get_first_release(
    release_group_mbid: str, input_year: Optional[int]
) -> Tuple[Optional[Dict[str, Any]], int]:
    releases = fetch_all_releases(release_group_mbid)
    if not releases:
        return None, 0

    evaluated: List[Dict[str, Any]] = []
    for release in releases:
        release_mbid = release.get("id", "")
        if not release_mbid:
            continue
        track_count, media_count = summarize_release_structure(release)
        release_year = parse_release_year(release.get("date"))
        evaluated.append(
            {
                "release": release,
                "track_count": track_count,
                "media_count": media_count,
                "release_year": release_year,
            }
        )

    if not evaluated:
        return None, 0

    filtered = [r for r in evaluated if r["track_count"] >= 5 and r["media_count"] <= 1]
    if filtered:
        filtered.sort(
            key=lambda r: (
                track_range_distance(r["track_count"]),
                year_distance(r["release_year"], input_year),
                -r["track_count"],
                r["release"].get("id", ""),
            )
        )
        return filtered[0]["release"], int(filtered[0]["track_count"])

    fallback = [r for r in evaluated if 0 < r["track_count"] < 25]
    if fallback:
        fallback.sort(
            key=lambda r: (
                -r["track_count"],
                year_distance(r["release_year"], input_year),
                r["release"].get("id", ""),
            )
        )
        return fallback[0]["release"], int(fallback[0]["track_count"])

    evaluated.sort(
        key=lambda r: (
            -r["track_count"],
            year_distance(r["release_year"], input_year),
            r["release"].get("id", ""),
        )
    )
    return evaluated[0]["release"], int(evaluated[0]["track_count"])


def fetch_release_with_tracks(release_mbid: str) -> Optional[Dict[str, Any]]:
    return mb_get(
        f"/release/{release_mbid}",
        {
            "fmt": "json",
            "inc": "recordings+media",
        },
    )


def extract_tracks(release_data: Dict[str, Any]) -> Tuple[List[str], int]:
    all_tracks: List[str] = []
    for medium in release_data.get("media", []):
        for track in medium.get("tracks", []):
            title = (track.get("title") or "").strip()
            if not title:
                recording = track.get("recording", {})
                if isinstance(recording, dict):
                    title = (recording.get("title") or "").strip()
            if title:
                all_tracks.append(title)

    track_count = len(all_tracks)
    unique_first_five: List[str] = []
    seen = set()
    for title in all_tracks:
        key = normalize_text(title)
        if not key or key in seen:
            continue
        seen.add(key)
        unique_first_five.append(title)
        if len(unique_first_five) == 5:
            break

    return unique_first_five, track_count


def enrich_row(row: Dict[str, str]) -> Dict[str, Any]:
    album = row.get("album", "")
    artist = row.get("artist", "")
    year = safe_int(row.get("year"))

    groups = search_release_groups(album=album, artist=artist, year=year)
    best_group, score, status = pick_best_release_group(groups, album, artist, year)
    if not best_group:
        return {
            "release_group_mbid": "",
            "release_mbid": "",
            "release_title": "",
            "top_tracks": "",
            "track_count": 0,
            "match_score": score,
            "match_status": "no_match",
        }

    release_group_mbid = best_group.get("id", "")

    ranked_groups = rank_release_groups(groups, album, artist, year)
    release = None
    selected_group_mbid = release_group_mbid

    for group in ranked_groups:
        candidate_group_mbid = group.get("id", "")
        if not candidate_group_mbid:
            continue
        candidate_release, candidate_track_count = get_first_release(candidate_group_mbid, year)
        if not candidate_release:
            continue
        release = candidate_release
        selected_group_mbid = candidate_group_mbid
        if candidate_track_count >= 5:
            break

    release_group_mbid = selected_group_mbid
    if not release:
        return {
            "release_group_mbid": release_group_mbid,
            "release_mbid": "",
            "release_title": "",
            "top_tracks": "",
            "track_count": 0,
            "match_score": max(0, score - 15),
            "match_status": "fuzzy" if status != "no_match" else "no_match",
        }

    release_mbid = release.get("id", "")
    release_title = (release.get("title") or "").strip()
    release_data = fetch_release_with_tracks(release_mbid) if release_mbid else None
    if not release_data:
        return {
            "release_group_mbid": release_group_mbid,
            "release_mbid": release_mbid,
            "release_title": release_title,
            "top_tracks": "",
            "track_count": 0,
            "match_score": max(0, score - 10),
            "match_status": "fuzzy" if status != "no_match" else "no_match",
        }

    top_tracks, track_count = extract_tracks(release_data)
    if track_count == 0 and status != "no_match":
        status = "fuzzy"
    return {
        "release_group_mbid": release_group_mbid,
        "release_mbid": release_mbid,
        "release_title": release_title,
        "top_tracks": "|".join(top_tracks),
        "track_count": track_count,
        "match_score": score,
        "match_status": status,
    }


def run(input_csv: str, output_csv: str) -> None:
    cache = load_cache(CACHE_FILE)

    with open(input_csv, "r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError("Input CSV has no data rows.")

    output_rows: List[Dict[str, Any]] = []
    for row in rows:
        key = cache_key(row.get("artist", ""), row.get("album", ""), row.get("year", ""))
        if key in cache:
            enrichment = cache[key]
        else:
            enrichment = enrich_row(row)
            cache[key] = enrichment

        out = dict(row)
        for field in EXTRA_FIELDS:
            out[field] = enrichment.get(field, "")
        output_rows.append(out)
        save_cache(CACHE_FILE, cache)

    fieldnames = list(rows[0].keys()) + EXTRA_FIELDS
    with open(output_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print("Usage: python3 enrich_albums.py <input_csv> <output_csv>")
        return 1
    input_csv, output_csv = argv[1], argv[2]
    run(input_csv, output_csv)
    print(f"Wrote {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
