#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sqlite3
import sys
import time
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3


ROOT_DIR = Path(__file__).resolve().parents[3]
LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import get_dataset_path


DATA_DIR = ROOT_DIR / "data"
CULTURE_DERIVED_DIR = get_dataset_path("culture_derived_dataset", fallback="data/derived/culture")
RAW_DIR = get_dataset_path("billboard_hot_100", fallback="data/raw/charts/billboard-hot-100.db").parent.parent
CANONICAL_RAW_DIR = RAW_DIR
PROCESSED_DIR = CULTURE_DERIVED_DIR / "processed"
INDEX_DIR = CULTURE_DERIVED_DIR / "index"
LOG_DIR = ROOT_DIR / "pipelines" / "support-data" / "logs"
SCRIPTS_DIR = ROOT_DIR / "pipelines" / "support-data" / "scripts"
LOG_PATH = LOG_DIR / "pipeline.log"
SQLITE_PATH = INDEX_DIR / "cultural_datasets.db"

MONTH_MAP = {
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
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)

RE_DATE_YYYY_MM_DD = re.compile(r"\b((?:19|20)\d{2})[-_/\.](0[1-9]|1[0-2])[-_/\.](0[1-9]|[12]\d|3[01])\b")
RE_DATE_YYYY_MM = re.compile(r"\b((?:19|20)\d{2})[-_/\.](0[1-9]|1[0-2])\b(?![-_/\.]\d)")
RE_DATE_MONTH_DD_YYYY = re.compile(
    rf"\b({MONTH_PATTERN})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,)?\s+((?:19|20)\d{{2}})\b",
    re.IGNORECASE,
)
RE_DATE_MONTH_YYYY = re.compile(rf"\b({MONTH_PATTERN})\s+((?:19|20)\d{{2}})\b", re.IGNORECASE)
RE_DATE_YEAR = re.compile(r"\b((?:19|20)\d{2})\b")


@dataclass
class ParsedDate:
    date: str
    year: int
    month: int


def _ensure_not_canonical_raw_write(path: Path) -> None:
    candidate = path.expanduser().resolve()
    canonical = CANONICAL_RAW_DIR.expanduser().resolve()
    if candidate == canonical or canonical in candidate.parents:
        raise RuntimeError("ERROR: raw-data is read-only (canonical dataset protection)")


