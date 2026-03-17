#!/usr/bin/env python3
"""Build the 1976 Diamonds and 1977 Spades RetroVerse card sets in one run."""

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from typing import Any

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = ROOT / "retroverse-1974" / "pipeline" / "scripts" / "rv_render_images.py"
PREMISE_SCRIPT_DIR = ROOT / "pipeline" / "scripts"

if str(PREMISE_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(PREMISE_SCRIPT_DIR))

from song_premise_generator import generate_song_premise

# Always load the RetroVerse root .env file
ENV_PATH = os.path.expanduser("~/Sites/retroverse/.env")
load_dotenv(ENV_PATH)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Ensure ~/Sites/retroverse/.env exists and contains the API key."
    )

CARD_WIDTH = 1024
CARD_HEIGHT = 1536
ART_CUTOUT_BOX = (156, 164, 868, 1012)
TITLE_BOX = (148, 1058, 876, 1138)
ARTIST_BOX = (192, 1148, 832, 1194)
RANK_LINE_BOX = (224, 78, 800, 126)
STATS_BOX = (228, 1204, 796, 1242)
FOOTER_BOX = (380, 1460, 644, 1498)
LIST_BOX = (178, 274, 846, 988)

OUTER_MARGIN = 24
INNER_MARGIN = 52
CORNER_BOX_LEFT = (50, 52, 130, 148)
CORNER_BOX_RIGHT = (894, 52, 974, 148)

FONT_CANDIDATES = {
    "regular": [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Baskerville.ttc",
        "/Library/Fonts/Times New Roman.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "bold": [
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/Library/Fonts/Times New Roman Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ],
}

RESAMPLE = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
STANDARD_CARD_ORDER = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
EDITORIAL_1978_CARD_ORDER = STANDARD_CARD_ORDER + ["R1", "R2", "R3", "R4"]
CARD_ORDER = EDITORIAL_1978_CARD_ORDER
COURT_RANGES = {"J": (11, 20), "Q": (21, 30), "K": (31, 40)}
STYLES = [
    "retro magazine cover illustration",
    "1970s disco nightclub poster",
    "illustrated album sleeve art",
    "vintage advertising illustration",
    "cinematic movie-poster collage",
    "neon nightlife illustration",
]

YEAR_CONFIGS: dict[str, dict[str, Any]] = {
    "1976": {
        "suit_name": "Diamonds",
        "suit_symbol": "\u2666",
        "run_id": "deck_1976_diamonds",
        "top_json": ROOT / "year_end_top_40_1976.json",
        "culture_json": ROOT / "cultural_events_1976.json",
        "deck_root": ROOT / "retroverse-output" / "decks" / "1976",
        "palette": {
            "outer": (39, 27, 18, 255),
            "inner": (82, 56, 32, 255),
            "accent": (196, 141, 76, 255),
            "accent_dim": (151, 101, 60, 255),
            "panel": (116, 74, 42, 255),
            "line": (244, 226, 198, 255),
            "text": (244, 231, 206, 255),
            "muted": (228, 201, 160, 255),
            "overlay": (35, 21, 12, 150),
        },
        "style_text": "Painterly 1970s realism. Analog film grain. Vintage print texture. Warm bicentennial gold, muted reds, cream parchment tones, subtle celebratory warmth.",
        "single_scene_tail": "Keep the performer central, commanding, and era-authentic, with a portrait-led composition.",
        "court_scene_tail": "Build a celebratory collage with layered period motifs and a warm archival glow.",
    },
    "1977": {
        "suit_name": "Spades",
        "suit_symbol": "\u2660",
        "run_id": "deck_1977_spades",
        "top_json": ROOT / "year_end_top_40_1977.json",
        "culture_json": ROOT / "cultural_events_1977.json",
        "deck_root": ROOT / "retroverse-output" / "decks" / "1977",
        "palette": {
            "outer": (15, 22, 20, 255),
            "inner": (28, 41, 37, 255),
            "accent": (164, 174, 176, 255),
            "accent_dim": (97, 119, 116, 255),
            "panel": (36, 57, 52, 255),
            "line": (219, 228, 226, 255),
            "text": (236, 242, 240, 255),
            "muted": (192, 208, 204, 255),
            "overlay": (11, 18, 16, 164),
        },
        "style_text": "Painterly 1970s realism. Analog film grain. Vintage print texture. Deep emerald black, silver highlights, smoky stage lighting, slight disco neon undertone, darker contrast.",
        "single_scene_tail": "Keep the performer central, dramatic, and elegant, with smoky depth and darker stage contrast.",
        "court_scene_tail": "Build a darker ensemble collage with silver-lit atmosphere and smoky layered depth.",
    },
    "1978": {
        "year": 1978,
        "data_key": "1978",
        "master_json": ROOT / "retroverse-output" / "retroverse_year_master_1958_2024.json",
        "suit_name": "Hearts",
        "suit_symbol": "\u2665",
        "run_id": "deck_1978_hearts",
        "top_json": ROOT / "year_end_top_40_1978.json",
        "culture_json": ROOT / "cultural_events_1978.json",
        "deck_root": ROOT / "retroverse-output" / "decks" / "1978",
        "palette": {
            "outer": (39, 27, 18, 255),
            "inner": (82, 56, 32, 255),
            "accent": (196, 141, 76, 255),
            "accent_dim": (151, 101, 60, 255),
            "panel": (116, 74, 42, 255),
            "line": (244, 226, 198, 255),
            "text": (244, 231, 206, 255),
            "muted": (228, 201, 160, 255),
            "overlay": (35, 21, 12, 150),
        },
        "style_text": "Painterly 1970s realism. Analog film grain. Vintage print texture. Warm archival tones with lively nightlife color accents.",
        "single_scene_tail": "Keep the performer central, commanding, and era-authentic, with a portrait-led composition.",
        "court_scene_tail": "Build a celebratory collage with layered period motifs and a warm archival glow.",
    },
    "1979": {
        "year": 1979,
        "data_key": "1979",
        "master_json": ROOT / "retroverse-output" / "retroverse_year_master_1958_2024.json",
        "suit_name": "Clubs",
        "suit_symbol": "\u2663",
        "run_id": "deck_1979_clubs",
        "top_json": ROOT / "year_end_top_40_1979.json",
        "culture_json": ROOT / "cultural_events_1979.json",
        "deck_root": ROOT / "retroverse-output" / "decks" / "1979",
        "palette": {
            "outer": (15, 22, 20, 255),
            "inner": (28, 41, 37, 255),
            "accent": (164, 174, 176, 255),
            "accent_dim": (97, 119, 116, 255),
            "panel": (36, 57, 52, 255),
            "line": (219, 228, 226, 255),
            "text": (236, 242, 240, 255),
            "muted": (192, 208, 204, 255),
            "overlay": (11, 18, 16, 164),
        },
        "style_text": "Painterly 1970s realism. Analog film grain. Vintage print texture. Deep emerald black, silver highlights, smoky stage lighting, slight disco neon undertone, darker contrast.",
        "single_scene_tail": "Keep the performer central, dramatic, and elegant, with smoky depth and darker stage contrast.",
        "court_scene_tail": "Build a darker ensemble collage with silver-lit atmosphere and smoky layered depth.",
    },
    "1980": {
        "year": 1980,
        "data_key": "1980",
        "master_json": ROOT / "retroverse-output" / "retroverse_year_master_1958_2024.json",
        "suit_name": "Diamonds",
        "suit_symbol": "\u2666",
        "run_id": "deck_1980_diamonds",
        "top_json": ROOT / "year_end_top_40_1980.json",
        "culture_json": ROOT / "cultural_events_1980.json",
        "deck_root": ROOT / "retroverse-output" / "decks" / "1980",
        "palette": {
            "outer": (39, 27, 18, 255),
            "inner": (82, 56, 32, 255),
            "accent": (196, 141, 76, 255),
            "accent_dim": (151, 101, 60, 255),
            "panel": (116, 74, 42, 255),
            "line": (244, 226, 198, 255),
            "text": (244, 231, 206, 255),
            "muted": (228, 201, 160, 255),
            "overlay": (35, 21, 12, 150),
        },
        "style_text": "Painterly 1970s realism. Analog film grain. Vintage print texture. Warm archival tones with lively nightlife color accents.",
        "single_scene_tail": "Keep the performer central, commanding, and era-authentic, with a portrait-led composition.",
        "court_scene_tail": "Build a celebratory collage with layered period motifs and a warm archival glow.",
    },
    "1981": {
        "year": 1981,
        "data_key": "1981",
        "master_json": ROOT / "retroverse-output" / "retroverse_year_master_1958_2024.json",
        "suit_name": "Spades",
        "suit_symbol": "\u2660",
        "run_id": "deck_1981_spades",
        "top_json": ROOT / "year_end_top_40_1981.json",
        "culture_json": ROOT / "cultural_events_1981.json",
        "deck_root": ROOT / "retroverse-output" / "decks" / "1981",
        "palette": {
            "outer": (15, 22, 20, 255),
            "inner": (28, 41, 37, 255),
            "accent": (164, 174, 176, 255),
            "accent_dim": (97, 119, 116, 255),
            "panel": (36, 57, 52, 255),
            "line": (219, 228, 226, 255),
            "text": (236, 242, 240, 255),
            "muted": (192, 208, 204, 255),
            "overlay": (11, 18, 16, 164),
        },
        "style_text": "Painterly 1970s realism. Analog film grain. Vintage print texture. Deep emerald black, silver highlights, smoky stage lighting, slight disco neon undertone, darker contrast.",
        "single_scene_tail": "Keep the performer central, dramatic, and elegant, with smoky depth and darker stage contrast.",
        "court_scene_tail": "Build a darker ensemble collage with silver-lit atmosphere and smoky layered depth.",
    },
}

