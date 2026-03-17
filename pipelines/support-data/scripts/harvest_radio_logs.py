#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Any

import pandas as pd

from pipeline_common import (
    PROCESSED_DIR,
    SQLITE_PATH,
    backup_if_exists,
    build_session,
    choose_best_date,
    deterministic_sort,
    ensure_directories,
    fetch_json,
    log_pipeline,
    safe_write_csv,
    write_sqlite_table,
)
from lineage_hook import run_with_lineage


OUTPUT_PATH = PROCESSED_DIR / "radio_airplay.csv"
IA_API = "https://archive.org/advancedsearch.php"

STATION_QUERIES = {
    "WLS Chicago": '(title:("WLS") AND (title:(playlist) OR title:(survey) OR title:("top 40") OR title:(aircheck) OR title:(radio))) AND mediatype:(texts)',
    "KHJ Los Angeles": '(title:("KHJ") AND (title:(playlist) OR title:(survey) OR title:("top 40") OR title:(aircheck) OR title:(radio))) AND mediatype:(texts)',
    "WABC New York": '(title:("WABC") AND (title:(playlist) OR title:(survey) OR title:("top 40") OR title:(aircheck) OR title:(radio))) AND mediatype:(texts)',
    "CKLW Detroit": '(title:("CKLW") AND (title:(playlist) OR title:(survey) OR title:("top 40") OR title:(aircheck) OR title:(radio))) AND mediatype:(texts)',
}

TIME_PATTERN = re.compile(r"\b(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?)\b")


def parse_rotation_category(text: str) -> str:
    lowered = text.lower()
    if "top 40" in lowered or "top-40" in lowered:
        return "Top 40"
    if "survey" in lowered:
        return "Survey"
    if "playlist" in lowered:
        return "Playlist"
    if "aircheck" in lowered:
        return "Aircheck"
    return ""


def parse_artist_title(raw_title: str, station_name: str) -> tuple[str, str]:
    title = raw_title.strip()
    if " - " in title:
        left, right = title.split(" - ", 1)
        if station_name.lower().split()[0] not in left.lower():
            return left.strip(), right.strip()
    return "", title


def build_row(station: str, title: str, identifier: str, date_text: str) -> dict[str, str] | None:
    parsed = choose_best_date(date_text, title, identifier)
    if not parsed:
        return None

    artist, parsed_title = parse_artist_title(title, station)
    time_match = TIME_PATTERN.search(title)
    archive_url = f"https://archive.org/details/{identifier}"
    return {
        "date": parsed.date,
        "station": station,
        "time": time_match.group(1) if time_match else "",
        "artist": artist,
        "title": parsed_title,
        "rotation_category": parse_rotation_category(title),
        "source": archive_url,
    }


def harvest(session, existing_sources: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for station, query in STATION_QUERIES.items():
        page = 1
        station_rows = 0
        while station_rows < 300:
            payload = fetch_json(
                session,
                IA_API,
                params={
                    "q": query,
                    "rows": 100,
                    "page": page,
                    "output": "json",
                    "fl[]": ["identifier", "title", "date"],
                },
                sleep_seconds=0.25,
            )
            docs = ((payload.get("response") or {}).get("docs")) or []
            if not docs:
                break

            for doc in docs:
                identifier = str(doc.get("identifier") or "").strip()
                if not identifier:
                    continue
                archive_url = f"https://archive.org/details/{identifier}"
                if archive_url in existing_sources:
                    continue

                title = str(doc.get("title") or "").strip()
                row = build_row(station, title, identifier, str(doc.get("date") or ""))
                if not row:
                    continue
                rows.append(row)
                existing_sources.add(archive_url)
                station_rows += 1
                if station_rows >= 300:
                    break

            if len(docs) < 100:
                break
            page += 1

    return rows


def main() -> None:
    ensure_directories()
    session = build_session()
    errors = 0

    if OUTPUT_PATH.exists():
        existing_df = pd.read_csv(OUTPUT_PATH, dtype=str).fillna("")
    else:
        existing_df = pd.DataFrame(
            columns=["date", "station", "time", "artist", "title", "rotation_category", "source"]
        )

    existing_sources = set(existing_df.get("source", pd.Series(dtype=str)).astype(str).str.strip()) - {""}

    try:
        new_rows = harvest(session, existing_sources)
    except Exception:  # noqa: BLE001
        new_rows = []
        errors += 1

    new_df = pd.DataFrame(new_rows)
    combined = pd.concat([existing_df, new_df], ignore_index=True)
    before = len(combined)
    combined = combined.drop_duplicates(
        subset=["date", "station", "time", "artist", "title", "source"],
        keep="first",
    )
    duplicates_removed = before - len(combined)

    combined = deterministic_sort(combined, ["date", "station", "time", "artist", "title"])
    combined = combined[["date", "station", "time", "artist", "title", "rotation_category", "source"]]

    safe_write_csv(combined, OUTPUT_PATH)
    backup_if_exists(SQLITE_PATH)
    write_sqlite_table(combined, "radio_airplay")

    records_collected = len(new_df)
    log_pipeline(
        script_name="harvest_radio_logs.py",
        records_collected=records_collected,
        errors=errors,
        duplicates_removed=duplicates_removed,
        message=f"output_rows={len(combined)}",
    )
    print(f"records_collected: {records_collected}")
    print(f"total_rows: {len(combined)}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