def ensure_directories() -> None:
    for directory in (DATA_DIR, RAW_DIR, PROCESSED_DIR, INDEX_DIR, LOG_DIR, SCRIPTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def _next_backup_path(path: Path) -> Path:
    idx = 1
    while True:
        candidate = path.with_name(f"{path.name}.bak.{idx:03d}")
        if not candidate.exists():
            return candidate
        idx += 1


def backup_if_exists(path: Path) -> Path | None:
    _ensure_not_canonical_raw_write(path)
    if not path.exists():
        return None
    backup_path = _next_backup_path(path)
    _ensure_not_canonical_raw_write(backup_path)
    shutil.copy2(path, backup_path)
    return backup_path


def safe_write_csv(df: pd.DataFrame, path: Path) -> None:
    _ensure_not_canonical_raw_write(path)
    ensure_directories()
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_if_exists(path)
    tmp_path = path.with_name(f"{path.name}.tmp")
    _ensure_not_canonical_raw_write(tmp_path)
    df.to_csv(tmp_path, index=False)
    tmp_path.replace(path)


def safe_write_json(payload: Any, path: Path) -> None:
    _ensure_not_canonical_raw_write(path)
    ensure_directories()
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_if_exists(path)
    tmp_path = path.with_name(f"{path.name}.tmp")
    _ensure_not_canonical_raw_write(tmp_path)
    tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(path)


def write_sqlite_table(df: pd.DataFrame, table_name: str, db_path: Path = SQLITE_PATH) -> None:
    _ensure_not_canonical_raw_write(db_path)
    ensure_directories()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        df.to_sql(table_name, connection, if_exists="replace", index=False)


def log_pipeline(script_name: str, records_collected: int, errors: int, duplicates_removed: int, message: str = "") -> None:
    ensure_directories()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not LOG_PATH.exists():
        LOG_PATH.write_text(
            "timestamp,script,records_collected,errors,duplicates_removed,message\n",
            encoding="utf-8",
        )
    safe_message = message.replace("\n", " ").replace('"', "'")
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(
            f'{timestamp},{script_name},{records_collected},{errors},{duplicates_removed},"{safe_message}"\n'
        )


def build_session() -> requests.Session:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()
    session.verify = False
    session.headers.update(
        {
            "User-Agent": "RetroVerseDataPipeline/1.0 (metadata crawler; rate-limited)",
            "Accept": "application/json, text/xml, application/xml, text/plain",
        }
    )
    return session


def fetch_json(
    session: requests.Session,
    url: str,
    params: dict[str, Any] | None = None,
    sleep_seconds: float = 0.25,
    retries: int = 3,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(url, params=params, timeout=45)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict) and payload.get("error"):
                raise RuntimeError(f"API error: {payload['error']}")
            time.sleep(sleep_seconds)
            return payload
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(sleep_seconds * (attempt + 1))
    raise RuntimeError(f"Unable to fetch JSON from {url}: {last_error}") from last_error


def fetch_text(
    session: requests.Session,
    url: str,
    params: dict[str, Any] | None = None,
    sleep_seconds: float = 0.25,
    retries: int = 3,
) -> str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(url, params=params, timeout=45)
            response.raise_for_status()
            text = response.text
            time.sleep(sleep_seconds)
            return text
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(sleep_seconds * (attempt + 1))
    raise RuntimeError(f"Unable to fetch text from {url}: {last_error}") from last_error


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def parse_date_text(value: str) -> ParsedDate | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None

    match = RE_DATE_YYYY_MM_DD.search(text)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        try:
            dt = datetime(year, month, day)
        except ValueError:
            return None
        return ParsedDate(date=dt.strftime("%Y-%m-%d"), year=year, month=month)

    match = RE_DATE_YYYY_MM.search(text)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        try:
            dt = datetime(year, month, 1)
        except ValueError:
            return None
        return ParsedDate(date=dt.strftime("%Y-%m-%d"), year=year, month=month)

    match = RE_DATE_MONTH_DD_YYYY.search(text)
    if match:
        month = MONTH_MAP.get(match.group(1).lower())
        if not month:
            return None
        year = int(match.group(3))
        day = int(match.group(2))
        try:
            dt = datetime(year, month, day)
        except ValueError:
            return None
        return ParsedDate(date=dt.strftime("%Y-%m-%d"), year=year, month=month)

    match = RE_DATE_MONTH_YYYY.search(text)
    if match:
        month = MONTH_MAP.get(match.group(1).lower())
        if not month:
            return None
        year = int(match.group(2))
        dt = datetime(year, month, 1)
        return ParsedDate(date=dt.strftime("%Y-%m-%d"), year=year, month=month)

    match = RE_DATE_YEAR.search(text)
    if match:
        year = int(match.group(1))
        dt = datetime(year, 1, 1)
        return ParsedDate(date=dt.strftime("%Y-%m-%d"), year=year, month=1)

    return None


def choose_best_date(*values: Any) -> ParsedDate | None:
    for value in values:
        parsed = parse_date_text(str(value or ""))
        if parsed:
            return parsed
    return None


def extract_archive_identifier(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        return ""
    cleaned = url.strip()
    marker = "/details/"
    if marker not in cleaned:
        return ""
    tail = cleaned.split(marker, 1)[1]
    return tail.split("/", 1)[0].split("?", 1)[0].strip()


def deterministic_sort(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    valid_columns = [column for column in columns if column in df.columns]
    if not valid_columns:
        return df
    return df.sort_values(by=valid_columns, kind="stable").reset_index(drop=True)
