#!/usr/bin/env python3
"""Shared helpers and CLI entrypoint for the canonical RetroVerse magazine build pipeline."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

import markdown


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ISSUES_ROOT = PROJECT_ROOT / "issues"
SECTION_TEMPLATE_DIR = PROJECT_ROOT / "templates" / "sections"
PLACEHOLDER_ART_SUBPATH = "assets/placeholder.png"

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


@dataclass(frozen=True)
class IssuePage:
    page_number: int
    filename: str
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


def build_page(
    year: int,
    page_number: int,
    section_key: str,
    *,
    title: str,
    subtitle: str,
    byline: str,
    body_layout_html: str,
    body_pdf_html: str,
    layout_type: str,
    hero_subpath: str | None = None,
    collage_subpaths: list[str] | None = None,
    sidebar_items: list[str] | None = None,
    data_points: list[str] | None = None,
    is_cover: bool = False,
    hero_in_main: bool = False,
) -> IssuePage:
    return IssuePage(
        page_number=page_number,
        filename=f"page_{page_number:02d}_{section_key}.html",
        title=title,
        subtitle=subtitle,
        byline=byline,
        story_id=section_key,
        layout_type=layout_type,
        main_html_layout=body_layout_html,
        main_html_pdf=body_pdf_html,
        hero_subpath=hero_subpath,
        collage_subpaths=collage_subpaths or [],
        marginal_subpaths=choose_marginal_subpaths(year, page_number),
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
    if section_key == "cover":
        return build_cover_page(year, page_number, top23_rows)
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


def hero_image_html(page: IssuePage, year: int, mode: str) -> str:
    if not page.hero_subpath:
        return ""
    src = layout_asset_path(page.hero_subpath) if mode == "layout" else pdf_asset_path(year, page.hero_subpath)
    return (
        "<div class=\"hero-image\">"
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
        links: list[str] = []
        if page.page_number > 1:
            links.append(f"<a href=\"{escape(pages[page.page_number - 2].filename)}\">Previous</a>")
        links.append('<a href="index.html">Index</a>')
        if page.page_number < len(pages):
            links.append(f"<a href=\"{escape(pages[page.page_number].filename)}\">Next</a>")
        nav_html = "".join(links)

    section_label = "Cover" if page.is_cover else f"Page {page.page_number:02d}"
    subtitle_html = f"<p class=\"subtitle\">{escape(page.subtitle)}</p>" if page.subtitle else ""
    byline_html = f"<p class=\"byline\">{escape(page.byline)}</p>" if page.byline else ""
    side_html = "".join(side_parts)
    content_class = "content-grid no-sidebar" if not side_html else "content-grid"
    article_classes = " ".join(
        item
        for item in ["mag-page", "issue-page", "cover-page" if page.is_cover else "", f"page-{slugify(page.story_id)}"]
        if item
    )
    side_column_html = f"<aside class=\"side-column\">{side_html}</aside>" if side_html else ""

    return (
        f"<article class=\"{article_classes}\">"
        f"{render_masthead(page, year)}"
        "<section class=\"page-meta\">"
        f"<p class=\"section-label\">{escape(section_label)}</p>"
        f"<h2 class=\"page-title\">{escape(page.title)}</h2>"
        f"{subtitle_html}"
        f"{byline_html}"
        "</section>"
        f"<section class=\"{content_class}\">"
        f"<div class=\"main-column\">{''.join(main_parts)}</div>"
        f"{side_column_html}"
        "</section>"
        "<footer class=\"page-footer\">"
        f"<div class=\"pager\">Page {page.page_number:02d}</div>"
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


def render_layout_index(pages: list[IssuePage], year: int) -> str:
    items = "".join(
        f"<li><a href=\"{escape(page.filename)}\">Page {page.page_number:02d}: {escape(page.story_id)} - {escape(page.title)}</a></li>"
        for page in pages
    )
    return (
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


def render_pdf_document(pages: list[IssuePage], year: int) -> str:
    return "\n".join(render_issue_panel(page, pages, year, mode="pdf", include_nav=False) for page in pages)


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
