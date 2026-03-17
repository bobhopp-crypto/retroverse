#!/usr/bin/env python3

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import get_dataset_path
from lineage_hook import run_with_lineage


YEAR_MASTER_DIR = get_dataset_path("year_master_dataset", fallback="data/derived/year-masters")
MUSIC_PATH = YEAR_MASTER_DIR / "retroverse_year_end_1958_2024_all.csv"
CULTURE_PATH = get_dataset_path(
    "retroverse_support_cultural",
    fallback="data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv",
)
OUTPUT_PATH = YEAR_MASTER_DIR / "retroverse_year_master_1958_2024.json"


def load_music():
    music_by_year = defaultdict(list)

    with MUSIC_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["first_chart_date"][:4])

            music_by_year[year].append({
                "rv_rank": int(row["rv_rank"]),
                "title": row["title"],
                "artist": row["artist"],
                "peak_rank": int(row["peak_rank"]),
                "weeks_on_chart": int(row["weeks_on_chart"]),
                "weeks_in_top_10": int(row["weeks_in_top_10"]),
                "weeks_in_top_40": int(row["weeks_in_top_40"])
            })

    for year in music_by_year:
        music_by_year[year].sort(key=lambda x: x["rv_rank"])

    return music_by_year


def load_culture():
    culture_by_year = {}

    with CULTURE_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            year = int(row["year"])

            films = [
                row[f"top_film_{i}"].strip()
                for i in range(1, 11)
                if row.get(f"top_film_{i}", "").strip()
            ]

            tv_programs = [
                row[f"top_tv_program_{i}"].strip()
                for i in range(1, 11)
                if row.get(f"top_tv_program_{i}", "").strip()
            ]

            headlines = [
                {
                    "event": row[f"headline_event_{i}"].strip(),
                    "date": row.get(f"headline_date_{i}", "").strip()
                }
                for i in range(1, 11)
                if row.get(f"headline_event_{i}", "").strip()
            ]

            culture_by_year[year] = {
                "top_films": films,
                "top_tv_programs": tv_programs,
                "headlines": headlines
            }

    return culture_by_year


def build_master():
    music = load_music()
    culture = load_culture()

    master = {}

    for year in range(1958, 2025):
        master[year] = {
            "year": year,
            "top_40": music.get(year, []),
            "culture": culture.get(year, {
                "top_films": [],
                "top_tv_programs": [],
                "headlines": []
            })
        }

    return master


def main():
    master = build_master()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(master, f, indent=2)

    print(f"Year master file written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
