#!/usr/bin/env python3
"""Shared helpers and CLI entrypoint for the canonical RetroVerse magazine build pipeline."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, replace
from html import escape
from pathlib import Path
from typing import Any

import markdown


PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Repo root: retroverse-magazine -> magazine -> apps -> retroverse
REPO_ROOT = PROJECT_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.satire_patterns import validate_satire_brief

# Import movies data pipeline from main RetroVerse repo (scripts/build_movie_memory_full.py)
try:
    from scripts.build_movie_memory_full import (
        build_movies_charts_page as _build_movies_charts_data,
        build_projection_booth_page as _build_projection_booth_data,
    )
except ImportError as e:
    _build_movies_charts_data = None
    _build_projection_booth_data = None
    _movie_import_error = str(e)

ISSUES_ROOT = PROJECT_ROOT / "issues"
SECTION_TEMPLATE_DIR = PROJECT_ROOT / "templates" / "sections"
PLACEHOLDER_ART_SUBPATH = "assets/placeholder.png"

# TV warehouse: env SCREEN_CULTURE_TV_WAREHOUSE or RETROVERSE_ROOT, else computed from repo root
def _resolve_tv_warehouse_path() -> Path:
    if path := os.environ.get("SCREEN_CULTURE_TV_WAREHOUSE"):
        return Path(path)
    root = Path(os.environ["RETROVERSE_ROOT"]) if os.environ.get("RETROVERSE_ROOT") else REPO_ROOT
    return root / "data" / "raw" / "screen-culture" / "screen-culture" / "warehouse" / "television_by_year.json"


TV_WAREHOUSE_PATH = _resolve_tv_warehouse_path()


def _validate_env_vars() -> list[str]:
    """Validate optional env vars when set. Returns list of error messages."""
    errors: list[str] = []
    if root := os.environ.get("RETROVERSE_ROOT"):
        p = Path(root)
        if not p.exists():
            errors.append(f"RETROVERSE_ROOT={root} does not exist")
        elif not p.is_dir():
            errors.append(f"RETROVERSE_ROOT={root} is not a directory")
    if path := os.environ.get("SCREEN_CULTURE_TV_WAREHOUSE"):
        p = Path(path)
        if not p.exists():
            errors.append(f"SCREEN_CULTURE_TV_WAREHOUSE={path} does not exist")
        elif not p.is_file():
            errors.append(f"SCREEN_CULTURE_TV_WAREHOUSE={path} is not a file")
    return errors


def run_preflight_check(year: int) -> dict[str, str]:
    """
    Verify required data sources and layout before build.
    Returns status dict: {"movies": "OK"|"FAIL", "tv": "OK"|"FAIL", "layout": "OK"|"FAIL", "env": "OK"|"FAIL"}.
    """
    status: dict[str, str] = {"movies": "OK", "tv": "OK", "layout": "OK", "env": "OK"}

    # Env vars
    env_errors = _validate_env_vars()
    if env_errors:
        status["env"] = "FAIL"
        for err in env_errors:
            print(f"  [ENV] {err}", file=sys.stderr)

    # Movies: import + movie_memory.json exists with year data
    movie_memory_path = (
        Path(os.environ["RETROVERSE_ROOT"]) / "data" / "movies" / "movie_memory.json"
        if os.environ.get("RETROVERSE_ROOT")
        else REPO_ROOT / "data" / "movies" / "movie_memory.json"
    )
    if _build_projection_booth_data is None or _build_movies_charts_data is None:
        status["movies"] = "FAIL"
        print(f"  [MOVIES] Movie data pipeline import failed: {_movie_import_error}", file=sys.stderr)
    elif not movie_memory_path.exists():
        status["movies"] = "FAIL"
        print(f"  [MOVIES] movie_memory.json not found: {movie_memory_path}", file=sys.stderr)
    else:
        try:
            data = json.loads(movie_memory_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not data.get(str(year)):
                status["movies"] = "FAIL"
                print(f"  [MOVIES] No data for year {year} in movie_memory.json", file=sys.stderr)
        except (json.JSONDecodeError, OSError) as e:
            status["movies"] = "FAIL"
            print(f"  [MOVIES] Failed to load movie_memory.json: {e}", file=sys.stderr)

    # TV: path exists and is readable
    if not TV_WAREHOUSE_PATH.exists():
        status["tv"] = "FAIL"
        print(f"  [TV] Television warehouse not found: {TV_WAREHOUSE_PATH}", file=sys.stderr)
    elif not TV_WAREHOUSE_PATH.is_file():
        status["tv"] = "FAIL"
        print(f"  [TV] TV path is not a file: {TV_WAREHOUSE_PATH}", file=sys.stderr)
    else:
        try:
            payload = json.loads(TV_WAREHOUSE_PATH.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                status["tv"] = "FAIL"
                print(f"  [TV] television_by_year.json is not a JSON object", file=sys.stderr)
        except (json.JSONDecodeError, OSError) as e:
            status["tv"] = "FAIL"
            print(f"  [TV] Failed to load television_by_year.json: {e}", file=sys.stderr)

    # Layout: expand_layout_pages runs without error
    try:
        assert_canonical_templates_exist()
        top23_rows = load_chart_top23_rows(year)
        canonical = [
            build_section_page(year, pn, sk, top23_rows)
            for pn, sk in enumerate(ISSUE_STRUCTURE, start=1)
        ]
        expanded = expand_layout_pages(year, canonical)
        if len(expanded) < len(ISSUE_STRUCTURE):
            status["layout"] = "FAIL"
            print(f"  [LAYOUT] expand_layout_pages returned {len(expanded)} pages, expected >= {len(ISSUE_STRUCTURE)}", file=sys.stderr)
    except Exception as e:
        status["layout"] = "FAIL"
        print(f"  [LAYOUT] Layout expansion failed: {e}", file=sys.stderr)

    return status

MARKDOWN_EXTENSIONS = ["extra", "tables", "fenced_code", "sane_lists"]
SANITIZE_RENDER_REPLACEMENTS: list[tuple[str, str]] = [
    (r"(?i)\bplaceholder content\.?", "RetroVerse Production Desk"),
    (
        r"(?i)\breplace the placeholder only when year-specific editorial content is ready\.?",
        "Replace this reserve slot when year-specific editorial content is approved.",
    ),
    (
        r"(?i)\b([A-Z][^.]*?) will be added in a later production pass\.?",
        r"\1 is staged here as part of the current editorial build.",
    ),
    (r"(?i)\bcoming soon\b", "scheduled for this issue"),
    (r"(?i)\bto be added\b", "queued for editorial completion"),
    (r"(?i)\blater production pass\b", "current editorial build"),
]

ISSUE_STRUCTURE = [
    "cover",
    "masthead",
    "editor_letter",
    "year_snapshot",
    "charts_overview",
    "top_song_1",
    "top_song_2",
    "top_song_3",
    "top_song_4",
    "top_song_5",
    "top_song_6",
    "top_song_7",
    "top_song_8",
    "top_song_9",
    "top_song_10",
    "movies",
    "projection_booth",
    "movies_charts",
    "television",
    "culture",
    "arcade",
    "retro_ad",
    "comic",
    "puzzle",
    "letters",
    "forgotten_hit",
    "one_hit_wonder",
    "album_spotlight",
    "year_timeline",
    "culture_collage",
    "retro_ads_page",
    "chart_top23",
]

ISSUE_SECTION_CONFIG: dict[str, dict[str, Any]] = {
    "masthead": {
        "source_name": "masthead.md",
        "title": "Masthead",
        "subtitle": "Editorial Staff and Publication Information",
        "layout_type": "department masthead",
        "trim_headings": ("RETROVERSE", "Press ▶ Play for the Past", "Masthead"),
    },
    "editor_letter": {
        "source_name": "editor_letter.md",
        "subtitle": "Letter From the Editor",
        "layout_type": "department letter",
    },
    "charts_overview": {
        "source_name": "charts_overview.md",
        "subtitle": "Top Songs Overview",
        "layout_type": "chart overview",
    },
    "movies": {
        "source_name": "movies.md",
        "subtitle": "Movies of the Year",
        "layout_type": "screen feature",
    },
    "projection_booth": {
        "source_name": "projection_booth.md",
        "subtitle": "From the Projection Booth",
        "layout_type": "projection_booth_editorial",
    },
    "movies_charts": {
        "source_name": "movies_charts.md",
        "subtitle": "Movies & Awards",
        "layout_type": "movies charts page",
    },
    "television": {
        "source_name": "television.md",
        "subtitle": "Television of the Year",
        "layout_type": "screen feature",
    },
    "culture": {
        "source_name": "culture.md",
        "subtitle": "Culture Department",
        "layout_type": "department feature",
    },
    "arcade": {
        "source_name": "arcade.md",
        "subtitle": "Arcade and Technology",
        "layout_type": "department feature",
    },
    "retro_ad": {
        "source_name": "ads.md",
        "title": "Retro Ad",
        "subtitle": "House Advertisement",
        "layout_type": "ad page",
    },
    "comic": {
        "source_name": "comic.md",
        "subtitle": "Comic Page",
        "layout_type": "comic page",
        "collage_folder": "comic",
        "collage_limit": 6,
    },
    "puzzle": {
        "source_name": "puzzle1.md",
        "subtitle": "Puzzle Page",
        "layout_type": "puzzle page",
        "hero_subpath": "parody/trivia_grid.png",
    },
    "letters": {
        "source_name": "letters.md",
        "subtitle": "Reader Mail",
        "layout_type": "department letters",
    },
    "chart_top23": {
        "source_name": "chart_top23.md",
        "title": "RetroVerse Top 23",
        "subtitle": "Year-End Song Ranking",
        "layout_type": "chart page",
        "trim_headings": ("RETROVERSE TOP 23", "The Biggest Songs of the Year"),
    },
}

STORY_SECTION_CONFIG: dict[str, dict[str, Any]] = {
    "forgotten_hit": {
        "story_id": "story_011",
        "fallback_title": "Forgotten Hit",
        "subtitle": "A near-miss worth preserving",
        "layout_type": "feature story",
    },
    "album_spotlight": {
        "story_id": "story_006",
        "fallback_title": "Album Spotlight",
        "subtitle": "Album-scale gravity in the year",
        "layout_type": "feature story",
    },
    "year_timeline": {
        "story_id": "story_010",
        "fallback_title": "Year Timeline",
        "subtitle": "The year in sequence",
        "layout_type": "timeline page",
    },
}

VALID_SATIRE_TYPES = {
    "deadpan_media",
    "fake_institution",
    "character",
    "cultural_exaggeration",
}

VALID_COMIC_PANEL_PURPOSES = {"setup", "build", "escalation", "shift", "punchline"}
COMIC_PANEL_PURPOSE_ORDER = {
    "setup": 0,
    "build": 1,
    "escalation": 2,
    "shift": 3,
    "punchline": 4,
}

SATIRE_TYPE_LABELS = {
    "deadpan_media": "Deadpan Media",
    "fake_institution": "Fake Institution",
    "character": "Character Satire",
    "cultural_exaggeration": "Cultural Exaggeration",
}

TOP_SONG_GROUP_PAGE_RANGES_1978: dict[int, tuple[int, int]] = {
    8: (3, 6),
    9: (7, 10),
}

TOP_SONG_GROUP_PAGE_CONFIG_1978: dict[int, dict[str, str]] = {
    8: {
        "title": "Top Songs #3-#6",
        "subtitle": "Short Takes From the Year's Biggest Singles",
        "deck": (
            "After the Bee Gees set the pace at the top, the chart widens into slow-dance records, "
            "ballroom declarations, and the kind of FM favorites that follow people from the club door "
            "to the ride home."
        ),
        "standout_line": "Soft lights, slow turns, and hooks built to linger.",
    },
    9: {
        "title": "Top Songs #7-#10",
        "subtitle": "Four More Records That Keep 1978 Moving",
        "deck": (
            "The lower half of the Top 10 is no afterthought. These are the records that stretch the year "
            "from theatrical disco sweep to easygoing groove and bass-first commands built to turn a room."
        ),
        "standout_line": "By this point in the Top 10, rhythm is running the room.",
    },
}

TOP_SONG_GROUP_BLURBS_1978: dict[int, str] = {
    3: (
        'Andy Gibb\'s "(Love Is) Thicker Than Water" arrives like the lights dropping a little lower. '
        "You hear it in the slow-dance pocket at clubs, on car radios after the last exit, and in living rooms "
        "where the night is winding down without losing its glow. The record feels warm rather than forceful, "
        "carried by a vocal that leans in instead of reaching out. In a year full of hard pulses and mirror-ball urgency, "
        "it stands out by trusting softness. It makes intimacy feel chart-sized, and that is a rarer trick than people admit."
    ),
    4: (
        '"Three Times A Lady" belongs to banquet rooms, wedding floors, hotel ballrooms, and the middle of the dial '
        "where a formal song can suddenly stop conversation cold. The Commodores play it with enough grace to make every step "
        "feel measured, and Lionel Richie sings it like the room should rise with him. Physically, it is a sway record: shoulders back, "
        "hands together, no rush anywhere in sight. That is exactly why it stands apart in 1978. Where other hits chase the moment, "
        "this one slows it down and makes the sentiment feel expensive."
    ),
    5: (
        '"Kiss You All Over" works best in places with low light and nowhere to be in a hurry: bar booths, parked cars, '
        "FM radio after dark, the dance floor after the crowd has thinned to couples. Exile gives the song a close-range pressure; "
        "it slides forward instead of striking, and that makes it feel more persuasive than loud. You feel it in the way the groove keeps narrowing the space "
        "between the singer and the listener. In a chart year crowded with polished hooks, this one stands out for sheer nerve. "
        "It knows exactly what it wants, and it never disguises it."
    ),
    6: (
        '"Can\'t Smile Without You" is heard where people are listening more carefully than they pretend: kitchen radios before dawn, '
        "car speakers after a date, and soft-lit lounges where the crowd has gone quieter. Barry Manilow sells the song through directness. "
        "There is no mystery in the lyric, and that is the point; the feeling lands immediately, with a melody that stays light on its feet even while the sentiment turns heavy. "
        "Physically, it feels like an exhale. In 1978, that plainspoken tenderness stands out against records built for spectacle. This one wins by sounding personal in public."
    ),
    7: (
        '"MacArthur Park" does not enter a room so much as sweep across it. You hear it under club lights, in car radios cruising boulevards, '
        "and anywhere a DJ wants to turn a single into full-scale drama. Donna Summer gives the record height, but the real thrill is the motion underneath: "
        "strings lifting, rhythm driving, the whole arrangement pushing forward like weather over a city. You feel it in the chest before you sort out the story. "
        "That is why it stands apart this year. Most hits capture a mood; this one builds an entire horizon and then dances across it."
    ),
    8: (
        '"Lay Down Sally" sounds like open windows, roadside bars, convertible radios, and the hour before the night decides what kind of night it will be. '
        "Eric Clapton keeps the groove loose, almost conversational, and that easy roll is the song's advantage. You feel it in the hips more than the feet, a relaxed sway instead of a club command. "
        "Set against 1978's glossy dance records and oversized declarations, it stands out by refusing strain. Nothing is overplayed, nothing forced. The whole track moves like it knows charm works better when it looks effortless."
    ),
    9: (
        '"Shadow Dancing" belongs under mirrored lights, at roller rinks, and on late-night FM when the city outside the windshield looks like streaks of color. '
        "Andy Gibb gives it a sleek, gliding vocal, but the real sensation is the rhythm tracing bodies through the room. It feels side-lit and satin-smooth, the kind of record that makes movement look easier than it is. "
        "That separates it from plenty of louder hits in 1978. \"Shadow Dancing\" does not need to shout to control the floor; it lets shape, glide, and atmosphere do the work."
    ),
    10: (
        '"Boogie Oogie Oogie" announces itself like a DJ dropping the needle at exactly the right second. It is heard in packed clubs, roller rinks, neighborhood parties, '
        "and through open car windows where the bass arrives before the rest of the song. A Taste Of Honey builds the whole thing from that irresistible forward pull, and physically it lands in the knees right away. "
        "People do not debate this record; they answer it. That is why it stands out in a crowded year. The hook is not merely memorable, it is functional. It tells a room what to do and gets immediate results."
    ),
}

SONG_NEW_ARTISTS_1978: list[dict[str, str]] = [
    {
        "artist": "Exile",
        "note": "Close-range slow-burn pressure.",
    },
    {
        "artist": "A Taste Of Honey",
        "note": "Bass-first floor trigger.",
    },
    {
        "artist": "Samantha Sang",
        "note": "Soft-focus FM glide.",
    },
    {
        "artist": "Gerry Rafferty",
        "note": "Sax-lit street sophistication.",
    },
]

MOVIE_PARODY_PANELS_1978: list[dict[str, str | int]] = [
    {
        "rank": 1,
        "title": "Grease",
        "visual": "parking lot / hot rod",
        "visual_token": "CAR",
        "parody_line": "Tell me about it, satin.",
        "setup": "The parking-lot entrance now requires three wardrobe decisions and one comb the size of a prop.",
        "tag": "",
    },
    {
        "rank": 2,
        "title": "Superman",
        "visual": "cape / skyline",
        "visual_token": "CAPE",
        "parody_line": "You'll believe a man can beat the popcorn line.",
        "setup": "Cape confidence meets the one crowd in town that refuses to move for anybody.",
        "tag": "Snack-bar heroics.",
    },
    {
        "rank": 3,
        "title": "Animal House",
        "visual": "toga / keg",
        "visual_token": "KEG",
        "parody_line": "Was it over when the keg ran dry? Not remotely.",
        "setup": "Every campus party in the country suddenly thinks volume is a philosophy.",
        "tag": "Chaos gets tenure.",
    },
    {
        "rank": 4,
        "title": "Heaven Can Wait",
        "visual": "angel desk / valet ticket",
        "visual_token": "HALO",
        "parody_line": "Even the afterlife has a waiting list.",
        "setup": "The calmest premise of the year still ends up stuck in a line with everybody else.",
        "tag": "",
    },
    {
        "rank": 5,
        "title": "Every Which Way But Loose",
        "visual": "pickup / orangutan",
        "visual_token": "APE",
        "parody_line": "Right turn, Clyde. The valet is glaring.",
        "setup": "A brawler, an ape, and a parking problem is somehow still the cleanest premise on the page.",
        "tag": "",
    },
    {
        "rank": 6,
        "title": "Hooper",
        "visual": "stunt ramp / crash car",
        "visual_token": "RAMP",
        "parody_line": "The stunt was fine. The landing wasn't.",
        "setup": "A profession built on swagger discovers that gravity keeps notes.",
        "tag": "",
    },
    {
        "rank": 7,
        "title": "Jaws 2",
        "visual": "fin / beach towel",
        "visual_token": "FIN",
        "parody_line": "You're going to need a larger beach towel.",
        "setup": "The sequel knows the crowd already understands the assignment, so it goes straight for the shoreline panic.",
        "tag": "Sand everywhere.",
    },
    {
        "rank": 8,
        "title": "Halloween",
        "visual": "mask / coatroom phone",
        "visual_token": "MASK",
        "parody_line": "The call is coming from the coatroom.",
        "setup": "Suburban calm walks into one long, quiet hallway and never gets it back.",
        "tag": "Quiet panic.",
    },
    {
        "rank": 9,
        "title": "The Deer Hunter",
        "visual": "bar table / jukebox",
        "visual_token": "BAR",
        "parody_line": "One wrong bet and the jukebox wins.",
        "setup": "The year's heaviest movie turns any ordinary room into a place you suddenly sit up straighter inside.",
        "tag": "",
    },
    {
        "rank": 10,
        "title": "Midnight Express",
        "visual": "corridor / departure board",
        "visual_token": "TRAIN",
        "parody_line": "Tonight's express leaves at last call.",
        "setup": "Claustrophobic momentum, no comfort, and the sense that every exit has already been checked twice.",
        "tag": "",
    },
]

TV_EDITORIAL_NOTES_1978: dict[str, dict[str, str]] = {
    "60 Minutes": {
        "network": "CBS",
        "hook": "The stopwatch still feels like a starting gun.",
        "premise": "A newsmagazine that turned Sunday-night seriousness into appointment television.",
        "why": "It made hard reporting feel like mass-viewing ritual instead of niche homework.",
    },
    "All in the Family": {
        "network": "CBS",
        "hook": "Argument as prime-time engine.",
        "premise": "A living-room battleground where every small remark lands like a weeklong debate starter.",
        "why": "It proved sitcom form could stay broad and still keep the national conversation uncomfortably close.",
    },
    "Angie": {
        "network": "ABC",
        "hook": "Romance with city grit still on the shoes.",
        "premise": "Blue-collar charm and glossy aspiration squeeze into the same half hour.",
        "why": "Its rise showed viewers still wanted warmth, but not without a little class tension in the room.",
    },
    "Dallas": {
        "hook": "Oil, money, and a grin you should not trust.",
        "premise": "Prime-time melodrama turns family dinner into a property dispute with better tailoring.",
        "why": "It announced the appetite for glossy, serialized trouble before the decade was even finished.",
    },
    "Diff'rent Strokes": {
        "hook": "A catchphrase with network velocity.",
        "premise": "Fish-out-of-water family comedy built to land quick laughs and instant recognition.",
        "why": "It arrived already sounding quotable, which is half the battle on television.",
    },
    "Eight Is Enough": {
        "network": "ABC",
        "hook": "Domestic sprawl, handled at full network width.",
        "premise": "Family drama where the household is big enough to carry comedy, conflict, and sentiment at once.",
        "why": "It kept the warm, ensemble side of the schedule alive while flashier shows grabbed headlines.",
    },
    "Laverne & Shirley": {
        "network": "ABC",
        "hook": "Working-girl comedy with elbow room.",
        "premise": "Physical gags, factory-floor rhythm, and a friendship sturdy enough to carry every scene change.",
        "why": "It kept blue-collar sitcom energy bright without sanding off the grit that made it pop.",
    },
    "M*A*S*H": {
        "network": "CBS",
        "hook": "Sharp wit, steady pulse, no wasted line.",
        "premise": "An ensemble that pivots from sarcasm to ache so quickly it barely looks like a pivot at all.",
        "why": "It remained the standard for television that could be funny, sad, and exact in the same breath.",
    },
    "Mork and Mindy": {
        "hook": "Alien velocity in an otherwise normal room.",
        "premise": "One performer turns manic improvisation into a full network event the second he enters frame.",
        "why": "It showed how fast a single comic voice could take over the schedule when the timing was right.",
    },
    "Taxi": {
        "hook": "Night-shift melancholy with punch lines attached.",
        "premise": "A dispatch office full of bruised dreamers, every one of them funnier than their circumstances.",
        "why": "It proved character comedy could stay intimate and still feel instantly essential.",
    },
    "The Ropers": {
        "network": "ABC",
        "hook": "Domestic side-eye in spin-off form.",
        "premise": "Neighborhood comedy powered by suspicion, impatience, and two people never fully sharing the same mood.",
        "why": "It captured television's confidence that a recognizable pair could carry a whole new lane on attitude alone.",
    },
    "Three's Company": {
        "network": "ABC",
        "hook": "Misunderstanding as a weekly athletic event.",
        "premise": "A roommate farce where the premise stays simple and the timing does the heavy lifting.",
        "why": "Its breezy pace made network comedy feel easy, even when every beat depended on precision.",
    },
    "WKRP in Cincinnati": {
        "hook": "Radio panic, finally written by people who understand the booth.",
        "premise": "A workplace comedy where DJs, sales headaches, and on-air disasters all move at music-industry speed.",
        "why": "It translated radio-era cool into television form without losing the workplace friction.",
    },
}


@dataclass(frozen=True)
class IssuePage:
    page_number: int
    filename: str
    page_label: str | None
    title: str
    subtitle: str
    byline: str
    story_id: str
    layout_type: str
    main_html_layout: str
    main_html_pdf: str
    hero_subpath: str | None
    collage_subpaths: list[str]
    marginal_subpaths: list[str]
    sidebar_items: list[str]
    data_points: list[str]
    is_cover: bool = False
    hero_in_main: bool = False


def issue_year_dir(year: int) -> Path:
    return ISSUES_ROOT / str(year)


def final_year_dir(year: int) -> Path:
    return ISSUES_ROOT / str(year) / "articles" / "final"


def issue_markdown_path(year: int, name: str) -> Path:
    return issue_year_dir(year) / name


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> Any | None:
    if not path.exists():
        return None
    return load_json(path)


def load_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "page"


def template_key_for_section(section_key: str) -> str:
    if section_key.startswith("top_song_"):
        return "top_song"
    return section_key


def template_path_for_section(section_key: str) -> Path:
    return SECTION_TEMPLATE_DIR / f"{template_key_for_section(section_key)}.html"


def assert_canonical_templates_exist() -> None:
    missing = [
        str(template_path_for_section(section).relative_to(PROJECT_ROOT))
        for section in ISSUE_STRUCTURE
        if not template_path_for_section(section).exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Missing canonical section templates:\n" + "\n".join(f"- {path}" for path in sorted(set(missing)))
        )


def art_subpath_if_exists(year: int, subpath: str) -> str | None:
    path = issue_year_dir(year) / "art" / subpath
    return subpath if path.exists() else None


def page_art_subpath(year: int, page_number: int) -> str | None:
    return art_subpath_if_exists(year, f"pages/page_{page_number:02d}.png")


def page_art_or_placeholder_subpath(year: int, page_number: int) -> str:
    return page_art_subpath(year, page_number) or PLACEHOLDER_ART_SUBPATH


def repeated_page_art_subpaths(year: int, page_number: int, count: int) -> list[str]:
    subpath = page_art_or_placeholder_subpath(year, page_number)
    return [subpath for _ in range(max(0, count))]


def first_existing_subpath(year: int, folder: str) -> str | None:
    directory = issue_year_dir(year) / "art" / folder
    if not directory.exists():
        return None
    for path in sorted(directory.glob("*")):
        if path.is_file():
            return path.relative_to(issue_year_dir(year) / "art").as_posix()
    return None


def subpaths_from_folder(year: int, folder: str, limit: int | None = None) -> list[str]:
    directory = issue_year_dir(year) / "art" / folder
    if not directory.exists():
        return []
    paths = [path.relative_to(issue_year_dir(year) / "art").as_posix() for path in sorted(directory.glob("*.png"))]
    return paths[:limit] if limit is not None else paths


def choose_marginal_subpaths(year: int, page_number: int, count: int = 2) -> list[str]:
    directory = issue_year_dir(year) / "art" / "marginals"
    if not directory.exists():
        return []
    paths = [path.relative_to(issue_year_dir(year) / "art").as_posix() for path in sorted(directory.glob("*.png"))]
    if not paths:
        return []
    start = (page_number - 1) % len(paths)
    return [paths[(start + index) % len(paths)] for index in range(min(count, len(paths)))]


def normalize_markdown_asset_paths(md_text: str, year: int, mode: str) -> str:
    if mode == "pdf":
        asset_prefix = f"issues/{year}/art/"
        return (
            md_text.replace("](../art/", f"]({asset_prefix}")
            .replace('src="../art/', f'src="{asset_prefix}')
            .replace("='../art/", f"='{asset_prefix}")
        )
    return md_text


def markdown_to_html(md_text: str, year: int, mode: str) -> str:
    normalized = normalize_markdown_asset_paths(md_text, year, mode)
    return markdown.markdown(normalized, extensions=MARKDOWN_EXTENSIONS, output_format="html5")


def sanitize_render_text(text: str) -> str:
    sanitized = text
    for pattern, replacement in SANITIZE_RENDER_REPLACEMENTS:
        sanitized = re.sub(pattern, replacement, sanitized)
    return sanitized


def extract_title_byline_and_body(md_text: str, fallback_title: str, fallback_byline: str) -> tuple[str, str, str]:
    lines = md_text.splitlines()
    title = fallback_title
    byline = fallback_byline
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        if line:
            if line.startswith("# "):
                title = line[2:].strip() or fallback_title
                index += 1
            break
        index += 1

    while index < len(lines) and not lines[index].strip():
        index += 1

    if index < len(lines):
        line = lines[index].strip()
        if line.startswith("*") and line.endswith("*") and len(line) > 2:
            byline = line.strip("*").strip() or fallback_byline
            index += 1

    while index < len(lines) and not lines[index].strip():
        index += 1

    body = "\n".join(lines[index:]).strip()
    return title, byline, body


def strip_leading_headings(md_text: str, headings: tuple[str, ...]) -> str:
    if not headings:
        return md_text.strip()

    body_lines = md_text.splitlines()
    trimmed = {heading.strip().lower() for heading in headings if heading.strip()}

    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    while body_lines:
        match = re.match(r"^#{1,6}\s+(.*)$", body_lines[0].strip())
        if not match:
            break
        heading = match.group(1).strip().lower()
        if heading not in trimmed:
            break
        body_lines.pop(0)
        while body_lines and not body_lines[0].strip():
            body_lines.pop(0)

    return "\n".join(body_lines).strip()


def extract_section_markdown(md_text: str, heading: str) -> str:
    lines = md_text.splitlines()
    collected: list[str] = []
    in_section = False

    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            if in_section:
                break
            in_section = stripped == f"## {heading}"
            continue
        if in_section:
            collected.append(raw_line)

    return "\n".join(collected).strip()


def extract_section_bullets(md_text: str, heading: str) -> list[str]:
    section_md = extract_section_markdown(md_text, heading)
    bullets: list[str] = []
    for line in section_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def first_paragraph(md_text: str) -> str:
    for part in re.split(r"\n{2,}", md_text.strip()):
        compact = " ".join(part.split())
        if compact and not compact.startswith("#"):
            return compact
    return ""


def parse_chart_top23_rows(md_text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in md_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "Song Title" not in md_text:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 6:
            continue
        if cells[0].lower() == "rank":
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(
            {
                "rank": cells[0],
                "song": cells[1],
                "artist": cells[2],
                "weeks": cells[3],
                "peak": cells[4],
                "score": cells[5],
            }
        )
    return rows


def load_chart_top23_rows(year: int) -> list[dict[str, str]]:
    md_text = load_text_if_exists(issue_markdown_path(year, "chart_top23.md"))
    if not md_text:
        return []
    return parse_chart_top23_rows(md_text)


def load_enriched_top_songs(year: int) -> list[dict[str, Any]]:
    payload = load_year_context(year)
    songs = payload.get("top_songs")
    if not isinstance(songs, list):
        return []
    return [song for song in songs if isinstance(song, dict)]


def load_year_context(year: int) -> dict[str, Any]:
    for suffix in ("_context_enriched.json", "_context.json"):
        payload = load_json_if_exists(ISSUES_ROOT / "context" / f"{year}{suffix}")
        if isinstance(payload, dict):
            return payload
    return {}


def asset_path_for_mode(year: int, subpath: str | None, mode: str) -> str:
    if not subpath:
        return ""
    return layout_asset_path(subpath) if mode == "layout" else pdf_asset_path(year, subpath)


def lookup_key(value: str) -> str:
    normalized = value.lower().replace("&", "and")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return normalized.strip()


def top_song_entry_by_rank(year: int, rank: int) -> dict[str, Any]:
    for song in load_enriched_top_songs(year):
        if int(song.get("rank") or 0) == rank:
            return song
    return {}


def top23_poster_art_subpath(year: int, page_number: int) -> str:
    direct = page_art_subpath(year, page_number)
    if direct:
        return direct

    pages_dir = issue_year_dir(year) / "art" / "pages"
    if pages_dir.exists():
        for pattern in ("*top_songs*.png", "*music*.png"):
            matches = sorted(pages_dir.glob(pattern))
            if matches:
                return matches[0].relative_to(issue_year_dir(year) / "art").as_posix()
    return PLACEHOLDER_ART_SUBPATH


def load_tv_reference_rows(year: int) -> list[dict[str, Any]]:
    if not TV_WAREHOUSE_PATH.exists():
        raise FileNotFoundError(
            f"Television warehouse not found: {TV_WAREHOUSE_PATH}. "
            "Set RETROVERSE_ROOT or SCREEN_CULTURE_TV_WAREHOUSE if using a custom path."
        )
    try:
        payload = load_json(TV_WAREHOUSE_PATH)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"television_by_year.json at {TV_WAREHOUSE_PATH} is not valid JSON: {e}"
        ) from e
    if not isinstance(payload, dict):
        raise ValueError(
            f"television_by_year.json at {TV_WAREHOUSE_PATH} is not a JSON object. "
            "Expected a dict keyed by year."
        )

    raw_rows = payload.get(str(year))
    if not isinstance(raw_rows, list):
        return []

    issue_context = load_year_context(year)
    issue_rows = issue_context.get("television")
    note_lookup: dict[str, dict[str, Any]] = {}
    if isinstance(issue_rows, list):
        for entry in issue_rows:
            if not isinstance(entry, dict):
                continue
            title = str(entry.get("title") or "").strip()
            if title:
                note_lookup[lookup_key(title)] = entry

    merged_rows: list[dict[str, Any]] = []
    for row in raw_rows:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "").strip()
        if not title or title.upper() == title and len(title) <= 4:
            continue
        lookup = note_lookup.get(lookup_key(title), {})
        merged = dict(row)
        if lookup and not merged.get("network"):
            merged["network"] = lookup.get("network")
        if lookup and lookup.get("note"):
            merged["issue_note"] = lookup.get("note")
        merged_rows.append(merged)

    def rank_value(entry: dict[str, Any]) -> int:
        signals = entry.get("viewership_signals")
        if isinstance(signals, dict):
            for key in ("issue_rank", "year_master_rank"):
                value = signals.get(key)
                if isinstance(value, int):
                    return value
        return 999

    return sorted(merged_rows, key=lambda item: (rank_value(item), str(item.get("title") or "")))[:16]


def page_brief_path(year: int, page_number: int, section_key: str) -> Path:
    return issue_year_dir(year) / "layout" / "page_briefs" / f"page_{page_number:02d}_{section_key}.json"


def load_page_brief_if_exists(year: int, page_number: int, section_key: str) -> dict[str, Any] | None:
    payload = load_json_if_exists(page_brief_path(year, page_number, section_key))
    return payload if isinstance(payload, dict) else None


def brief_text_block_content(brief: dict[str, Any], block_id: str) -> str:
    text_blocks = brief.get("text_blocks")
    if not isinstance(text_blocks, list):
        return ""
    for block in text_blocks:
        if not isinstance(block, dict):
            continue
        if str(block.get("id") or "").strip() != block_id:
            continue
        return str(block.get("content") or "").strip()
    return ""


def comic_asset_path(year: int, subpath: str | None, mode: str) -> str:
    if not subpath:
        return ""
    if subpath.startswith("assets/"):
        return f"../../../{subpath}" if mode == "layout" else subpath
    return f"../art/{subpath}" if mode == "layout" else f"issues/{year}/art/{subpath}"


def normalize_comic_panel_subpath(year: int, image_value: str) -> str:
    value = image_value.strip()
    issue_prefix = f"issues/{year}/art/"
    if value.startswith(issue_prefix):
        value = value[len(issue_prefix):]
    elif value.startswith("art/"):
        value = value[len("art/"):]
    path = issue_year_dir(year) / "art" / value
    if path.exists():
        return value
    return PLACEHOLDER_ART_SUBPATH


def normalize_comic_panel_dialogue(panel: dict[str, Any]) -> list[str]:
    dialogue_raw = panel.get("dialogue")
    if isinstance(dialogue_raw, list):
        return [str(item).strip() for item in dialogue_raw if str(item).strip()]
    if dialogue_raw:
        line = str(dialogue_raw).strip()
        return [line] if line else []
    return []


def comic_caption_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def normalize_comic_panel_arc(brief: dict[str, Any], panel_count: int) -> list[dict[str, str]]:
    raw = brief.get("panel_arc")
    if not isinstance(raw, list):
        return []

    entries: list[dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Comic panel_arc entry {index} must be an object.")
        beat = str(item.get("beat") or "").strip().lower()
        summary = str(item.get("summary") or "").strip()
        if beat not in VALID_COMIC_PANEL_PURPOSES:
            raise ValueError(f"Comic panel_arc entry {index} has invalid beat: {beat or 'missing'}")
        entries.append({"beat": beat, "summary": summary})

    if len(entries) != panel_count:
        raise ValueError("Comic panel_arc must match the number of panels.")
    if entries[0]["beat"] != "setup":
        raise ValueError("Comic panel_arc must begin with a setup beat.")
    if entries[-1]["beat"] != "punchline":
        raise ValueError("Comic panel_arc must end with a punchline beat.")
    missing = [beat for beat in ("build", "escalation", "shift") if beat not in {entry["beat"] for entry in entries}]
    if missing:
        raise ValueError(f"Comic panel_arc is missing required beats: {', '.join(missing)}")
    return entries


def validate_and_normalize_comic_panels(brief: dict[str, Any], panels_raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    panels = [panel for panel in panels_raw if isinstance(panel, dict)]
    if not 4 <= len(panels) <= 6:
        raise ValueError("Comic pages must define between 4 and 6 panels.")

    arc_entries = normalize_comic_panel_arc(brief, len(panels))
    normalized: list[dict[str, Any]] = []
    previous_order = -1
    seen_required_beats: set[str] = set()

    for index, panel in enumerate(panels, start=1):
        purpose = str(panel.get("purpose") or "").strip().lower()
        if purpose not in VALID_COMIC_PANEL_PURPOSES:
            raise ValueError(f"Comic panel {index} has invalid purpose: {purpose or 'missing'}")
        if arc_entries and purpose != arc_entries[index - 1]["beat"]:
            raise ValueError(f"Comic panel {index} purpose does not match panel_arc.")
        purpose_order = COMIC_PANEL_PURPOSE_ORDER[purpose]
        if purpose_order < previous_order:
            raise ValueError("Comic panel purposes must progress from setup to build to escalation to shift to punchline.")
        previous_order = purpose_order
        if purpose in {"build", "escalation", "shift"}:
            seen_required_beats.add(purpose)

        scene = str(panel.get("scene") or "").strip()
        visual_description = str(panel.get("visual_description") or "").strip()
        caption = str(panel.get("caption") or "").strip()
        heading = str(panel.get("heading") or f"Panel {index}").strip()
        image = str(panel.get("image") or "").strip()
        dialogue = normalize_comic_panel_dialogue(panel)

        if not scene:
            raise ValueError(f"Comic panel {index} is missing `scene`.")
        if not visual_description:
            raise ValueError(f"Comic panel {index} is missing `visual_description`.")
        if not (caption or dialogue):
            raise ValueError(f"Comic panel {index} must include caption or dialogue.")
        if caption and comic_caption_word_count(caption) > 10:
            raise ValueError(f"Comic panel {index} caption exceeds 10 words.")
        if len(dialogue) > 2:
            raise ValueError(f"Comic panel {index} has more than 2 dialogue lines.")

        normalized.append(
            {
                "heading": heading,
                "image": image,
                "scene": scene,
                "visual_description": visual_description,
                "caption": caption,
                "dialogue": dialogue,
                "purpose": purpose,
            }
        )

    if normalized[0]["purpose"] != "setup":
        raise ValueError("Comic sequence must begin with a setup panel.")
    if normalized[-1]["purpose"] != "punchline":
        raise ValueError("Comic sequence must end with a punchline panel.")
    if arc_entries:
        missing = [beat for beat in ("build", "escalation", "shift") if beat not in seen_required_beats]
        if missing:
            raise ValueError(f"Comic sequence must include: {', '.join(missing)}.")
    elif len(normalized) > 2 and "escalation" not in seen_required_beats:
        raise ValueError("Comic sequence must include at least one escalation panel before the punchline.")

    return normalized


def render_comic_panels_html(year: int, panels: list[dict[str, Any]], mode: str) -> str:
    panel_tags: list[str] = []
    for index, panel in enumerate(panels, start=1):
        image_value = str(panel.get("image") or "").strip()
        caption = str(panel.get("caption") or "").strip()
        purpose = str(panel.get("purpose") or "").strip().lower() or "setup"
        dialogue_lines = normalize_comic_panel_dialogue(panel)
        panel_type = "dialogue" if dialogue_lines else "caption"
        image_subpath = normalize_comic_panel_subpath(year, image_value) if image_value else PLACEHOLDER_ART_SUBPATH
        src = comic_asset_path(year, image_subpath, mode)
        alt_text = str(panel.get("visual_description") or panel.get("scene") or panel.get("heading") or f"Panel {index}")
        dialogue_html = ""
        if dialogue_lines:
            lines = "".join(f"<p>{escape(line)}</p>" for line in dialogue_lines)
            dialogue_html = f"<div class=\"comic-dialogue\">{lines}</div>"
        caption_html = (
            f"<div class=\"comic-caption-box\"><p class=\"comic-caption\">{escape(caption)}</p></div>"
            if caption
            else ""
        )
        panel_tags.append(
            f"<article class=\"comic-panel comic-panel-{escape(purpose)}\">"
            f"<figure class=\"comic-panel-art\"><img src=\"{escape(src)}\" alt=\"{escape(alt_text)}\" /></figure>"
            "<div class=\"comic-panel-copy\">"
            f"{dialogue_html}"
            f"{caption_html}"
            "</div>"
            f"<p class=\"comic-panel-type sr-only\">{escape(purpose)} / {escape(panel_type)}</p>"
            "</article>"
        )
    return "<section class=\"comic-panel-grid\">" + "".join(panel_tags) + "</section>"


def build_comic_page_from_brief(
    year: int,
    page_number: int,
    section_key: str,
    brief: dict[str, Any],
) -> IssuePage | None:
    page_format = str(brief.get("format") or "").strip().lower()
    if page_format != "comic":
        return None

    panels_raw = brief.get("panels")
    if not isinstance(panels_raw, list):
        return None
    panels = validate_and_normalize_comic_panels(brief, panels_raw)

    title = str(brief.get("title") or "Comic Page").strip()
    subtitle = str(brief.get("subtitle") or "Comic Page").strip()
    writer = brief.get("writer") if isinstance(brief.get("writer"), dict) else {}
    byline = str(writer.get("byline") or writer.get("name") or "RetroVerse Production Desk").strip()
    panels_layout_html = render_comic_panels_html(year, panels, "layout")
    panels_pdf_html = render_comic_panels_html(year, panels, "pdf")
    layout_html = f"<section class=\"comic-feature\">{panels_layout_html}</section>"
    pdf_html = f"<section class=\"comic-feature\">{panels_pdf_html}</section>"

    return build_page(
        year,
        page_number,
        section_key,
        title=title,
        subtitle=subtitle,
        byline=byline,
        body_layout_html=layout_html,
        body_pdf_html=pdf_html,
        layout_type="comic page",
    )


def build_page(
    year: int,
    page_number: int,
    section_key: str,
    *,
    page_label: str | None = None,
    title: str,
    subtitle: str,
    byline: str,
    body_layout_html: str,
    body_pdf_html: str,
    layout_type: str,
    hero_subpath: str | None = None,
    collage_subpaths: list[str] | None = None,
    marginal_subpaths: list[str] | None = None,
    sidebar_items: list[str] | None = None,
    data_points: list[str] | None = None,
    is_cover: bool = False,
    hero_in_main: bool = False,
) -> IssuePage:
    return IssuePage(
        page_number=page_number,
        filename=f"page_{page_number:02d}_{section_key}.html",
        page_label=page_label,
        title=title,
        subtitle=subtitle,
        byline=byline,
        story_id=section_key,
        layout_type=layout_type,
        main_html_layout=body_layout_html,
        main_html_pdf=body_pdf_html,
        hero_subpath=hero_subpath,
        collage_subpaths=collage_subpaths or [],
        marginal_subpaths=marginal_subpaths if marginal_subpaths is not None else choose_marginal_subpaths(year, page_number),
        sidebar_items=sidebar_items or [],
        data_points=data_points or [],
        is_cover=is_cover,
        hero_in_main=hero_in_main,
    )


def build_page_from_markdown(
    year: int,
    page_number: int,
    section_key: str,
    md_text: str,
    *,
    fallback_title: str,
    fallback_byline: str = "",
    subtitle: str = "",
    layout_type: str,
    title_override: str | None = None,
    byline_override: str | None = None,
    hero_subpath: str | None = None,
    collage_subpaths: list[str] | None = None,
    sidebar_items: list[str] | None = None,
    data_points_heading: str | None = None,
    trim_headings: tuple[str, ...] = (),
    is_cover: bool = False,
    hero_in_main: bool = False,
) -> IssuePage:
    md_text = sanitize_render_text(md_text)
    title, byline, body_md = extract_title_byline_and_body(md_text, fallback_title, fallback_byline)
    body_md = strip_leading_headings(body_md, trim_headings)
    if title_override is not None:
        title = title_override
    if byline_override is not None:
        byline = byline_override
    data_points = extract_section_bullets(body_md, data_points_heading) if data_points_heading else []
    return build_page(
        year,
        page_number,
        section_key,
        title=title,
        subtitle=subtitle,
        byline=byline,
        body_layout_html=markdown_to_html(body_md, year, "layout"),
        body_pdf_html=markdown_to_html(body_md, year, "pdf"),
        layout_type=layout_type,
        hero_subpath=hero_subpath,
        collage_subpaths=collage_subpaths,
        sidebar_items=sidebar_items,
        data_points=data_points,
        is_cover=is_cover,
        hero_in_main=hero_in_main,
    )


def build_placeholder_page(
    year: int,
    page_number: int,
    section_key: str,
    *,
    title: str,
    subtitle: str,
    hero_subpath: str | None = None,
    sidebar_items: list[str] | None = None,
    collage_subpaths: list[str] | None = None,
) -> IssuePage:
    md_text = (
        f"# {title}\n"
        "*RetroVerse Production Desk*\n\n"
        "This page slot is part of the canonical RetroVerse issue structure.\n\n"
        f"The `{section_key}` section is wired into the build pipeline and currently holds a reserve editorial slot for {year}.\n\n"
        "## Production Note\n"
        "- Keep this slot in the issue order.\n"
        "- Replace this reserve slot when year-specific editorial content is approved.\n"
    )
    return build_page_from_markdown(
        year,
        page_number,
        section_key,
        md_text,
        fallback_title=title,
        subtitle=subtitle,
        layout_type=f"{template_key_for_section(section_key)} reserve page",
        hero_subpath=hero_subpath,
        sidebar_items=sidebar_items,
        collage_subpaths=collage_subpaths,
        data_points_heading="Production Note",
    )


def build_cover_page(year: int, page_number: int, top23_rows: list[dict[str, str]]) -> IssuePage:
    md_text = load_text_if_exists(issue_markdown_path(year, "cover.md")) or ""
    teasers = extract_section_bullets(md_text, "Cover Teasers")
    illustration_note = first_paragraph(extract_section_markdown(md_text, "Cover Illustration Description"))
    lead_row = top23_rows[0] if top23_rows else None
    lead_line = ""
    if lead_row:
        lead_line = (
            f"<p class=\"deck\">Led by No. {escape(lead_row['rank'])} "
            f"{escape(lead_row['song'])} by {escape(lead_row['artist'])}, "
            f"the {year} issue closes with the full RetroVerse Top 23.</p>"
        )
    items = "".join(f"<li>{escape(item)}</li>" for item in teasers)
    illustration_html = (
        f"<p><strong>Cover Illustration:</strong> {escape(illustration_note)}</p>" if illustration_note else ""
    )
    body_html = (
        f"{lead_line}"
        "<h3>Inside This Issue</h3>"
        f"<ol class=\"contents-list\">{items}</ol>"
        f"{illustration_html}"
    )
    hero_subpath = page_art_or_placeholder_subpath(year, page_number)
    return build_page(
        year,
        page_number,
        "cover",
        title=str(year),
        subtitle="Annual Issue",
        byline="",
        body_layout_html=body_html,
        body_pdf_html=body_html,
        layout_type="cover",
        hero_subpath=hero_subpath,
        sidebar_items=[],
        data_points=[],
        is_cover=True,
        hero_in_main=True,
    )


def build_issue_markdown_section(year: int, page_number: int, section_key: str) -> IssuePage:
    config = ISSUE_SECTION_CONFIG[section_key]
    md_text = load_text_if_exists(issue_markdown_path(year, str(config["source_name"])))
    if not md_text:
        return build_placeholder_page(
            year,
            page_number,
            section_key,
            title=str(config.get("title") or section_key.replace("_", " ").title()),
            subtitle=str(config.get("subtitle", "")),
            hero_subpath=art_subpath_if_exists(year, str(config.get("hero_subpath", "")).strip())
            if config.get("hero_subpath")
            else None,
        )

    collage_subpaths: list[str] = []
    folder = str(config.get("collage_folder", "")).strip()
    if folder:
        limit = int(config.get("collage_limit", 0)) or None
        tile_count = len(subpaths_from_folder(year, folder, limit)) or (limit or 1)
        collage_subpaths = repeated_page_art_subpaths(year, page_number, tile_count)

    hero_subpath = None if collage_subpaths else page_art_or_placeholder_subpath(year, page_number)
    hero_in_main = section_key in {"masthead", "chart_top23"}

    return build_page_from_markdown(
        year,
        page_number,
        section_key,
        md_text,
        fallback_title=str(config.get("title") or section_key.replace("_", " ").title()),
        fallback_byline=str(config.get("byline", "")),
        subtitle=str(config.get("subtitle", "")),
        layout_type=str(config.get("layout_type", template_key_for_section(section_key))),
        title_override=str(config["title"]) if "title" in config else None,
        byline_override=str(config["byline"]) if "byline" in config else None,
        hero_subpath=hero_subpath,
        collage_subpaths=collage_subpaths,
        trim_headings=tuple(config.get("trim_headings", ())),
        hero_in_main=hero_in_main,
    )


def build_year_snapshot_page(year: int, page_number: int, top23_rows: list[dict[str, str]]) -> IssuePage:
    editorial = load_json_if_exists(issue_year_dir(year) / "data" / "editorial.json") or {}
    feature_story = editorial.get("feature_story", {}) if isinstance(editorial, dict) else {}
    headline = str(feature_story.get("headline", f"{year} in Motion")).strip()
    byline = str(feature_story.get("byline", "By RetroVerse Desk")).strip()
    paragraphs = feature_story.get("paragraphs", [])
    if not isinstance(paragraphs, list):
        paragraphs = []
    quick_rows = top23_rows[:3]
    quick_signals = "\n".join(
        f"- No. {row['rank']}: {row['song']} - {row['artist']} ({row['weeks']} weeks, peak {row['peak']}, score {row['score']})"
        for row in quick_rows
    )
    quote = str(feature_story.get("quote", "")).strip()
    quote_block = f"\n> {quote}\n" if quote else ""
    intro = "\n\n".join(str(paragraph).strip() for paragraph in paragraphs[:3] if str(paragraph).strip())
    if not intro:
        intro = (
            f"{year} moves between radio momentum, marquee-size spectacle, and living-room ritual.\n\n"
            "The canonical issue structure keeps those signals in one fixed editorial sequence."
        )
    md_text = (
        f"# Year Snapshot: {headline}\n"
        f"*{byline}*\n\n"
        f"{intro}\n\n"
        "## Quick Signals\n"
        f"{quick_signals or '- Chart snapshot pending.'}\n"
        f"{quote_block}"
    )
    sidebar_items = feature_story.get("sidebar_facts", [])
    if not isinstance(sidebar_items, list):
        sidebar_items = []
    return build_page_from_markdown(
        year,
        page_number,
        "year_snapshot",
        md_text,
        fallback_title=f"Year Snapshot {year}",
        subtitle="The year at a glance",
        layout_type="snapshot page",
        hero_subpath=page_art_or_placeholder_subpath(year, page_number),
        sidebar_items=[str(item) for item in sidebar_items if str(item).strip()],
        data_points_heading="Quick Signals",
    )


def build_top_song_page(
    year: int,
    page_number: int,
    section_key: str,
    rank: int,
    top23_rows: list[dict[str, str]],
) -> IssuePage:
    song_path = issue_year_dir(year) / "songs" / f"{rank:02d}.md"
    md_text = load_text_if_exists(song_path)
    hero_subpath = page_art_or_placeholder_subpath(year, page_number)

    if md_text:
        return build_page_from_markdown(
            year,
            page_number,
            section_key,
            md_text,
            fallback_title=f"Top Song {rank}",
            subtitle=f"Top Song #{rank}",
            layout_type="top song page",
            hero_subpath=hero_subpath,
            data_points_heading="Data Snapshot",
        )

    if rank <= len(top23_rows):
        row = top23_rows[rank - 1]
        md_text = (
            f"# {row['rank']}. {row['song']} - {row['artist']}\n"
            "*By RetroVerse Music Desk*\n\n"
            f"{row['song']} holds position No. {row['rank']} in the RetroVerse {year} Top 23.\n\n"
            "## Data Snapshot\n"
            f"- Artist: {row['artist']}\n"
            f"- Weeks on chart: {row['weeks']}\n"
            f"- Peak position: #{row['peak']}\n"
            f"- RetroVerse yearly score: {row['score']}\n"
        )
        return build_page_from_markdown(
            year,
            page_number,
            section_key,
            md_text,
            fallback_title=f"Top Song {rank}",
            subtitle=f"Top Song #{rank}",
            layout_type="top song page",
            hero_subpath=hero_subpath,
            data_points_heading="Data Snapshot",
        )

    return build_placeholder_page(
        year,
        page_number,
        section_key,
        title=f"Top Song {rank}",
        subtitle=f"Top Song #{rank}",
        hero_subpath=hero_subpath,
    )


def build_top_songs_group_page(year: int, page_number: int) -> IssuePage | None:
    page_range = TOP_SONG_GROUP_PAGE_RANGES_1978.get(page_number)
    page_config = TOP_SONG_GROUP_PAGE_CONFIG_1978.get(page_number)
    if year != 1978 or not page_range or not page_config:
        return None

    songs = load_enriched_top_songs(year)
    songs_by_rank = {
        int(song["rank"]): song
        for song in songs
        if isinstance(song.get("rank"), int)
    }
    start_rank, end_rank = page_range
    selected_ranks = list(range(start_rank, end_rank + 1))
    selected_songs = [songs_by_rank[rank] for rank in selected_ranks if rank in songs_by_rank]
    if len(selected_songs) != len(selected_ranks):
        return None

    cards: list[str] = []
    data_points: list[str] = []
    for song in selected_songs:
        rank = int(song["rank"])
        title = str(song.get("title") or "").strip()
        artist = str(song.get("artist") or "").strip()
        weeks = str(song.get("weeks_on_chart") or song.get("weeks") or "").strip()
        peak = str(song.get("peak") or "").strip()
        notable_fact = str(song.get("notable_fact") or "").strip()
        blurb = TOP_SONG_GROUP_BLURBS_1978.get(rank, "").strip()
        if not (title and artist and blurb):
            return None

        card_classes = ["data-card", "song-card", f"song-card-rank-{rank:02d}"]
        if page_number == 8 and rank == 3:
            card_classes.append("lead-song-card")
        cards.append(
            f"<article class=\"{' '.join(card_classes)}\">"
            f"<p class=\"section-label\">No. {rank:02d}</p>"
            f"<h3>{escape(title)}</h3>"
            f"<p class=\"credit\">{escape(artist)} • {escape(weeks)} weeks • peak #{escape(peak)}</p>"
            f"<p>{escape(blurb)}</p>"
            "</article>"
        )
        fact_suffix = f" {notable_fact}" if notable_fact else ""
        data_points.append(f"No. {rank}: {title} — {artist} ({weeks} weeks, peak #{peak}).{fact_suffix}")

    standout_line = page_config.get("standout_line", "").strip()
    standout_html = (
        f"<blockquote class=\"pull-quote spread-quote\">{escape(standout_line)}</blockquote>"
        if standout_line
        else ""
    )
    spread_class = f"top-songs-spread-page-{page_number:02d}"
    grid_class = f"top-songs-grid-page-{page_number:02d}"
    body_html = (
        f"<section class=\"top-songs-spread {spread_class}\">"
        f"<p class=\"deck\">{escape(page_config['deck'])}</p>"
        f"{standout_html}"
        f"<section class=\"data-card-grid top-songs-grid {grid_class}\">"
        f"{''.join(cards)}"
        "</section>"
        "</section>"
    )
    return build_page(
        year,
        page_number,
        "top_songs_group",
        title=page_config["title"],
        subtitle=page_config["subtitle"],
        byline="By Bob Jones, Music Features Editor",
        body_layout_html=body_html,
        body_pdf_html=body_html,
        layout_type="grouped top songs page",
        hero_subpath=page_art_or_placeholder_subpath(year, page_number),
        data_points=data_points,
        hero_in_main=True,
    )


def song_new_artist_entries(year: int, top23_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if year == 1978:
        return SONG_NEW_ARTISTS_1978

    seen: set[str] = set()
    entries: list[dict[str, str]] = []
    for row in top23_rows:
        artist = str(row.get("artist") or "").strip()
        if not artist or artist in seen:
            continue
        seen.add(artist)
        entries.append(
            {
                "artist": artist,
                "note": f"{artist} breaks through the year-end ranking with {row.get('song', 'a major single')}.",
            }
        )
        if len(entries) == 4:
            break
    return entries


def music_moment_lines(year: int, top23_rows: list[dict[str, str]]) -> list[str]:
    context = load_year_context(year)
    album_dynamics = context.get("album_dynamics") if isinstance(context.get("album_dynamics"), dict) else {}
    sonic_profile = context.get("sonic_profile") if isinstance(context.get("sonic_profile"), dict) else {}
    top_artists = context.get("top_artists") if isinstance(context.get("top_artists"), list) else []
    chart_dynamics = context.get("chart_dynamics") if isinstance(context.get("chart_dynamics"), dict) else {}

    moments: list[str] = []

    longest_number_one_runs = album_dynamics.get("longest_number_one_runs")
    if isinstance(longest_number_one_runs, list):
        first_album = next((item for item in longest_number_one_runs if isinstance(item, dict)), None)
        if first_album:
            album = str(first_album.get("album") or "The leading LP").strip()
            weeks = str(first_album.get("weeks_on_chart") or "").strip()
            moments.append(f"{album}: {weeks} weeks on the LP wall.")
        grease_album = next(
            (item for item in longest_number_one_runs if isinstance(item, dict) and "grease" in str(item.get("album") or "").lower()),
            None,
        )
        if grease_album:
            moments.append("Grease: theater traffic turned singalong spillover.")

    danceable = sonic_profile.get("danceable_tracks_percent")
    dominant_mood = str(sonic_profile.get("dominant_mood") or "").strip()
    if isinstance(danceable, int):
        moments.append(f"{danceable}% danceable; the room stayed {dominant_mood or 'upbeat'}.")

    if isinstance(top_artists, list) and len(top_artists) >= 2:
        leaders = [
            f"{str(item.get('artist') or '').strip()} ({str(item.get('song_count') or '').strip()} entries)"
            for item in top_artists[:2]
            if isinstance(item, dict) and str(item.get("artist") or "").strip()
        ]
        if leaders:
            moments.append("Repeat hitters: " + ", ".join(leaders) + ".")

    if isinstance(chart_dynamics.get("longest_chart_runs"), list):
        long_run = next((item for item in chart_dynamics["longest_chart_runs"] if isinstance(item, dict)), None)
        if long_run:
            title = str(long_run.get("title") or "").strip()
            weeks = str(long_run.get("weeks") or "").strip()
            moments.append(f"{title}: {weeks} weeks, pure radio stamina.")

    return moments[:4]


def fastest_riser_lines(year: int) -> list[str]:
    context = load_year_context(year)
    chart_dynamics = context.get("chart_dynamics") if isinstance(context.get("chart_dynamics"), dict) else {}
    rows = chart_dynamics.get("fastest_risers") if isinstance(chart_dynamics.get("fastest_risers"), list) else []
    lines: list[str] = []
    for item in rows[:4]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        artist = str(item.get("artist") or "").strip()
        if title and artist:
            lines.append(f"{title} / {artist}")
    return lines


def scene_cue_line(text: str) -> str:
    cleaned = re.sub(r"^Use it for\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = cleaned.replace(" or any scene where the city and the beat feel locked together.", "")
    parts = [part.strip(" .") for part in cleaned.split(",") if part.strip()]
    return " • ".join(parts[:3])


def render_chart_top23_poster_html(year: int, page_number: int, top23_rows: list[dict[str, str]], mode: str) -> str:
    lead_row = top23_rows[0] if top23_rows else {}
    lead_song = top_song_entry_by_rank(year, 1)
    lead_title = str(lead_song.get("title") or lead_row.get("song") or "No. 1").strip()
    lead_artist = str(lead_song.get("artist") or lead_row.get("artist") or "").strip()
    lead_weeks = str(lead_song.get("weeks_on_chart") or lead_song.get("weeks") or lead_row.get("weeks") or "").strip()
    lead_peak = str(lead_song.get("peak") or lead_row.get("peak") or "").strip()
    lead_fact = str(lead_song.get("notable_fact") or "").strip()
    scene_use = scene_cue_line(str(lead_song.get("scene_use") or "").strip())
    spotlight_chips = [
        f"{lead_weeks} weeks" if lead_weeks else "",
        f"peak #{lead_peak}" if lead_peak else "",
        "No. 1 all year long" if lead_peak == "1" else "",
    ]
    spotlight_chips = [item for item in spotlight_chips if item]
    spotlight_bullets = [
        "Night record. Public-facing. Impossible to miss.",
        "Clipped pulse, falsetto glide, mirrored-room energy.",
        f"Scene cue: {scene_use}" if scene_use else "",
        lead_fact,
    ]
    spotlight_bullets = [item for item in spotlight_bullets if item][:3]

    ranking_rows: list[str] = []
    for row in top23_rows:
        rank = int(str(row.get("rank") or "0") or 0)
        row_classes = ["top23-rank-row"]
        if rank <= 5:
            row_classes.append("top23-rank-top-five")
        elif rank <= 10:
            row_classes.append("top23-rank-top-ten")
        weeks = escape(str(row.get("weeks") or "").strip())
        peak = escape(str(row.get("peak") or "").strip())
        ranking_rows.append(
            f"<li class=\"{' '.join(row_classes)}\">"
            f"<span class=\"top23-rank-number\">{rank:02d}</span>"
            "<div class=\"top23-rank-copy\">"
            f"<p class=\"top23-song-title\">{escape(str(row.get('song') or '').strip())}</p>"
            f"<p class=\"top23-song-artist\">{escape(str(row.get('artist') or '').strip())}</p>"
            "</div>"
            f"<p class=\"top23-rank-stat\">{weeks}w / #{peak}</p>"
            "</li>"
        )

    context = load_year_context(year)
    albums = context.get("albums", {}).get("top_albums", []) if isinstance(context.get("albums"), dict) else []
    album_rows = []
    for item in albums[:4]:
        if not isinstance(item, dict):
            continue
        album_rows.append(
            "<li>"
            f"<strong>{escape(str(item.get('album') or '').strip())}</strong>"
            f"<span>{escape(str(item.get('artist') or '').strip())} • {escape(str(item.get('weeks_on_chart') or '').strip())} weeks</span>"
            "</li>"
        )

    newcomer_rows = [
        "<li>"
        f"<strong>{escape(entry['artist'])}</strong>"
        f"<span>{escape(entry['note'])}</span>"
        "</li>"
        for entry in song_new_artist_entries(year, top23_rows)
    ]

    moment_rows = [f"<li>{escape(item)}</li>" for item in music_moment_lines(year, top23_rows)]
    trend_rows = [f"<li>{escape(item)}</li>" for item in fastest_riser_lines(year)]

    art_subpath = top23_poster_art_subpath(year, page_number)
    art_src = asset_path_for_mode(year, art_subpath, mode)

    return (
        "<section class=\"chart-collage-page\">"
        "<span class=\"poster-shape poster-shape-star poster-shape-1\"></span>"
        "<span class=\"poster-shape poster-shape-star poster-shape-2\"></span>"
        "<span class=\"poster-shape poster-shape-burst poster-shape-3\"></span>"
        "<span class=\"poster-shape poster-shape-arrow poster-shape-4\"></span>"
        "<span class=\"poster-scribble poster-scribble-1\"></span>"
        "<span class=\"poster-scribble poster-scribble-2\"></span>"
        f"<figure class=\"chart-collage-art\"><img src=\"{escape(art_src)}\" alt=\"Poster illustration for the top songs page\" /></figure>"
        "<header class=\"chart-title-stack\">"
        "<p class=\"chart-kicker\">Year-End Wall Chart</p>"
        "<div class=\"chart-title-cluster\">"
        "<p class=\"chart-title-shadow\">TOP 23</p>"
        "<h3 class=\"chart-title-main\">TOP 23</h3>"
        "</div>"
        "<p class=\"chart-title-sub\">SONGS</p>"
        f"<p class=\"chart-title-year\">{year}</p>"
        "<p class=\"chart-title-scribble\">Twenty-three hooks. No quiet corners.</p>"
        "</header>"
        "<section class=\"chart-rank-slab\">"
        "<p class=\"chart-rank-label\">Ranked + stacked</p>"
        f"<ol class=\"top23-ranked-list\">{''.join(ranking_rows)}</ol>"
        "</section>"
        "<article class=\"chart-sticker chart-sticker-spotlight\">"
        "<p class=\"sticker-label\">#1 Song of the Year</p>"
        f"<h4>{escape(lead_title)}</h4>"
        f"<p class=\"sticker-credit\">{escape(lead_artist)}</p>"
        "<ul class=\"poster-chip-list\">"
        f"{''.join(f'<li>{escape(item)}</li>' for item in spotlight_chips)}"
        "</ul>"
        "<ul class=\"sticker-list sticker-list-tight\">"
        f"{''.join(f'<li>{escape(item)}</li>' for item in spotlight_bullets)}"
        "</ul>"
        "</article>"
        "<article class=\"chart-sticker chart-sticker-albums\">"
        "<p class=\"sticker-label\">Biggest Albums</p>"
        "<ul class=\"sticker-list\">"
        f"{''.join(album_rows)}"
        "</ul>"
        "</article>"
        "<article class=\"chart-sticker chart-sticker-artists\">"
        "<p class=\"sticker-label\">New Artists</p>"
        "<ul class=\"sticker-list sticker-list-tight\">"
        f"{''.join(newcomer_rows)}"
        "</ul>"
        "</article>"
        "<article class=\"chart-sticker chart-sticker-moments\">"
        "<p class=\"sticker-label\">Music Moments</p>"
        "<ul class=\"sticker-list sticker-list-tight\">"
        f"{''.join(moment_rows)}"
        "</ul>"
        "</article>"
        "<article class=\"chart-sticker chart-sticker-risers\">"
        "<p class=\"sticker-label\">Fastest Risers</p>"
        "<ul class=\"sticker-list sticker-list-tight\">"
        f"{''.join(trend_rows)}"
        "</ul>"
        "</article>"
        "</section>"
    )


def build_chart_top23_poster_page(year: int, page_number: int, top23_rows: list[dict[str, str]]) -> IssuePage:
    if not top23_rows:
        return build_issue_markdown_section(year, page_number, "chart_top23")

    return build_page(
        year,
        page_number,
        "chart_top23",
        title="Top 23 Songs",
        subtitle="Poster sheet for the year's biggest records",
        byline="RetroVerse Music Desk",
        body_layout_html=render_chart_top23_poster_html(year, page_number, top23_rows, "layout"),
        body_pdf_html=render_chart_top23_poster_html(year, page_number, top23_rows, "pdf"),
        layout_type="poster chart page",
        marginal_subpaths=[],
    )


def movie_parody_panels(year: int) -> list[dict[str, str | int]]:
    if year == 1978:
        return MOVIE_PARODY_PANELS_1978
    return []


def render_movies_parody_html(year: int, panels: list[dict[str, str | int]], part: int) -> str:
    header_title = "LINES THE YEAR COULDN'T SHAKE"
    deck = (
        "Five box-office favorites per page, reduced to one big line and one clean visual beat."
    )

    panel_cards: list[str] = []
    for panel in panels:
        rank = int(panel.get("rank") or 0)
        visual = str(panel.get("visual") or "").strip()
        visual_token = str(panel.get("visual_token") or "").strip()
        caption = str(panel.get("tag") or "").strip()
        panel_caption_html = f"<p class=\"movie-panel-caption\">{escape(caption)}</p>" if caption else ""
        panel_cards.append(
            "<article class=\"movie-parody-panel\">"
            "<header class=\"movie-panel-head\">"
            f"<p class=\"movie-panel-rank\">#{rank}</p>"
            f"<h4 class=\"movie-panel-title\">{escape(str(panel.get('title') or '').strip())}</h4>"
            "</header>"
            f"<figure class=\"movie-panel-stage\" role=\"img\" aria-label=\"{escape(visual)}\">"
            f"<span class=\"movie-panel-token\">{escape(visual_token)}</span>"
            "</figure>"
            f"<blockquote class=\"movie-panel-line\">{escape(str(panel.get('parody_line') or '').strip())}</blockquote>"
            f"{panel_caption_html}"
            "</article>"
        )

    return (
        "<section class=\"movies-parody-page\">"
        "<header class=\"movies-parody-head\">"
        f"<h3>{escape(header_title)}</h3>"
        f"<p class=\"movies-parody-subhead\">{escape(deck)}</p>"
        "</header>"
        f"<section class=\"movies-parody-grid movies-parody-grid-part-{part}\">{''.join(panel_cards)}</section>"
        "</section>"
    )


def render_projection_booth_html(page_data: dict[str, Any]) -> str:
    """Render projection booth page data as HTML."""
    headline = page_data.get("headline", "From the Projection Booth")
    intro = page_data.get("intro", "")
    films = page_data.get("films", [])
    cult = page_data.get("cult_classic", {})

    parts = [
        f"<section class=\"projection-booth-page\" data-page-type=\"projection_booth_editorial\">",
        f"<h2>{escape(headline)}</h2>",
    ]
    if intro:
        parts.append(f"<p class=\"projection-booth-intro\">{escape(intro)}</p>")
    for f in films:
        title = escape(f.get("title", ""))
        text = escape(f.get("text", ""))
        parts.append(f"<article class=\"projection-booth-film\"><h4>{title}</h4><p>{text}</p></article>")
    if cult:
        label = escape(cult.get("label", ""))
        title = escape(cult.get("title", ""))
        text = escape(cult.get("text", ""))
        parts.append(f"<aside class=\"projection-booth-cult\"><h4>{label}</h4><p><strong>{title}</strong> {text}</p></aside>")
    parts.append("</section>")
    return "".join(parts)


def build_projection_booth_section_page(year: int, page_number: int) -> IssuePage:
    """Build Projection Booth editorial page. Uses structured data from build_movie_memory_full."""
    if _build_projection_booth_data is None:
        raise ImportError(
            "Movies data pipeline required for projection_booth. "
            f"Could not import scripts.build_movie_memory_full: {_movie_import_error}"
        )
    page_data = _build_projection_booth_data(year, debug=False)
    return build_page(
        year,
        page_number,
        "projection_booth",
        title="From the Projection Booth",
        subtitle=page_data.get("intro", "A few that stuck, a few that surprised people."),
        byline="RetroVerse Film Desk",
        body_layout_html=render_projection_booth_html(page_data),
        body_pdf_html=render_projection_booth_html(page_data),
        layout_type="projection_booth_editorial",
        marginal_subpaths=[],
    )


def render_movies_charts_html(page_data: dict[str, Any]) -> str:
    """Render movies charts page data as HTML."""
    top10 = page_data.get("top_10_movies", [])
    awards = page_data.get("academy_awards", {})
    also = page_data.get("also_playing", [])

    rows = "".join(
        f"<tr><td>{r['rank']}</td><td>{escape(r['title'])}</td></tr>"
        for r in top10
    )
    awards_rows = "".join(
        f"<tr><td>{escape(k.replace('_', ' ').title())}</td><td>{escape(str(v))}</td></tr>"
        for k, v in awards.items() if v
    )
    also_items = "".join(f"<li>{escape(t)}</li>" for t in also)

    parts = [
        "<section class=\"movies-charts-page\" data-page-type=\"movies_charts\">",
        "<h3>Top 10 Movies</h3>",
        f"<table class=\"movies-charts-table\"><tbody>{rows}</tbody></table>",
    ]
    if awards_rows:
        parts.append(f"<h4>Academy Awards</h4><table class=\"movies-charts-awards\"><tbody>{awards_rows}</tbody></table>")
    if also_items:
        parts.append(f"<h4>Also Playing</h4><ul class=\"movies-charts-also\">{also_items}</ul>")
    parts.append("</section>")
    return "".join(parts)


def build_movies_charts_section_page(year: int, page_number: int) -> IssuePage:
    """Build Movies Charts page (data-driven). Uses structured data from build_movie_memory_full."""
    if _build_movies_charts_data is None:
        raise ImportError(
            "Movies data pipeline required for movies_charts. "
            f"Could not import scripts.build_movie_memory_full: {_movie_import_error}"
        )
    page_data = _build_movies_charts_data(year, debug=False)
    return build_page(
        year,
        page_number,
        "movies_charts",
        title="Movies & Awards",
        subtitle="Top 10, Academy Awards, and more",
        byline="RetroVerse Film Desk",
        body_layout_html=render_movies_charts_html(page_data),
        body_pdf_html=render_movies_charts_html(page_data),
        layout_type="movies charts page",
        marginal_subpaths=[],
    )


def build_movies_parody_page(year: int, page_number: int, part: int, *, page_label: str | None = None) -> IssuePage:
    panels = movie_parody_panels(year)
    start = (part - 1) * 5
    part_panels = panels[start : start + 5]
    if not part_panels:
        return build_issue_markdown_section(year, page_number, "movies")

    section_key = "movies" if part == 1 else "movies_spread_2"
    title = "Movies Parody Spread"
    subtitle = "Famous lines, bent just enough to catch the decade"
    return build_page(
        year,
        page_number,
        section_key,
        page_label=page_label,
        title=title,
        subtitle=subtitle,
        byline="RetroVerse Film Desk",
        body_layout_html=render_movies_parody_html(year, part_panels, part),
        body_pdf_html=render_movies_parody_html(year, part_panels, part),
        layout_type="movie parody spread",
        marginal_subpaths=[],
    )


def build_movies_parody_companion_page(year: int, page_number: int) -> IssuePage | None:
    if len(movie_parody_panels(year)) <= 5:
        return None

    companion = build_movies_parody_page(year, page_number, part=2)
    return IssuePage(
        page_number=companion.page_number,
        filename=f"page_{page_number:02d}_movies_spread_2.html",
        page_label=None,
        title=companion.title,
        subtitle=companion.subtitle,
        byline=companion.byline,
        story_id=companion.story_id,
        layout_type=companion.layout_type,
        main_html_layout=companion.main_html_layout,
        main_html_pdf=companion.main_html_pdf,
        hero_subpath=companion.hero_subpath,
        collage_subpaths=companion.collage_subpaths,
        marginal_subpaths=companion.marginal_subpaths,
        sidebar_items=companion.sidebar_items,
        data_points=companion.data_points,
        is_cover=companion.is_cover,
        hero_in_main=companion.hero_in_main,
    )


def tv_editorial_fields(year: int, row: dict[str, Any]) -> dict[str, str]:
    title = str(row.get("title") or "").strip()
    lookup = TV_EDITORIAL_NOTES_1978.get(title) or TV_EDITORIAL_NOTES_1978.get(title.replace("&", "and"))
    network = str(row.get("network") or (lookup or {}).get("network") or "Network TV").strip()
    signals = row.get("viewership_signals") if isinstance(row.get("viewership_signals"), dict) else {}
    rank_value = signals.get("issue_rank") or signals.get("year_master_rank")
    rank = f"#{int(rank_value):02d}" if isinstance(rank_value, int) else "TV"
    issue_note = str(row.get("issue_note") or "").strip()

    if lookup:
        return {
            "title": title,
            "hook": lookup["hook"],
            "premise": lookup["premise"],
            "why": lookup["why"],
            "network": network,
            "rank": rank,
        }

    fallback_premise = issue_note or f"{title} holds its slot through repeatable characters and reliable return-viewing rhythm."
    return {
        "title": title,
        "hook": "Weekly return viewing, no wasted explanation.",
        "premise": fallback_premise,
        "why": "It mattered because people built a week around it instead of discovering it by accident.",
        "network": network,
        "rank": rank,
    }


def render_television_grid_html(year: int) -> str:
    rows = load_tv_reference_rows(year)
    cards: list[str] = []

    comedy_count = 0
    network_names: set[str] = set()
    for row in rows:
        genres = row.get("genres")
        if isinstance(genres, list) and any(str(item).lower() == "comedy" for item in genres):
            comedy_count += 1
        fields = tv_editorial_fields(year, row)
        if fields["network"]:
            network_names.add(fields["network"])
        cards.append(
            "<article class=\"tv-show-card\">"
            "<div class=\"tv-show-meta\">"
            f"<span>{escape(fields['rank'])}</span>"
            f"<span>{escape(fields['network'])}</span>"
            "</div>"
            f"<h4>{escape(fields['title'])}</h4>"
            f"<p class=\"tv-show-hook\">{escape(fields['hook'])}</p>"
            f"<p class=\"tv-show-premise\">{escape(fields['premise'])}</p>"
            f"<p class=\"tv-show-impact\"><strong>Why it mattered</strong> {escape(fields['why'])}</p>"
            "</article>"
        )

    stats = [
        ("Shows", str(len(rows))),
        ("Comedy Load", str(comedy_count or 0)),
        ("Networks", str(len(network_names) or 1)),
    ]
    stats_html = "".join(
        f"<div class=\"tv-stat\"><strong>{escape(label)}</strong><span>{escape(value)}</span></div>" for label, value in stats
    )

    return (
        "<section class=\"tv-grid-page\">"
        "<header class=\"tv-grid-head\">"
        "<div>"
        "<p class=\"poster-overline\">Television Grid</p>"
        "<h3>The Shows Keeping the Week in Sync</h3>"
        "<p class=\"subtitle\">Hooks, premises, and the reason each title kept returning to the conversation.</p>"
        "</div>"
        f"<div class=\"tv-stats-strip\">{stats_html}</div>"
        "</header>"
        f"<section class=\"tv-show-grid\">{''.join(cards)}</section>"
        "</section>"
    )


def build_television_grid_page(year: int, page_number: int) -> IssuePage:
    rows = load_tv_reference_rows(year)
    if not rows:
        return build_issue_markdown_section(year, page_number, "television")

    return build_page(
        year,
        page_number,
        "television",
        title="Television Grid",
        subtitle="Dense editorial notes on the shows shaping the week",
        byline="RetroVerse Television Desk",
        body_layout_html=render_television_grid_html(year),
        body_pdf_html=render_television_grid_html(year),
        layout_type="television grid page",
        marginal_subpaths=[],
    )


def build_story_section_page(year: int, page_number: int, section_key: str) -> IssuePage:
    config = STORY_SECTION_CONFIG[section_key]
    story_path = final_year_dir(year) / f"{config['story_id']}.md"
    md_text = load_text_if_exists(story_path)
    hero_subpath = page_art_or_placeholder_subpath(year, page_number)
    if not md_text:
        return build_placeholder_page(
            year,
            page_number,
            section_key,
            title=str(config["fallback_title"]),
            subtitle=str(config["subtitle"]),
            hero_subpath=hero_subpath,
        )
    return build_page_from_markdown(
        year,
        page_number,
        section_key,
        md_text,
        fallback_title=str(config["fallback_title"]),
        subtitle=str(config["subtitle"]),
        layout_type=str(config["layout_type"]),
        hero_subpath=hero_subpath,
    )


def build_culture_collage_page(year: int, page_number: int) -> IssuePage:
    editorial = load_json_if_exists(issue_year_dir(year) / "data" / "editorial.json") or {}
    collage = editorial.get("collage", {}) if isinstance(editorial, dict) else {}
    tiles = collage.get("tiles", []) if isinstance(collage, dict) else []
    if not isinstance(tiles, list):
        tiles = []
    tile_count = len(subpaths_from_folder(year, "collage", limit=9)) or 9
    collage_subpaths = repeated_page_art_subpaths(year, page_number, tile_count)
    bullets = "\n".join(f"- {str(tile).strip()}" for tile in tiles if str(tile).strip())
    if not bullets:
        bullets = "- Collage notes pending."
    md_text = (
        "# Culture Collage\n"
        "*RetroVerse Art Desk*\n\n"
        "A collage page resets the pacing late in the issue and keeps visual ephemera in the canonical structure.\n\n"
        "## Collage Notes\n"
        f"{bullets}\n"
    )
    if not collage_subpaths:
        return build_placeholder_page(
            year,
            page_number,
            "culture_collage",
            title="Culture Collage",
            subtitle="Visual fragments from the year",
        )
    return build_page_from_markdown(
        year,
        page_number,
        "culture_collage",
        md_text,
        fallback_title="Culture Collage",
        subtitle="Visual fragments from the year",
        layout_type="collage page",
        collage_subpaths=collage_subpaths,
        data_points_heading="Collage Notes",
    )


def build_retro_ads_page(year: int, page_number: int) -> IssuePage:
    hero_subpath = page_art_or_placeholder_subpath(year, page_number)
    md_text = (
        "# Retro Ads Page\n"
        "*RetroVerse Promotion Desk*\n\n"
        "The canonical issue reserves a late-book ad roundup page for house ads, fake products, and print-era visual texture.\n\n"
        "## House Ads\n"
        "- Mail-order stereo bundle\n"
        "- Weekend arcade coupon sheet\n"
        "- Night-show cinema promotion block\n"
        "- Record-club membership insert\n"
    )
    return build_page_from_markdown(
        year,
        page_number,
        "retro_ads_page",
        md_text,
        fallback_title="Retro Ads Page",
        subtitle="Late-book ad roundup",
        layout_type="ad roundup",
        hero_subpath=hero_subpath,
        data_points_heading="House Ads",
    )


def build_section_page(year: int, page_number: int, section_key: str, top23_rows: list[dict[str, str]]) -> IssuePage:
    brief = load_page_brief_if_exists(year, page_number, section_key)
    if brief is not None:
        satire_errors = validate_satire_brief(brief)
        if satire_errors:
            joined = "; ".join(satire_errors)
            raise ValueError(f"Page {page_number:02d} / {section_key} has invalid satire pattern data: {joined}")
        comic_page = build_comic_page_from_brief(year, page_number, section_key, brief)
        if comic_page is not None:
            return comic_page
    grouped_page = build_top_songs_group_page(year, page_number)
    if grouped_page is not None:
        return grouped_page
    if section_key == "cover":
        return build_cover_page(year, page_number, top23_rows)
    if section_key == "movies":
        return build_movies_parody_page(year, page_number, part=1)
    if section_key == "projection_booth":
        return build_projection_booth_section_page(year, page_number)
    if section_key == "movies_charts":
        return build_movies_charts_section_page(year, page_number)
    if section_key == "television":
        return build_television_grid_page(year, page_number)
    if section_key == "chart_top23":
        return build_chart_top23_poster_page(year, page_number, top23_rows)
    if section_key in ISSUE_SECTION_CONFIG:
        return build_issue_markdown_section(year, page_number, section_key)
    if section_key == "year_snapshot":
        return build_year_snapshot_page(year, page_number, top23_rows)
    if section_key.startswith("top_song_"):
        rank = int(section_key.rsplit("_", 1)[1])
        return build_top_song_page(year, page_number, section_key, rank, top23_rows)
    if section_key in STORY_SECTION_CONFIG:
        return build_story_section_page(year, page_number, section_key)
    if section_key == "culture_collage":
        return build_culture_collage_page(year, page_number)
    if section_key == "retro_ads_page":
        return build_retro_ads_page(year, page_number)
    if section_key == "one_hit_wonder":
        return build_placeholder_page(
            year,
            page_number,
            section_key,
            title="One Hit Wonder",
            subtitle="Reserved canonical feature slot",
            hero_subpath=page_art_or_placeholder_subpath(year, page_number),
        )
    return build_placeholder_page(
        year,
        page_number,
        section_key,
        title=section_key.replace("_", " ").title(),
        subtitle="Canonical structure reserve slot",
    )


def expected_issue_page_count(year: int) -> int:
    return len(ISSUE_STRUCTURE)


def build_issue_pages(year: int) -> list[IssuePage]:
    assert_canonical_templates_exist()
    top23_rows = load_chart_top23_rows(year)
    return [
        build_section_page(year, page_number, section_key, top23_rows)
        for page_number, section_key in enumerate(ISSUE_STRUCTURE, start=1)
    ]


def expand_layout_pages(year: int, pages: list[IssuePage]) -> list[IssuePage]:
    layout_pages: list[IssuePage] = []
    for page in pages:
        layout_pages.append(page)
        if page.story_id == "movies":
            companion = build_movies_parody_companion_page(year, page.page_number)
            if companion is not None:
                layout_pages.append(companion)
    return layout_pages


def normalize_page_numbers(pages: list[IssuePage]) -> list[IssuePage]:
    """Assign sequential page numbers 1..N. Remove A/B labels. Update filenames."""
    return [
        replace(
            page,
            page_number=i + 1,
            filename=f"page_{i + 1:02d}_{page.story_id}.html",
            page_label=None,
        )
        for i, page in enumerate(pages)
    ]


def layout_asset_path(subpath: str | None) -> str:
    if not subpath:
        return ""
    if subpath.startswith("assets/"):
        return f"../../../{subpath}"
    return f"../art/{subpath}"


def pdf_asset_path(year: int, subpath: str | None) -> str:
    if not subpath:
        return ""
    if subpath.startswith("assets/"):
        return subpath
    return f"issues/{year}/art/{subpath}"


def _hero_size_class(story_id: str) -> str:
    """Return hero size modifier based on section type (cover/feature/data)."""
    if story_id == "cover":
        return "hero-image--cover"
    if story_id in (
        "masthead", "editor_letter", "year_snapshot",
        "movies", "movies_spread_2", "projection_booth", "television", "culture",
        "top_songs_group",
    ) or (story_id and story_id.startswith("top_song_")):
        return "hero-image--feature"
    return "hero-image--data"


def hero_image_html(page: IssuePage, year: int, mode: str) -> str:
    if not page.hero_subpath:
        return ""
    src = layout_asset_path(page.hero_subpath) if mode == "layout" else pdf_asset_path(year, page.hero_subpath)
    size_class = _hero_size_class(page.story_id or "")
    classes = f"hero-image {size_class}".strip()
    return (
        f"<div class=\"{classes}\">"
        f"<img src=\"{escape(src)}\" alt=\"Illustration for {escape(page.title)}\" />"
        "</div>"
    )


def collage_html(page: IssuePage, year: int, mode: str) -> str:
    if not page.collage_subpaths:
        return ""
    tiles: list[str] = []
    for index, subpath in enumerate(page.collage_subpaths, start=1):
        src = layout_asset_path(subpath) if mode == "layout" else pdf_asset_path(year, subpath)
        tiles.append(
            "<figure class=\"collage-tile\">"
            f"<img src=\"{escape(src)}\" alt=\"Collage tile {index} for {escape(page.title)}\" />"
            "</figure>"
        )
    return "<section class=\"collage-grid\">" + "".join(tiles) + "</section>"


def marginal_gallery_html(page: IssuePage, year: int, mode: str) -> str:
    if not page.marginal_subpaths:
        return ""
    tags: list[str] = []
    for index, subpath in enumerate(page.marginal_subpaths, start=1):
        src = layout_asset_path(subpath) if mode == "layout" else pdf_asset_path(year, subpath)
        tags.append(
            f"<img class=\"marginal-thumb\" src=\"{escape(src)}\" alt=\"Marginal gag {page.page_number}-{index}\" />"
        )
    return "<section class=\"marginal-gallery\">" + "".join(tags) + "</section>"


def render_masthead(page: IssuePage, year: int) -> str:
    title = "RetroVerse" if page.is_cover else f"RetroVerse • {year}"
    subtitle = "Press ▶ Play for the Past" if page.is_cover or page.story_id == "masthead" else ""
    parts = ["<header class=\"masthead\">", f"<h1 class=\"brand-name\">{escape(title)}</h1>"]
    if subtitle:
        parts.append(f"<p class=\"masthead-subtitle\">{escape(subtitle)}</p>")
    parts.append("</header>")
    return "".join(parts)


def render_issue_panel(page: IssuePage, pages: list[IssuePage], year: int, mode: str, include_nav: bool) -> str:
    main_html = page.main_html_layout if mode == "layout" else page.main_html_pdf
    main_parts: list[str] = []
    side_parts: list[str] = []

    hero_html = hero_image_html(page, year, mode)
    collage_grid = collage_html(page, year, mode)
    marginals = marginal_gallery_html(page, year, mode)

    if mode == "pdf":
        if hero_html:
            main_parts.append(hero_html)
    elif page.hero_in_main:
        main_parts.append(hero_html)
    elif hero_html:
        side_parts.append(hero_html)

    if collage_grid:
        main_parts.append(collage_grid)

    main_parts.append(f"<section class=\"story-body\">{main_html}</section>")

    if page.sidebar_items and mode == "layout":
        items = "".join(f"<li>{escape(item)}</li>" for item in page.sidebar_items)
        side_parts.append(f"<section class=\"sidebar-box\"><h3>Production Inputs</h3><ul>{items}</ul></section>")

    if page.data_points and mode == "layout":
        items = "".join(f"<li>{escape(item)}</li>" for item in page.data_points[:6])
        side_parts.append(f"<section class=\"data-box\"><h3>Data References</h3><ul>{items}</ul></section>")

    if marginals and mode == "layout":
        side_parts.append(marginals)

    nav_html = ""
    if include_nav:
        current_index = next((index for index, item in enumerate(pages) if item.filename == page.filename), -1)
        links: list[str] = []
        if current_index > 0:
            links.append(f"<a href=\"{escape(pages[current_index - 1].filename)}\">Previous</a>")
        links.append('<a href="index.html">Index</a>')
        if 0 <= current_index < len(pages) - 1:
            links.append(f"<a href=\"{escape(pages[current_index + 1].filename)}\">Next</a>")
        nav_html = "".join(links)

    section_label = "Cover" if page.is_cover else (page.page_label or f"Page {page.page_number:02d}")
    subtitle_html = f"<p class=\"subtitle\">{escape(page.subtitle)}</p>" if page.subtitle else ""
    byline_html = f"<p class=\"byline\">{escape(page.byline)}</p>" if page.byline else ""
    side_html = "".join(side_parts)
    content_class = "content-grid no-sidebar" if not side_html else "content-grid"
    story_slug = slugify(page.story_id)
    is_editorial_feature_shell = story_slug in {"movies", "movies_spread_2"}
    article_classes = " ".join(
        item
        for item in ["mag-page", "issue-page", "cover-page" if page.is_cover else "", f"page-{story_slug}"]
        if item
    )
    side_column_html = f"<aside class=\"side-column\">{side_html}</aside>" if side_html else ""
    masthead_html = "" if is_editorial_feature_shell else render_masthead(page, year)
    page_meta_html = (
        ""
        if is_editorial_feature_shell
        else (
            "<section class=\"page-meta\">"
            f"<p class=\"section-label\">{escape(section_label)}</p>"
            f"<h2 class=\"page-title\">{escape(page.title)}</h2>"
            f"{subtitle_html}"
            f"{byline_html}"
            "</section>"
        )
    )

    return (
        f"<article class=\"{article_classes}\">"
        f"{masthead_html}"
        f"{page_meta_html}"
        f"<section class=\"{content_class}\">"
        f"<div class=\"main-column\">{''.join(main_parts)}</div>"
        f"{side_column_html}"
        "</section>"
        "<footer class=\"page-footer\">"
        f"<div class=\"pager\">{escape(section_label)}</div>"
        f"<nav class=\"page-nav\">{nav_html}</nav>"
        "</footer>"
        "</article>"
    )


def render_layout_page(page: IssuePage, pages: list[IssuePage], year: int) -> str:
    panel = render_issue_panel(page, pages, year, mode="layout", include_nav=True)
    return (
        "<!doctype html>"
        "<html lang=\"en\">"
        "<head>"
        "<meta charset=\"utf-8\" />"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />"
        f"<title>RetroVerse {year} | Page {page.page_number:02d}</title>"
        "<link rel=\"stylesheet\" href=\"../../../assets/css/magazine.css\" />"
        "</head>"
        "<body>"
        "<div class=\"preview-shell\">"
        f"{panel}"
        "</div>"
        "</body>"
        "</html>"
    )


def _index_display_title(page: IssuePage) -> str:
    """Human-readable title for index. Never leak raw IDs like top_song_1."""
    title = (page.title or "").strip()
    sid = page.story_id or ""
    if title and "top_song_" not in title:
        return title
    if sid == "top_songs_group":
        return title or "Top Songs"
    if sid.startswith("top_song_"):
        return title or f"Top Song #{sid.rsplit('_', 1)[-1]}"
    return title or sid.replace("_", " ").title()


def _is_song_page(page: IssuePage) -> bool:
    """True if page is a top-song entry (story_id or title pattern)."""
    if (page.story_id or "").startswith("top_song"):
        return True
    title = (page.title or "").strip()
    return bool(re.match(r"^\d{2}\.\s", title))


def _build_index_items(pages: list[IssuePage], year: int) -> tuple[str, str | None]:
    """Build index list items, grouping song pages into one entry. Returns (items_html, debug_range)."""
    items: list[str] = []
    i = 0
    debug_range: str | None = None

    while i < len(pages):
        page = pages[i]
        if not _is_song_page(page):
            items.append(
                f"<li><a href=\"{escape(page.filename)}\">{escape(page.page_label or f'Page {page.page_number:02d}')}: {escape(_index_display_title(page))}</a></li>"
            )
            i += 1
            continue

        # Collect consecutive song pages
        song_start = i
        while i < len(pages) and _is_song_page(pages[i]):
            i += 1
        song_end = i - 1

        first = pages[song_start]
        last = pages[song_end]
        start_num = first.page_number
        end_num = last.page_number
        label = f"Page {start_num:02d}–{end_num}" if start_num != end_num else f"Page {start_num:02d}"
        title = f"Top Songs of {year}"

        items.append(f"<li><a href=\"{escape(first.filename)}\">{escape(label)}: {escape(title)}</a></li>")
        debug_range = f"{start_num:02d}–{end_num:02d}" if start_num != end_num else f"{start_num:02d}"

    return "".join(items), debug_range


def render_layout_index(pages: list[IssuePage], year: int) -> tuple[str, str | None]:
    """Build index dynamically from actual rendered pages. Song pages grouped into one entry.
    Returns (html, song_page_range e.g. '06–15' or None if no song pages)."""
    items, song_range = _build_index_items(pages, year)
    html = (
        "<!doctype html>"
        "<html lang=\"en\">"
        "<head>"
        "<meta charset=\"utf-8\" />"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />"
        f"<title>RetroVerse {year} | Canonical Layout Index</title>"
        "<link rel=\"stylesheet\" href=\"../../../assets/css/magazine.css\" />"
        "</head>"
        "<body>"
        "<div class=\"preview-index\">"
        f"<h1>RetroVerse {year}</h1>"
        "<p>Canonical issue build generated from the fixed RetroVerse issue structure.</p>"
        f"<p><strong>Total pages:</strong> {len(pages)}</p>"
        f"<ol>{items}</ol>"
        "</div>"
        "</body>"
        "</html>"
    )
    return html, song_range


def render_pdf_document(pages: list[IssuePage], year: int) -> str:
    return "\n".join(render_issue_panel(page, pages, year, mode="pdf", include_nav=False) for page in pages)


def render_combined_print_html(pages: list[IssuePage], year: int) -> str:
    """Single HTML with all pages for print/PDF export. Uses layout-relative asset paths."""
    panels = "\n".join(
        render_issue_panel(page, pages, year, mode="layout", include_nav=False) for page in pages
    )
    return (
        "<!doctype html>"
        "<html lang=\"en\">"
        "<head>"
        "<meta charset=\"utf-8\" />"
        f"<title>RetroVerse {year} | Print</title>"
        "<link rel=\"stylesheet\" href=\"../../../assets/css/magazine.css\" />"
        "</head>"
        "<body>"
        f"<div class=\"preview-shell print-shell\">{panels}</div>"
        "</body>"
        "</html>"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the canonical RetroVerse magazine pipeline.")
    parser.add_argument("--year", default="1978", help="Issue year to build (default: 1978)")
    parser.add_argument(
        "--overwrite-art",
        action="store_true",
        help="Regenerate artwork even if cached assets already exist.",
    )
    return parser.parse_args()


def run_pipeline_step(script_path: Path, year: str, extra_args: list[str] | None = None) -> None:
    cmd = [sys.executable, str(script_path), "--year", year]
    if extra_args:
        cmd.extend(extra_args)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Pipeline step failed: {' '.join(cmd)}")


def main() -> int:
    print("This CLI entrypoint is deprecated. Run `python3 pipeline/run_issue_pipeline.py --year <year>` instead.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
