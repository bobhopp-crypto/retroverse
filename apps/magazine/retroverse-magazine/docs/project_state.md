# Project State

<!-- secretary:managed:start -->
Updated: 2026-03-14T20:39:40-05:00

## Current Architecture

- Canonical issue entrypoint remains `pipeline/run_issue_pipeline.py`.
- The current layout engine still mixes editorial planning and rendering inside `scripts/magazine_pipeline.py`.
- Page briefs exist, but the renderer does not yet treat them as the source of truth.
- The target architecture is page-brief-first: planning moves to `generate_issue_page_briefs.py`; rendering remains in `magazine_pipeline.py`.

## Documentation Artifacts Reviewed

- `pipeline_architecture_audit.md`: Documents the real issue pipeline flow, issue tree, shared-asset reuse paths, and architecture conflicts.
- `build_issue_pages_analysis.md`: Shows that build_issue_pages(year) still owns page order, slugs, source routing, and ignores page briefs.
- `page_first_refactor_plan.md`: Defines the target page-first split: editorial planning moves to generate_issue_page_briefs.py while rendering stays in magazine_pipeline.py.

## Issue 1978 Snapshot

- Trace manifest pages: 30
- Pages with duplicate-image warnings: 0
- Pages with missing-image warnings: 0
- Pages with placeholder-or-fallback warnings: 5
- Pages with layout/prompt mismatch warnings: 30
- Visual QA status: HTML visual QA index present, JSON visual QA manifest present

## QA Status

- `1978_art_direction_QA.md`: PASS
- `1978_art_prompt_QA.md`: PASS
- `1978_layout_QA.md`: PASS
- `1978_page_briefs_QA.md`: PASS
- `1978_press_check_QA.md`: PASS
<!-- secretary:managed:end -->

## Manual Notes

