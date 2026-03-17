#!/usr/bin/env python3

import csv
import json
import sys
from pathlib import Path

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import get_dataset_path
from lineage_hook import run_with_lineage


OUTPUT_DIR = get_dataset_path("year_master_dataset", fallback="data/derived/year-masters")
CULTURE_FILE = get_dataset_path(
    "retroverse_support_cultural",
    fallback="data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv",
)

START_YEAR = 1958
END_YEAR = 2024


def load_top40(year):
    path = OUTPUT_DIR / f"retroverse_year_end_{year}_top40.csv"
    songs = []

    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "rv_rank": int(row["rv_rank"]),
                "title": row["title"],
                "artist": row["artist"],
                "peak_rank": int(row["peak_rank"]),
                "weeks_on_chart": int(row["weeks_on_chart"]),
                "weeks_in_top_10": int(row["weeks_in_top_10"]),
                "weeks_in_top_40": int(row["weeks_in_top_40"]),
            })

    return songs


def load_culture():
    culture_data = {}

    with CULTURE_FILE.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["year"])

            films = [row[f"top_film_{i}"] for i in range(1, 11)]
            tv = [row[f"top_tv_program_{i}"] for i in range(1, 11)]

            headlines = []
            for i in range(1, 11):
                headlines.append({
                    "event": row[f"headline_event_{i}"],
                    "date": row[f"headline_date_{i}"]
                })

            culture_data[year] = {
                "films": films,
                "tv": tv,
                "headlines": headlines
            }

    return culture_data


def main():
    culture = load_culture()
    master = {}

    for year in range(START_YEAR, END_YEAR + 1):
        top40 = load_top40(year)

        master[str(year)] = {
            "year": year,
            "top_40": top40,
            "culture": culture.get(year, {})
        }

    output_path = OUTPUT_DIR / "retroverse_year_master_1958_2024.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(master, f, indent=2)

    print("Rebuilt master JSON with culture included.")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
