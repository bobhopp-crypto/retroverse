#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from pipeline_common import (
    PROCESSED_DIR,
    SQLITE_PATH,
    backup_if_exists,
    build_session,
    choose_best_date,
    deterministic_sort,
    ensure_directories,
    fetch_json,
    fetch_text,
    log_pipeline,
    normalize_text,
    safe_write_csv,
    write_sqlite_table,
)
from lineage_hook import run_with_lineage


OUTPUT_PATH = PROCESSED_DIR / "magazine_issues.csv"
IA_API = "https://archive.org/advancedsearch.php"
HATHI_ISSN_API = "https://catalog.hathitrust.org/api/volumes/brief/issn/{issn}.json"
GOOGLE_FEED_API = "https://books.google.com/books/feeds/volumes"

MAGAZINES = [
    "MAD Magazine",
    "National Lampoon",
    "Billboard",
    "People",
    "Entertainment Weekly",
    "Tiger Beat",
    "Teen Beat",
    "Seventeen",
    "Cosmopolitan",
    "New York Magazine",
    "TV Guide",
    "Rolling Stone",
]

HATHI_ISSN = {
    "MAD Magazine": "0024-9319",
    "National Lampoon": "0027-9528",
    "Billboard": "0006-2510",
    "People": "0093-7673",
    "Entertainment Weekly": "1049-0434",
    "Seventeen": "0037-301X",
    "Cosmopolitan": "0010-9541",
    "New York Magazine": "0028-7369",
    "TV Guide": "0039-8548",
    "Rolling Stone": "0035-7914",
}


def _base_row(
    magazine: str,
    title: str,
    parsed_date: Any,
    identifier: str,
    archive_url: str,
    source_repository: str,
) -> dict[str, Any]:
    return {
        "magazine": magazine,
        "title": title.strip(),
        "date": parsed_date.date if parsed_date else "",
        "year": parsed_date.year if parsed_date else "",
        "month": parsed_date.month if parsed_date else "",
        "identifier": identifier.strip(),
        "archive_url": archive_url.strip(),
        "source_repository": source_repository,
    }


