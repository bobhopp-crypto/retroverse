# Decision Log

<!-- secretary:managed:start -->
Updated: 2026-03-14T20:39:40-05:00

## Confirmed Decisions

- The canonical issue pipeline entrypoint is `pipeline/run_issue_pipeline.py`.
- The current renderer still reconstructs pages in `scripts/magazine_pipeline.py`; page-first migration has not started.
- The approved target split is: editorial planning moves to `pipeline/generate_issue_page_briefs.py`, rendering stays in `scripts/magazine_pipeline.py`.
- Visual QA support artifacts live under `issues/<year>/qa/`.
- Project continuity records live under `docs/project_state.md`, `docs/decision_log.md`, `docs/open_issues.md`, `docs/change_log.md`, and `docs/next_steps.md`.
<!-- secretary:managed:end -->

## Manual Notes