SINGLE_PROMPT_OVERRIDES: dict[tuple[str, str, str], str] = {}

EDITORIAL_STYLE_GUARDRAILS = (
    "Editorial cartoon only. Satirical magazine look. Bold black ink outlines. "
    "Hand-drawn, hand-lettered feel. Flat retro color palette. Halftone print texture. "
    "Humorous background details. Avoid photorealism, baseball-card styling, trading-card styling, "
    "modern poster layouts, and slick digital rendering."
)

EDITORIAL_1978_TOP10_SPECS: dict[str, dict[str, str]] = {
    "A": {
        "title": "Stayin' Alive",
        "artist": "Bee Gees",
        "premise": "The disco floor feels so alive that dancers seem physically controlled by the beat, as if the whole nightclub is a living creature.",
        "headline": "DOCTORS BAFFLED BY DISCO FEVER OUTBREAK",
        "tone": "high-energy disco panic",
        "movie_ref": "Grease",
        "tv_ref": "Laverne & Shirley",
    },
    "2": {
        "title": "Shadow Dancing",
        "artist": "Andy Gibb",
        "premise": "A dancer's shadow becomes the real celebrity and steals every spotlight from the humans.",
        "headline": "SHADOW SIGNS SOLO CONTRACT",
        "tone": "playful disco absurdity",
        "movie_ref": "Superman",
        "tv_ref": "Three's Company",
    },
    "3": {
        "title": "Hot Child in the City",
        "artist": "Nick Gilder",
        "premise": "A flashy young trendsetter struts through a city heatwave so extreme that eggs fry on sidewalks; keep it clearly non-sexual and comedic.",
        "headline": "EGG FRIES ON SIDEWALK!",
        "tone": "urban heatwave chaos",
        "movie_ref": "Animal House",
        "tv_ref": "Mork & Mindy",
    },
    "4": {
        "title": "Kiss You All Over",
        "artist": "Exile",
        "premise": "An overly romantic city is flooded with floating kisses, flowers, and playful affection; keep the mood warm, funny, dreamy, and safe.",
        "headline": "CITY DECLARES ROMANCE STATE OF EMERGENCY",
        "tone": "romantic comedy",
        "movie_ref": "Heaven Can Wait",
        "tv_ref": "Angie",
    },
    "5": {
        "title": "Night Fever",
        "artist": "Bee Gees",
        "premise": "The nightclub overheats so badly that city officials treat the dance floor like a public-health emergency zone.",
        "headline": "DANCE FLOOR TEMPERATURE HITS 106",
        "tone": "disco meltdown",
        "movie_ref": "Saturday Night Fever",
        "tv_ref": "60 Minutes",
    },
    "6": {
        "title": "Boogie Oogie Oogie",
        "artist": "A Taste of Honey",
        "premise": "A haunted disco is overrun by funky dancing ghosts who refuse to leave until the last song ends.",
        "headline": "LOCAL CLUB BLAMES FUNK ON SPIRITS",
        "tone": "playful spooky disco",
        "movie_ref": "Revenge of the Pink Panther",
        "tv_ref": "M*A*S*H",
    },
    "7": {
        "title": "Lay Down Sally",
        "artist": "Eric Clapton",
        "premise": "An entire town begs one stubborn woman named Sally to sit and relax while everyone else loses composure.",
        "headline": "CITY PLEADS WITH SALLY TO TAKE A LOAD OFF",
        "tone": "laid-back comic frustration",
        "movie_ref": "Hooper",
        "tv_ref": "The Ropers",
    },
    "8": {
        "title": "You're the One That I Want",
        "artist": "John Travolta / Olivia Newton-John",
        "premise": "A whole crowd chases one ideal romantic target like a prize no one can quite catch.",
        "headline": "ROMANTIC SHORTAGE LEAVES CITY DESPERATE",
        "tone": "musical-comedy chaos",
        "movie_ref": "Grease",
        "tv_ref": "All in the Family",
    },
    "9": {
        "title": "(Love Is) Thicker Than Water",
        "artist": "Andy Gibb",
        "premise": "Romance becomes a literal extra-thick liquid and couples wade through it while everyone else gets hilariously stuck.",
        "headline": "CITY DROWNS IN EXTRA-THICK LOVE",
        "tone": "gooey romance parody",
        "movie_ref": "Jaws 2",
        "tv_ref": "Eight Is Enough",
    },
    "10": {
        "title": "I Love the Nightlife",
        "artist": "Alicia Bridges",
        "premise": "A nightlife addict treats every disco and neon sign like a sacred calling.",
        "headline": "WOMAN FILES TAX RETURN AS DEPENDENT OF DISCO",
        "tone": "nightlife obsession",
        "movie_ref": "Every Which Way But Loose",
        "tv_ref": "ABC",
    },
}

