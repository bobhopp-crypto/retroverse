#!/usr/bin/env python3
"""Build RetroVerse art direction outputs from context, plans, and writer drafts."""

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RetroVerse art director engine.")
    parser.add_argument("--year", type=int, required=True, help="Issue year")
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def unique_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def parse_project_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing project state file: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    section = ""
    editorial_staff: list[dict[str, str]] = []
    generation_rules: list[str] = []
    magazine_structure: list[str] = []
    role_buffer: str | None = None

    for raw in lines:
        line = raw.strip()
        if line.startswith("## "):
            section = line
            role_buffer = None
            continue
        if not line or set(line) == {"-"}:
            continue

        if section == "## Editorial Staff":
            if role_buffer is None:
                role_buffer = line
                continue
            editorial_staff.append({"role": role_buffer, "name": line})
            role_buffer = None
            continue

        if section == "## Generation Rules":
            generation_rules.append(line)
            continue

        if section == "## Magazine Structure":
            magazine_structure.append(line)

    art_director_name = "Unassigned Art Director"
    for member in editorial_staff:
        if "art director" in member["role"].lower():
            art_director_name = member["name"]
            break

    return {
        "editorial_staff": editorial_staff,
        "generation_rules": generation_rules,
        "magazine_structure": magazine_structure,
        "art_director": art_director_name,
    }


def infer_story_medium(story: dict[str, Any]) -> str:
    explicit = story.get("primary_medium")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip().lower()

    category = str(story.get("category", "")).lower()
    story_type = str(story.get("story_type") or story.get("format") or "").lower()
    headline = str(story.get("headline") or story.get("title") or "").lower()
    signals = [str(item).lower() for item in story.get("supporting_signals", []) if isinstance(item, str)]
    joined = " ".join([category, story_type, headline, " ".join(signals)])

    if "television" in joined or " tv" in joined:
        return "television"
    if "movie" in joined or "film" in joined or "screen" in joined:
        return "movies"
    if "culture" in joined or "cultural_events" in joined:
        return "culture"
    if "chart" in joined or "song" in joined or "album" in joined or "artist" in joined:
        return "music"
    return "culture"


def story_role_from_signals(story: dict[str, Any]) -> tuple[str, str]:
    category = str(story.get("category", "")).lower()
    story_type = str(story.get("story_type") or story.get("format") or "").lower()
    medium = infer_story_medium(story)

    if "cover_feature" in category:
        return "cover feature", "cover-led opener"
    if story_type == "feature":
        return "feature spread", "two-page spread"
    if story_type == "profile":
        return "profile page", "single-page profile"
    if story_type == "chart breakdown":
        return "chart breakdown", "single-page infographic"
    if story_type == "timeline":
        return "timeline spread", "timeline spread"
    if story_type == "sidebar":
        return "sidebar box", "modular sidebar"
    if story_type == "data card set":
        return "data card set", "multi-card set"
    if medium in {"movies", "television"}:
        return "screen feature", "screen feature spread"
    if medium == "culture":
        return "culture collage", "collage page"
    return "short narrative page", "single-page narrative"


def target_map(story: dict[str, Any], role: str) -> tuple[str | int, str, str]:
    story_type = str(story.get("story_type") or story.get("format") or "").lower()
    signals = story.get("supporting_signals", [])
    signal_count = len(signals) if isinstance(signals, list) else 0

    if role == "cover feature":
        return 2, "900-1200", "2-3"
    if story_type == "feature":
        return 2, "900-1200", "2"
    if story_type == "profile":
        return 1, "500-700", "1"
    if story_type == "chart breakdown":
        return 1, "350-500", "2-3"
    if story_type == "timeline":
        pages = 2 if signal_count >= 4 else 1
        return pages, "450-850", "2"
    if story_type == "sidebar":
        return 1, "150-250", "1"
    if story_type == "data card set":
        return "multi-card set", "50-120 per card", "4-8"
    if story_type == "list":
        return 1, "300-450", "1-2"
    if story_type == "short narrative":
        return 1, "250-400", "1"
    return 1, "400-700", "1-2"


def needs_illustration(role: str) -> bool:
    return role not in {"chart breakdown", "data card set", "timeline spread"}


def choose_dependency(role: str) -> str:
    if role in {"chart breakdown", "data card set", "timeline spread"}:
        return "data card can be designed from structured facts"
    return "article must be finalized first"


