# RetroVerse Pipeline Repair Report

Date: March 12, 2026

## Issues Found

- `python3 scripts/magazine_pipeline.py --year 1978` was not a real pipeline entrypoint; it exited without rebuilding HTML or PDF.
- The canonical build only assembled the 14 production-target story pages and ignored issue section files such as `masthead.md`, `editor_letter.md`, `charts_overview.md`, `letters.md`, `ads.md`, `comic.md`, `arcade.md`, `puzzle1.md`, `puzzle2.md`, and `chart_top23.md`.
- The generated PDF relied on a WeasyPrint layout path that overflowed heavily and produced far more physical pages than designed pages.
- The masthead font stack rendered the brand in all caps visually and degraded the interior bullet separator.
- `chart_top23` was absent from the generated issue.
- `image_prompts.json` was stale because the canonical command did not regenerate it, and the Easter egg instruction was not guaranteed as a required rule.
- Illustration generation required an OpenAI client up front even when all art assets were already cached.

## Files Modified

- `scripts/magazine_pipeline.py`
- `scripts/generate_art_prompts.py`
- `scripts/generate_illustrations.py`
- `tools/magazine_builder/build_issue.py`
- `tools/magazine_builder/render_browser_pdf.mjs`
- `tools/magazine_builder/style.css`
- `assets/css/magazine.css`
- `layout-library/css/layout-library.css`
- `magazine_template.html`

Generated outputs refreshed:

- `issues/1978/layout/index.html`
- `issues/1978/layout/page_*.html`
- `issues/1978/art/image_prompts.json`
- `output/RetroVerse_1978.pdf`

## Fixes Applied

- Turned `scripts/magazine_pipeline.py` into the actual canonical CLI pipeline entrypoint.
- Kept the existing story-page builder, but expanded the assembled issue to include the missing section markdown sources and a dedicated `chart_top23` page.
- Added intentional story splitting for overlong story layouts so the finished issue lands in magazine range instead of forcing uncontrolled PDF overflow.
- Added a no-sidebar rendering path for pages that should use the full body width.
- Made the Easter egg rule mandatory and appended it consistently to every generated art prompt.
- Made illustration generation lazy-load the OpenAI client so cached builds can run without regenerating images.
- Added a browser-based PDF renderer that captures the designed HTML pages and writes a deterministic one-page-per-layout PDF, with the older WeasyPrint path retained only as fallback.
- Replaced the masthead font stack with a mixed-case serif that preserves `RetroVerse` and `RetroVerse • 1978` correctly.

## Final Page Count

- HTML layout pages: 31
- Final PDF pages: 31

## Verification Results

- Canonical command now works: `python3 scripts/magazine_pipeline.py --year 1978`
- Output confirmed:
  - `issues/1978/layout/index.html`
  - `output/RetroVerse_1978.pdf`
- Cover masthead renders as `RetroVerse`
- Cover tagline renders as `Press ▶ Play for the Past`
- Interior header renders as `RetroVerse • 1978`
- `chart_top23` exists at `issues/1978/layout/page_13_chart_top23.html`
- `chart_top23` includes the required columns: rank, song title, artist, weeks, peak, score
- `chart_top23` contains exactly 23 entries
- `issues/1978/art/image_prompts.json` now includes `Hide the word "RetroVerse" subtly somewhere in the illustration as an Easter egg.` on every prompt
- Final PDF page count is within the requested magazine range

## Notes

- The browser PDF renderer captures the final designed HTML pages into the PDF. This makes the PDF page count stable and keeps the visual output aligned with the reviewed layout pages.
