#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote_plus

from lineage_hook import run_with_lineage


INPUT_PATH = Path("MAGAZINE_ISSUE_MANIFEST.csv")
OUTPUT_PATH = Path("MAGAZINE_ISSUE_MANIFEST_DATED.csv")

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

MONTH_PATTERN = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
    r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)

RE_YYYY_MM_DD = re.compile(
    r"\b((?:19|20)\d{2})[-_/\.](0[1-9]|1[0-2])[-_/\.](0[1-9]|[12]\d|3[01])\b",
    re.IGNORECASE,
)
RE_YYYY_MM = re.compile(
    r"\b((?:19|20)\d{2})[-_/\.](0[1-9]|1[0-2])\b(?![-_/\.]\d)",
    re.IGNORECASE,
)
RE_MONTH_DD_YYYY = re.compile(
    rf"\b({MONTH_PATTERN})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,)?\s+((?:19|20)\d{{2}})\b",
    re.IGNORECASE,
)
RE_MONTH_YYYY = re.compile(
    rf"\b({MONTH_PATTERN})\s+((?:19|20)\d{{2}})\b",
    re.IGNORECASE,
)


def build_iso(year: int, month: int, day: int) -> str | None:
    try:
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return None


def extract_date(text: str) -> str | None:
    if not text:
        return None

    cleaned = unquote_plus(text)

    match = RE_YYYY_MM_DD.search(cleaned)
    if match:
        iso = build_iso(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        if iso:
            return iso

    match = RE_YYYY_MM.search(cleaned)
    if match:
        iso = build_iso(int(match.group(1)), int(match.group(2)), 1)
        if iso:
            return iso

    match = RE_MONTH_DD_YYYY.search(cleaned)
    if match:
        month_key = match.group(1).lower()
        month = MONTHS.get(month_key)
        if month:
            iso = build_iso(int(match.group(3)), month, int(match.group(2)))
            if iso:
                return iso

    match = RE_MONTH_YYYY.search(cleaned)
    if match:
        month_key = match.group(1).lower()
        month = MONTHS.get(month_key)
        if month:
            iso = build_iso(int(match.group(2)), month, 1)
            if iso:
                return iso

    return None


def recover_issue_dates(input_path: Path, output_path: Path) -> tuple[int, int, int]:
    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if "issue_date" not in fieldnames:
        raise ValueError("Input CSV is missing required column: issue_date")

    total_records = len(rows)
    recovered_dates = 0

    for row in rows:
        current_date = (row.get("issue_date") or "").strip()
        if current_date:
            continue

        issue_title = (row.get("issue_title") or "").strip()
        issue_url = (row.get("issue_url") or "").strip()

        recovered = extract_date(issue_title) or extract_date(issue_url)
        if recovered:
            row["issue_date"] = recovered
            recovered_dates += 1

    remaining_missing_dates = sum(1 for row in rows if not (row.get("issue_date") or "").strip())

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return total_records, recovered_dates, remaining_missing_dates


def main() -> None:
    total_records, recovered_dates, remaining_missing_dates = recover_issue_dates(INPUT_PATH, OUTPUT_PATH)
    print(f"total_records: {total_records}")
    print(f"recovered_dates: {recovered_dates}")
    print(f"remaining_missing_dates: {remaining_missing_dates}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
