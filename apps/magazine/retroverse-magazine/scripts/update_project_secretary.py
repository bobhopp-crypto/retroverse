#!/usr/bin/env python3
"""Maintain lightweight project continuity docs from known project artifacts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
ISSUES_DIR = PROJECT_ROOT / "issues"
ARTIFACTS_ROOT = PROJECT_ROOT / "artifacts" / "output"
MANAGED_START = "<!-- secretary:managed:start -->"
MANAGED_END = "<!-- secretary:managed:end -->"
MANUAL_NOTES_HEADING = "## Manual Notes"
OVERALL_RE = re.compile(r"Overall:\s+\*\*(PASS|FAIL)\*\*")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update project continuity docs from current artifacts.")
    parser.add_argument("--year", type=int, required=True, help="Issue year to inspect")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def first_heading(path: Path) -> str | None:
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def replace_managed_block(path: Path, title: str, managed_body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    managed = f"{MANAGED_START}\n{managed_body.rstrip()}\n{MANAGED_END}"

    if not path.exists():
        content = f"# {title}\n\n{managed}\n\n{MANUAL_NOTES_HEADING}\n\n"
        path.write_text(content, encoding="utf-8")
        return

    existing = path.read_text(encoding="utf-8")
    if MANAGED_START in existing and MANAGED_END in existing:
        before, remainder = existing.split(MANAGED_START, 1)
        _, after = remainder.split(MANAGED_END, 1)
        updated = before.rstrip() + "\n\n" + managed + after
        path.write_text(updated.rstrip() + "\n", encoding="utf-8")
        return

    existing = existing.rstrip()
    if MANUAL_NOTES_HEADING not in existing:
        existing = existing + f"\n\n{MANUAL_NOTES_HEADING}\n"
    updated = existing + "\n\n" + managed + "\n"
    path.write_text(updated, encoding="utf-8")


def update_change_log(path: Path, title: str, entry_markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        content = f"# {title}\n\n{MANAGED_START}\n{entry_markdown.rstrip()}\n{MANAGED_END}\n\n{MANUAL_NOTES_HEADING}\n\n"
        path.write_text(content, encoding="utf-8")
        return

    existing = path.read_text(encoding="utf-8")
    if MANAGED_START in existing and MANAGED_END in existing:
        before, remainder = existing.split(MANAGED_START, 1)
        managed_old, after = remainder.split(MANAGED_END, 1)
        managed_old = managed_old.strip()
        merged = entry_markdown.rstrip()
        if managed_old:
            merged = merged + "\n\n" + managed_old
        updated = before.rstrip() + "\n\n" + MANAGED_START + "\n" + merged + "\n" + MANAGED_END + after
        path.write_text(updated.rstrip() + "\n", encoding="utf-8")
        return

    existing = existing.rstrip()
    if MANUAL_NOTES_HEADING not in existing:
        existing = existing + f"\n\n{MANUAL_NOTES_HEADING}\n"
    updated = existing + "\n\n" + MANAGED_START + "\n" + entry_markdown.rstrip() + "\n" + MANAGED_END + "\n"
    path.write_text(updated, encoding="utf-8")


def summarize_doc(path: Path) -> str:
    name = path.name
    summaries = {
        "pipeline_architecture_audit.md": "Documents the real issue pipeline flow, issue tree, shared-asset reuse paths, and architecture conflicts.",
        "build_issue_pages_analysis.md": "Shows that build_issue_pages(year) still owns page order, slugs, source routing, and ignores page briefs.",
        "page_first_refactor_plan.md": "Defines the target page-first split: editorial planning moves to generate_issue_page_briefs.py while rendering stays in magazine_pipeline.py.",
    }
    return summaries.get(name, f"Documentation artifact present: {name}.")


def qa_summary(year: int) -> tuple[list[dict[str, str]], list[str]]:
    qa_dir = ARTIFACTS_ROOT / str(year) / "qa"
    reports: list[dict[str, str]] = []
    lines: list[str] = []
    if not qa_dir.exists():
        return reports, lines

    for path in sorted(qa_dir.glob("*.md")):
        text = read_text(path)
        match = OVERALL_RE.search(text)
        overall = match.group(1) if match else "UNKNOWN"
        reports.append({"report": path.name, "overall": overall})
        lines.append(f"- `{path.name}`: {overall}")
    return reports, lines


def trace_summary(year: int) -> dict[str, Any]:
    trace_path = ISSUES_DIR / str(year) / "trace" / "trace_manifest.json"
    payload = read_json(trace_path)
    summary = {
        "page_count": 0,
        "duplicate_pages": 0,
        "missing_image_pages": 0,
        "placeholder_pages": 0,
        "prompt_mismatch_pages": 0,
    }
    if not isinstance(payload, dict) or not isinstance(payload.get("pages"), list):
        return summary

    pages = payload["pages"]
    summary["page_count"] = len(pages)
    for page in pages:
        if not isinstance(page, dict):
            continue
        warnings = page.get("warnings", {}) if isinstance(page.get("warnings"), dict) else {}
        if warnings.get("duplicate_images"):
            summary["duplicate_pages"] += 1
        if warnings.get("missing_image") is True:
            summary["missing_image_pages"] += 1
        if warnings.get("placeholder_or_fallback"):
            summary["placeholder_pages"] += 1
        if warnings.get("layout_prompt_mismatch"):
            summary["prompt_mismatch_pages"] += 1
    return summary


def secretary_state(year: int) -> dict[str, Any]:
    docs_to_summarize = [
        DOCS_DIR / "pipeline_architecture_audit.md",
        DOCS_DIR / "build_issue_pages_analysis.md",
        DOCS_DIR / "page_first_refactor_plan.md",
    ]
    present_docs = [path for path in docs_to_summarize if path.exists()]
    qa_reports, qa_lines = qa_summary(year)
    trace = trace_summary(year)

    visual_html = ISSUES_DIR / str(year) / "qa" / "page_visual_index.html"
    visual_json = ISSUES_DIR / str(year) / "qa" / "page_visual_index.json"

    return {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "year": year,
        "docs": present_docs,
        "qa_reports": qa_reports,
        "qa_lines": qa_lines,
        "trace": trace,
        "visual_html_exists": visual_html.exists(),
        "visual_json_exists": visual_json.exists(),
    }


def build_project_state(state: dict[str, Any]) -> str:
    doc_lines = "\n".join(f"- `{path.name}`: {summarize_doc(path)}" for path in state["docs"])
    qa_lines = "\n".join(state["qa_lines"]) or "- No QA reports found."
    trace = state["trace"]
    visual_status = []
    if state["visual_html_exists"]:
        visual_status.append("HTML visual QA index present")
    if state["visual_json_exists"]:
        visual_status.append("JSON visual QA manifest present")
    visual_line = ", ".join(visual_status) if visual_status else "No visual QA index generated yet."

    return f"""Updated: {state['timestamp']}