EDITORIAL_1978_HERO_SPECS: dict[str, dict[str, str]] = {
    "J": {
        "title": "Sultans of Swing",
        "artist": "Dire Straits",
        "premise": "A shabby bar band is treated like royal court musicians while almost nobody notices.",
        "headline": "BAR BAND DEMANDS THRONE, GETS CORNER STAGE",
        "tone": "dry barroom satire",
        "movie_ref": "The Deer Hunter",
        "tv_ref": "60 Minutes",
    },
    "Q": {
        "title": "Roll With the Changes",
        "artist": "REO Speedwagon",
        "premise": "People literally roll through a city where everything keeps changing faster than anyone can keep up.",
        "headline": "WORKERS ADVISED TO PANIC, THEN ADAPT",
        "tone": "chaotic resilience",
        "movie_ref": "Superman",
        "tv_ref": "Three's Company",
    },
    "K": {
        "title": "Baker Street",
        "artist": "Gerry Rafferty",
        "premise": "A weary city drifter tries to look cool and profound while the block drowns in saxophone, smoke, and regret.",
        "headline": "LOCAL STREET FOUND TO BE 80% MOOD",
        "tone": "urban melancholy satire",
        "movie_ref": "Heaven Can Wait",
        "tv_ref": "M*A*S*H",
    },
}

EDITORIAL_1978_RECAP_SPECS: dict[str, dict[str, Any]] = {
    "R1": {
        "title": "Recap 11-20",
        "artist": "Top 40 Recap",
        "premise": "A jukebox and radio countdown scene listing songs 11-20 amid playful cartoon clutter.",
        "headline": "MIDDLE OF THE CHART, MAXIMUM DRAMA",
        "tone": "countdown clutter comedy",
        "movie_ref": "Grease",
        "tv_ref": "Laverne & Shirley",
        "songs": [
            "11 You Needed Me",
            "12 Three Times a Lady",
            "13 Grease",
            "14 If I Can't Have You",
            "15 Emotion",
            "16 Can't Smile Without You",
            "17 Feels So Good",
            "18 Miss You",
            "19 Baker Street",
            "20 It's a Heartache",
        ],
    },
    "R2": {
        "title": "Recap 21-30",
        "artist": "Top 40 Recap",
        "premise": "A record-store wall chart scene listing songs 21-30 with humorous retail chaos.",
        "headline": "TEN MORE HITS, ZERO SELF-CONTROL",
        "tone": "retail chart chaos",
        "movie_ref": "National Lampoon's Animal House",
        "tv_ref": "Three's Company",
        "songs": [
            "21 Love Is Like Oxygen",
            "22 MacArthur Park",
            "23 Hopelessly Devoted to You",
            "24 Jack and Jill",
            "25 Take a Chance on Me",
            "26 The Closer I Get to You",
            "27 Love Is in the Air",
            "28 Last Dance",
            "29 Hot Blooded",
            "30 How Deep Is Your Love",
        ],
    },
    "R3": {
        "title": "Recap 31-40",
        "artist": "Top 40 Recap",
        "premise": "A magazine contents-page scene listing songs 31-40 with tiny visual jokes and marginal doodles.",
        "headline": "BOTTOM OF THE TOP 40, STILL FULL OF TROUBLE",
        "tone": "busy magazine satire",
        "movie_ref": "Jaws 2",
        "tv_ref": "Mork & Mindy",
        "songs": [
            "31 How Much I Feel",
            "32 Dust in the Wind",
            "33 Reminiscing",
            "34 I Go Crazy",
            "35 Whenever I Call You \"Friend\"",
            "36 Just the Way You Are",
            "37 Dance With Me",
            "38 With a Little Luck",
            "39 Too Much, Too Little, Too Late",
            "40 You Never Done It Like That",
        ],
    },
    "R4": {
        "title": "1978 Year Overview",
        "artist": "RetroVerse Editorial Desk",
        "premise": "A full-page 1978 satirical splash image summarizing disco, movies, TV, nightlife, fashion, and pop-culture madness.",
        "headline": "AMERICA DECLARES BELL BOTTOMS A WAY OF LIFE",
        "tone": "maximal year-end satire",
        "movie_ref": "Every Which Way But Loose",
        "tv_ref": "All in the Family",
        "songs": [],
    },
}


def normalize_space(text: str) -> str:
    return " ".join(str(text).split())


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def render_rank_for_label(label: str) -> int:
    if label in STANDARD_CARD_ORDER:
        return STANDARD_CARD_ORDER.index(label) + 1
    if label in {"R1", "R2", "R3", "R4"}:
        return 13 + int(label[1])
    raise ValueError(f"Unsupported card label: {label}")


def lookup_song(top_40: list[dict[str, Any]], *, rv_rank: int | None = None, title: str | None = None, artist: str | None = None) -> dict[str, Any] | None:
    if rv_rank is not None:
        for song in top_40:
            if int(song["rv_rank"]) == rv_rank:
                return song
        return None

    if title is None:
        return None

    title_key = normalized_key(title)
    artist_key = normalized_key(artist) if artist else ""
    for song in top_40:
        if normalized_key(str(song["title"])) != title_key:
            continue
        if artist_key and normalized_key(str(song["artist"])) != artist_key:
            continue
        return song
    return None


def editorial_premise_text(premise: str, tone: str, *, list_block: str | None = None) -> str:
    lines = [
        normalize_space(premise),
        f"Tone: {normalize_space(tone)}.",
    ]
    if list_block:
        lines.append(list_block)
    lines.append(EDITORIAL_STYLE_GUARDRAILS)
    lines.append("Keep it playful and clearly non-violent, non-sexual, and suitable for a satirical magazine audience.")
    return "\n".join(lines)


def choose_editorial_stats(song: dict[str, Any] | None, *, fallback_peak: int, fallback_weeks: int) -> tuple[int, int]:
    if song is None:
        return fallback_peak, fallback_weeks
    return int(song["peak_rank"]), int(song["weeks_on_chart"])


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    family = "bold" if bold else "regular"
    for candidate in FONT_CANDIDATES[family]:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    if not text:
        return 0
    left, _, right, _ = draw.textbbox((0, 0), text, font=font)
    return right - left