def supporting_assets(story: dict[str, Any], role: str) -> list[str]:
    assets = ["article blueprint json", "writer draft markdown"]
    signals = [str(item).lower() for item in story.get("supporting_signals", []) if isinstance(item, str)]
    medium = infer_story_medium(story)

    if any("chart_dynamics" in signal or "album_dynamics" in signal for signal in signals):
        assets.append("chart movement tables")
    if any("top_songs" in signal or "top_artists" in signal or "artist_power_index" in signal for signal in signals):
        assets.append("song and artist ranking tables")
    if any("sonic_profile" in signal or "sonic_extremes" in signal for signal in signals):
        assets.append("sonic profile metrics")
    if any("movies" in signal or "television" in signal for signal in signals) or medium in {"movies", "television"}:
        assets.append("screen-culture warehouse extracts")
    if any("cultural_events" in signal for signal in signals) or medium == "culture":
        assets.append("cultural event timeline")
    if role in {"chart breakdown", "data card set"}:
        assets.append("data callout templates")
    return sorted(unique_list(assets))


def derive_palette(year: int, context: dict[str, Any], medium: str) -> str:
    sonic_profile = context.get("sonic_profile")
    danceability = 0.0
    energy = 0.0
    if isinstance(sonic_profile, dict):
        danceability = float(sonic_profile.get("average_danceability") or 0.0)
        energy = float(sonic_profile.get("average_energy") or 0.0)

    if medium in {"movies", "television"}:
        return "cinema marquee red, projector gold, CRT teal"
    if danceability >= 0.58 or energy >= 0.62:
        return "late-70s nightlife glow with warm neon and chrome accents"
    if 1970 <= year <= 1979:
        return "earthy newsprint base with saturated orange, cyan, and mustard accents"
    return "retro print palette with bold primaries and warm paper tones"


def era_markers(year: int) -> list[str]:
    if 1970 <= year <= 1979:
        return [
            "late-1970s editorial typography",
            "analog print grain",
            "halftone texture and warm paper stock",
        ]
    if 1980 <= year <= 1989:
        return ["bold geometric type", "airbrush gradients", "broadcast-era visual cues"]
    if 1990 <= year <= 1999:
        return ["high-contrast photo cutouts", "magazine collage edges", "neon accent bars"]
    return ["period-correct typography", "print-era layout rhythm", "archival texture layers"]


def key_objects_for_story(story: dict[str, Any], role: str) -> list[str]:
    medium = infer_story_medium(story)
    signals = [str(item).lower() for item in story.get("supporting_signals", []) if isinstance(item, str)]
    objects: list[str] = []

    if medium in {"music", "charts"}:
        objects.extend(["vinyl record", "chart arrow ladder", "radio dial"])
    if medium == "movies":
        objects.extend(["film reel", "theater marquee", "ticket stub"])
    if medium == "television":
        objects.extend(["rabbit-ear television", "channel guide grid", "living room glow"])
    if medium == "culture":
        objects.extend(["newspaper clippings", "street posters", "event flyers"])
    if any("sonic_profile" in signal for signal in signals):
        objects.append("equalizer bars")
    if any("album" in signal for signal in signals):
        objects.append("album stack")
    if role == "cover feature":
        objects.append("RetroVerse masthead lockup zone")
    return unique_list(objects)[:6]


def visual_type_for_role(role: str) -> str:
    mapping = {
        "cover feature": "cover concept",
        "feature spread": "full illustration",
        "profile page": "spot illustration",
        "chart breakdown": "infographic",
        "timeline spread": "timeline graphic",
        "sidebar box": "chart card",
        "data card set": "chart card",
        "short narrative page": "spot illustration",
        "screen feature": "collage",
        "culture collage": "collage",
    }
    return mapping.get(role, "spot illustration")


def visual_goal_for_role(role: str) -> str:
    mapping = {
        "cover feature": "Establish the year-defining narrative at first glance.",
        "feature spread": "Deliver a cinematic narrative visual that carries two pages.",
        "profile page": "Center one subject with clear supporting context.",
        "chart breakdown": "Make rank movement and chart facts immediately legible.",
        "timeline spread": "Show sequence and turning points across the year.",
        "sidebar box": "Provide a quick visual callout that supports nearby features.",
        "data card set": "Enable modular facts that can be reused across formats.",
        "short narrative page": "Support compact storytelling with one visual anchor.",
        "screen feature": "Blend film and television context into one editorial scene.",
        "culture collage": "Present a multi-signal snapshot of year-wide culture.",
    }
    return mapping.get(role, "Support the article with a clear period-correct visual anchor.")


