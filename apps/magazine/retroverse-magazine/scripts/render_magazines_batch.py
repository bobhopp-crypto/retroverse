#!/usr/bin/env python3
"""Render a fixed batch of RetroVerse magazine years sequentially."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


YEARS = ["1969", "1978", "1984"]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = PROJECT_ROOT / "logs"


def run_command(log_file, command: list[str]) -> int:
    log_file.write(f"$ {' '.join(command)}\n")
    log_file.flush()

    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    for line in process.stdout:
        sys.stdout.write(line)
        log_file.write(line)

    return_code = process.wait()
    log_file.write(f"\n[exit_code] {return_code}\n\n")
    log_file.flush()
    return return_code


def run_year(year: str) -> int:
    print(f"===== Rendering RetroVerse {year} =====")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"render_{year}.log"
    prompts_path = PROJECT_ROOT / "issues" / year / "art" / "image_prompts.json"

    with log_path.open("w", encoding="utf-8") as log_file:
        if not prompts_path.exists():
            prompt_command = ["python3", "scripts/generate_issue_art_prompts.py", "--year", year]
            print(f"Missing prompts for {year}; generating {prompts_path.relative_to(PROJECT_ROOT)}")
            return_code = run_command(log_file, prompt_command)
            if return_code != 0:
                return return_code

        render_command = ["python3", "scripts/generate_illustrations.py", "--year", year, "--force"]
        return run_command(log_file, render_command)


def main() -> int:
    failures: list[str] = []

    for year in YEARS:
        return_code = run_year(year)
        if return_code != 0:
            failures.append(year)
            print(f"Render failed for {year}. See logs/render_{year}.log")

    print("Render complete for all years.")
    if failures:
        print(f"Failed years: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