def line_height(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> int:
    _, top, _, bottom = draw.textbbox((0, 0), "Ag", font=font)
    return bottom - top


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = normalize_space(text).split()
    if not words:
        return []
    lines = [words[0]]
    for word in words[1:]:
        probe = f"{lines[-1]} {word}"
        if text_width(draw, probe, font) <= max_width:
            lines[-1] = probe
        else:
            lines.append(word)
    return lines


def truncate_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    candidate = normalize_space(text)
    if text_width(draw, candidate, font) <= max_width:
        return candidate
    ellipsis = "..."
    parts = candidate.split()
    while parts:
        probe = f"{' '.join(parts)}{ellipsis}"
        if text_width(draw, probe, font) <= max_width:
            return probe
        parts.pop()
    return ellipsis


def fit_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    *,
    max_size: int,
    min_size: int,
    max_lines: int,
    bold: bool = False,
) -> tuple[ImageFont.ImageFont, list[str]]:
    width = box[2] - box[0]
    height = box[3] - box[1]
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, bold=bold)
        lines = wrap_text(draw, text, font, width)
        if len(lines) > max_lines:
            lines = lines[: max_lines - 1] + [truncate_text(draw, " ".join(lines[max_lines - 1 :]), font, width)]
        if not lines:
            return font, []
        lh = line_height(draw, font)
        gap = max(2, size // 8)
        total = lh * len(lines) + gap * max(0, len(lines) - 1)
        if total <= height and all(text_width(draw, line, font) <= width for line in lines):
            return font, lines
    fallback = load_font(min_size, bold=bold)
    lines = wrap_text(draw, text, fallback, width)
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + [truncate_text(draw, " ".join(lines[max_lines - 1 :]), fallback, width)]
    return fallback, lines


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    *,
    max_size: int,
    min_size: int,
    max_lines: int,
    fill: tuple[int, int, int, int],
    bold: bool = False,
    align: str = "center",
) -> None:
    font, lines = fit_lines(draw, text, box, max_size=max_size, min_size=min_size, max_lines=max_lines, bold=bold)
    if not lines:
        return
    lh = line_height(draw, font)
    gap = max(2, getattr(font, "size", min_size) // 8)
    total = lh * len(lines) + gap * max(0, len(lines) - 1)
    y = box[1] + ((box[3] - box[1] - total) / 2)
    for line in lines:
        width = text_width(draw, line, font)
        if align == "left":
            x = box[0]
        elif align == "right":
            x = box[2] - width
        else:
            x = box[0] + ((box[2] - box[0] - width) / 2)
        draw.text((x, y), line, font=font, fill=fill)
        y += lh + gap


def load_top_40(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    top_40 = payload.get("top_40")
    year = str(payload.get("year"))
    if not isinstance(top_40, list) or len(top_40) < 40:
        raise ValueError(f"{path} must contain 40 top_40 entries")
    if year not in YEAR_CONFIGS:
        raise ValueError(f"Unsupported year in {path}: {year}")
    return top_40[:40]


def load_culture(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload.get("films"), list) or not isinstance(payload.get("tv"), list) or not isinstance(payload.get("headlines"), list):
        raise ValueError(f"{path} must contain films, tv, and headlines arrays")
    return payload


def load_openai_api_key() -> str:
    loaded_api_key = os.getenv("OPENAI_API_KEY")
    if not loaded_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. Ensure ~/Sites/retroverse/.env exists and contains the API key."
        )
    return loaded_api_key


def card_label_for_rank(rank: int) -> str:
    return "A" if rank == 1 else str(rank)


def raw_image_name(year: str, label: str) -> str:
    if label.isdigit() and len(label) == 1:
        return f"{year}_raw_0{label}.png"
    return f"{year}_raw_{label}.png"


def final_image_name(year: str, label: str) -> str:
    if label.isdigit() and len(label) == 1:
        return f"{year}_final_0{label}.png"
    return f"{year}_final_{label}.png"


def headline_text(raw_value: Any) -> str:
    if isinstance(raw_value, dict):
        return normalize_space(raw_value.get("event", ""))
    return normalize_space(raw_value)


def style_for_card(index: int, rv_rank: int | None = None) -> str:
    if rv_rank == 1:
        return "retro cultural collage poster"
    return STYLES[index % len(STYLES)]


def culture_snapshot(culture: dict[str, Any], limit: int = 3) -> tuple[list[str], list[str], list[str]]:
    films = [normalize_space(item) for item in culture.get("films", []) if normalize_space(item)]
    tv_items = [normalize_space(item) for item in culture.get("tv", []) if normalize_space(item)]
    headlines = [headline_text(item) for item in culture.get("headlines", []) if headline_text(item)]
    return films[:limit], tv_items[:limit], headlines[:limit]


def pick_reference(items: list[str], *, default: str = "Unavailable") -> str:
    if not items:
        return default
    return random.choice(items)


def build_single_prompt(year: str, config: dict[str, Any], song: dict[str, Any], culture: dict[str, Any], index: int) -> str:
    title = normalize_space(song["title"])
    artist = normalize_space(song["artist"])
    override = SINGLE_PROMPT_OVERRIDES.get((year, title, artist))
    if override:
        return override

    films = culture["films"]
    tv_items = culture["tv"]
    headlines = culture["headlines"]
    film = normalize_space(films[index]) if index < len(films) else "Unavailable"
    tv = normalize_space(tv_items[index]) if index < len(tv_items) else "Unavailable"
    headline = headline_text(headlines[index]) if index < len(headlines) else "Unavailable"
    rv_rank = int(song["rv_rank"])
    style = style_for_card(index, rv_rank=rv_rank)
    peak_rank = int(song["peak_rank"])
    weeks_on_chart = int(song["weeks_on_chart"])

    if rv_rank == 1:
        films_top, tv_top, headlines_top = culture_snapshot(culture, limit=3)
        return dedent(
            f"""
            {style}

            Stylized illustration for the year {year}

            Song: "{title}" by {artist}

            Build an ace-card year portrait that represents the full cultural atmosphere of {year}.
            Include a layered cultural collage using these references:
            Films: {", ".join(films_top) if films_top else "Unavailable"}
            TV: {", ".join(tv_top) if tv_top else "Unavailable"}
            Headlines: {" | ".join(headlines_top) if headlines_top else "Unavailable"}

            Visual cues inspired by the era, including fashion, nightlife, vinyl records, and retro typography.
            Avoid photorealism.
            Use bold poster-style composition.
            Clear readable layout suitable for a playing card.

            Rank context: #{rv_rank} song of {year} | Peak #{peak_rank} | {weeks_on_chart} weeks on chart.
            """
        ).strip()

    return dedent(
        f"""
        {style}

        Stylized illustration for the year {year}

        Song: "{title}" by {artist}

        Include rank context: #{rv_rank} song of {year} | Peak #{peak_rank} | {weeks_on_chart} weeks on chart.
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
        f"- #{int(song['rv_rank'])}: {normalize_space(song['title'])} by {normalize_space(song['artist'])}"
        for song in songs
    )


def build_court_prompt(year: str, config: dict[str, Any], label: str, songs: list[dict[str, Any]], index: int) -> str:
    start = int(songs[0]["rv_rank"])
    end = int(songs[-1]["rv_rank"])
    style = style_for_card(index)
    return dedent(
        f"""
        {style}

        Stylized illustration for the year {year}

        Song block: "{label} card" covering ranks #{start} to #{end}

        Build a composite collage inspired by this song range:
        {build_song_list_block(songs)}

        Visual cues inspired by the era, including fashion, nightlife, vinyl records, and retro typography.
        Avoid photorealism.
        Use bold poster-style composition.
        Clear readable layout suitable for a playing card.
        """
    ).strip()


def build_1978_editorial_prompt_records(
    year: str,
    config: dict[str, Any],
    top_40: list[dict[str, Any]],
    raw_dir: Path,
    run_dir: Path,
    only_labels: set[str] | None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    run_id = str(config["run_id"])
    logs_dir = run_dir / "logs"
    suit = str(config["suit_symbol"])

    hero_fallbacks = {
        "J": (4, 18),
        "Q": (8, 16),
        "K": (2, 20),
    }

    for label in EDITORIAL_1978_CARD_ORDER:
        if only_labels and label not in only_labels:
            continue

        spec: dict[str, Any]
        card_type: str
        song: dict[str, Any] | None = None

        if label in EDITORIAL_1978_TOP10_SPECS:
            spec = EDITORIAL_1978_TOP10_SPECS[label]
            rv_rank = 1 if label == "A" else int(label)
            song = lookup_song(top_40, rv_rank=rv_rank)
            peak_position, weeks_on_chart = choose_editorial_stats(song, fallback_peak=1, fallback_weeks=18)
            card_type = "top10_song"
            list_block = None
        elif label in EDITORIAL_1978_HERO_SPECS:
            spec = EDITORIAL_1978_HERO_SPECS[label]
            song = lookup_song(top_40, title=spec["title"], artist=spec["artist"])
            fallback_peak, fallback_weeks = hero_fallbacks[label]
            peak_position, weeks_on_chart = choose_editorial_stats(song, fallback_peak=fallback_peak, fallback_weeks=fallback_weeks)
            card_type = "hero_song"
            list_block = None
        else:
            spec = EDITORIAL_1978_RECAP_SPECS[label]
            if label in {"R1", "R2", "R3"}:
                songs = list(spec.get("songs", []))
                list_block = "Display this ranked list clearly in the scene:\n" + "\n".join(f"- {line}" for line in songs)
                peak_position, weeks_on_chart = (1, 10)
                card_type = "recap"
            else:
                list_block = None
                peak_position, weeks_on_chart = (1, 52)
                card_type = "year_overview"

        title = normalize_space(str(spec["title"]))
        artist = normalize_space(str(spec["artist"]))
        basename = f"{year}_raw_{label}_{slugify(title)}__{slugify(artist)}"
        cartoon_premise = editorial_premise_text(str(spec["premise"]), str(spec["tone"]), list_block=list_block)
        headline = normalize_space(str(spec["headline"]))

        record: dict[str, Any] = {
            "run_id": run_id,
            "year": int(year),
            "card_label": label,
            "rank": render_rank_for_label(label),
            "basename": basename,
            "song_title": title,
            "artist": artist,
            "song_theme": normalize_space(str(spec["tone"])),
            "visual_metaphor": "",
            "cartoon_premise": cartoon_premise,
            "peak_position": peak_position,
            "weeks_on_chart": weeks_on_chart,
            "suit": suit,
            "film": normalize_space(str(spec["movie_ref"])),
            "tv": normalize_space(str(spec["tv_ref"])),
            "trend": headline,
            "prompt_text": cartoon_premise,
            "image_path": str(raw_dir / raw_image_name(year, label)),
            "log_path": str(logs_dir / f"{basename}.render.json"),
            "card_type": card_type,
            "rank_line_text": f"#{label} • {year}",
            "headline": headline,
        }
        if label in {"R1", "R2", "R3"}:
            record["recap_lines"] = list(spec.get("songs", []))
        records.append(record)

    return records


def build_prompt_records(
    year: str,
    config: dict[str, Any],
    top_40: list[dict[str, Any]],
    culture: dict[str, Any],
    raw_dir: Path,
    run_dir: Path,
    only_labels: set[str] | None,
) -> list[dict[str, Any]]:
    if year == "1978":
        return build_1978_editorial_prompt_records(year, config, top_40, raw_dir, run_dir, only_labels)

    records: list[dict[str, Any]] = []
    run_id = str(config["run_id"])
    logs_dir = run_dir / "logs"
    suit = str(config["suit_symbol"])

    film_refs = [normalize_space(item) for item in culture.get("films", []) if normalize_space(item)]
    tv_refs = [normalize_space(item) for item in culture.get("tv", []) if normalize_space(item)]
    trend_refs = [headline_text(item) for item in culture.get("headlines", []) if headline_text(item)]

    for index, song in enumerate(top_40[:10]):
        label = card_label_for_rank(int(song["rv_rank"]))
        if only_labels and label not in only_labels:
            continue
        title = normalize_space(song["title"])
        artist = normalize_space(song["artist"])
        premise_payload = generate_song_premise(title, artist)
        song_theme = normalize_space(str(premise_payload.get("song_theme", "")))
        visual_metaphor = normalize_space(str(premise_payload.get("visual_metaphor", "")))
        cartoon_premise = normalize_space(str(premise_payload.get("cartoon_premise", "")))
        peak_position = int(song["peak_rank"])
        weeks_on_chart = int(song["weeks_on_chart"])
        basename = f"{year}_raw_{label}_{slugify(title)}__{slugify(artist)}"
        records.append(
            {
                "run_id": run_id,
                "year": int(year),
                "card_label": label,
                "rank": int(song["rv_rank"]),
                "basename": basename,
                "song_title": title,
                "artist": artist,
                "song_theme": song_theme,
                "visual_metaphor": visual_metaphor,
                "cartoon_premise": cartoon_premise,
                "peak_position": peak_position,
                "weeks_on_chart": weeks_on_chart,
                "suit": suit,
                "film": pick_reference(film_refs),
                "tv": pick_reference(tv_refs),
                "trend": pick_reference(trend_refs),
                "prompt_text": build_single_prompt(year, config, song, culture, index),
                "image_path": str(raw_dir / raw_image_name(year, label)),
                "log_path": str(logs_dir / f"{basename}.render.json"),
            }
        )

    for label, (start, end) in COURT_RANGES.items():
        if only_labels and label not in only_labels:
            continue
        songs = top_40[start - 1 : end]
        card_index = CARD_ORDER.index(label)
        basename = f"{year}_raw_{label}_ranks_{start:02d}_{end:02d}"
        medley_title = f"{year} {label} Card Medley"
        premise_payload = generate_song_premise(medley_title, "Various Artists")
        song_theme = normalize_space(str(premise_payload.get("song_theme", "")))
        visual_metaphor = normalize_space(str(premise_payload.get("visual_metaphor", "")))
        cartoon_premise = normalize_space(str(premise_payload.get("cartoon_premise", "")))
        peak_position = min(int(song["peak_rank"]) for song in songs)
        weeks_on_chart = max(int(song["weeks_on_chart"]) for song in songs)
        records.append(
            {
                "run_id": run_id,
                "year": int(year),
                "card_label": label,
                "rank": start,
                "basename": basename,
                "song_title": medley_title,
                "artist": "Various Artists",
                "song_theme": song_theme,
                "visual_metaphor": visual_metaphor,
                "cartoon_premise": cartoon_premise,
                "peak_position": peak_position,
                "weeks_on_chart": weeks_on_chart,
                "suit": suit,
                "film": pick_reference(film_refs),
                "tv": pick_reference(tv_refs),
                "trend": pick_reference(trend_refs),
                "prompt_text": build_court_prompt(year, config, label, songs, card_index),
                "image_path": str(raw_dir / raw_image_name(year, label)),
                "log_path": str(logs_dir / f"{basename}.render.json"),
            }
        )

    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_render_config(path: Path, run_id: str, *, skip_if_image_exists: bool) -> None:
    config_text = (
        f"run_id: {run_id}\n"
        "runs_root: runs\n"
        "image:\n"
        f"  width: {CARD_WIDTH}\n"
        f"  height: {CARD_HEIGHT}\n"
        "render:\n"
        "  provider: openai\n"
        "  model: gpt-image-1\n"
        "  concurrency: 2\n"
        "  timeout_seconds: 240\n"
        "resume:\n"
        f"  skip_if_image_exists: {'true' if skip_if_image_exists else 'false'}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config_text, encoding="utf-8")


def render_run(config_path: Path) -> None:
    if not RENDERER_PATH.exists():
        raise FileNotFoundError(f"Renderer not found: {RENDERER_PATH}")
    subprocess.run([sys.executable, str(RENDERER_PATH), "--config", str(config_path)], check=True, cwd=ROOT)


def add_texture(draw: ImageDraw.ImageDraw, seed: int, palette: dict[str, tuple[int, int, int, int]]) -> None:
    import random

    rng = random.Random(seed)
    for _ in range(1100):
        x = rng.randint(OUTER_MARGIN, CARD_WIDTH - OUTER_MARGIN)
        y = rng.randint(OUTER_MARGIN, CARD_HEIGHT - OUTER_MARGIN)
        radius = rng.choice((1, 1, 2))
        color = rng.choice(
            (
                (255, 255, 255, 18),
                (0, 0, 0, 20),
                palette["accent"][:3] + (18,),
            )
        )
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def clear_alpha_box(image: Image.Image, box: tuple[int, int, int, int], radius: int) -> None:
    alpha = image.getchannel("A")
    alpha_draw = ImageDraw.Draw(alpha)
    alpha_draw.rounded_rectangle(box, radius=radius, fill=0)
    image.putalpha(alpha)


def build_frame(year: str, config: dict[str, Any]) -> Path:
    deck_root = Path(config["deck_root"])
    assets_dir = deck_root / "assets"
    frame_path = assets_dir / f"frame_{year}.png"
    assets_dir.mkdir(parents=True, exist_ok=True)

    palette = config["palette"]
    frame = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), palette["outer"])
    draw = ImageDraw.Draw(frame, "RGBA")

    draw.rounded_rectangle((OUTER_MARGIN, OUTER_MARGIN, CARD_WIDTH - OUTER_MARGIN, CARD_HEIGHT - OUTER_MARGIN), radius=42, fill=palette["outer"])
    draw.rounded_rectangle((INNER_MARGIN, INNER_MARGIN, CARD_WIDTH - INNER_MARGIN, CARD_HEIGHT - INNER_MARGIN), radius=34, fill=palette["inner"], outline=palette["accent"], width=4)
    draw.rounded_rectangle((72, 72, CARD_WIDTH - 72, CARD_HEIGHT - 72), radius=28, outline=palette["line"], width=2)
    draw.rounded_rectangle((RANK_LINE_BOX[0] - 22, RANK_LINE_BOX[1] - 10, RANK_LINE_BOX[2] + 22, RANK_LINE_BOX[3] + 10), radius=22, fill=palette["panel"], outline=palette["accent"], width=3)
    draw.rounded_rectangle((ART_CUTOUT_BOX[0] - 16, ART_CUTOUT_BOX[1] - 16, ART_CUTOUT_BOX[2] + 16, ART_CUTOUT_BOX[3] + 16), radius=30, fill=palette["inner"], outline=palette["accent"], width=3)
    draw.rounded_rectangle((TITLE_BOX[0] - 12, TITLE_BOX[1] - 8, TITLE_BOX[2] + 12, TITLE_BOX[3] + 8), radius=24, fill=palette["panel"], outline=palette["accent"], width=3)
    draw.rounded_rectangle((ARTIST_BOX[0] - 10, ARTIST_BOX[1] - 6, ARTIST_BOX[2] + 10, ARTIST_BOX[3] + 6), radius=18, fill=palette["panel"], outline=palette["accent_dim"], width=2)
    draw.rounded_rectangle((STATS_BOX[0] - 10, STATS_BOX[1] - 6, STATS_BOX[2] + 10, STATS_BOX[3] + 6), radius=16, fill=palette["panel"], outline=palette["accent_dim"], width=2)
    draw.rounded_rectangle((FOOTER_BOX[0] - 16, FOOTER_BOX[1] - 8, FOOTER_BOX[2] + 16, FOOTER_BOX[3] + 8), radius=16, fill=palette["panel"], outline=palette["accent_dim"], width=2)

    for corner_box in (CORNER_BOX_LEFT, CORNER_BOX_RIGHT):
        draw.rounded_rectangle(corner_box, radius=18, fill=palette["panel"], outline=palette["accent"], width=3)

    draw.rounded_rectangle(LIST_BOX, radius=24, outline=palette["accent_dim"], width=3)
    add_texture(draw, int(year), palette)
    clear_alpha_box(frame, ART_CUTOUT_BOX, radius=22)

    lip = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    lip_draw = ImageDraw.Draw(lip, "RGBA")
    lip_draw.rounded_rectangle(ART_CUTOUT_BOX, radius=22, outline=palette["accent"], width=3)
    lip_draw.rounded_rectangle((ART_CUTOUT_BOX[0] + 8, ART_CUTOUT_BOX[1] + 8, ART_CUTOUT_BOX[2] - 8, ART_CUTOUT_BOX[3] - 8), radius=16, outline=palette["line"][:3] + (96,), width=2)
    frame = Image.alpha_composite(frame, lip)
    frame.save(frame_path)
    return frame_path


def fit_art_to_window(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(f"Missing raw artwork: {path}")
    with Image.open(path) as raw:
        image = raw.convert("RGBA")
    target = (ART_CUTOUT_BOX[2] - ART_CUTOUT_BOX[0], ART_CUTOUT_BOX[3] - ART_CUTOUT_BOX[1])
    return ImageOps.fit(image, target, method=RESAMPLE, centering=(0.5, 0.5))


def draw_corner_pips(
    draw: ImageDraw.ImageDraw,
    *,
    label: str,
    suit_symbol: str,
    palette: dict[str, tuple[int, int, int, int]],
) -> None:
    rank_font = load_font(34, bold=True)
    suit_font = load_font(30, bold=True)

    left_rank_w = text_width(draw, label, rank_font)
    left_suit_w = text_width(draw, suit_symbol, suit_font)
    draw.text((CORNER_BOX_LEFT[0] + (CORNER_BOX_LEFT[2] - CORNER_BOX_LEFT[0] - left_rank_w) / 2, CORNER_BOX_LEFT[1] + 8), label, font=rank_font, fill=palette["text"])
    draw.text((CORNER_BOX_LEFT[0] + (CORNER_BOX_LEFT[2] - CORNER_BOX_LEFT[0] - left_suit_w) / 2, CORNER_BOX_LEFT[1] + 54), suit_symbol, font=suit_font, fill=palette["muted"])

    right_rank_w = text_width(draw, label, rank_font)
    right_suit_w = text_width(draw, suit_symbol, suit_font)
    draw.text((CORNER_BOX_RIGHT[2] - 12 - right_rank_w, CORNER_BOX_RIGHT[1] + 8), label, font=rank_font, fill=palette["text"])
    draw.text((CORNER_BOX_RIGHT[2] - 12 - right_suit_w, CORNER_BOX_RIGHT[1] + 54), suit_symbol, font=suit_font, fill=palette["muted"])


def compose_number_card(
    year: str,
    config: dict[str, Any],
    frame: Image.Image,
    raw_dir: Path,
    final_dir: Path,
    song: dict[str, Any],
) -> Path:
    label = card_label_for_rank(int(song["rv_rank"]))
    card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), config["palette"]["outer"])
    art = fit_art_to_window(raw_dir / raw_image_name(year, label))
    card.paste(art, ART_CUTOUT_BOX[:2], art)
    card = Image.alpha_composite(card, frame)
    draw = ImageDraw.Draw(card)

    palette = config["palette"]
    draw_corner_pips(draw, label=label, suit_symbol=config["suit_symbol"], palette=palette)
    draw_text_block(draw, f"#{int(song['rv_rank'])} Song of {year}", RANK_LINE_BOX, max_size=28, min_size=16, max_lines=1, fill=palette["muted"], bold=True)
    draw_text_block(draw, normalize_space(song["title"]), TITLE_BOX, max_size=40, min_size=18, max_lines=2, fill=palette["text"], bold=True)
    draw_text_block(draw, normalize_space(song["artist"]), ARTIST_BOX, max_size=24, min_size=14, max_lines=1, fill=palette["muted"], bold=True)
    stats = f"Peak #{int(song['peak_rank'])} • {int(song['weeks_on_chart'])} Weeks on Chart"
    draw_text_block(draw, stats, STATS_BOX, max_size=19, min_size=12, max_lines=1, fill=palette["text"])
    draw_text_block(draw, year, FOOTER_BOX, max_size=24, min_size=14, max_lines=1, fill=palette["muted"], bold=True)

    output = final_dir / final_image_name(year, label)
    output.parent.mkdir(parents=True, exist_ok=True)
    card.save(output)
    return output


def compose_court_card(
    year: str,
    config: dict[str, Any],
    frame: Image.Image,
    raw_dir: Path,
    final_dir: Path,
    label: str,
    songs: list[dict[str, Any]],
) -> Path:
    card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), config["palette"]["outer"])
    art = fit_art_to_window(raw_dir / raw_image_name(year, label))
    card.paste(art, ART_CUTOUT_BOX[:2], art)
    card = Image.alpha_composite(card, frame)
    draw = ImageDraw.Draw(card)

    palette = config["palette"]
    draw_corner_pips(draw, label=label, suit_symbol=config["suit_symbol"], palette=palette)

    start = int(songs[0]["rv_rank"])
    end = int(songs[-1]["rv_rank"])
    line_text = f"{start}-{end} Songs of {year}"
    draw_text_block(draw, line_text, RANK_LINE_BOX, max_size=28, min_size=16, max_lines=1, fill=palette["muted"], bold=True)
    draw_text_block(draw, line_text, TITLE_BOX, max_size=36, min_size=18, max_lines=1, fill=palette["text"], bold=True)
    draw_text_block(draw, year, FOOTER_BOX, max_size=24, min_size=14, max_lines=1, fill=palette["muted"], bold=True)

    overlay = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")
    overlay_draw.rounded_rectangle(LIST_BOX, radius=22, fill=config["palette"]["overlay"], outline=palette["line"][:3] + (180,), width=2)
    card = Image.alpha_composite(card, overlay)
    draw = ImageDraw.Draw(card)

    inner_left = LIST_BOX[0] + 28
    inner_top = LIST_BOX[1] + 18
    inner_width = LIST_BOX[2] - LIST_BOX[0] - 56
    row_height = 68
    display_lines = [f"{int(song['rv_rank'])}. {normalize_space(song['title'])}" for song in songs]

    for index, text in enumerate(display_lines):
        y = inner_top + index * row_height
        draw_text_block(
            draw,
            text,
            (inner_left, y, inner_left + inner_width, y + row_height - 6),
            max_size=20,
            min_size=12,
            max_lines=1,
            fill=palette["text"],
            bold=False,
            align="left",
        )

    output = final_dir / final_image_name(year, label)
    output.parent.mkdir(parents=True, exist_ok=True)
    card.save(output)
    return output


def compose_editorial_song_card(
    year: str,
    config: dict[str, Any],
    frame: Image.Image,
    raw_dir: Path,
    final_dir: Path,
    record: dict[str, Any],
) -> Path:
    label = normalize_space(str(record["card_label"]))
    card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), config["palette"]["outer"])
    art = fit_art_to_window(raw_dir / raw_image_name(year, label))
    card.paste(art, ART_CUTOUT_BOX[:2], art)
    card = Image.alpha_composite(card, frame)
    draw = ImageDraw.Draw(card)

    palette = config["palette"]
    draw_corner_pips(draw, label=label, suit_symbol=config["suit_symbol"], palette=palette)
    rank_line = normalize_space(str(record.get("rank_line_text") or f"#{label} • {year}"))
    draw_text_block(draw, rank_line, RANK_LINE_BOX, max_size=28, min_size=14, max_lines=1, fill=palette["muted"], bold=True)
    draw_text_block(draw, normalize_space(str(record["song_title"])), TITLE_BOX, max_size=36, min_size=16, max_lines=2, fill=palette["text"], bold=True)
    draw_text_block(draw, normalize_space(str(record["artist"])), ARTIST_BOX, max_size=22, min_size=12, max_lines=1, fill=palette["muted"], bold=True)

    peak_position = normalize_space(str(record.get("peak_position", "")))
    weeks_on_chart = normalize_space(str(record.get("weeks_on_chart", "")))
    stats = f"Peak #{peak_position} • {weeks_on_chart} Weeks on Chart"
    draw_text_block(draw, stats, STATS_BOX, max_size=18, min_size=11, max_lines=1, fill=palette["text"])
    draw_text_block(draw, year, FOOTER_BOX, max_size=24, min_size=14, max_lines=1, fill=palette["muted"], bold=True)

    output = final_dir / final_image_name(year, label)
    output.parent.mkdir(parents=True, exist_ok=True)
    card.save(output)
    return output


def compose_editorial_recap_card(
    year: str,
    config: dict[str, Any],
    frame: Image.Image,
    raw_dir: Path,
    final_dir: Path,
    record: dict[str, Any],
) -> Path:
    label = normalize_space(str(record["card_label"]))
    card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), config["palette"]["outer"])
    art = fit_art_to_window(raw_dir / raw_image_name(year, label))
    card.paste(art, ART_CUTOUT_BOX[:2], art)
    card = Image.alpha_composite(card, frame)
    draw = ImageDraw.Draw(card)

    palette = config["palette"]
    draw_corner_pips(draw, label=label, suit_symbol=config["suit_symbol"], palette=palette)
    rank_line = normalize_space(str(record.get("rank_line_text") or f"#{label} • {year}"))
    draw_text_block(draw, rank_line, RANK_LINE_BOX, max_size=28, min_size=14, max_lines=1, fill=palette["muted"], bold=True)

    title = normalize_space(str(record.get("headline") or record["song_title"]))
    draw_text_block(draw, title, TITLE_BOX, max_size=30, min_size=14, max_lines=2, fill=palette["text"], bold=True)
    draw_text_block(draw, year, FOOTER_BOX, max_size=24, min_size=14, max_lines=1, fill=palette["muted"], bold=True)

    overlay = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")
    overlay_draw.rounded_rectangle(LIST_BOX, radius=22, fill=config["palette"]["overlay"], outline=palette["line"][:3] + (180,), width=2)
    card = Image.alpha_composite(card, overlay)
    draw = ImageDraw.Draw(card)

    recap_lines = [normalize_space(str(item)) for item in record.get("recap_lines", []) if normalize_space(str(item))]
    if recap_lines:
        inner_left = LIST_BOX[0] + 28
        inner_top = LIST_BOX[1] + 18
        inner_width = LIST_BOX[2] - LIST_BOX[0] - 56
        row_height = 68
        for index, text in enumerate(recap_lines):
            y = inner_top + index * row_height
            draw_text_block(
                draw,
                text,
                (inner_left, y, inner_left + inner_width, y + row_height - 6),
                max_size=20,
                min_size=11,
                max_lines=1,
                fill=palette["text"],
                bold=False,
                align="left",
            )

    output = final_dir / final_image_name(year, label)
    output.parent.mkdir(parents=True, exist_ok=True)
    card.save(output)
    return output


def compose_1978_editorial_year(year: str, config: dict[str, Any], prompt_records: list[dict[str, Any]], only_labels: set[str] | None) -> list[Path]:
    deck_root = Path(config["deck_root"])
    raw_dir = deck_root / "raw"
    final_dir = deck_root / "final"
    frame_path = build_frame(year, config)
    frame = Image.open(frame_path).convert("RGBA")
    by_label = {normalize_space(str(record["card_label"])): record for record in prompt_records}

    outputs: list[Path] = []
    for label in EDITORIAL_1978_CARD_ORDER:
        if only_labels and label not in only_labels:
            continue
        record = by_label.get(label)
        if not record:
            continue
        if label in {"R1", "R2", "R3"}:
            outputs.append(compose_editorial_recap_card(year, config, frame, raw_dir, final_dir, record))
            continue
        outputs.append(compose_editorial_song_card(year, config, frame, raw_dir, final_dir, record))
    return outputs


def compose_year(year: str, config: dict[str, Any], top_40: list[dict[str, Any]], only_labels: set[str] | None) -> list[Path]:
    deck_root = Path(config["deck_root"])
    raw_dir = deck_root / "raw"
    final_dir = deck_root / "final"
    frame_path = build_frame(year, config)
    frame = Image.open(frame_path).convert("RGBA")

    outputs: list[Path] = []
    for song in top_40[:10]:
        label = card_label_for_rank(int(song["rv_rank"]))
        if only_labels and label not in only_labels:
            continue
        outputs.append(compose_number_card(year, config, frame, raw_dir, final_dir, song))

    for label, (start, end) in COURT_RANGES.items():
        if only_labels and label not in only_labels:
            continue
        outputs.append(compose_court_card(year, config, frame, raw_dir, final_dir, label, top_40[start - 1 : end]))
    return outputs


def parse_cli(argv: list[str]) -> tuple[bool, list[str] | None, list[str] | None]:
    force_flag = "--force-rerender"
    years_prefix = "--only-years="
    labels_prefix = "--only-labels="
    force = False
    years: list[str] | None = None
    labels: list[str] | None = None
    unknown: list[str] = []

    for arg in argv:
        if arg == force_flag:
            force = True
            continue
        if arg.startswith(years_prefix):
            selected = [value.strip() for value in arg[len(years_prefix) :].split(",") if value.strip()]
            if not selected:
                raise ValueError("--only-years requires at least one year")
            years = selected
            continue
        if arg.startswith(labels_prefix):
            selected = [value.strip().upper() for value in arg[len(labels_prefix) :].split(",") if value.strip()]
            if not selected:
                raise ValueError("--only-labels requires at least one label")
            normalized: list[str] = []
            for value in selected:
                if value in CARD_ORDER:
                    label = value
                elif value.isdigit():
                    label = str(int(value))
                else:
                    raise ValueError(f"Unsupported card label: {value}")
                if label not in CARD_ORDER:
                    raise ValueError(f"Unsupported card label: {value}")
                if label not in normalized:
                    normalized.append(label)
            labels = normalized
            continue
        unknown.append(arg)

    if unknown:
        raise ValueError(f"Unsupported arguments: {' '.join(unknown)}")
    return force, years, labels


def ensure_years(years: list[str] | None) -> list[str]:
    selected = years or ["1976", "1977"]
    for year in selected:
        if year not in YEAR_CONFIGS:
            raise ValueError(f"Unsupported year: {year}")
    return selected


def expected_raw_paths(year: str, top_40: list[dict[str, Any]], only_labels: set[str] | None, raw_dir: Path) -> list[Path]:
    expected: list[Path] = []
    for song in top_40[:10]:
        label = card_label_for_rank(int(song["rv_rank"]))
        if only_labels and label not in only_labels:
            continue
        expected.append(raw_dir / raw_image_name(year, label))
    for label in COURT_RANGES:
        if only_labels and label not in only_labels:
            continue
        expected.append(raw_dir / raw_image_name(year, label))
    return expected


def build_year(year: str, *, force_rerender: bool, only_labels: set[str] | None) -> list[Path]:
    config = YEAR_CONFIGS[year]
    top_40 = load_top_40(Path(config["top_json"]))
    culture = load_culture(Path(config["culture_json"]))

    deck_root = Path(config["deck_root"])
    raw_dir = deck_root / "raw"
    run_id = str(config["run_id"])
    if only_labels:
        run_id = f"{run_id}_partial_{'-'.join(sorted(only_labels, key=CARD_ORDER.index))}"
    run_dir = ROOT / "runs" / run_id

    prompt_records = build_prompt_records(year, {**config, "run_id": run_id}, top_40, culture, raw_dir, run_dir, only_labels)
    prompts_path = run_dir / "prompts.jsonl"
    config_path = run_dir / "render_config.yaml"
    write_jsonl(prompts_path, prompt_records)
    write_render_config(config_path, run_id, skip_if_image_exists=not force_rerender)

    print(f"[{year}] prompts={len(prompt_records)} -> {prompts_path}")
    render_run(config_path)

    missing_raw = [Path(str(record["image_path"])) for record in prompt_records if not Path(str(record["image_path"])).exists()]
    if missing_raw:
        print("Rendering incomplete — skipping compose stage.")
        return []

    if year == "1978":
        outputs = compose_1978_editorial_year(year, config, prompt_records, only_labels)
    else:
        outputs = compose_year(year, config, top_40, only_labels)
    return outputs


def main() -> None:
    force_rerender, years_arg, labels_arg = parse_cli(sys.argv[1:])
    selected_years = ensure_years(years_arg)
    only_labels = set(labels_arg) if labels_arg else None
    load_openai_api_key()

    all_outputs: list[Path] = []
    for year in selected_years:
        outputs = build_year(year, force_rerender=force_rerender, only_labels=only_labels)
        all_outputs.extend(outputs)

    print("[complete]")
    for path in all_outputs:
        print(path)


if __name__ == "__main__":
    main()