## Current Architecture

- Canonical issue entrypoint remains `pipeline/run_issue_pipeline.py`.
- The current layout engine still mixes editorial planning and rendering inside `scripts/magazine_pipeline.py`.
- Page briefs exist, but the renderer does not yet treat them as the source of truth.
- The target architecture is page-brief-first: planning moves to `generate_issue_page_briefs.py`; rendering remains in `magazine_pipeline.py`.

## Documentation Artifacts Reviewed

{doc_lines or '- No architecture docs reviewed.'}

## Issue {state['year']} Snapshot

- Trace manifest pages: {trace['page_count']}
- Pages with duplicate-image warnings: {trace['duplicate_pages']}
- Pages with missing-image warnings: {trace['missing_image_pages']}
- Pages with placeholder-or-fallback warnings: {trace['placeholder_pages']}
- Pages with layout/prompt mismatch warnings: {trace['prompt_mismatch_pages']}
- Visual QA status: {visual_line}

## QA Status

{qa_lines}
"""


def build_decision_log(state: dict[str, Any]) -> str:
    return f"""Updated: {state['timestamp']}

## Confirmed Decisions

- The canonical issue pipeline entrypoint is `pipeline/run_issue_pipeline.py`.
- The current renderer still reconstructs pages in `scripts/magazine_pipeline.py`; page-first migration has not started.
- The approved target split is: editorial planning moves to `pipeline/generate_issue_page_briefs.py`, rendering stays in `scripts/magazine_pipeline.py`.
- Visual QA support artifacts live under `issues/<year>/qa/`.
- Project continuity records live under `docs/project_state.md`, `docs/decision_log.md`, `docs/open_issues.md`, `docs/change_log.md`, and `docs/next_steps.md`.
"""


def build_open_issues(state: dict[str, Any]) -> str:
    trace = state["trace"]
    items = [
        "- `build_issue_pages(year)` still owns page order, slugs, source routing, and layout-type assignment.",
        "- `pipeline/common.page_records()` still derives records from `build_issue_pages(year)` instead of loading the page brief manifest directly.",
        "- Template mapping in `magazine_pipeline.py` is validation-only and not an active rendering dependency.",
        f"- Trace warnings remain on {trace['prompt_mismatch_pages']} pages for layout/prompt asset mismatch entries.",
        "- Legacy artifact families remain beside canonical outputs; no cleanup has happened yet by design.",
    ]
    if trace["placeholder_pages"] > 0:
        items.append(f"- Trace warnings flag placeholder-or-fallback usage on {trace['placeholder_pages']} pages.")
    return "Updated: {timestamp}\n\n## Unresolved Technical Issues\n\n{items}\n".format(
        timestamp=state["timestamp"],
        items="\n".join(items),
    )


def build_next_steps(state: dict[str, Any]) -> str:
    return f"""Updated: {state['timestamp']}

