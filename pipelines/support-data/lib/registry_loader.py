#!/usr/bin/env python3
"""Helpers for loading dataset paths from data/registry/DATA_REGISTRY.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


ROOT_DIR = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT_DIR / "data" / "registry" / "DATA_REGISTRY.yaml"


def _minimal_parse_registry(content: str) -> dict[str, Any]:
    datasets: dict[str, dict[str, Any]] = {}
    in_datasets = False
    current_id: str | None = None
    current_list_key: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        if line == "datasets:":
            in_datasets = True
            continue

        if not in_datasets:
            continue

        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            current_id = line.strip()[:-1]
            datasets[current_id] = {}
            current_list_key = None
            continue

        if current_id and line.startswith("    "):
            stripped = line.strip()
            if current_list_key and stripped.startswith("- "):
                datasets[current_id].setdefault(current_list_key, []).append(stripped[2:].strip().strip("'\""))
                continue

            key, sep, value = stripped.partition(":")
            if sep:
                cleaned_value = value.strip().strip("'\"")
                if cleaned_value:
                    datasets[current_id][key] = cleaned_value
                    current_list_key = None
                else:
                    datasets[current_id][key] = []
                    current_list_key = key

    return {"datasets": datasets}


@lru_cache(maxsize=1)
def load_registry() -> dict[str, Any]:
    """Load and cache the registry payload."""
    if not REGISTRY_PATH.exists():
        return {"datasets": {}}

    content = REGISTRY_PATH.read_text(encoding="utf-8")
    if yaml is None:
        return _minimal_parse_registry(content)

    return yaml.safe_load(content) or {"datasets": {}}


def get_dataset_path(dataset_id: str, fallback: str | Path | None = None) -> Path:
    """
    Resolve a dataset path from the registry.

    If the registry is missing, the dataset entry is absent, or the entry has no path,
    the provided fallback is used instead. Relative fallbacks are resolved from repo root.
    """

    datasets = load_registry().get("datasets", {})
    entry = datasets.get(dataset_id, {})
    path_value = entry.get("path") if isinstance(entry, dict) else None

    if path_value:
        return (ROOT_DIR / str(path_value)).resolve()

    if fallback is None:
        raise KeyError(f"Dataset '{dataset_id}' not found in {REGISTRY_PATH}")

    fallback_path = Path(fallback)
    if not fallback_path.is_absolute():
        fallback_path = ROOT_DIR / fallback_path
    return fallback_path.resolve()
