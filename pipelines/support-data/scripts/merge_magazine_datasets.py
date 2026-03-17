#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd

from lineage_hook import run_with_lineage


MANIFEST_PATH = Path("MAGAZINE_ISSUE_MANIFEST_DATED.csv")
HARVEST_PATH = Path("MAGAZINE_ARCHIVE_HARVEST.csv")
OUTPUT_PATH = Path("MAGAZINE_MASTER_ARCHIVE.csv")

TARGET_COLUMNS = ["magazine", "title", "date", "identifier", "archive_url"]


def extract_archive_identifier(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        return ""

    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    if "archive.org" not in host:
        return ""

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 2 and parts[0].lower() in {"details", "download"}:
        return unquote(parts[1]).strip()
    return ""


def normalize_manifest(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")

    magazine = df["magazine"] if "magazine" in df.columns else pd.Series([""] * len(df))
    if "magazine_title" in df.columns:
        magazine = magazine.where(magazine.str.strip().ne(""), df["magazine_title"])

    title = df["title"] if "title" in df.columns else pd.Series([""] * len(df))
    if "issue_title" in df.columns:
        title = title.where(title.str.strip().ne(""), df["issue_title"])

    date = df["date"] if "date" in df.columns else pd.Series([""] * len(df))
    if "issue_date" in df.columns:
        date = date.where(date.str.strip().ne(""), df["issue_date"])

    identifier = df["identifier"] if "identifier" in df.columns else pd.Series([""] * len(df))

    archive_url = df["archive_url"] if "archive_url" in df.columns else pd.Series([""] * len(df))
    if "issue_url" in df.columns:
        issue_url = df["issue_url"]
        mask = archive_url.str.strip().eq("")
        archive_url = archive_url.where(~mask, issue_url)

    manifest = pd.DataFrame(
        {
            "magazine": magazine.astype(str).str.strip(),
            "title": title.astype(str).str.strip(),
            "date": date.astype(str).str.strip(),
            "identifier": identifier.astype(str).str.strip(),
            "archive_url": archive_url.astype(str).str.strip(),
        }
    )

    # Pull identifiers only from archive.org URLs.
    missing_identifier = manifest["identifier"].eq("")
    manifest.loc[missing_identifier, "identifier"] = (
        manifest.loc[missing_identifier, "archive_url"].apply(extract_archive_identifier)
    )

    # If archive URL is missing but identifier exists, construct canonical Archive URL.
    missing_archive_url = manifest["archive_url"].eq("")
    has_identifier = manifest["identifier"].ne("")
    manifest.loc[missing_archive_url & has_identifier, "archive_url"] = (
        "https://archive.org/details/" + manifest.loc[missing_archive_url & has_identifier, "identifier"]
    )

    return manifest[TARGET_COLUMNS]


def normalize_harvest(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    for column in TARGET_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[TARGET_COLUMNS].copy()


def main() -> None:
    if OUTPUT_PATH.exists():
        raise FileExistsError(f"{OUTPUT_PATH} already exists. Refusing to overwrite.")

    manifest_df = normalize_manifest(MANIFEST_PATH)
    harvest_df = normalize_harvest(HARVEST_PATH)

    merged = pd.concat([manifest_df, harvest_df], ignore_index=True)
    records_before_merge = len(merged)

    with_identifier = merged[merged["identifier"].str.strip().ne("")].copy()
    without_identifier = merged[merged["identifier"].str.strip().eq("")].copy()
    with_identifier = with_identifier.drop_duplicates(subset=["identifier"], keep="first")
    unified = pd.concat([with_identifier, without_identifier], ignore_index=True)

    unified["_mag_sort"] = unified["magazine"].str.lower()
    unified["_date_sort"] = pd.to_datetime(unified["date"], errors="coerce")
    unified = unified.sort_values(
        by=["_mag_sort", "_date_sort", "date", "title", "identifier"],
        kind="stable",
    ).drop(columns=["_mag_sort", "_date_sort"])

    unified.to_csv(OUTPUT_PATH, index=False)

    records_after_merge = len(unified)
    unique_magazines = int(unified["magazine"].replace("", pd.NA).dropna().nunique())
    date_missing_count = int(unified["date"].fillna("").str.strip().eq("").sum())

    print(f"records_before_merge: {records_before_merge}")
    print(f"records_after_merge: {records_after_merge}")
    print(f"unique_magazines: {unique_magazines}")
    print(f"date_missing_count: {date_missing_count}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
