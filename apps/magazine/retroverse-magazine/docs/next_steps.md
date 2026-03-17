# Next Steps

<!-- secretary:managed:start -->
Updated: 2026-03-14T20:39:40-05:00

## Recommended Next Steps

- Make `issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json` the authoritative issue manifest.
- Change `pipeline/common.page_records()` to load the page brief manifest instead of calling `build_issue_pages(year)`.
- Convert `build_issue_pages(year)` into a renderer-side loader for page briefs rather than a planner/dispatcher.
- Resolve the trace manifest layout/prompt asset-path mismatch so visual QA warnings reflect only real rendering problems.
- Keep rerunning the visual QA index and secretary updater after each architecture step to maintain continuity.
<!-- secretary:managed:end -->

## Manual Notes

