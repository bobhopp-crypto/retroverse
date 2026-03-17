#!/usr/bin/env python3
"""Run multiple illustration-generation passes for a RetroVerse issue."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repeated illustration-generation passes.")
    parser.add_argument("--year", required=True, help="Issue year to generate")
    parser.add_argument("--runs", type=int, default=3, help="Number of full-generation passes to run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "illustration_runs.log"

    with log_path.open("a", encoding="utf-8") as log_handle:
        for run in range(args.runs):
            message = f"Starting run {run + 1} of {args.runs}"
            print(message, flush=True)
            log_handle.write(message + "\n")
            log_handle.flush()

            command = [
                "python3",
                "scripts/generate_illustrations.py",
                "--year",
                str(args.year),
                "--force",
            ]
            subprocess.run(
                command,
                cwd=project_root,
                check=False,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            log_handle.flush()

            if run < args.runs - 1:
                time.sleep(20)

    print("Overnight illustration batch complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
