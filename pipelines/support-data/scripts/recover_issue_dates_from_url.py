#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import unquote_plus

from lineage_hook import run_with_lineage


INPUT_PATH = Path("MAGAZINE_ISSUE_MANIFEST.csv")
OUTPUT_PATH = Path("MAGAZINE_ISSUE_MANIFEST_DATED.csv")

# Requested regex patterns
RE_YYYY_MM_DD = re.compile(r"(19|20)\d{2}-\d{2}-\d{2}")
RE_YYYY_MM = re.compile(r"(19|20)\d{2}-\d{2}")
RE_YYYY = re.compile(r"(19|20)\d{2}")


def extract_date_from_url(issue_url: str) -> str | None:
    if not issue_url:
        return None

    text = unquote_plus(issue_url)

    match = RE_YYYY_MM_DD.search(text)
    if match:
        return match.group(0)

    match = RE_YYYY_MM.search(text)
    if match:
        return f"{match.group(0)}-01"

    match = RE_YYYY.search(text)
    if match:
        return f"{match.group(0)}-01-01"

    return None


def recover_issue_dates_from_url(input_path: Path, output_path: Path) -> tuple[int, int, int]:
    with input_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if "issue_date" not in fieldnames:
        raise ValueError("Input CSV missing required column: issue_date")
    if "issue_url" not in fieldnames:
        raise ValueError("Input CSV missing required column: issue_url")

    total_records = len(rows)
    recovered_dates = 0

    for row in rows:
        if (row.get("issue_date") or "").strip():
            continue

        recovered = extract_date_from_url((row.get("issue_url") or "").strip())
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
    total_records, recovered_dates, remaining_missing_dates = recover_issue_dates_from_url(INPUT_PATH, OUTPUT_PATH)
    print(f"total_records: {total_records}")
    print(f"recovered_dates: {recovered_dates}")
    print(f"remaining_missing_dates: {remaining_missing_dates}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
