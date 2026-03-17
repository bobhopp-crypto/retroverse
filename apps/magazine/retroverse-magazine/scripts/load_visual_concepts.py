#!/usr/bin/env python3
"""Helpers for loading page visual concept metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_visual_concepts(year: int) -> dict[int, dict[str, Any]]:
    """Load page visual concepts for an issue year, keyed by page number."""
    path = PROJECT_ROOT / f"issues/{year}/art_direction/page_visual_concepts_{year}.json"
    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("pages", []) if isinstance(payload, dict) else []
    concepts: dict[int, dict[str, Any]] = {}

    if not isinstance(rows, list):
        return concepts

    for row in rows:
        if not isinstance(row, dict):
            continue
        raw_number = row.get("page_number", row.get("page"))
        try:
            page_number = int(raw_number)
        except (TypeError, ValueError):
            continue
        concepts[page_number] = row
    return concepts