def harvest_internet_archive(session, magazine: str, existing_ids: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 1
    max_rows = 500

    while len(rows) < max_rows:
        payload = fetch_json(
            session,
            IA_API,
            params={
                "q": f'title:("{magazine}") AND mediatype:(texts)',
                "rows": 100,
                "page": page,
                "output": "json",
                "fl[]": ["identifier", "title", "date", "creator"],
            },
            sleep_seconds=0.2,
        )

        docs = ((payload.get("response") or {}).get("docs")) or []
        if not docs:
            break

        for doc in docs:
            identifier = str(doc.get("identifier") or "").strip()
            if not identifier or identifier in existing_ids:
                continue

            title = str(doc.get("title") or "").strip()
            parsed_date = choose_best_date(doc.get("date"), title, identifier)
            row = _base_row(
                magazine=magazine,
                title=title,
                parsed_date=parsed_date,
                identifier=identifier,
                archive_url=f"https://archive.org/details/{identifier}",
                source_repository="Internet Archive",
            )
            rows.append(row)
            existing_ids.add(identifier)
            if len(rows) >= max_rows:
                break

        if len(docs) < 100:
            break
        page += 1

    return rows


def harvest_hathitrust(session, magazine: str, existing_ids: set[str]) -> list[dict[str, Any]]:
    issn = HATHI_ISSN.get(magazine)
    if not issn:
        return []

    payload = fetch_json(session, HATHI_ISSN_API.format(issn=issn.replace("-", "")), sleep_seconds=0.25)
    rows: list[dict[str, Any]] = []
    items = payload.get("items") if isinstance(payload.get("items"), list) else []

    for item in items[:250]:
        if not isinstance(item, dict):
            continue
        identifier = str(item.get("htid") or "").strip()
        if not identifier:
            continue
        if identifier in existing_ids:
            continue

        enumcron = str(item.get("enumcron") or "").strip()
        item_url = str(item.get("itemURL") or "").strip()
        parsed_date = choose_best_date(enumcron, item.get("lastUpdate"))
        title = f"{magazine} {enumcron}".strip()
        rows.append(
            _base_row(
                magazine=magazine,
                title=title,
                parsed_date=parsed_date,
                identifier=identifier,
                archive_url=item_url,
                source_repository="HathiTrust",
            )
        )
        existing_ids.add(identifier)

    return rows


def harvest_google_books(session, magazine: str, existing_ids: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    max_rows = 120
    start_index = 1
    page_size = 20
    magazine_norm = normalize_text(magazine)

    while len(rows) < max_rows:
        xml_text = fetch_text(
            session,
            GOOGLE_FEED_API,
            params={
                "q": f'"{magazine}" magazine',
                "start-index": str(start_index),
                "max-results": str(page_size),
            },
            sleep_seconds=0.3,
        )
        soup = BeautifulSoup(xml_text, "xml")
        entries = soup.find_all("entry")
        if not entries:
            break

        for entry in entries:
            id_node = entry.find("id")
            identifier_tail = id_node.text.strip().split("/")[-1] if id_node and id_node.text else ""
            if not identifier_tail:
                continue
            identifier = f"gbooks:{identifier_tail}"
            if identifier in existing_ids:
                continue

            title_node = entry.find("dc:title") or entry.find("title")
            title = title_node.text.strip() if title_node and title_node.text else ""
            title_norm = normalize_text(title)
            if magazine_norm and magazine_norm not in title_norm:
                formats = [tag.text.strip().lower() for tag in entry.find_all("dc:format") if tag.text]
                if not any("magazine" in item for item in formats):
                    continue

            date_node = entry.find("dc:date")
            date_text = date_node.text.strip() if date_node and date_node.text else ""
            parsed_date = choose_best_date(date_text, title)

            alt_url = ""
            for link in entry.find_all("link"):
                if link.get("rel") == "alternate":
                    alt_url = (link.get("href") or "").strip()
                    break

            rows.append(
                _base_row(
                    magazine=magazine,
                    title=title,
                    parsed_date=parsed_date,
                    identifier=identifier,
                    archive_url=alt_url,
                    source_repository="Google Books",
                )
            )
            existing_ids.add(identifier)
            if len(rows) >= max_rows:
                break

        if len(entries) < page_size:
            break
        start_index += page_size

    return rows


def dedupe_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    temp = df.copy()
    for column in ("magazine", "title", "date", "year", "month", "identifier", "archive_url", "source_repository"):
        if column not in temp.columns:
            temp[column] = ""
        temp[column] = temp[column].fillna("").astype(str).str.strip()

    temp["_dedupe_key"] = temp["identifier"]
    missing_id = temp["_dedupe_key"].eq("")
    if missing_id.any():
        fallback_keys = temp.loc[
            missing_id, ["magazine", "title", "date", "archive_url", "source_repository"]
        ].apply(lambda row: "|".join(str(value).strip() for value in row.values), axis=1)
        temp.loc[missing_id, "_dedupe_key"] = fallback_keys

    before = len(temp)
    deduped = temp.drop_duplicates(subset=["_dedupe_key"], keep="first").drop(columns=["_dedupe_key"])
    duplicates_removed = before - len(deduped)
    return deduped, duplicates_removed


def main() -> None:
    ensure_directories()
    session = build_session()
    errors = 0
    new_rows: list[dict[str, Any]] = []

    if OUTPUT_PATH.exists():
        existing_df = pd.read_csv(OUTPUT_PATH, dtype=str).fillna("")
    else:
        existing_df = pd.DataFrame(columns=["magazine", "title", "date", "year", "month", "identifier", "archive_url", "source_repository"])

    existing_ids = set(existing_df.get("identifier", pd.Series(dtype=str)).astype(str).str.strip()) - {""}

    for magazine in MAGAZINES:
        try:
            new_rows.extend(harvest_internet_archive(session, magazine, existing_ids))
            new_rows.extend(harvest_hathitrust(session, magazine, existing_ids))
            new_rows.extend(harvest_google_books(session, magazine, existing_ids))
        except Exception:  # noqa: BLE001
            errors += 1

    new_df = pd.DataFrame(new_rows)
    combined = pd.concat([existing_df, new_df], ignore_index=True)
    combined, duplicates_removed = dedupe_rows(combined)
    combined = deterministic_sort(
        combined,
        ["magazine", "date", "title", "identifier", "source_repository"],
    )
    combined = combined[["magazine", "title", "date", "year", "month", "identifier", "archive_url", "source_repository"]]

    safe_write_csv(combined, OUTPUT_PATH)
    backup_if_exists(SQLITE_PATH)
    write_sqlite_table(combined, "magazine_issues")

    records_collected = len(new_df)
    log_pipeline(
        script_name="harvest_magazines.py",
        records_collected=records_collected,
        errors=errors,
        duplicates_removed=duplicates_removed,
        message=f"output_rows={len(combined)}",
    )
    print(f"records_collected: {records_collected}")
    print(f"total_rows: {len(combined)}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
