#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3

from lineage_hook import run_with_lineage


MAGAZINES = [
    "MAD Magazine",
    "National Lampoon",
    "Billboard",
    "Cosmopolitan",
    "Seventeen",
    "People",
    "Entertainment Weekly",
    "New York Magazine",
    "Tiger Beat",
    "Teen Beat",
]

API_URL = "https://archive.org/advancedsearch.php"
OUTPUT_FILE = Path("MAGAZINE_ARCHIVE_HARVEST.csv")
MAX_RESULTS_PER_MAGAZINE = 500
ROWS_PER_PAGE = 100
FIELDS = ["identifier", "title", "date", "creator"]


def normalize_creator(value: Any) -> str:
    if isinstance(value, list):
        return " | ".join(str(item).strip() for item in value if str(item).strip())
    if value is None:
        return ""
    return str(value).strip()


def fetch_magazine_results(session: requests.Session, magazine: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    page = 1

    while len(records) < MAX_RESULTS_PER_MAGAZINE:
        params: dict[str, Any] = {
            "q": f'title:("{magazine}") AND mediatype:(texts)',
            "rows": ROWS_PER_PAGE,
            "page": page,
            "output": "json",
            "fl[]": FIELDS,
        }

        response = session.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(f"Archive API error for '{magazine}': {payload['error']}")
        docs = (payload.get("response") or {}).get("docs") or []

        if not docs:
            break

        for doc in docs:
            identifier = str(doc.get("identifier", "")).strip()
            if not identifier:
                continue
            records.append(
                {
                    "magazine": magazine,
                    "title": str(doc.get("title", "")).strip(),
                    "date": str(doc.get("date", "")).strip(),
                    "identifier": identifier,
                    "archive_url": f"https://archive.org/details/{identifier}",
                    "creator": normalize_creator(doc.get("creator")),
                }
            )
            if len(records) >= MAX_RESULTS_PER_MAGAZINE:
                break

        if len(docs) < ROWS_PER_PAGE:
            break

        page += 1

    return records


def main() -> None:
    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"{OUTPUT_FILE} already exists. Refusing to overwrite existing dataset."
        )

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "RetroVerseMagazineHarvester/1.0 (metadata only)",
            "Accept": "application/json",
        }
    )
    session.verify = False

    all_rows: list[dict[str, str]] = []
    for magazine in MAGAZINES:
        all_rows.extend(fetch_magazine_results(session, magazine))

    df = pd.DataFrame(all_rows)
    if not df.empty:
        # Deduplicate harvested issues by identifier across all magazine queries.
        df = df.drop_duplicates(subset=["identifier"], keep="first")
        df = df.sort_values(by=["magazine", "date", "title", "identifier"], kind="stable")

    # Keep only requested output columns.
    df_out = df[["magazine", "title", "date", "identifier", "archive_url"]] if not df.empty else pd.DataFrame(
        columns=["magazine", "title", "date", "identifier", "archive_url"]
    )
    df_out.to_csv(OUTPUT_FILE, index=False)

    print(f"records_collected: {len(df_out)}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
