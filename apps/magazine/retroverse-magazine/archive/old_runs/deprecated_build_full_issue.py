#!/usr/bin/env python3
"""Run the full RetroVerse issue pipeline for a given year."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run editorial + art + layout build pipeline.")
    parser.add_argument("--year", default="1978", help="Issue year to build (default: 1978)")
    parser.add_argument(
        "--overwrite-art",
        action="store_true",
        help="Regenerate artwork even if cached files already exist.",
    )
    return parser.parse_args()


def run_step(script_path: Path, year: str, extra_args: list[str] | None = None) -> None:
    cmd = [sys.executable, str(script_path), "--year", year]
    if extra_args:
        cmd.extend(extra_args)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Pipeline step failed: {' '.join(cmd)}")


def main() -> int:
    args = parse_args()
    year = str(args.year)
    script_dir = Path(__file__).resolve().parent

    illustration_args = ["--overwrite"] if args.overwrite_art else []
    marginal_args = ["--overwrite"] if args.overwrite_art else []
    steps = [
        (script_dir / "generate_editorial.py", []),
        (script_dir / "generate_art_prompts.py", []),
        (script_dir / "generate_illustrations.py", illustration_args),
        (script_dir / "generate_marginals.py", marginal_args),
        (script_dir / "build_issue.py", []),
    ]

    try:
        for step, extra_args in steps:
            run_step(step, year, extra_args)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    preview_path = script_dir.parents[0] / "issues" / year / "preview" / "index.html"
    print("Full issue pipeline complete.")
    print(f"Open preview: {preview_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
