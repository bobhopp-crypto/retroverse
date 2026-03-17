#!/usr/bin/env python3
"""Orchestrate the controlled single-page rebuild workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from common import WORKFLOW_ROOT
from common import output_path


STEPS = [
    "generate_page_brief.py",
    "qa_page_brief.py",
    "generate_art_direction.py",
    "qa_art_direction.py",
    "generate_page_art_prompt.py",
    "qa_art_prompt.py",
    "build_mock_page.py",
    "qa_layout.py",
]


OUTPUTS = [
    "page_brief.json",
    "page_brief_QA.md",
    "art_direction.json",
    "art_direction_QA.md",
    "art_prompt.txt",
    "art_prompt_QA.md",
    "mock_page.html",
    "layout_QA.md",
]


def run_step(script_name: str, year: int, page_slug: str) -> None:
    script_path = WORKFLOW_ROOT / script_name
    command = [sys.executable, str(script_path), "--year", str(year), "--page-slug", page_slug]
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise SystemExit(f"Step failed: {script_name}")


def main() -> None:
    year = 1978
    page_slug = "movies"

    for script_name in STEPS:
        run_step(script_name, year, page_slug)

    print("SINGLE PAGE REBUILD READY:")
    print("1978 Movies of the Year")
    for suffix in OUTPUTS:
        print(f"- {Path(output_path(year, page_slug, suffix)).as_posix()}")


if __name__ == "__main__":
    main()
