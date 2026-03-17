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


OUTPUT_PATH = PROCESSED_DIR / "tv_listings.csv"
IA_API = "https://archive.org/advancedsearch.php"
YEAR_MIN = 1970
YEAR_MAX = 2000

QUERIES = [
    'title:("TV Guide") AND mediatype:(texts)',
    'title:("television listings") AND mediatype:(texts)',
    'title:("tv listings") AND mediatype:(texts)',
    'title:("newspaper tv section") AND mediatype:(texts)',
]

NETWORK_PATTERN = re.compile(r"\b(ABC|CBS|NBC|PBS|FOX|HBO|CW)\b", re.IGNORECASE)
TIME_PATTERN = re.compile(r"\b(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?)\b")


def build_row(title: str, archive_identifier: str, date_text: str) -> dict[str, str]:
    parsed = choose_best_date(date_text, title, archive_identifier)
    if not parsed:
        return {}
    if parsed.year < YEAR_MIN or parsed.year > YEAR_MAX:
        return {}

    network_match = NETWORK_PATTERN.search(title or "")
    time_match = TIME_PATTERN.search(title or "")

    return {
        "date": parsed.date,
        "network": network_match.group(1).upper() if network_match else "",
        "time": time_match.group(1) if time_match else "",
        "program": (title or "").strip(),
        "episode": "",
        "source": "Internet Archive",
        "archive_url": f"https://archive.org/details/{archive_identifier}",
    }


def harvest(session, existing_identifiers: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    max_rows = 1200

    for query in QUERIES:
        page = 1
        while len(rows) < max_rows:
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
                if not identifier or identifier in existing_identifiers:
                    continue
                title = str(doc.get("title") or "").strip()
                row = build_row(title, identifier, str(doc.get("date") or ""))
                if not row:
                    continue
                rows.append(row)
                existing_identifiers.add(identifier)
                if len(rows) >= max_rows:
                    break

            if len(docs) < 100:
                break
            page += 1

        if len(rows) >= max_rows:
            break

    return rows


def main() -> None:
    ensure_directories()
    session = build_session()
    errors = 0

    if OUTPUT_PATH.exists():
        existing_df = pd.read_csv(OUTPUT_PATH, dtype=str).fillna("")
    else:
        existing_df = pd.DataFrame(columns=["date", "network", "time", "program", "episode", "source", "archive_url"])

    existing_identifiers = set(
        existing_df.get("archive_url", pd.Series(dtype=str))
        .astype(str)
        .str.extract(r"/details/([^/?#]+)")[0]
        .dropna()
        .tolist()
    )

    try:
        new_rows = harvest(session, existing_identifiers)
    except Exception:  # noqa: BLE001
        new_rows = []
        errors += 1

    new_df = pd.DataFrame(new_rows)
    combined = pd.concat([existing_df, new_df], ignore_index=True)
    before = len(combined)
    combined = combined.drop_duplicates(
        subset=["date", "network", "time", "program", "archive_url"],
        keep="first",
    )
    duplicates_removed = before - len(combined)

    combined = deterministic_sort(combined, ["date", "network", "time", "program", "archive_url"])
    combined = combined[["date", "network", "time", "program", "episode", "source", "archive_url"]]

    safe_write_csv(combined, OUTPUT_PATH)
    backup_if_exists(SQLITE_PATH)
    write_sqlite_table(combined, "tv_listings")

    records_collected = len(new_df)
    log_pipeline(
        script_name="harvest_tv_listings.py",
        records_collected=records_collected,
        errors=errors,
        duplicates_removed=duplicates_removed,
        message=f"output_rows={len(combined)}",
    )
    print(f"records_collected: {records_collected}")
    print(f"total_rows: {len(combined)}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
