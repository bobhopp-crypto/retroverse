# Open Issues

<!-- secretary:managed:start -->
Updated: 2026-03-14T20:39:40-05:00

## Unresolved Technical Issues

- `build_issue_pages(year)` still owns page order, slugs, source routing, and layout-type assignment.
- `pipeline/common.page_records()` still derives records from `build_issue_pages(year)` instead of loading the page brief manifest directly.
- Template mapping in `magazine_pipeline.py` is validation-only and not an active rendering dependency.
- Trace warnings remain on 30 pages for layout/prompt asset mismatch entries.
- Legacy artifact families remain beside canonical outputs; no cleanup has happened yet by design.
- Trace warnings flag placeholder-or-fallback usage on 5 pages.
<!-- secretary:managed:end -->

## Manual Notes

