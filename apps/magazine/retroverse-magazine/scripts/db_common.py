#!/usr/bin/env python3
"""Shared SQLite and YAML helpers for RetroVerse data scripts."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_simple_yaml(text: str) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    current_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            payload[current_key] = {}
            continue
        if current_key and line.startswith("  ") and ":" in line:
            field, value = line.strip().split(":", 1)
            payload[current_key][field.strip()] = parse_scalar(value.strip())
    return payload


def load_data_sources(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        payload = yaml.safe_load(text)
        if isinstance(payload, dict):
            return payload
        return {}
    except Exception:
        return parse_simple_yaml(text)


def resolve_path(project_root: Path, path_text: str) -> Path:
    path = Path(path_text).expanduser()
    if path.is_absolute():
        return path
    return (project_root / path_text).resolve()


def project_relative(project_root: Path, path: Path) -> str:
    absolute = path.resolve()
    try:
        return absolute.relative_to(project_root).as_posix()
    except ValueError:
        return absolute.as_posix()


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [str(row[0]) for row in rows]


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [str(row["name"]) for row in rows]


def sql_year_expression(column: str) -> str:
    # Handles common forms:
    # YYYY-MM-DD, YYYYMMDD, plain YYYY, and mixed text variants with leading year.
    return (
        "CASE "
        f"WHEN {column} IS NULL THEN NULL "
        f"WHEN length(trim(CAST({column} AS TEXT))) >= 4 THEN substr(trim(CAST({column} AS TEXT)), 1, 4) "
        "ELSE NULL END"
    )

