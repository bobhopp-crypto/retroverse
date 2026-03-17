#!/usr/bin/env python3
"""Generate a standalone year deck run and render it with the existing pipeline renderer."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from typing import Any

DEFAULT_YEAR = "1974"
YEAR = DEFAULT_YEAR
RUN_ID = "deck_1974"
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1536
SUIT_NAME = "Hearts"
PROMPT_STYLE = "premium_collectible_card_v1"
CARD_ORDER = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
STYLES = [
    "retro magazine cover illustration",
    "1970s disco nightclub poster",
    "illustrated album sleeve art",
    "vintage advertising illustration",
    "cinematic movie-poster collage",
    "neon nightlife illustration",
]

SINGLE_PROMPT_TEMPLATE_1974 = dedent(
    """
    Create a premium, fully illustrated vertical collectible trading card in 1024x1536 capturing the mood and atmosphere of 1974.

    This must read as one cohesive illustrated artwork, not a flat template, not a baseball card, and not a rigid graphic layout. It should feel cinematic, dramatic, vibrant, richly layered, and visually luxurious.

    Use high-contrast lighting, deep blacks, radiant golden highlights, subtle lens flares, volumetric light beams, warm disco-era glow, rich color separation, and dramatic depth. The atmosphere should pulse with 1970s energy: soulful, radiant, immersive, and alive.

    Main focus:
    "{title}" by {artist}
    Ranked #{rank} song of 1974
    Peak #{peak} • {weeks} weeks on chart

    Create a powerful central scene inspired by the spirit, rhythm, and emotional feel of the song. The performer, or a symbolic interpretation of the song's energy, should dominate the composition with movement, charisma, and strong emotional presence. Make the scene feel alive, dynamic, and cinematic.

    {scene_hint}
    Organically integrate subtle cultural references into the environment:
    – Film: "{film}"
    – TV: "{tv}"
    – Headline: "{headline}"

    These references should appear naturally within the world of the illustration as posters, newspaper headlines, marquees, background screens, signage, props, or environmental details. They must feel embedded in the scene, never placed in rigid boxes, stat panels, or infographic sections.

    Typography must be fully integrated into the illustration in elegant, dimensional gold or cream lettering, styled as part of the artwork itself:
    – "#{rank} Song of 1974"
    – "{title}"
    – "{artist}"
    – "Peak #{peak} • {weeks} Weeks on Chart"
    – "1974"

    Include an ornamental vintage border that feels illustrated into the composition itself: dimensional, glowing, premium, detailed, and cohesive with the surrounding art. It should feel handcrafted and luxurious, not flat, pasted-on, or templated.

    In the upper right corner only, include a small, subtle playing card marking:
    "{rank_symbol} of {suit}"
    This should be refined, elegant, and unobtrusive.

    The final image must feel premium, cinematic, emotionally immersive, nostalgic, and highly collectible, like a high-end illustrated time capsule of 1974.
    """
).strip()

COURT_PROMPT_TEMPLATE_1974 = dedent(
    """
    Create a premium, fully illustrated vertical collectible trading card in 1024x1536 capturing the mood and atmosphere of 1974.

    This must read as one cohesive illustrated artwork, not a flat template, not a baseball card, and not a rigid graphic layout. It should feel cinematic, dramatic, vibrant, richly layered, and visually luxurious.

    Use high-contrast lighting, deep blacks, radiant golden highlights, subtle lens flares, volumetric light beams, warm disco-era glow, rich color separation, and dramatic depth. The atmosphere should pulse with 1970s energy: soulful, radiant, immersive, and alive.

    Main focus:
    "{rank_symbol} of {suit}"
    Represents ranks #{rank_start} through #{rank_end} songs of 1974

    Build a dramatic ensemble composition inspired by the collective energy of these songs. The scene should feel like a premium year-end cultural montage from 1974 with motion, layered symbolism, and cinematic depth. Let the imagery feel alive and interconnected rather than segmented.

    Featured songs to weave into the artwork's mood and visual storytelling:
    {song_list}

    Render an integrated two-column list of these song titles as part of the illustrated design itself, in refined gold or cream typography that feels naturally embedded in the composition rather than placed in rigid panels.

    Typography must be fully integrated into the illustration in elegant, dimensional gold or cream lettering, styled as part of the artwork itself:
    – "{rank_symbol} of {suit}"
    – "{rank_start}-{rank_end} Songs of 1974"
    – "1974"

    Include an ornamental vintage border that feels illustrated into the composition itself: dimensional, glowing, premium, detailed, and cohesive with the surrounding art. It should feel handcrafted and luxurious, not flat, pasted-on, or templated.

    In the upper right corner only, include a small, subtle playing card marking:
    "{rank_symbol} of {suit}"
    Keep this refined, elegant, and unobtrusive.

    The final image must feel premium, cinematic, emotionally immersive, nostalgic, and highly collectible, like a high-end illustrated time capsule of 1974.
    """
).strip()

SINGLE_SCENE_HINTS_1974 = {
    ("Dancing Machine", "Jackson 5"): (
        "Emphasize a vibrant disco dancefloor, mirrored stage lights, rhythmic movement, and kinetic club energy "
        "without making the composition feel chaotic."
    ),
}

SINGLE_PROMPT_OVERRIDES_1974 = {
    ("Bennie And The Jets", "Elton John"): dedent(
        """
        Create a premium, fully illustrated vertical collectible trading card in 1024x1536 capturing the mood and atmosphere of 1974.

        This must read as one cohesive illustrated artwork, not a flat template, not a baseball card, and not a rigid graphic layout. It should feel cinematic, dramatic, vibrant, richly layered, and visually luxurious.

        Use high-contrast lighting, deep blacks, radiant golden highlights, subtle lens flares, volumetric light beams, warm stage glow, rich color separation, and dramatic depth. The atmosphere should pulse with 1970s glam-rock energy: electric, theatrical, immersive, and alive.

        Main focus:
        "Bennie And The Jets" by Elton John
        Ranked #3 song of 1974
        Peak #1 • 18 weeks on chart

        Create a dramatic central scene built around a stylized glam-rock concert environment: a grand piano silhouette, chrome stage lights, amplified crowd energy, suspended haze, and kinetic motion. Favor a performance-driven symbolic stage tableau over intimate close-up imagery. Keep all figures non-suggestive, performance-focused, and fully clothed.

        Organically integrate subtle cultural references into the environment:
        – Film: "Young Frankenstein"
        – TV: "Chico and the Man"
        – Headline: "Two members of the Japanese Red Army and two members of the Popular Front for the Liberation of Palestine made a failed attempt to blow up oil tanks at the Shell oil refinery complex on Pulau Bukom at Singapore."

        These references should appear naturally within the world of the illustration as posters, newspaper headlines, marquees, background screens, signage, props, or environmental details. They must feel embedded in the scene, never placed in rigid boxes, stat panels, or infographic sections.

        Typography must be fully integrated into the illustration in elegant, dimensional gold or cream lettering, styled as part of the artwork itself:
        – "#3 Song of 1974"
        – "Bennie And The Jets"
        – "Elton John"
        – "Peak #1 • 18 Weeks on Chart"
        – "1974"

        Include an ornamental vintage border that feels illustrated into the composition itself: dimensional, glowing, premium, detailed, and cohesive with the surrounding art. It should feel handcrafted and luxurious, not flat, pasted-on, or templated.

        In the upper right corner only, include a small, subtle playing card marking:
        "3 of Hearts"
        This should be refined, elegant, and unobtrusive.

        The final image must feel premium, cinematic, emotionally immersive, nostalgic, and highly collectible, like a high-end illustrated time capsule of 1974.
        """
    ).strip(),
}

SINGLE_PROMPT_TEMPLATE_1975 = dedent(
    """
    Create a premium collectible vertical trading card illustration in 1024x1536 capturing the mood and atmosphere of 1975.

    The visual style must match a high-end RetroVerse 1974 deck aesthetic: an ornate integrated vintage border, rich blacks, cinematic lighting, glowing highlights, textured depth, and dramatic contrast. This is not a baseball card layout, not a rigid infographic, and not a flat template. It must feel like a cinematic time capsule illustration rendered as one cohesive artwork.

    Apply a subtle emerald-gold atmospheric wash across the lighting and highlights to distinguish the 1975 Clubs suit. The glow should feel deep, elegant, and premium, never neon green, but a refined emerald tone infused into warm golden light.

    Main focus:
    "{title}" by {artist}
    Ranked #{rank} song of 1975
    Peak #{peak} • {weeks} weeks on chart

    Create a dramatic central scene inspired by the emotional tone and spirit of the song. The performer should be evocative rather than an exact celebrity likeness, but clearly inspired by the era. Use volumetric stage lighting, layered depth, subtle sparkle, rich shadows, and cinematic focus. The composition should feel alive, immersive, and premium.

    {scene_hint}
    Organically integrate subtle environmental references to 1975 culture:
    – Film of the year: "{film}"
    – TV program of the year: "{tv}"
    – Headline: "{headline}"

    These references should appear naturally in the background as posters, marquees, newspapers, television screens, signage, props, or environmental details. They must be embedded in the illustrated world, never separated into rigid panels, boxes, stats sections, or infographic blocks.

    Render integrated premium typography as part of the artwork itself in dimensional cream, gold, or softly emerald-tinted metallic lettering for:
    – "{title}"
    – "{artist}"
    – "# {rank} Song of 1975"
    – "Peak #{peak} • {weeks} Weeks on Chart"
    – "1975"

    The typography should feel elegant, collectible, and fully woven into the illustration rather than pasted on top.

    Include an ornate border that feels illustrated into the composition itself: vintage, dimensional, glowing, premium, and cohesive with the surrounding art. It should match the RetroVerse 1974 deck's luxury aesthetic while subtly carrying the emerald-toned Clubs identity.

    In the upper right corner only, include a small, refined playing card indicator:
    "{rank_symbol} of {suit}"
    Keep this minimal, elegant, and unobtrusive.

    The final result must feel collectible, cinematic, cohesive, emotionally immersive, and fully consistent with the premium RetroVerse 1974 deck aesthetic, but distinguished by an emerald-toned atmosphere for the Clubs suit.
    """
).strip()

COURT_PROMPT_TEMPLATE_1975 = dedent(
    """
    Create a premium collectible vertical trading card illustration in 1024x1536 capturing the mood and atmosphere of 1975.

    The visual style must match a high-end RetroVerse 1974 deck aesthetic: an ornate integrated vintage border, rich blacks, cinematic lighting, glowing highlights, textured depth, and dramatic contrast. This is not a baseball card layout, not a rigid infographic, and not a flat template. It must feel like a cinematic time capsule illustration rendered as one cohesive artwork.

    Apply a subtle emerald-gold atmospheric wash across the lighting and highlights to distinguish the 1975 Clubs suit. The glow should feel deep, elegant, and premium, never neon green, but a refined emerald tone infused into warm golden light.

    Main focus:
    "{rank_symbol} of {suit}"
    Represents ranks #{rank_start} through #{rank_end} songs of 1975

    Build a dramatic ensemble composition inspired by the collective energy of these songs. The scene should feel like a premium year-end cultural montage from 1975 with motion, layered symbolism, and cinematic depth. Let the imagery feel alive and interconnected rather than segmented.

    Featured songs to weave into the artwork's mood and visual storytelling:
    {song_list}

    Render an integrated two-column list of these song titles as part of the illustrated design itself, in refined cream, gold, or softly emerald-tinted metallic typography that feels naturally embedded in the composition rather than placed in rigid panels.

    Typography must be fully integrated into the illustration in elegant, dimensional lettering styled as part of the artwork itself:
    – "{rank_symbol} of {suit}"
    – "{rank_start}-{rank_end} Songs of 1975"
    – "1975"

    Include an ornate border that feels illustrated into the composition itself: vintage, dimensional, glowing, premium, and cohesive with the surrounding art. It should match the RetroVerse 1974 deck's luxury aesthetic while subtly carrying the emerald-toned Clubs identity.

    In the upper right corner only, include a small, refined playing card indicator:
    "{rank_symbol} of {suit}"
    Keep this minimal, elegant, and unobtrusive.

    The final result must feel collectible, cinematic, cohesive, emotionally immersive, and fully consistent with the premium RetroVerse 1974 deck aesthetic, but distinguished by an emerald-toned atmosphere for the Clubs suit.
    """
).strip()

SINGLE_SCENE_HINTS_1975: dict[tuple[str, str], str] = {}
SINGLE_PROMPT_OVERRIDES_1975: dict[tuple[str, str], str] = {
    ("Shining Star", "Earth, Wind"): dedent(
        """
        Create a premium collectible vertical trading card illustration in 1024x1536 capturing the mood and atmosphere of 1975.

        The visual style must match a high-end RetroVerse 1974 deck aesthetic: an ornate integrated vintage border, rich blacks, cinematic lighting, glowing highlights, textured depth, and dramatic contrast. This is not a baseball card layout, not a rigid infographic, and not a flat template. It must feel like a cinematic time capsule illustration rendered as one cohesive artwork.

        Apply a subtle emerald-gold atmospheric wash across the lighting and highlights to distinguish the 1975 Clubs suit. The glow should feel deep, elegant, and premium, never neon green, but a refined emerald tone infused into warm golden light.

        Main focus:
        "Shining Star" by Earth, Wind
        Ranked #8 song of 1975
        Peak #1 • 20 weeks on chart

        Create a dramatic central scene inspired by uplift, confidence, and radiant stage presence. Use a symbolic performance tableau: a luminous stage, silhouetted musicians, mirrored lights, celestial motifs, and rich layered depth. Keep the composition performance-focused and abstractly celebratory rather than intimate or sensual.

        Organically integrate subtle environmental references to 1975 culture:
        – Film of the year: "The Return of the Pink Panther"
        – TV program of the year: "All in the Family"
        – Headline: "August 15 – President of Bangladesh Sheikh Mujibur Rahman is assassinated during a military coup."

        These references should appear naturally in the background as posters, marquees, newspapers, television screens, signage, props, or environmental details. They must be embedded in the illustrated world, never separated into rigid panels, boxes, stats sections, or infographic blocks.

        Render integrated premium typography as part of the artwork itself in dimensional cream, gold, or softly emerald-tinted metallic lettering for:
        – "Shining Star"
        – "Earth, Wind"
        – "# 8 Song of 1975"
        – "Peak #1 • 20 Weeks on Chart"
        – "1975"

        The typography should feel elegant, collectible, and fully woven into the illustration rather than pasted on top.

        Include an ornate border that feels illustrated into the composition itself: vintage, dimensional, glowing, premium, and cohesive with the surrounding art. It should match the RetroVerse 1974 deck's luxury aesthetic while subtly carrying the emerald-toned Clubs identity.

        In the upper right corner only, include a small, refined playing card indicator:
        "8 of Clubs"
        Keep this minimal, elegant, and unobtrusive.

        The final result must feel collectible, cinematic, cohesive, emotionally immersive, and fully consistent with the premium RetroVerse 1974 deck aesthetic, but distinguished by an emerald-toned atmosphere for the Clubs suit.
        """
    ).strip(),
}

SINGLE_PROMPT_TEMPLATE = SINGLE_PROMPT_TEMPLATE_1974
COURT_PROMPT_TEMPLATE = COURT_PROMPT_TEMPLATE_1974
SINGLE_SCENE_HINTS = dict(SINGLE_SCENE_HINTS_1974)
SINGLE_PROMPT_OVERRIDES = dict(SINGLE_PROMPT_OVERRIDES_1974)

YEAR_SETTINGS = {
    "1974": {
        "run_id": "deck_1974",
        "suit_name": "Hearts",
        "prompt_style": "premium_collectible_card_v1",
        "single_prompt_template": SINGLE_PROMPT_TEMPLATE_1974,
        "court_prompt_template": COURT_PROMPT_TEMPLATE_1974,
        "single_scene_hints": SINGLE_SCENE_HINTS_1974,
        "single_prompt_overrides": SINGLE_PROMPT_OVERRIDES_1974,
    },
    "1975": {
        "run_id": "deck_1975",
        "suit_name": "Clubs",
        "prompt_style": "premium_collectible_card_v1_1975_clubs",
        "single_prompt_template": SINGLE_PROMPT_TEMPLATE_1975,
        "court_prompt_template": COURT_PROMPT_TEMPLATE_1975,
        "single_scene_hints": SINGLE_SCENE_HINTS_1975,
        "single_prompt_overrides": SINGLE_PROMPT_OVERRIDES_1975,
    },
}


def apply_year_settings(year: str) -> None:
    global YEAR, RUN_ID, SUIT_NAME, PROMPT_STYLE
    global SINGLE_PROMPT_TEMPLATE, COURT_PROMPT_TEMPLATE
    global SINGLE_SCENE_HINTS, SINGLE_PROMPT_OVERRIDES

    config = YEAR_SETTINGS.get(year)
    if config is None:
        raise ValueError(f"Unsupported year: {year}")

    YEAR = year
    RUN_ID = str(config["run_id"])
    SUIT_NAME = str(config["suit_name"])
    PROMPT_STYLE = str(config["prompt_style"])
    SINGLE_PROMPT_TEMPLATE = str(config["single_prompt_template"])
    COURT_PROMPT_TEMPLATE = str(config["court_prompt_template"])
    SINGLE_SCENE_HINTS = dict(config["single_scene_hints"])
    SINGLE_PROMPT_OVERRIDES = dict(config["single_prompt_overrides"])


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_year_data(master_json_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    with master_json_path.open("r", encoding="utf-8") as handle:
        master = json.load(handle)

    year_data = master.get(YEAR)
    if not isinstance(year_data, dict):
        raise ValueError(f"Year {YEAR} not found in {master_json_path}")

    top_40 = year_data.get("top_40")
    culture = year_data.get("culture")
    if not isinstance(top_40, list):
        raise ValueError(f"top_40 missing for year {YEAR}")
    if len(top_40) < 40:
        raise ValueError(f"Expected 40 songs for {YEAR}, found {len(top_40)}")
    if not isinstance(culture, dict):
        raise ValueError(f"culture missing for year {YEAR}")
    return top_40[:40], culture


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def image_name(card_label: str) -> str:
    prefix = f"{YEAR}_deck"
    if card_label.isdigit() and len(card_label) == 1:
        return f"{prefix}_0{card_label}.png"
    return f"{prefix}_{card_label}.png"


def single_card_label(rank: int) -> str:
    return "A" if rank == 1 else str(rank)


def normalize_line(value: Any) -> str:
    return " ".join(str(value).split())


def headline_text(raw_headline: Any) -> str:
    if isinstance(raw_headline, dict):
        headline = raw_headline.get("event", "")
    else:
        headline = raw_headline
    return normalize_line(headline)


def style_for_card(index: int, rv_rank: int | None = None) -> str:
    if rv_rank == 1:
        return "retro cultural collage poster"
    return STYLES[index % len(STYLES)]


def culture_snapshot(culture: dict[str, Any], limit: int = 3) -> tuple[list[str], list[str], list[str]]:
    films = [normalize_line(item) for item in culture.get("films", []) if normalize_line(item)]
    tv_items = [normalize_line(item) for item in culture.get("tv", []) if normalize_line(item)]
    headlines = [headline_text(item) for item in culture.get("headlines", []) if headline_text(item)]
    return films[:limit], tv_items[:limit], headlines[:limit]


def build_scene_hint(title: str, artist: str) -> str:
    hint = SINGLE_SCENE_HINTS.get((title, artist))
    if not hint:
        return ""
    return f"Additional scene cue:\n{hint}\n"


def build_single_prompt(song: dict[str, Any], culture: dict[str, Any], index: int) -> str:
    films = culture.get("films") or []
    tv_programs = culture.get("tv") or []
    headlines = culture.get("headlines") or []

    title = normalize_line(song["title"])
    artist = normalize_line(song["artist"])
    override = SINGLE_PROMPT_OVERRIDES.get((title, artist))
    if override:
        return override

    rank = int(song["rv_rank"])
    peak = int(song["peak_rank"])
    weeks = int(song["weeks_on_chart"])
    film = normalize_line(films[index]) if index < len(films) else "Unavailable"
    tv = normalize_line(tv_programs[index]) if index < len(tv_programs) else "Unavailable"
    headline = headline_text(headlines[index]) if index < len(headlines) else "Unavailable"
    style = style_for_card(index, rv_rank=rank)

    if rank == 1:
        films_top, tv_top, headlines_top = culture_snapshot(culture, limit=3)
        return dedent(
            f"""
            {style}

            Stylized illustration for the year {YEAR}

            Song: "{title}" by {artist}

            Build an ace-card year portrait that represents the full cultural atmosphere of {YEAR}.
            Include a layered cultural collage using these references:
            Films: {", ".join(films_top) if films_top else "Unavailable"}
            TV: {", ".join(tv_top) if tv_top else "Unavailable"}
            Headlines: {" | ".join(headlines_top) if headlines_top else "Unavailable"}

            Visual cues inspired by the era, including fashion, nightlife, vinyl records, and retro typography.
            Avoid photorealism.
            Use bold poster-style composition.
            Clear readable layout suitable for a playing card.

            Rank context: #{rank} song of {YEAR} | Peak #{peak} | {weeks} weeks on chart.
            """
        ).strip()

    return dedent(
        f"""
        {style}

        Stylized illustration for the year {YEAR}

        Song: "{title}" by {artist}

        Include rank context: #{rank} song of {YEAR} | Peak #{peak} | {weeks} weeks on chart.
        Optional cultural accents for atmosphere:
        Film reference: {film}
        TV reference: {tv}
        Headline reference: {headline}

        Visual cues inspired by the era, including fashion, nightlife, vinyl records, and retro typography.
        Avoid photorealism.
        Use bold poster-style composition.
        Clear readable layout suitable for a playing card.
        """
    ).strip()


def build_song_list_block(songs: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"– #{int(song['rv_rank'])}: \"{normalize_line(song['title'])}\" by {normalize_line(song['artist'])}"
        for song in songs
    )


def build_court_prompt(label: str, songs: list[dict[str, Any]], index: int) -> str:
    rank_start = int(songs[0]["rv_rank"])
    rank_end = int(songs[-1]["rv_rank"])
    style = style_for_card(index)
    return dedent(
        f"""
        {style}

        Stylized illustration for the year {YEAR}

        Song block: "{label} card" covering ranks #{rank_start} to #{rank_end}

        Build a composite collage inspired by this song range:
        {build_song_list_block(songs)}

        Visual cues inspired by the era, including fashion, nightlife, vinyl records, and retro typography.
        Avoid photorealism.
        Use bold poster-style composition.
        Clear readable layout suitable for a playing card.
        """
    ).strip()


def normalize_card_label(label: str) -> str:
    raw = label.strip().upper()
    if raw in {"A", "J", "Q", "K"}:
        return raw
    if raw.isdigit():
        return str(int(raw))
    raise ValueError(f"Unsupported card label: {label}")


def build_prompt_records(
    run_id: str,
    output_dir: Path,
    logs_dir: Path,
    top_40: list[dict[str, Any]],
    culture: dict[str, Any],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    films = culture.get("films") or []
    tv_programs = culture.get("tv") or []
    headlines = culture.get("headlines") or []

    for index, song in enumerate(top_40[:10]):
        rv_rank = int(song["rv_rank"])
        label = single_card_label(rv_rank)
        title = str(song["title"])
        artist = str(song["artist"])
        basename = f"{YEAR}_deck_{label}_{slugify(title)}__{slugify(artist)}"

        records.append(
            {
                "run_id": run_id,
                "year": int(YEAR),
                "card_label": label,
                "prompt_style": PROMPT_STYLE,
                "rank": rv_rank,
                "rv_rank_start": rv_rank,
                "rv_rank_end": rv_rank,
                "rank_symbol": label,
                "suit": SUIT_NAME,
                "title": title,
                "artist": artist,
                "peak_rank": int(song["peak_rank"]),
                "weeks_on_chart": int(song["weeks_on_chart"]),
                "film": str(films[index]) if index < len(films) else "",
                "tv": str(tv_programs[index]) if index < len(tv_programs) else "",
                "headline": headline_text(headlines[index]) if index < len(headlines) else "",
                "prompt_text": build_single_prompt(song, culture, index),
                "basename": basename,
                "image_path": str(output_dir / image_name(label)),
                "log_path": str(logs_dir / f"{basename}.render.json"),
            }
        )

    court_groups = {
        "J": top_40[10:20],
        "Q": top_40[20:30],
        "K": top_40[30:40],
    }

    for label, songs in court_groups.items():
        start_rank = int(songs[0]["rv_rank"])
        end_rank = int(songs[-1]["rv_rank"])
        card_index = CARD_ORDER.index(label)
        basename = f"{YEAR}_deck_{label}_ranks_{start_rank:02d}_{end_rank:02d}"

        records.append(
            {
                "run_id": run_id,
                "year": int(YEAR),
                "card_label": label,
                "prompt_style": PROMPT_STYLE,
                "rank": start_rank,
                "rv_rank_start": start_rank,
                "rv_rank_end": end_rank,
                "rank_symbol": label,
                "suit": SUIT_NAME,
                "titles": [str(song["title"]) for song in songs],
                "artists": [str(song["artist"]) for song in songs],
                "prompt_text": build_court_prompt(label, songs, card_index),
                "basename": basename,
                "image_path": str(output_dir / image_name(label)),
                "log_path": str(logs_dir / f"{basename}.render.json"),
            }
        )

    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_render_config(path: Path, run_id: str, *, skip_if_image_exists: bool = True) -> None:
    config_text = (
        f"run_id: {run_id}\n"
        "runs_root: runs\n"
        "image:\n"
        f"  width: {IMAGE_WIDTH}\n"
        f"  height: {IMAGE_HEIGHT}\n"
        "render:\n"
        "  provider: openai\n"
        "  model: gpt-image-1\n"
        "  concurrency: 1\n"
        "  timeout_seconds: 180\n"
        "resume:\n"
        f"  skip_if_image_exists: {'true' if skip_if_image_exists else 'false'}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config_text, encoding="utf-8")


def load_openai_api_key(root: Path) -> None:
    if os.getenv("OPENAI_API_KEY"):
        return

    env_candidates = [
        root / "public" / YEAR / ".env",
        root / "public" / "1974" / ".env",
        root / ".env",
    ]
    for env_path in env_candidates:
        if not env_path.exists():
            continue

        with env_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].strip()
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() != "OPENAI_API_KEY":
                    continue
                cleaned = value.strip().strip('"').strip("'")
                if cleaned:
                    os.environ["OPENAI_API_KEY"] = cleaned
                    return


def render_with_existing_pipeline(config_path: Path) -> None:
    renderer_path = repo_root() / "retroverse-1974" / "pipeline" / "scripts" / "rv_render_images.py"
    if not renderer_path.exists():
        raise FileNotFoundError(f"Renderer not found: {renderer_path}")

    subprocess.run(
        [sys.executable, str(renderer_path), "--config", str(config_path)],
        check=True,
        cwd=repo_root(),
    )


def parse_cli_args(argv: list[str]) -> tuple[str, bool, list[str] | None]:
    force_flag = "--force-rerender"
    only_prefix = "--only-labels="
    year_prefix = "--year="
    selected_year = DEFAULT_YEAR
    force_rerender = False
    only_labels: list[str] | None = None
    unknown: list[str] = []
    index = 0

    while index < len(argv):
        arg = argv[index]
        if arg == force_flag:
            force_rerender = True
            index += 1
            continue
        if arg == "--year":
            if index + 1 >= len(argv):
                raise ValueError("--year requires a value")
            selected_year = argv[index + 1].strip()
            index += 2
            continue
        if arg.startswith(year_prefix):
            selected_year = arg[len(year_prefix) :].strip()
            if not selected_year:
                raise ValueError("--year requires a value")
            index += 1
            continue
        if arg.startswith(only_prefix):
            raw_values = arg[len(only_prefix) :]
            selected = [normalize_card_label(value) for value in raw_values.split(",") if value.strip()]
            if not selected:
                raise ValueError("--only-labels requires at least one label")
            deduped: list[str] = []
            for label in selected:
                if label not in deduped:
                    deduped.append(label)
            only_labels = deduped
            index += 1
            continue
        unknown.append(arg)
        index += 1

    if unknown:
        raise ValueError(f"Unsupported arguments: {' '.join(unknown)}")
    return selected_year, force_rerender, only_labels


def main() -> None:
    selected_year, force_rerender, only_labels = parse_cli_args(sys.argv[1:])
    apply_year_settings(selected_year)
    root = repo_root()
    master_json_path = root / "retroverse-output" / "retroverse_year_master_1958_2024.json"
    active_run_id = RUN_ID
    if only_labels:
        active_run_id = f"{RUN_ID}_partial_{'-'.join(only_labels)}"
    run_dir = root / "runs" / active_run_id
    prompts_path = run_dir / "prompts.jsonl"
    config_path = run_dir / "render_config.yaml"
    output_dir = (root / "retroverse-output" / "decks" / YEAR).resolve()
    logs_dir = run_dir / "logs"

    top_40, culture = load_year_data(master_json_path)
    prompt_records = build_prompt_records(active_run_id, output_dir, logs_dir, top_40, culture)
    if only_labels:
        allowed = set(only_labels)
        prompt_records = [record for record in prompt_records if str(record["card_label"]) in allowed]
        if not prompt_records:
            raise ValueError(f"No prompt records matched labels: {', '.join(only_labels)}")

    write_jsonl(prompts_path, prompt_records)
    write_render_config(config_path, active_run_id, skip_if_image_exists=not force_rerender)
    load_openai_api_key(root)

    print(f"Wrote {len(prompt_records)} prompt records to {prompts_path}")
    if force_rerender:
        print("Force rerender enabled; existing images will be overwritten.")
    if only_labels:
        print(f"Targeted render labels: {', '.join(only_labels)}")
    print(f"Rendering images into {output_dir}")
    render_with_existing_pipeline(config_path)


if __name__ == "__main__":
    main()