## Recommended Next Steps

- Make `issues/{{year}}/layout/page_briefs/{{year}}_page_briefs_manifest.json` the authoritative issue manifest.
- Change `pipeline/common.page_records()` to load the page brief manifest instead of calling `build_issue_pages(year)`.
- Convert `build_issue_pages(year)` into a renderer-side loader for page briefs rather than a planner/dispatcher.
- Resolve the trace manifest layout/prompt asset-path mismatch so visual QA warnings reflect only real rendering problems.
- Keep rerunning the visual QA index and secretary updater after each architecture step to maintain continuity.
"""


def update_docs(state: dict[str, Any]) -> list[Path]:
    updated: list[Path] = []

    project_state_path = DOCS_DIR / "project_state.md"
    replace_managed_block(project_state_path, "Project State", build_project_state(state))
    updated.append(project_state_path)

    decision_log_path = DOCS_DIR / "decision_log.md"
    replace_managed_block(decision_log_path, "Decision Log", build_decision_log(state))
    updated.append(decision_log_path)

    open_issues_path = DOCS_DIR / "open_issues.md"
    replace_managed_block(open_issues_path, "Open Issues", build_open_issues(state))
    updated.append(open_issues_path)

    next_steps_path = DOCS_DIR / "next_steps.md"
    replace_managed_block(next_steps_path, "Next Steps", build_next_steps(state))
    updated.append(next_steps_path)

    change_log_path = DOCS_DIR / "change_log.md"
    entry = f"""## {state['timestamp']}

- Reviewed architecture artifacts in `docs/`.
- Refreshed project continuity docs from issue {state['year']} trace, QA, and visual QA artifacts.
- Recorded current confirmed state, open issues, and recommended next actions.
"""
    update_change_log(change_log_path, "Change Log", entry)
    updated.append(change_log_path)

    return updated


def main() -> int:
    args = parse_args()
    state = secretary_state(args.year)
    updated = update_docs(state)
    print("Updated secretary docs:")
    for path in updated:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