def setting_for_story(story: dict[str, Any], role: str) -> str:
    medium = infer_story_medium(story)
    if role in {"chart breakdown", "data card set", "timeline spread"}:
        return "editorial data field with period print textures"
    if medium in {"movies", "television"}:
        return "split theater and living-room tableau"
    if medium == "culture":
        return "street-level collage grounded in year events"
    return "stylized editorial scene anchored in chart-era motifs"


def text_integration_notes(role: str) -> str:
    if role == "cover feature":
        return "Reserve top band for masthead and left column for teaser stack."
    if role in {"chart breakdown", "data card set", "timeline spread"}:
        return "Reserve a side rail for stats, labels, and source callouts."
    if role in {"feature spread", "screen feature", "culture collage"}:
        return "Leave clear headline zone and two pull-quote anchor zones."
    return "Maintain clean margin system for short copy and one quote callout."


def composition_notes(role: str) -> str:
    if role in {"chart breakdown", "timeline spread"}:
        return "Use directional movement so readers can parse sequence instantly."
    if role == "cover feature":
        return "Build a single dominant focal point with secondary signal motifs."
    if role == "data card set":
        return "Use a repeatable card grid with consistent icon placement."
    return "Use one hero focal point with supporting objects arranged by narrative weight."


def assignment_priority(story: dict[str, Any]) -> str:
    priority = story.get("priority")
    if isinstance(priority, str) and priority.strip():
        value = priority.strip().lower()
        if value in {"high", "medium", "low"}:
            return value
    return "medium"


def build_design_assignment(story: dict[str, Any]) -> dict[str, Any]:
    role, layout_type = story_role_from_signals(story)
    pages, word_target, image_target = target_map(story, role)
    priority = assignment_priority(story)
    dependency = choose_dependency(role)
    medium = infer_story_medium(story)

    return {
        "story_id": story["story_id"],
        "headline": story["headline"],
        "assigned_visual_role": role,
        "layout_type": layout_type,
        "page_count_estimate": pages,
        "word_count_target": word_target,
        "image_count_target": image_target,
        "visual_priority": priority,
        "illustration_required": needs_illustration(role),
        "illustration_dependency": dependency,
        "supporting_assets": supporting_assets(story, role),
        "primary_medium": medium,
        "writer": story["writer"],
    }


