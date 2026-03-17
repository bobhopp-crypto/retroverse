#!/usr/bin/env python3
"""Shared helpers for automatic lineage regeneration after successful runs."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
LINEAGE_SCRIPT = ROOT_DIR / "pipelines" / "support-data" / "scripts" / "generate_data_lineage.py"
SKIP_ENV = "RETROVERSE_SKIP_LINEAGE"


def run_lineage_generation() -> None:
    if os.environ.get(SKIP_ENV):
        return
    subprocess.run([sys.executable, str(LINEAGE_SCRIPT)], check=True, cwd=ROOT_DIR)


def run_with_lineage(main_func: Callable[[], Any]) -> int:
    result = main_func()
    run_lineage_generation()
    return 0 if result is None else int(result)
