#!/usr/bin/env python3
"""Generate RetroVerse art prompt payloads from editorial data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EASTER_EGG_RULE = (
    'Hide the word "RetroVerse" subtly somewhere in the illustration as an Easter egg.'
)


class PromptBuildError(Exception):
    """Raised when prompt generation inputs are missing or malformed."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PromptBuildError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PromptBuildError(f"Invalid JSON in {path}: {exc}") from exc


def add_easter_egg_rule(prompt: str) -> str:
    clean_prompt = prompt.strip()
    if EASTER_EGG_RULE in clean_prompt:
        return clean_prompt
    clean_prompt = clean_prompt.rstrip(". ")
    return f"{clean_prompt}. {EASTER_EGG_RULE}"


def build_feature_prompt(year: str, headline: str, deck: str) -> str:
    return add_easter_egg_rule(
        f"{year} cultural magazine illustration, bustling night street with cinema marquee, disco glow, "
        f"record store windows, hand-drawn ink lines with watercolor textures, editorial print style; "
        f"story focus: {headline}. Subtheme: {deck}"
    )


def build_collage_prompts(year: str, tiles: list[Any]) -> list[str]:
    prompts: list[str] = []
    for item in tiles[:9]:
        prompts.append(
            add_easter_egg_rule(
                f"{year} artifact illustration, {str(item).lower()}, hand-drawn editorial ink and watercolor, "
                "slightly worn paper texture, magazine collage panel"
            )
        )
    while len(prompts) < 9:
        index = len(prompts) + 1
        prompts.append(add_easter_egg_rule(f"{year} retro collage artifact #{index}, hand-drawn magazine illustration, ink and watercolor"))
    return prompts


def build_comic_prompts(year: str, panels: list[Any]) -> list[str]:
    prompts: list[str] = []
    for panel in panels[:6]:
        if isinstance(panel, dict):
            scene = panel.get("scene", "weekend culture scene")
        else:
            scene = str(panel)
        prompts.append(
            add_easter_egg_rule(
                f"{year} narrative comic panel, {scene}, expressive linework, limited color wash, "
                "retro humor magazine style"
            )
        )
    while len(prompts) < 6:
        index = len(prompts) + 1
        prompts.append(add_easter_egg_rule(f"{year} narrative comic panel #{index}, city nightlife sequence, retro editorial art"))
    return prompts


def build_prompt_payload(year: str, editorial: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(editorial, dict):
        raise PromptBuildError("editorial.json root must be an object.")

    feature = editorial.get("feature_story", {})
    collage = editorial.get("collage", {})
    comic = editorial.get("comic", {})

    headline = str(feature.get("headline", "1978 culture feature"))
    deck = str(feature.get("deck", "music, film, television, and street culture in motion"))
    tiles = collage.get("tiles", [])
    panels = comic.get("panels", [])

    if not isinstance(tiles, list):
        tiles = []
    if not isinstance(panels, list):
        panels = []

    feature_prompt = build_feature_prompt(year, headline, deck)
    collage_prompts = build_collage_prompts(year, tiles)
    comic_prompts = build_comic_prompts(year, panels)

    # Keep compatibility keys so existing page configs can still look up specific prompt labels.
    return {
        "feature_hero": feature_prompt,
        "collage_tiles": collage_prompts,
        "comic_panels": comic_prompts,
        "cover": add_easter_egg_rule(
            f"{year} magazine cover illustration, neon city nightlife, disco marquee, arcade glow, hand-painted editorial style"
        ),
        "feature_cinema": add_easter_egg_rule(
            f"{year} movie theater marquee with crowd line, rainy sidewalk reflections, retro ink and watercolor style"
        ),
        "parody_console": add_easter_egg_rule(
            f"{year} satirical gadget advertisement art, chrome control panel, glowing buttons, exaggerated retro illustration"
        ),
        "collage_items": collage_prompts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RetroVerse art prompts from editorial data.")
    parser.add_argument("--year", default="1978", help="Issue year to generate (default: 1978)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    year = str(args.year)
    year_dir = root / "issues" / year
    editorial_path = year_dir / "data" / "editorial.json"
    output_path = year_dir / "art" / "image_prompts.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        editorial = load_json(editorial_path)
        prompt_payload = build_prompt_payload(year, editorial)
    except PromptBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    output_path.write_text(json.dumps(prompt_payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote image prompts: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