def build_visual_brief(
    year: int,
    story: dict[str, Any],
    design_assignment: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    role = str(design_assignment["assigned_visual_role"])
    medium = infer_story_medium(story)
    concept_seed = story["headline"].split(":")[0].strip()
    concept_seed = concept_seed if concept_seed else story["headline"]
    concept_name = f"{concept_seed[:56]} Visual"
    visual_type = visual_type_for_role(role)
    dependency = str(design_assignment["illustration_dependency"])

    return {
        "concept_name": concept_name,
        "related_story_id": story["story_id"],
        "related_headline": story["headline"],
        "visual_goal": visual_goal_for_role(role),
        "visual_type": visual_type,
        "key_objects": key_objects_for_story(story, role),
        "setting": setting_for_story(story, role),
        "era_markers": era_markers(year),
        "mood": "kinetic and nostalgic" if role in {"feature spread", "cover feature"} else "grounded and editorial",
        "palette_direction": derive_palette(year, context, medium),
        "composition_notes": composition_notes(role),
        "text_integration_notes": text_integration_notes(role),
        "dependency": dependency,
    }


def story_card(design: dict[str, Any]) -> dict[str, Any]:
    return {
        "story_id": design["story_id"],
        "headline": design["headline"],
        "layout_type": design["layout_type"],
        "page_count_estimate": design["page_count_estimate"],
        "visual_priority": design["visual_priority"],
    }


def build_issue_sections(designs: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {item["story_id"]: item for item in designs}
    priority_order = {"high": 0, "medium": 1, "low": 2}

    sorted_designs = sorted(
        designs,
        key=lambda item: (
            priority_order.get(str(item.get("visual_priority", "medium")), 1),
            str(item["story_id"]),
        ),
    )

    cover = next((item for item in sorted_designs if item["assigned_visual_role"] == "cover feature"), None)
    if cover is None and sorted_designs:
        cover = sorted_designs[0]

    used: set[str] = set()
    if cover:
        used.add(str(cover["story_id"]))

    def pick(predicate: Any) -> list[dict[str, Any]]:
        picked: list[dict[str, Any]] = []
        for item in sorted_designs:
            story_id = str(item["story_id"])
            if story_id in used:
                continue
            if predicate(item):
                picked.append(story_card(item))
                used.add(story_id)
        return picked

    front_of_book = pick(
        lambda item: item["assigned_visual_role"] in {"sidebar box", "short narrative page", "profile page"}
    )
    feature_well = pick(
        lambda item: item["assigned_visual_role"] in {"feature spread", "cover feature", "culture collage", "screen feature"}
    )
    charts_section = pick(
        lambda item: item["assigned_visual_role"] in {"chart breakdown", "timeline spread", "data card set"}
        or item["primary_medium"] in {"music", "charts"}
    )
    screen_section = pick(lambda item: item["primary_medium"] in {"movies", "television"} or item["assigned_visual_role"] == "screen feature")
    culture_section = pick(lambda item: item["primary_medium"] == "culture" or item["assigned_visual_role"] == "culture collage")

    back_of_book: list[dict[str, Any]] = []
    for item in sorted_designs:
        story_id = str(item["story_id"])
        if story_id in used:
            continue
        back_of_book.append(story_card(item))
        used.add(story_id)

    return {
        "cover": story_card(cover) if cover else {},
        "front_of_book": front_of_book,
        "feature_well": feature_well,
        "charts_section": charts_section,
        "screen_section": screen_section,
        "culture_section": culture_section,
        "back_of_book": back_of_book,
    }


def anchor_category_suggestions(story: dict[str, Any]) -> list[str]:
    categories: list[str] = []
    medium = infer_story_medium(story)
    if medium in {"music", "charts"}:
        categories.append("music")
    if medium == "movies":
        categories.append("film")
    if medium == "television":
        categories.append("television")
    if medium == "culture":
        categories.append("cultural events")

    signals = [str(item).lower() for item in story.get("supporting_signals", []) if isinstance(item, str)]
    if any("sonic_profile" in signal or "sonic_extremes" in signal for signal in signals):
        categories.append("sonic profile")
    if any("chart_dynamics" in signal or "album_dynamics" in signal for signal in signals):
        categories.append("chart dynamics")

    if not categories:
        categories = ["music", "film", "television", "cultural events"]

    return unique_list(categories)


def normalize_anchor(text: str) -> str:
    return " ".join(text.strip().lower().split())


def anchor_excerpt(text: str, limit: int = 140) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def detect_anchor_reuse(stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}

    for story in stories:
        context_text = str(story.get("cultural_context", "")).strip()
        if not context_text:
            continue
        key = normalize_anchor(context_text)
        bucket = groups.setdefault(key, {"text": context_text, "stories": []})
        bucket["stories"].append(story)

    warnings: list[dict[str, Any]] = []
    for bucket in groups.values():
        story_list = bucket["stories"]
        if len(story_list) <= 1:
            continue
        alt_categories: list[str] = []
        for story in story_list:
            alt_categories.extend(anchor_category_suggestions(story))
        warnings.append(
            {
                "anchor_excerpt": anchor_excerpt(str(bucket["text"])),
                "duplicate_count": len(story_list),
                "story_ids": [str(story["story_id"]) for story in story_list],
                "recommended_anchor_categories": unique_list(alt_categories),
                "note": "Rotate anchors across music, film, television, cultural events, sonic profile, and chart dynamics.",
            }
        )

    return sorted(warnings, key=lambda item: (-int(item["duplicate_count"]), str(item["story_ids"][0])))


def load_story_inputs(year: int) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    context_path = CONTEXT_DIR / f"{year}_context.json"
    plan_path = PLANS_DIR / f"{year}_narrative_plan.json"
    article_dir = ISSUES_ROOT / str(year) / "articles" / "final"

    if not context_path.exists():
        raise FileNotFoundError(f"Missing year context file: {context_path}")
    if not plan_path.exists():
        raise FileNotFoundError(f"Missing narrative plan file: {plan_path}")
    if not article_dir.exists():
        raise FileNotFoundError(f"Missing finalized article directory: {article_dir}")

    context = read_json(context_path)
    plan = read_json(plan_path)
    if not isinstance(context, dict):
        raise ValueError(f"Context payload is not an object: {context_path}")
    if not isinstance(plan, dict):
        raise ValueError(f"Narrative plan payload is not an object: {plan_path}")

    assignments = plan.get("story_assignments")
    if not isinstance(assignments, list):
        raise ValueError("Narrative plan missing story_assignments[]")

    assignment_by_id: dict[str, dict[str, Any]] = {}
    for item in assignments:
        if not isinstance(item, dict):
            continue
        story_id = item.get("story_id") or item.get("id")
        if isinstance(story_id, str) and story_id.strip():
            assignment_by_id[story_id.strip()] = item

    article_rows: list[dict[str, Any]] = []
    for path in sorted(article_dir.glob("*.json")):
        article = read_json(path)
        if not isinstance(article, dict):
            continue
        story_id = article.get("story_id")
        if not isinstance(story_id, str) or not story_id.strip():
            continue
        sid = story_id.strip()
        md_path = article_dir / f"{sid}.md"
        if not md_path.exists():
            raise FileNotFoundError(f"Missing article markdown companion file: {md_path}")
        md_text = md_path.read_text(encoding="utf-8")

        assignment = assignment_by_id.get(sid, {})
        source_signals = article.get("supporting_signals")
        if not isinstance(source_signals, list):
            source_signals = assignment.get("supporting_signals")
        if not isinstance(source_signals, list):
            source_signals = assignment.get("source_basis")
        if not isinstance(source_signals, list):
            source_signals = []

        article_rows.append(
            {
                "story_id": sid,
                "headline": str(article.get("headline") or assignment.get("headline") or assignment.get("title") or sid),
                "story_type": str(article.get("story_type") or assignment.get("story_type") or assignment.get("format") or "short narrative"),
                "category": str(assignment.get("category") or ""),
                "priority": str(assignment.get("priority") or "medium"),
                "primary_medium": str(article.get("primary_medium") or assignment.get("primary_medium") or "").strip().lower(),
                "supporting_signals": [str(item) for item in source_signals],
                "writer": str(article.get("writer") or "Unassigned"),
                "cultural_context": str(article.get("sections", {}).get("cultural_context", "")),
                "article_json_path": str(path.relative_to(PROJECT_ROOT)),
                "article_md_path": str(md_path.relative_to(PROJECT_ROOT)),
                "md_excerpt": " ".join(md_text.split())[:240],
            }
        )

    if not article_rows:
        raise ValueError(f"No finalized article JSON files found under {article_dir}")

    article_ids = {row["story_id"] for row in article_rows}
    missing_assignments = sorted(set(assignment_by_id.keys()) - article_ids)
    if missing_assignments:
        raise ValueError(
            "Missing finalized articles for planned story ids: " + ", ".join(missing_assignments)
        )

    article_rows = sorted(article_rows, key=lambda item: str(item["story_id"]))
    return context, plan, article_rows


def build_markdown(
    year: int,
    art_director: str,
    issue_sections: dict[str, Any],
    design_assignments: list[dict[str, Any]],
    visual_briefs: list[dict[str, Any]],
    anchor_warnings: list[dict[str, Any]],
    production_targets_path: Path,
) -> str:
    lines: list[str] = []
    lines.append(f"# RetroVerse {year} Issue Map")
    lines.append("")
    lines.append(f"- Art Director: {art_director}")
    lines.append(f"- Stories mapped: {len(design_assignments)}")
    lines.append(f"- Production targets file: {production_targets_path.relative_to(PROJECT_ROOT).as_posix()}")
    lines.append("")

    lines.append("## Issue Map")
    lines.append("")
    cover = issue_sections.get("cover", {})
    if isinstance(cover, dict) and cover:
        lines.append(f"- Cover: {cover.get('story_id')} - {cover.get('headline')}")
    for section_name in [
        "front_of_book",
        "feature_well",
        "charts_section",
        "screen_section",
        "culture_section",
        "back_of_book",
    ]:
        lines.append(f"- {section_name.replace('_', ' ').title()}:")
        rows = issue_sections.get(section_name, [])
        if isinstance(rows, list) and rows:
            for row in rows:
                lines.append(f"  - {row.get('story_id')}: {row.get('headline')} ({row.get('layout_type')})")
        else:
            lines.append("  - None")
    lines.append("")

    lines.append("## Story Design Assignments")
    lines.append("")
    for row in design_assignments:
        lines.append(
            f"- {row['story_id']}: {row['assigned_visual_role']} | {row['layout_type']} | "
            f"pages={row['page_count_estimate']} | words={row['word_count_target']} | "
            f"images={row['image_count_target']} | priority={row['visual_priority']}"
        )
    lines.append("")

    lines.append("## Visual Briefs")
    lines.append("")
    for brief in visual_briefs:
        lines.append(
            f"- {brief['related_story_id']}: {brief['concept_name']} | {brief['visual_type']} | "
            f"dependency={brief['dependency']}"
        )
    lines.append("")

    lines.append("## Anchor Reuse Warnings")
    lines.append("")
    if anchor_warnings:
        for warning in anchor_warnings:
            lines.append(
                f"- {warning['duplicate_count']} drafts reuse anchor: \"{warning['anchor_excerpt']}\" "
                f"(stories: {', '.join(warning['story_ids'])})"
            )
            lines.append(
                f"  Suggested alternates: {', '.join(warning['recommended_anchor_categories'])}"
            )
    else:
        lines.append("- No duplicate anchor reuse detected.")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def run(year: int) -> dict[str, Any]:
    project_state = parse_project_state(PROJECT_STATE_PATH)
    context, plan, stories = load_story_inputs(year)

    design_assignments = [build_design_assignment(story) for story in stories]
    visual_briefs = [
        build_visual_brief(year, story, design, context)
        for story, design in zip(stories, design_assignments)
    ]
    anchor_warnings = detect_anchor_reuse(stories)
    issue_sections = build_issue_sections(design_assignments)

    issue_map_payload = {
        "year": year,
        "art_director": project_state["art_director"],
        "editorial_rules_applied": project_state["generation_rules"],
        "magazine_structure_reference": project_state["magazine_structure"],
        "story_design_assignments": design_assignments,
        "visual_briefs": visual_briefs,
        "anchor_reuse_warnings": anchor_warnings,
        "issue_map": issue_sections,
    }

    production_targets = {
        "year": year,
        "art_director": project_state["art_director"],
        "targets": [
            {
                "story_id": design["story_id"],
                "headline": design["headline"],
                "writer": design["writer"],
                "final_word_count_target": design["word_count_target"],
                "layout_type": design["layout_type"],
                "visual_requirements": {
                    "assigned_visual_role": design["assigned_visual_role"],
                    "image_count_target": design["image_count_target"],
                    "illustration_required": design["illustration_required"],
                    "illustration_dependency": design["illustration_dependency"],
                },
                "asset_requirements": design["supporting_assets"],
                "final_prose_required_before_art": design["illustration_dependency"]
                == "article must be finalized first",
            }
            for design in design_assignments
        ],
    }

    layout_dir = ISSUES_ROOT / str(year) / "layout"
    layout_dir.mkdir(parents=True, exist_ok=True)
    issue_map_json_path = layout_dir / f"{year}_issue_map.json"
    issue_map_md_path = layout_dir / f"{year}_issue_map.md"
    production_targets_path = layout_dir / f"{year}_production_targets.json"

    issue_map_json_path.write_text(
        json.dumps(issue_map_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    production_targets_path.write_text(
        json.dumps(production_targets, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    issue_map_md_path.write_text(
        build_markdown(
            year,
            str(project_state["art_director"]),
            issue_sections,
            design_assignments,
            visual_briefs,
            anchor_warnings,
            production_targets_path,
        ),
        encoding="utf-8",
    )

    return {
        "year": year,
        "art_director": project_state["art_director"],
        "stories_processed": len(stories),
        "visual_briefs": len(visual_briefs),
        "anchor_reuse_warnings": len(anchor_warnings),
        "issue_map_json_path": issue_map_json_path,
        "issue_map_md_path": issue_map_md_path,
        "production_targets_path": production_targets_path,
    }


def main() -> int:
    args = parse_args()
    try:
        result = run(args.year)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"Art Director: {result['art_director']}")
    print(f"Stories processed: {result['stories_processed']}")
    print(f"Visual briefs generated: {result['visual_briefs']}")
    print(f"Anchor reuse warnings: {result['anchor_reuse_warnings']}")
    print(f"Issue map JSON: {result['issue_map_json_path']}")
    print(f"Issue map Markdown: {result['issue_map_md_path']}")
    print(f"Production targets: {result['production_targets_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
