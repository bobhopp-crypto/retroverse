#!/usr/bin/env python3
"""Run the canonical RetroVerse HTML and PDF builders."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the canonical RetroVerse magazine outputs.")
    parser.add_argument("--year", type=int, required=True, help="Issue year to build.")
    return parser.parse_args()


def run_step(script: Path, args: list[str]) -> None:
    cmd = [sys.executable, str(script), *args]
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Build step failed: {' '.join(cmd)}")


def main() -> int:
    args = parse_args()
    year = str(args.year)

    html_builder = PROJECT_ROOT / "scripts" / "build_issue.py"
    pdf_builder = PROJECT_ROOT / "tools" / "magazine_builder" / "build_issue.py"

    try:
        run_step(html_builder, ["--year", year])
        run_step(pdf_builder, ["--year", year])
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Canonical magazine build complete for {year}")
    print(f"HTML index: {PROJECT_ROOT / 'issues' / year / 'layout' / 'index.html'}")
    print(f"PDF: {PROJECT_ROOT / 'output' / f'RetroVerse_{year}.pdf'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
