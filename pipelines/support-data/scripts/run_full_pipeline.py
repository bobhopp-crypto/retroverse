#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

from pipeline_common import CANONICAL_RAW_DIR, INDEX_DIR, PROCESSED_DIR, ensure_directories
from lineage_hook import run_with_lineage


ROOT_DIR = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT_DIR / "pipelines" / "support-data" / "scripts"
RAW_TRANSIENT_SUFFIXES = ("-wal", "-shm", "-journal")

PIPELINE_STEPS = [
    "harvest_magazines.py",
    "harvest_billboard.py",
    "harvest_tv_listings.py",
    "harvest_radio_logs.py",
    "build_cultural_index.py",
]


def run_step(script_name: str) -> None:
    script_path = SCRIPT_DIR / script_name
    print(f"running: {script_name}")
    env = os.environ.copy()
    env["RETROVERSE_SKIP_LINEAGE"] = "1"
    subprocess.run([sys.executable, str(script_path)], check=True, cwd=ROOT_DIR, env=env)


def count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return len(pd.read_csv(path, dtype=str))
    except Exception:  # noqa: BLE001
        return 0


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_raw_data() -> list[tuple[str, int, str]]:
    if not CANONICAL_RAW_DIR.exists():
        return []
    snapshot: list[tuple[str, int, str]] = []
    for file_path in sorted(path for path in CANONICAL_RAW_DIR.rglob("*") if path.is_file()):
        name = file_path.name.lower()
        if name.startswith("."):
            continue
        if any(name.endswith(suffix) for suffix in RAW_TRANSIENT_SUFFIXES):
            continue
        rel = str(file_path.relative_to(ROOT_DIR))
        size = file_path.stat().st_size
        checksum = _file_sha256(file_path)
        snapshot.append((rel, size, checksum))
    return snapshot


def main() -> None:
    ensure_directories()
    raw_before = snapshot_raw_data()

    for step in PIPELINE_STEPS:
        run_step(step)

    raw_after = snapshot_raw_data()
    if raw_before != raw_after:
        raise RuntimeError("ERROR: raw-data is read-only (canonical dataset protection)")

    magazines_collected = count_rows(PROCESSED_DIR / "magazine_issues.csv")
    billboard_rows = count_rows(PROCESSED_DIR / "billboard_hot100.csv")
    tv_listings_rows = count_rows(PROCESSED_DIR / "tv_listings.csv")
    radio_logs_rows = count_rows(PROCESSED_DIR / "radio_airplay.csv")
    cultural_index_rows = count_rows(INDEX_DIR / "cultural_week_index.csv")

    print(f"magazines_collected: {magazines_collected}")
    print(f"billboard_rows: {billboard_rows}")
    print(f"tv_listings_rows: {tv_listings_rows}")
    print(f"radio_logs_rows: {radio_logs_rows}")
    print(f"cultural_index_rows: {cultural_index_rows}")
    print("raw_data_unchanged: true")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
