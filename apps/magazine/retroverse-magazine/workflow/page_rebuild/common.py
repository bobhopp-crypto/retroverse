#!/usr/bin/env python3
"""Shared helpers for the single-page rebuild workflow."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WORKFLOW_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = WORKFLOW_ROOT.parents[1]
OUTPUT_DIR = WORKFLOW_ROOT / "output"
SCHEMA_PATH = WORKFLOW_ROOT / "page_brief_schema.json"

PAGE_DIMENSIONS = {
    "width_px": 900,
    "height_px": 1200,
    "unit": "px",
}

DEFAULT_TEXT_SAFE_ZONES = [
    {
        "id": "title_zone",
        "label": "Title Block",
        "x": 7,
        "y": 6,
        "width": 54,
        "height": 14,
        "unit": "percent",
        "purpose": "Title, subtitle, byline, and deck overlay area.",
    },
    {
        "id": "body_zone",
        "label": "Body Copy",
        "x": 7,
        "y": 24,
        "width": 58,
        "height": 62,
        "unit": "percent",
        "purpose": "Two-column article body overlay area.",
    },
    {
        "id": "sidebar_zone",
        "label": "Sidebar / Stat Box",
        "x": 68,
        "y": 49,
        "width": 23,
        "height": 28,
        "unit": "percent",
        "purpose": "Verified facts and ranking sidebar overlay area.",
    },
    {
        "id": "footer_zone",
        "label": "Footer",
        "x": 7,
        "y": 93,
        "width": 86,
        "height": 3,
        "unit": "percent",
        "purpose": "Page number and issue footer overlay area.",
    },
]

BODY_LAYOUT_METRICS = {
    "font_size_px": 13.8,
    "line_height": 1.48,
    "columns": 2,
    "column_gap_px": 30,
    "padding_px": 24,
}

SIDEBAR_LAYOUT_METRICS = {
    "font_size_px": 12.4,
    "line_height": 1.45,
    "columns": 1,
    "column_gap_px": 0,
    "padding_px": 18,
}

TITLE_LAYOUT_METRICS = {
    "font_size_px": 40,
    "line_height": 1.08,
    "columns": 1,
    "column_gap_px": 0,
    "padding_px": 20,
}


@dataclass(frozen=True)
class PageTarget:
    year: int
    page_slug: str
    story_id: str
    page_number: int
    page_type: str
    canonical_markdown: str
    canonical_layout_html: str
    final_story_json: str
    final_story_md: str
    draft_story_json: str
    movies_data_json: str
    context_json: str
    production_targets_json: str
    narrative_plan_json: str
    issue_map_json: str


TARGETS = {
    (1978, "movies"): PageTarget(
        year=1978,
        page_slug="movies",
        story_id="story_008",
        page_number=16,
        page_type="screen feature",
        canonical_markdown="issues/1978/movies.md",
        canonical_layout_html="issues/1978/layout/page_16_movies.html",
        final_story_json="issues/1978/articles/final/story_008.json",
        final_story_md="issues/1978/articles/final/story_008.md",
        draft_story_json="issues/1978/articles/story_008.json",
        movies_data_json="issues/1978/data/movies.json",
        context_json="issues/context/1978_context.json",
        production_targets_json="issues/1978/layout/1978_production_targets.json",
        narrative_plan_json="issues/plans/1978_narrative_plan.json",
        issue_map_json="issues/1978/layout/1978_issue_map.json",
    )
}


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--year", type=int, default=1978)
    parser.add_argument("--page-slug", default="movies")
    return parser


def get_target(year: int, page_slug: str) -> PageTarget:
    target = TARGETS.get((year, page_slug))
    if target is None:
        supported = ", ".join(f"{y}/{slug}" for y, slug in sorted(TARGETS))
        raise ValueError(f"Unsupported target {year}/{page_slug}. Supported targets: {supported}")
    return target


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def output_path(year: int, page_slug: str, suffix: str) -> Path:
    ensure_output_dir()
    return OUTPUT_DIR / f"{year}_{page_slug}_{suffix}"


def project_path(relative_path: str) -> Path:
    return PROJECT_ROOT / relative_path


def relative_path(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(load_text(path))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.write_text(payload.rstrip() + "\n", encoding="utf-8")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_check(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("/", " ")
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


def parse_markdown_page(markdown_text: str) -> tuple[str, str, list[str]]:
    lines = markdown_text.splitlines()
    title = ""
    byline = ""
    body_lines: list[str] = []
    body_started = False

    for line in lines:
        stripped = line.strip()
        if not stripped and not body_started:
            continue
        if not title and stripped.startswith("# "):
            title = stripped[2:].strip()
            continue
        if not byline and stripped.startswith("*") and stripped.endswith("*"):
            byline = stripped.strip("*").strip()
            continue
        body_started = True
        body_lines.append(line)

    paragraphs: list[str] = []
    current: list[str] = []
    for line in body_lines:
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(clean_text(" ".join(current)))
                current = []
            continue
        if stripped.startswith("#"):
            if current:
                paragraphs.append(clean_text(" ".join(current)))
                current = []
            continue
        if stripped.startswith("- "):
            current.append(stripped[2:].strip())
            continue
        current.append(stripped)
    if current:
        paragraphs.append(clean_text(" ".join(current)))

    return title, byline, paragraphs


def find_story_entry(entries: list[dict[str, Any]], story_id: str, field_name: str = "story_id") -> dict[str, Any] | None:
    for entry in entries:
        if entry.get(field_name) == story_id or entry.get("id") == story_id or entry.get("related_story_id") == story_id:
            return entry
    return None


def find_song_entry(top_songs: list[dict[str, Any]], title: str) -> dict[str, Any] | None:
    normalized_title = normalize_for_check(title)
    for index, entry in enumerate(top_songs, start=1):
        if normalize_for_check(str(entry.get("title", ""))) == normalized_title:
            song = dict(entry)
            song["rank"] = index
            return song
    return None


def zone_lookup(zones: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {zone["id"]: zone for zone in zones}


def estimate_text_capacity(
    zone: dict[str, Any],
    *,
    metrics: dict[str, float],
    page_dimensions: dict[str, Any] | None = None,
) -> int:
    dims = page_dimensions or PAGE_DIMENSIONS
    width_px = dims["width_px"] * float(zone["width"]) / 100.0
    height_px = dims["height_px"] * float(zone["height"]) / 100.0
    padding_px = float(metrics["padding_px"])
    column_gap_px = float(metrics["column_gap_px"])
    columns = int(metrics["columns"])
    font_size_px = float(metrics["font_size_px"])
    line_height = float(metrics["line_height"])

    usable_width = max(40.0, width_px - (padding_px * 2))
    usable_height = max(40.0, height_px - (padding_px * 2))
    if columns > 1:
        usable_width = max(40.0, (usable_width - column_gap_px * (columns - 1)) / columns)

    char_width_px = font_size_px * 0.54
    chars_per_line = max(12, int(usable_width / char_width_px))
    lines = max(3, int(usable_height / (font_size_px * line_height)))
    return chars_per_line * lines * columns


def load_page_bundle(year: int, page_slug: str) -> dict[str, Any]:
    target = get_target(year, page_slug)

    canonical_markdown_path = project_path(target.canonical_markdown)
    canonical_layout_path = project_path(target.canonical_layout_html)
    final_story_json_path = project_path(target.final_story_json)
    final_story_md_path = project_path(target.final_story_md)
    draft_story_json_path = project_path(target.draft_story_json)
    movies_data_path = project_path(target.movies_data_json)
    context_path = project_path(target.context_json)
    production_targets_path = project_path(target.production_targets_json)
    narrative_plan_path = project_path(target.narrative_plan_json)
    issue_map_path = project_path(target.issue_map_json)

    canonical_markdown = load_text(canonical_markdown_path)
    canonical_title, canonical_byline, canonical_paragraphs = parse_markdown_page(canonical_markdown)

    final_story = load_json(final_story_json_path)
    draft_story = load_json(draft_story_json_path)
    movies_data = load_json(movies_data_path)
    context = load_json(context_path)
    production_targets = load_json(production_targets_path)
    narrative_plan = load_json(narrative_plan_path)
    issue_map = load_json(issue_map_path)

    production_target = find_story_entry(production_targets.get("targets", []), target.story_id)
    narrative_story = find_story_entry(narrative_plan.get("story_assignments", []), target.story_id, field_name="id")
    story_design = find_story_entry(issue_map.get("story_design_assignments", []), target.story_id)
    visual_brief = find_story_entry(issue_map.get("visual_briefs", []), target.story_id)

    source_paths = [
        canonical_markdown_path,
        canonical_layout_path,
        final_story_json_path,
        final_story_md_path,
        draft_story_json_path,
        movies_data_path,
        context_path,
        production_targets_path,
        narrative_plan_path,
        issue_map_path,
    ]

    return {
        "target": target,
        "canonical_markdown_path": canonical_markdown_path,
        "canonical_layout_path": canonical_layout_path,
        "final_story_json_path": final_story_json_path,
        "final_story_md_path": final_story_md_path,
        "draft_story_json_path": draft_story_json_path,
        "movies_data_path": movies_data_path,
        "context_path": context_path,
        "production_targets_path": production_targets_path,
        "narrative_plan_path": narrative_plan_path,
        "issue_map_path": issue_map_path,
        "canonical_markdown": canonical_markdown,
        "canonical_title": canonical_title,
        "canonical_byline": canonical_byline,
        "canonical_paragraphs": canonical_paragraphs,
        "final_story": final_story,
        "draft_story": draft_story,
        "movies_data": movies_data,
        "context": context,
        "production_target": production_target,
        "narrative_story": narrative_story,
        "story_design": story_design,
        "visual_brief": visual_brief,
        "source_files": [relative_path(path) for path in source_paths],
    }


def qa_report_markdown(title: str, target_label: str, checks: list[dict[str, Any]], notes: list[str] | None = None) -> str:
    passed = all(check["passed"] for check in checks)
    lines = [
        f"# {title}",
        "",
        f"Target: `{target_label}`",
        "",
        f"Overall: **{'PASS' if passed else 'FAIL'}**",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(f"- [{status}] {check['label']}: {check['detail']}")
    if notes:
        lines.extend(["", "## Notes", ""])
        for note in notes:
            lines.append(f"- {note}")
    return "\n".join(lines)
