#!/usr/bin/env python3
"""Find reusable art assets by tags/prompt text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def tokenize(query: str) -> list[str]:
    return [token.lower() for token in query.replace("_", " ").split() if token.strip()]


def load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.exists():
        return {"assets": []}
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"assets": []}
    if not isinstance(payload, dict):
        return {"assets": []}
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        payload["assets"] = []
    return payload


def score_asset(entry: dict[str, Any], query_tokens: set[str], query_text: str) -> float:
    tags = {str(tag).lower() for tag in entry.get("tags", []) if isinstance(tag, str)}
    prompt = str(entry.get("prompt", "")).lower()
    file_ref = str(entry.get("file", "")).lower()

    score = 0.0
    score += 4.0 * len(query_tokens & tags)
    score += 1.5 * sum(1 for token in query_tokens if token in prompt)
    score += 1.0 * sum(1 for token in query_tokens if token in file_ref)
    if query_text and query_text in prompt:
        score += 5.0
    if file_ref.startswith("art-library/"):
        score += 1.0
    return score


def search_art_assets(query: str, limit: int = 5) -> list[dict[str, Any]]:
    root = project_root()
    payload = load_index(root / "art-library" / "art_index.json")
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        return []

    query_tokens = set(tokenize(query))
    if not query_tokens:
        return []
    query_text = " ".join(tokenize(query))

    scored: list[tuple[float, dict[str, Any]]] = []
    for entry in assets:
        if not isinstance(entry, dict):
            continue
        score = score_asset(entry, query_tokens, query_text)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in scored[:limit]]


def find_art_asset(query: str) -> str | None:
    """Return best-matching asset file path (or None if not found)."""
    matches = search_art_assets(query, limit=1)
    if not matches:
        return None
    return str(matches[0].get("file", ""))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find reusable art assets by search text.")
    parser.add_argument("query", help='Search text, for example: "disco ball"')
    parser.add_argument("--limit", type=int, default=5, help="Maximum results (default: 5)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = search_art_assets(args.query, limit=args.limit)
    if not results:
        print("No matching assets found.")
        return 1

    for idx, entry in enumerate(results, start=1):
        print(
            f"{idx}. {entry.get('file')} | category={entry.get('category')} | "
            f"source_issue={entry.get('source_issue')} | tags={entry.get('tags', [])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
