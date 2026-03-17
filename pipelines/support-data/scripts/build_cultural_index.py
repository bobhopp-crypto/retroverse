#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd

from pipeline_common import INDEX_DIR, PROCESSED_DIR, ensure_directories, log_pipeline, safe_write_csv
from lineage_hook import run_with_lineage


MAGAZINES_PATH = PROCESSED_DIR / "magazine_issues.csv"
BILLBOARD_PATH = PROCESSED_DIR / "billboard_hot100.csv"
TV_PATH = PROCESSED_DIR / "tv_listings.csv"
RADIO_PATH = PROCESSED_DIR / "radio_airplay.csv"
OUTPUT_PATH = INDEX_DIR / "cultural_week_index.csv"


def _week_start(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce")
    week_start = dt - pd.to_timedelta(dt.dt.weekday, unit="D")
    return week_start.dt.strftime("%Y-%m-%d")


def _load_csv(path, columns) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    return pd.DataFrame(columns=columns)


def _join_unique(values: pd.Series, limit: int = 5) -> str:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    unique = sorted(set(cleaned))
    return "; ".join(unique[:limit])


def main() -> None:
    ensure_directories()
    errors = 0

    magazines = _load_csv(MAGAZINES_PATH, ["magazine", "title", "date"])
    billboard = _load_csv(BILLBOARD_PATH, ["chart_date", "rank", "title", "artist"])
    tv = _load_csv(TV_PATH, ["date", "program"])
    radio = _load_csv(RADIO_PATH, ["date", "artist", "title"])

    billboard["rank"] = pd.to_numeric(billboard.get("rank", pd.Series(dtype=float)), errors="coerce")
    billboard_top = billboard[billboard["rank"] == 1].copy()
    billboard_top["week_date"] = _week_start(billboard_top.get("chart_date", pd.Series(dtype=str)))
    billboard_top = billboard_top[billboard_top["week_date"].notna() & billboard_top["week_date"].ne("")]
    billboard_top = billboard_top.sort_values(by=["chart_date", "title", "artist"], kind="stable")
    billboard_week = billboard_top.groupby("week_date", as_index=False).first()

    tv["week_date"] = _week_start(tv.get("date", pd.Series(dtype=str)))
    tv_week = (
        tv[tv["week_date"].notna() & tv["week_date"].ne("")]
        .groupby("week_date")["program"]
        .apply(_join_unique)
        .reset_index(name="tv_programs")
    )

    magazines["week_date"] = _week_start(magazines.get("date", pd.Series(dtype=str)))
    magazine_titles = magazines["title"].where(magazines["title"].str.strip().ne(""), magazines["magazine"])
    magazines = magazines.assign(_title=magazine_titles)
    magazines_week = (
        magazines[magazines["week_date"].notna() & magazines["week_date"].ne("")]
        .groupby("week_date")["_title"]
        .apply(_join_unique)
        .reset_index(name="magazine_titles")
    )

    radio["week_date"] = _week_start(radio.get("date", pd.Series(dtype=str)))
    radio["track"] = radio["artist"].where(
        radio["artist"].str.strip().ne(""),
        "",
    )
    radio["track"] = radio.apply(
        lambda row: (
            f"{row['artist']} - {row['title']}".strip(" -")
            if str(row.get("artist", "")).strip()
            else str(row.get("title", "")).strip()
        ),
        axis=1,
    )
    radio_week = (
        radio[radio["week_date"].notna() & radio["week_date"].ne("")]
        .groupby("week_date")["track"]
        .apply(_join_unique)
        .reset_index(name="radio_top_tracks")
    )

    all_weeks = sorted(set(billboard_week["week_date"]))
    if not all_weeks:
        all_weeks = sorted(set(tv_week["week_date"]) | set(magazines_week["week_date"]) | set(radio_week["week_date"]))

    index_df = pd.DataFrame({"week_date": all_weeks})
    index_df = index_df.merge(
        billboard_week[["week_date", "title", "artist"]].rename(columns={"title": "top_song", "artist": "top_artist"}),
        on="week_date",
        how="left",
    )
    index_df = index_df.merge(tv_week, on="week_date", how="left")
    index_df = index_df.merge(magazines_week, on="week_date", how="left")
    index_df = index_df.merge(radio_week, on="week_date", how="left")
    index_df = index_df.fillna("")
    index_df = index_df[
        ["week_date", "top_song", "top_artist", "tv_programs", "magazine_titles", "radio_top_tracks"]
    ].sort_values(by=["week_date"], kind="stable")

    safe_write_csv(index_df, OUTPUT_PATH)
    log_pipeline(
        script_name="build_cultural_index.py",
        records_collected=len(index_df),
        errors=errors,
        duplicates_removed=0,
        message=f"output_rows={len(index_df)}",
    )
    print(f"records_collected: {len(index_df)}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
