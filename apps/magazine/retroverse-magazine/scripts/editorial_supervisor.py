#!/usr/bin/env python3
"""Coordinate data preparation and integrity checks for a RetroVerse issue."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_STATE_PATH = PROJECT_ROOT / "PROJECT_STATE.md"
DATA_SOURCES_PATH = PROJECT_ROOT / "data" / "DATA_SOURCES.yaml"
DATA_INVENTORY_PATH = PROJECT_ROOT / "DATA_INVENTORY.md"
CONTEXT_DIR = PROJECT_ROOT / "issues" / "context"
PLANS_DIR = PROJECT_ROOT / "issues" / "plans"
UPDATE_INVENTORY_SCRIPT = PROJECT_ROOT / "scripts" / "update_data_inventory.py"
GENERATE_CONTEXT_SCRIPT = PROJECT_ROOT / "scripts" / "generate_year_context.py"
AUDIT_SCREEN_CULTURE_SCRIPT = PROJECT_ROOT / "scripts" / "audit_screen_culture_data.py"
ANALYZE_DYNAMICS_SCRIPT = PROJECT_ROOT / "scripts" / "analyze_chart_dynamics.py"
GENERATE_NARRATIVE_SCRIPT = PROJECT_ROOT / "scripts" / "generate_year_narrative.py"
RUN_STAFF_WRITERS_SCRIPT = PROJECT_ROOT / "scripts" / "run_staff_writers.py"
RUN_ART_DIRECTOR_SCRIPT = PROJECT_ROOT / "scripts" / "run_art_director.py"
GENERATE_FINAL_ARTICLES_SCRIPT = PROJECT_ROOT / "scripts" / "generate_final_articles.py"
SCREEN_CULTURE_AUDIT_REPORT_PATH = PROJECT_ROOT / "docs" / "SCREEN_CULTURE_DATA_AUDIT.md"
ARTICLES_DIR = PROJECT_ROOT / "issues" / "articles"
LAYOUT_DIR = PROJECT_ROOT / "issues" / "layout"
FINAL_DIR = PROJECT_ROOT / "issues" / "final"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RetroVerse editorial supervisor checks.")
    parser.add_argument("--year", default="1978", help="Issue year (default: 1978)")
    return parser.parse_args()


def run_script(script_path: Path, args: list[str]) -> None:
    cmd = [sys.executable, str(script_path), *args]
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with code {result.returncode}: {' '.join(cmd)}")


def ensure_project_state() -> None:
    if not PROJECT_STATE_PATH.exists():
        raise FileNotFoundError("PROJECT_STATE.md not found")
    _ = PROJECT_STATE_PATH.read_text(encoding="utf-8")


def ensure_data_sources() -> None:
    if not DATA_SOURCES_PATH.exists():
        raise FileNotFoundError("data/DATA_SOURCES.yaml not found")
    _ = DATA_SOURCES_PATH.read_text(encoding="utf-8")


def ensure_data_inventory() -> str:
    if DATA_INVENTORY_PATH.exists():
        return "OK"
    run_script(UPDATE_INVENTORY_SCRIPT, ["--write"])
    return "GENERATED"


def context_needs_refresh(payload: dict[str, object]) -> bool:
    context_sources = payload.get("context_sources")
    if not isinstance(context_sources, dict):
        return True
    required_keys = ["billboard_hot100", "billboard_200", "audio_features", "year_end_top_40", "retroverse_master"]
    return any(key not in context_sources for key in required_keys)


def ensure_year_context(year: str) -> Path:
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    context_path = CONTEXT_DIR / f"{year}_context.json"

    if context_path.exists():
        try:
            payload = json.loads(context_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and not context_needs_refresh(payload):
                return context_path
        except json.JSONDecodeError:
            pass

    run_script(GENERATE_CONTEXT_SCRIPT, ["--year", year])
    return context_path


def ensure_screen_culture_coverage(year: str) -> tuple[str, list[str]]:
    cmd = [sys.executable, str(AUDIT_SCREEN_CULTURE_SCRIPT), "--year", year]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)

    warnings: list[str] = []
    if result.returncode != 0:
        warnings.append(f"Screen/culture audit command failed with code {result.returncode}.")
        if result.stderr.strip():
            warnings.append(result.stderr.strip().splitlines()[-1])
        return "INCOMPLETE", warnings

    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    match = re.search(r"Overall coverage status:\s*(OK|INCOMPLETE)", output)
    status = match.group(1) if match else "INCOMPLETE"

    if not SCREEN_CULTURE_AUDIT_REPORT_PATH.exists():
        warnings.append("Screen/culture audit report file was not generated.")

    if status == "INCOMPLETE":
        warnings.append("Screen/culture coverage is below thresholds for at least one required category.")

    return status, warnings


def ensure_chart_dynamics(year: str, context_path: Path) -> str:
    run_script(ANALYZE_DYNAMICS_SCRIPT, ["--year", year])
    payload = json.loads(context_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Context file is not an object: {context_path}")
    if "chart_dynamics" not in payload or "album_dynamics" not in payload:
        raise ValueError("Chart dynamics stage did not append expected keys to context.")
    return "OK"


def ensure_year_narrative_plan(year: str) -> str:
    run_script(GENERATE_NARRATIVE_SCRIPT, ["--year", year])
    plan_path = PLANS_DIR / f"{year}_narrative_plan.json"
    if not plan_path.exists():
        raise ValueError(f"Narrative plan file missing: {plan_path}")

    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Narrative plan is not a JSON object: {plan_path}")

    required_keys = {
        "year_identity",
        "table_of_contents",
        "story_assignments",
        "chart_highlights",
        "year_snapshot_boxes",
        "visual_concepts",
    }
    missing = [key for key in sorted(required_keys) if key not in payload]
    if missing:
        raise ValueError(f"Narrative plan missing required keys: {', '.join(missing)}")
    return "OK"


def ensure_staff_writer_drafts(year: str) -> tuple[str, int, int]:
    run_script(RUN_STAFF_WRITERS_SCRIPT, ["--year", year])

    plan_path = PLANS_DIR / f"{year}_narrative_plan.json"
    if not plan_path.exists():
        raise ValueError(f"Narrative plan file missing for writer run: {plan_path}")

    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Narrative plan is not a JSON object: {plan_path}")

    story_assignments = payload.get("story_assignments")
    if not isinstance(story_assignments, list):
        raise ValueError("Narrative plan missing story_assignments[] for writer validation")

    expected_story_ids: list[str] = []
    for assignment in story_assignments:
        if not isinstance(assignment, dict):
            continue
        story_id = assignment.get("story_id") or assignment.get("id")
        if isinstance(story_id, str) and story_id.strip():
            expected_story_ids.append(story_id.strip())

    if not expected_story_ids:
        raise ValueError("Narrative plan has no story ids for writer validation")

    article_dir = ARTICLES_DIR / year
    if not article_dir.exists():
        raise ValueError(f"Articles directory missing after writer run: {article_dir}")

    for story_id in expected_story_ids:
        json_path = article_dir / f"{story_id}.json"
        md_path = article_dir / f"{story_id}.md"
        if not json_path.exists():
            raise ValueError(f"Missing article JSON for story {story_id}: {json_path}")
        if not md_path.exists():
            raise ValueError(f"Missing article Markdown for story {story_id}: {md_path}")
        article = json.loads(json_path.read_text(encoding="utf-8"))
        if isinstance(article, dict):
            writer_name = article.get("writer")
            if not isinstance(writer_name, str) or not writer_name.strip():
                raise ValueError(f"Missing writer name in article JSON: {json_path}")

    return "OK", len(expected_story_ids), len(expected_story_ids)


def ensure_art_director_outputs(year: str) -> tuple[str, str, str]:
    run_script(RUN_ART_DIRECTOR_SCRIPT, ["--year", year])

    issue_map_json = LAYOUT_DIR / f"{year}_issue_map.json"
    issue_map_md = LAYOUT_DIR / f"{year}_issue_map.md"
    production_targets = LAYOUT_DIR / f"{year}_production_targets.json"

    map_created = "YES" if issue_map_json.exists() and issue_map_md.exists() else "NO"
    targets_created = "YES" if production_targets.exists() else "NO"

    if map_created == "NO":
        raise ValueError(f"Issue map files missing after art director run for year {year}")
    if targets_created == "NO":
        raise ValueError(f"Production targets file missing after art director run for year {year}")

    map_payload = json.loads(issue_map_json.read_text(encoding="utf-8"))
    if not isinstance(map_payload, dict):
        raise ValueError(f"Issue map JSON is not an object: {issue_map_json}")

    required_map_keys = {
        "year",
        "issue_map",
        "story_design_assignments",
        "visual_briefs",
        "anchor_reuse_warnings",
    }
    missing_keys = [key for key in sorted(required_map_keys) if key not in map_payload]
    if missing_keys:
        raise ValueError(f"Issue map JSON missing required keys: {', '.join(missing_keys)}")

    story_assignments = map_payload.get("story_design_assignments")
    visual_briefs = map_payload.get("visual_briefs")
    if not isinstance(story_assignments, list):
        raise ValueError("Issue map missing story_design_assignments[]")
    if not isinstance(visual_briefs, list):
        raise ValueError("Issue map missing visual_briefs[]")

    story_ids: set[str] = set()
    for item in story_assignments:
        if not isinstance(item, dict):
            continue
        story_id = item.get("story_id")
        if isinstance(story_id, str) and story_id.strip():
            story_ids.add(story_id.strip())

    brief_ids: set[str] = set()
    for item in visual_briefs:
        if not isinstance(item, dict):
            continue
        story_id = item.get("related_story_id")
        if isinstance(story_id, str) and story_id.strip():
            brief_ids.add(story_id.strip())

    missing_briefs = sorted(story_ids - brief_ids)
    if missing_briefs:
        raise ValueError("Missing visual briefs for stories: " + ", ".join(missing_briefs))

    article_dir = ARTICLES_DIR / year
    article_story_ids = {path.stem for path in article_dir.glob("*.json")} if article_dir.exists() else set()
    missing_for_articles = sorted(article_story_ids - brief_ids)
    if missing_for_articles:
        raise ValueError(
            "Missing visual briefs for article drafts: " + ", ".join(missing_for_articles)
        )

    return "OK", map_created, targets_created


def expected_story_ids(year: str) -> list[str]:
    plan_path = PLANS_DIR / f"{year}_narrative_plan.json"
    if not plan_path.exists():
        raise ValueError(f"Narrative plan file missing: {plan_path}")

    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Narrative plan is not a JSON object: {plan_path}")

    story_assignments = payload.get("story_assignments")
    if not isinstance(story_assignments, list):
        raise ValueError("Narrative plan missing story_assignments[]")

    ids: list[str] = []
    for assignment in story_assignments:
        if not isinstance(assignment, dict):
            continue
        story_id = assignment.get("story_id") or assignment.get("id")
        if isinstance(story_id, str) and story_id.strip():
            ids.append(story_id.strip())

    unique_ids: list[str] = []
    seen: set[str] = set()
    for story_id in ids:
        if story_id in seen:
            continue
        seen.add(story_id)
        unique_ids.append(story_id)
    return unique_ids


def ensure_final_prose_outputs(year: str) -> tuple[str, int]:
    run_script(GENERATE_FINAL_ARTICLES_SCRIPT, ["--year", year])

    story_ids = expected_story_ids(year)
    if not story_ids:
        raise ValueError("No story ids available for final prose validation")

    final_year_dir = FINAL_DIR / year
    if not final_year_dir.exists():
        raise ValueError(f"Final article output directory missing: {final_year_dir}")

    required_dataset_labels = {
        "Billboard Hot 100 data",
        "Billboard 200 album data",
        "chart_dynamics",
        "album_dynamics",
        "sonic_profile",
        "screen_culture_warehouse",
    }

    finalized_count = 0
    for story_id in story_ids:
        json_path = final_year_dir / f"{story_id}.json"
        md_path = final_year_dir / f"{story_id}.md"
        if not json_path.exists():
            raise ValueError(f"Missing finalized article JSON for story {story_id}: {json_path}")
        if not md_path.exists():
            raise ValueError(f"Missing finalized article Markdown for story {story_id}: {md_path}")

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Final article JSON is not an object: {json_path}")

        required_top_keys = {
            "story_id",
            "headline",
            "byline",
            "word_count",
            "target_word_range",
            "sections",
            "datasets_used",
            "data_references",
        }
        missing_top = [key for key in sorted(required_top_keys) if key not in payload]
        if missing_top:
            raise ValueError(
                f"Final article JSON missing required keys ({', '.join(missing_top)}): {json_path}"
            )

        sections = payload.get("sections")
        if not isinstance(sections, dict):
            raise ValueError(f"Final article sections value is not an object: {json_path}")
        required_sections = {
            "lede",
            "analysis",
            "data_context",
            "cultural_significance",
            "closing",
        }
        missing_sections = [key for key in sorted(required_sections) if key not in sections]
        if missing_sections:
            raise ValueError(
                f"Final article sections missing keys ({', '.join(missing_sections)}): {json_path}"
            )

        word_count = payload.get("word_count")
        target_range = payload.get("target_word_range")
        if not isinstance(word_count, int):
            raise ValueError(f"Final article word_count is not an integer: {json_path}")
        if not isinstance(target_range, dict):
            raise ValueError(f"Final article target_word_range is not an object: {json_path}")

        min_words = target_range.get("min")
        max_words = target_range.get("max")
        if not isinstance(min_words, int) or not isinstance(max_words, int):
            raise ValueError(
                f"Final article target_word_range min/max are not integers: {json_path}"
            )
        if word_count < min_words or word_count > max_words:
            raise ValueError(
                f"Final article word count out of bounds for {story_id}: "
                f"{word_count} not in {min_words}-{max_words}"
            )

        datasets_used = payload.get("datasets_used")
        if not isinstance(datasets_used, list) or not datasets_used:
            raise ValueError(f"Final article datasets_used[] missing or empty: {json_path}")
        dataset_set = {str(item) for item in datasets_used if isinstance(item, str)}
        missing_datasets = sorted(required_dataset_labels - dataset_set)
        if missing_datasets:
            raise ValueError(
                f"Final article missing required dataset labels "
                f"({', '.join(missing_datasets)}): {json_path}"
            )

        data_references = payload.get("data_references")
        if not isinstance(data_references, list) or not data_references:
            raise ValueError(f"Final article data_references[] missing or empty: {json_path}")

        finalized_count += 1

    return "OK", finalized_count


def load_context(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Context file is not an object: {path}")
    return payload


def source_status(payload: dict[str, object], key: str) -> str:
    context_sources = payload.get("context_sources")
    if not isinstance(context_sources, dict):
        return "missing"
    status = context_sources.get(key)
    if isinstance(status, str) and status in {"canonical", "fallback", "missing"}:
        return status
    return "missing"


def print_report(
    year: str,
    inventory_state: str,
    context_path: Path,
    context_payload: dict[str, object],
    screen_culture_state: str,
    screen_culture_warnings: list[str],
    chart_dynamics_state: str,
    narrative_plan_state: str,
    staff_writer_state: str,
    staff_writer_count: int,
    articles_generated: int,
    art_director_state: str,
    issue_map_created: str,
    production_targets_created: str,
    final_prose_state: str,
    articles_finalized: int,
) -> None:
    rel_context = context_path.relative_to(PROJECT_ROOT).as_posix()

    hot100 = source_status(context_payload, "billboard_hot100")
    b200 = source_status(context_payload, "billboard_200")
    audio = source_status(context_payload, "audio_features")
    year_end = source_status(context_payload, "year_end_top_40")
    master = source_status(context_payload, "retroverse_master")

    print("## Editorial Supervisor Report")
    print("")
    print("Project state: OK")
    print("Data source map: OK")
    print(f"Data inventory: {'OK' if inventory_state == 'OK' else 'GENERATED'}")
    print(f"Screen & Culture coverage: {screen_culture_state}")
    print(f"Chart dynamics: {chart_dynamics_state}")
    print(f"Year narrative plan: {narrative_plan_state}")
    print(f"Staff writer engine: {staff_writer_state}")
    print(f"Staff writers assigned: {staff_writer_count}")
    print(f"Articles generated: {articles_generated}")
    print(f"Art director engine: {art_director_state}")
    print(f"Issue map created: {issue_map_created}")
    print(f"Production targets created: {production_targets_created}")
    print(f"Final prose engine: {final_prose_state}")
    print(f"Articles finalized: {articles_finalized}")
    print(f"Context file: {rel_context}")
    print("")
    print("Context sources:")
    print(f"Billboard Hot 100: {hot100}")
    print(f"Billboard 200: {b200}")
    print(f"Audio Features: {audio}")
    print("")
    print("Fallback sources:")
    fallback_rows = []
    if year_end == "fallback":
        fallback_rows.append("Year End Top 40: fallback")
    if master == "fallback":
        fallback_rows.append("RetroVerse Master: fallback")
    if fallback_rows:
        for row in fallback_rows:
            print(row)
    else:
        print("None")

    degraded_canonical: list[str] = []
    if hot100 != "canonical":
        degraded_canonical.append(f"Billboard Hot 100 ({hot100})")
    if b200 != "canonical":
        degraded_canonical.append(f"Billboard 200 ({b200})")
    if audio != "canonical":
        degraded_canonical.append(f"Audio Features ({audio})")

    if degraded_canonical:
        print("")
        print("WARNING: Canonical music layer degraded:")
        for label in degraded_canonical:
            print(f"- {label}")

    if screen_culture_warnings:
        print("")
        print("WARNING: Screen & Culture coverage:")
        for warning in screen_culture_warnings:
            print(f"- {warning}")

    print("")
    print(f"Ready to assign stories for {year}")


def main() -> int:
    args = parse_args()
    year = str(args.year)

    try:
        ensure_project_state()
        ensure_data_sources()
        inventory_state = ensure_data_inventory()
        context_path = ensure_year_context(year)
        screen_culture_state, screen_culture_warnings = ensure_screen_culture_coverage(year)
        chart_dynamics_state = ensure_chart_dynamics(year, context_path)
        narrative_plan_state = ensure_year_narrative_plan(year)
        staff_writer_state, staff_writer_count, articles_generated = ensure_staff_writer_drafts(year)
        art_director_state, issue_map_created, production_targets_created = ensure_art_director_outputs(year)
        final_prose_state, articles_finalized = ensure_final_prose_outputs(year)
        payload = load_context(context_path)
        print_report(
            year,
            inventory_state,
            context_path,
            payload,
            screen_culture_state,
            screen_culture_warnings,
            chart_dynamics_state,
            narrative_plan_state,
            staff_writer_state,
            staff_writer_count,
            articles_generated,
            art_director_state,
            issue_map_created,
            production_targets_created,
            final_prose_state,
            articles_finalized,
        )
        return 0
    except (FileNotFoundError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
