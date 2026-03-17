#!/usr/bin/env python3
"""Assign staff writers and generate structured story drafts from the narrative plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_STATE_PATH = PROJECT_ROOT / "PROJECT_STATE.md"
CONTEXT_DIR = PROJECT_ROOT / "issues" / "context"
PLANS_DIR = PROJECT_ROOT / "issues" / "plans"
ISSUES_ROOT = PROJECT_ROOT / "issues"

WAREHOUSE_ROOT = Path("/Users/bobhopp/Sites/retroverse/data/raw/screen-culture/warehouse")
MOVIES_BY_YEAR_PATH = WAREHOUSE_ROOT / "movies_by_year.json"
TELEVISION_BY_YEAR_PATH = WAREHOUSE_ROOT / "television_by_year.json"
INVENTORY_PATH = WAREHOUSE_ROOT / "screen_culture_inventory.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RetroVerse staff writer assignment and draft generation.")
    parser.add_argument("--year", type=int, required=True, help="Issue year")
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_role_to_beat(role: str) -> str:
    lowered = role.lower()
    if "music" in lowered:
        return "music"
    if "chart" in lowered:
        return "charts"
    if "culture" in lowered:
        return "culture"
    if "film" in lowered or "television" in lowered or "tv" in lowered:
        return "screen"
    if "humor" in lowered or "comic" in lowered:
        return "humor"
    if "editor in chief" in lowered:
        return "editorial"
    if "art director" in lowered:
        return "art"
    return "general"


def build_writer_voice(role: str, beat: str) -> str:
    if beat == "music":
        return "music-first and era-aware"
    if beat == "charts":
        return "data-forward chart narration"
    if beat == "culture":
        return "wide-lens cultural framing"
    if beat == "screen":
        return "screen-criticism with historical context"
    if beat == "humor":
        return "light satirical commentary"
    if beat == "editorial":
        return "editorial oversight voice"
    return role


def build_writer_data_focus(beat: str) -> str:
    if beat in {"music", "charts"}:
        return "chart_dynamics, artist_power_index, sonic_profile"
    if beat == "screen":
        return "movies, television, screen_culture_warehouse"
    if beat == "culture":
        return "cultural_events, year timeline signals"
    if beat == "humor":
        return "sidebars, fast-facts, reusable callouts"
    return "issue context and editorial continuity"


def parse_project_state(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    staff_writers: list[dict[str, str]] = []
    in_staff = False
    role_buffer: str | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if line == "## Editorial Staff":
            in_staff = True
            continue
        if in_staff and line.startswith("## "):
            in_staff = False
        if not in_staff:
            continue
        if not line or set(line) == {"-"}:
            continue

        if role_buffer is None:
            role_buffer = line
            continue

        name = line
        role = role_buffer
        role_buffer = None

        beat = normalize_role_to_beat(role)
        staff_writers.append(
            {
                "name": name,
                "role": role,
                "beat": beat,
                "voice": build_writer_voice(role, beat),
                "data_focus": build_writer_data_focus(beat),
            }
        )

    editorial_rules: list[str] = []
    in_rules = False
    for raw_line in lines:
        line = raw_line.strip()
        if line == "## Generation Rules":
            in_rules = True
            continue
        if in_rules and line.startswith("## "):
            break
        if not in_rules:
            continue
        if not line or set(line) == {"-"}:
            continue
        editorial_rules.append(line)

    return staff_writers, editorial_rules


def get_source_basis(assignment: dict[str, Any]) -> list[str]:
    signals = assignment.get("supporting_signals")
    if isinstance(signals, list):
        return [str(item) for item in signals]
    basis = assignment.get("source_basis")
    if isinstance(basis, list):
        return [str(item) for item in basis]
    return []


def lookup_path(payload: dict[str, Any], dotted_path: str) -> Any:
    node: Any = payload
    for part in dotted_path.split("."):
        if isinstance(node, dict):
            node = node.get(part)
        else:
            return None
    return node


def summarize_value(path: str, value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, list):
        if not value:
            return f"{path}: 0 entries"
        sample = value[0]
        if isinstance(sample, dict):
            if "title" in sample and "artist" in sample:
                return f"{path}: {len(value)} entries; sample {sample.get('title')} — {sample.get('artist')}"
            if "label" in sample and "subject" in sample:
                return f"{path}: {len(value)} highlights; sample {sample.get('label')}: {sample.get('subject')}"
            sample_text = ", ".join(str(item) for item in list(sample.values())[:2])
            return f"{path}: {len(value)} entries; sample {sample_text}"
        return f"{path}: {len(value)} entries; sample {sample}"

    if isinstance(value, dict):
        keys = list(value.keys())
        return f"{path}: {len(keys)} fields ({', '.join(keys[:3])})"

    return f"{path}: {value}"


def infer_story_medium(assignment: dict[str, Any], context: dict[str, Any]) -> str:
    explicit_medium = assignment.get("primary_medium")
    if isinstance(explicit_medium, str) and explicit_medium.strip():
        return explicit_medium.strip().lower()

    category = str(assignment.get("category", "")).lower()
    title = str(assignment.get("title") or assignment.get("headline") or "").lower()
    basis_items = [item.lower() for item in get_source_basis(assignment)]

    joined = " ".join([category, title, " ".join(basis_items)])

    if "television" in joined or " tv" in joined:
        return "television"
    if "movie" in joined or "film" in joined or "screen" in category:
        return "movies"
    if "culture" in category or "cultural_events" in joined:
        return "culture"
    if "chart" in category or any(item.startswith("chart_dynamics") for item in basis_items):
        return "charts"
    if any(token in joined for token in ["album", "song", "artist", "sonic", "music"]):
        return "music"

    if isinstance(context.get("movies"), list) and isinstance(context.get("television"), list):
        return "culture"
    return "music"


def pick_writer(staff_writers: list[dict[str, str]], medium: str, category: str) -> dict[str, str]:
    category_lower = category.lower()

    preferred_order: list[str]
    if "chart" in category_lower:
        preferred_order = ["charts", "music", "editorial"]
    elif medium == "music":
        preferred_order = ["music", "charts", "editorial"]
    elif medium in {"movies", "television", "screen"}:
        preferred_order = ["screen", "culture", "editorial"]
    elif medium == "culture":
        preferred_order = ["culture", "screen", "editorial"]
    elif medium == "humor":
        preferred_order = ["humor", "culture", "editorial"]
    else:
        preferred_order = ["editorial", "culture", "music"]

    for beat in preferred_order:
        for writer in staff_writers:
            if writer.get("beat") == beat:
                return writer

    return staff_writers[0] if staff_writers else {
        "name": "Unassigned",
        "beat": "general",
        "voice": "general",
        "data_focus": "context",
    }


def unique_list(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def build_data_highlights(
    assignment: dict[str, Any],
    year: int,
    context: dict[str, Any],
    movies_by_year: dict[str, Any],
    television_by_year: dict[str, Any],
) -> list[str]:
    highlights: list[str] = []
    basis_items = get_source_basis(assignment)

    for path in basis_items:
        value = lookup_path(context, path)
        summary = summarize_value(path, value)
        if summary:
            highlights.append(summary)

    year_key = str(year)
    movie_rows = movies_by_year.get(year_key) if isinstance(movies_by_year, dict) else None
    tv_rows = television_by_year.get(year_key) if isinstance(television_by_year, dict) else None

    if isinstance(movie_rows, list):
        highlights.append(f"screen_culture_warehouse.movies_by_year[{year_key}]: {len(movie_rows)} records")
    if isinstance(tv_rows, list):
        highlights.append(f"screen_culture_warehouse.television_by_year[{year_key}]: {len(tv_rows)} records")

    return unique_list(highlights)[:6]


def build_cultural_context(year: int, context: dict[str, Any]) -> str:
    events = context.get("cultural_events")
    if isinstance(events, list) and events:
        first = events[0]
        if isinstance(first, dict):
            event_text = str(first.get("event") or first.get("headline") or "").strip()
            event_date = str(first.get("date") or "").strip()
            if event_text and event_date:
                return f"Context anchor: {event_date} — {event_text}"
            if event_text:
                return f"Context anchor: {event_text}"
        if isinstance(first, str):
            return f"Context anchor: {first}"

    movies = context.get("movies")
    if isinstance(movies, list) and movies:
        return f"Screen context: {len(movies)} film references in year data."

    television = context.get("television")
    if isinstance(television, list) and television:
        return f"Television context: {len(television)} TV references in year data."

    return "Context anchor: This draft is grounded in internal RetroVerse year data."


def build_article(
    year: int,
    assignment: dict[str, Any],
    writer: dict[str, str],
    editorial_rules: list[str],
    context: dict[str, Any],
    movies_by_year: dict[str, Any],
    television_by_year: dict[str, Any],
) -> dict[str, Any]:
    story_id = str(assignment.get("story_id") or assignment.get("id") or "").strip()
    if not story_id:
        raise ValueError("Story assignment is missing id/story_id")

    headline = str(assignment.get("headline") or assignment.get("title") or story_id).strip()
    story_type = str(assignment.get("story_type") or assignment.get("format") or "short narrative").strip()
    category = str(assignment.get("category") or "").strip()
    medium = infer_story_medium(assignment, context)

    highlights = build_data_highlights(assignment, year, context, movies_by_year, television_by_year)
    source_basis = get_source_basis(assignment)

    rules_excerpt = "; ".join(editorial_rules[:2]) if editorial_rules else "Use real historical data from internal datasets."

    lede = (
        f"{writer['name']} ({writer['role']}) opens this {story_type} by framing {headline} through "
        f"{medium} evidence from the {year} RetroVerse dataset."
    )
    analysis = (
        f"Primary lens: {writer['voice']}. Beat alignment: {writer['beat']}. "
        f"Data focus: {writer['data_focus']}."
    )

    cultural_context = build_cultural_context(year, context)
    closing = (
        f"Editorial rule check: {rules_excerpt}. This draft remains a data-grounded planning draft for the full article stage."
    )

    sources_used = unique_list(
        [
            PROJECT_STATE_PATH.relative_to(PROJECT_ROOT).as_posix(),
            (PLANS_DIR / f"{year}_narrative_plan.json").relative_to(PROJECT_ROOT).as_posix(),
            (CONTEXT_DIR / f"{year}_context.json").relative_to(PROJECT_ROOT).as_posix(),
            str(MOVIES_BY_YEAR_PATH),
            str(TELEVISION_BY_YEAR_PATH),
            str(INVENTORY_PATH),
            *source_basis,
        ]
    )

    article = {
        "story_id": story_id,
        "headline": headline,
        "writer": writer["name"],
        "writer_role": writer.get("role", ""),
        "story_type": story_type,
        "primary_medium": medium,
        "supporting_signals": source_basis,
        "sections": {
            "lede": lede,
            "analysis": analysis,
            "data_highlights": highlights,
            "cultural_context": cultural_context,
            "closing": closing,
        },
        "sources_used": sources_used,
    }

    return article


def to_markdown(article: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {article['headline']}")
    lines.append("")
    lines.append(f"- Story ID: {article['story_id']}")
    lines.append(f"- Writer: {article['writer']} ({article.get('writer_role', '')})")
    lines.append(f"- Story Type: {article.get('story_type', '')}")
    lines.append(f"- Primary Medium: {article.get('primary_medium', '')}")
    lines.append("")

    sections = article.get("sections", {})
    lines.append("## Lede")
    lines.append("")
    lines.append(str(sections.get("lede", "")))
    lines.append("")

    lines.append("## Analysis")
    lines.append("")
    lines.append(str(sections.get("analysis", "")))
    lines.append("")

    lines.append("## Data Highlights")
    lines.append("")
    for item in sections.get("data_highlights", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Cultural Context")
    lines.append("")
    lines.append(str(sections.get("cultural_context", "")))
    lines.append("")

    lines.append("## Closing")
    lines.append("")
    lines.append(str(sections.get("closing", "")))
    lines.append("")

    lines.append("## Sources Used")
    lines.append("")
    for source in article.get("sources_used", []):
        lines.append(f"- {source}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def run(year: int) -> dict[str, Any]:
    staff_writers, editorial_rules = parse_project_state(PROJECT_STATE_PATH)
    if not staff_writers:
        raise ValueError("No staff writers could be parsed from PROJECT_STATE.md")

    plan_path = PLANS_DIR / f"{year}_narrative_plan.json"
    context_path = CONTEXT_DIR / f"{year}_context.json"

    if not plan_path.exists():
        raise FileNotFoundError(f"Narrative plan missing: {plan_path}")
    if not context_path.exists():
        raise FileNotFoundError(f"Year context missing: {context_path}")

    plan = read_json(plan_path)
    context = read_json(context_path)

    if not isinstance(plan, dict):
        raise ValueError(f"Narrative plan is invalid JSON object: {plan_path}")
    if not isinstance(context, dict):
        raise ValueError(f"Year context is invalid JSON object: {context_path}")

    story_assignments = plan.get("story_assignments")
    if not isinstance(story_assignments, list):
        raise ValueError("Narrative plan missing story_assignments[]")

    movies_by_year = read_json(MOVIES_BY_YEAR_PATH) if MOVIES_BY_YEAR_PATH.exists() else {}
    television_by_year = read_json(TELEVISION_BY_YEAR_PATH) if TELEVISION_BY_YEAR_PATH.exists() else {}

    article_dir = ISSUES_ROOT / str(year) / "articles"
    article_dir.mkdir(parents=True, exist_ok=True)

    generated_files: list[str] = []
    writer_assignments: dict[str, int] = {}

    for index, assignment in enumerate(story_assignments, start=1):
        if not isinstance(assignment, dict):
            continue

        category = str(assignment.get("category") or "").strip()
        medium = infer_story_medium(assignment, context)
        writer = pick_writer(staff_writers, medium, category)

        article = build_article(
            year,
            assignment,
            writer,
            editorial_rules,
            context,
            movies_by_year if isinstance(movies_by_year, dict) else {},
            television_by_year if isinstance(television_by_year, dict) else {},
        )

        story_id = article["story_id"]
        json_path = article_dir / f"{story_id}.json"
        md_path = article_dir / f"{story_id}.md"

        json_path.write_text(json.dumps(article, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md_path.write_text(to_markdown(article), encoding="utf-8")

        generated_files.append(json_path.name)
        generated_files.append(md_path.name)
        writer_name = writer["name"]
        writer_assignments[writer_name] = writer_assignments.get(writer_name, 0) + 1

    return {
        "year": year,
        "story_assignments": len([item for item in story_assignments if isinstance(item, dict)]),
        "articles_generated": len([name for name in generated_files if name.endswith(".json")]),
        "article_dir": article_dir,
        "writer_assignments": writer_assignments,
    }


def main() -> int:
    args = parse_args()
    try:
        result = run(args.year)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"Staff writers assigned: {sum(result['writer_assignments'].values())}")
    print(f"Articles generated: {result['articles_generated']}")
    print(f"Output directory: {result['article_dir']}")
    for writer_name, count in sorted(result["writer_assignments"].items()):
        print(f"- {writer_name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
