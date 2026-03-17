#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from lineage_hook import run_with_lineage


INPUT_PATH = Path("MAGAZINE_MASTER_ARCHIVE.csv")
CSV_OUTPUT_PATH = Path("MAGAZINE_YEAR_INDEX.csv")
JSON_OUTPUT_PATH = Path("public/data/magazine-year-index.json")

DATE_PATTERN = re.compile(r"^\s*((?:19|20)\d{2})(?:-(\d{2})(?:-(\d{2}))?)?\s*$")


def extract_year(value: object) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    match = DATE_PATTERN.match(text)
    if not match:
        return None
    return int(match.group(1))


def main() -> None:
    df = pd.read_csv(INPUT_PATH, dtype=str).fillna("")

    df["year"] = df["date"].apply(extract_year)
    df_year = df[df["year"].notna()].copy()
    df_year["year"] = df_year["year"].astype(int)

    summary_rows: list[dict[str, object]] = []
    json_payload: dict[str, dict[str, object]] = {}

    for year, group in df_year.groupby("year", sort=True):
        issue_count = int(len(group))
        magazines = sorted(set(group["magazine"].astype(str).str.strip()) - {""})
        magazine_count = len(magazines)

        top_counts = (
            group.assign(magazine=group["magazine"].astype(str).str.strip())
            .query("magazine != ''")
            .groupby("magazine")
            .size()
            .reset_index(name="count")
            .sort_values(by=["count", "magazine"], ascending=[False, True], kind="stable")
        )
        top_magazines_list = top_counts["magazine"].head(3).tolist()

        summary_rows.append(
            {
                "year": year,
                "issue_count": issue_count,
                "magazine_count": magazine_count,
                "top_magazines": " | ".join(top_magazines_list),
            }
        )

        json_payload[str(year)] = {
            "issue_count": issue_count,
            "magazines": magazines,
            "top_magazines": top_magazines_list,
        }

    summary_df = pd.DataFrame(summary_rows, columns=["year", "issue_count", "magazine_count", "top_magazines"])
    summary_df.to_csv(CSV_OUTPUT_PATH, index=False)

    JSON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT_PATH.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    years_detected = len(summary_df)
    if years_detected == 0:
        earliest_year = ""
        latest_year = ""
    else:
        earliest_year = int(summary_df["year"].min())
        latest_year = int(summary_df["year"].max())

    print(f"years_detected: {years_detected}")
    print(f"earliest_year: {earliest_year}")
    print(f"latest_year: {latest_year}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
