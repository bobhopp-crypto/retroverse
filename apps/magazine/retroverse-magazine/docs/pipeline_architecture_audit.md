# RetroVerse Magazine Pipeline Architecture Audit

Project root: `retroverse/apps/magazine/retroverse-magazine`

Scope: inspect the current pipeline architecture and report the real execution flow. No files were modified outside creation of this audit.

## 1. Pipeline Entrypoint

Canonical entrypoint: `pipeline/run_issue_pipeline.py`

Why this is the entrypoint:

- It is the only script that orchestrates the full issue run in one place.
- It handles the top-level CLI flags: `--year`, `--skip-context`, `--overwrite-art`, `--skip-illustration`, and `--skip-pdf`.
- It launches each downstream stage in order with blocking subprocess calls.

Related but not entrypoint scripts:

- `scripts/build_issue.py`: layout-only build stage.
- `scripts/magazine_pipeline.py`: page assembly and HTML rendering engine used by `scripts/build_issue.py`.

## 2. Actual Execution Order

The orchestrator runs these stages in this order:

| Stage | Script | Purpose | Output artifacts | Output location |
|---|---|---|---|---|
| 0 | `scripts/generate_year_context.py` | Build canonical year context from chart DB plus support data. Skipped when `--skip-context` is provided and `issues/context/{year}_context.json` already exists. | Year context JSON | `issues/context/{year}_context.json` |
| 1 | `scripts/generate_year_narrative.py` | Convert year context into the editorial narrative plan. | Narrative plan JSON and Markdown | `issues/plans/{year}_narrative_plan.json`, `issues/plans/{year}_narrative_plan.md` |
| 2 | `scripts/run_staff_writers.py` | Assign staff voices and generate structured article drafts. | Draft article JSON and Markdown | `issues/{year}/articles/story_*.json`, `issues/{year}/articles/story_*.md` |
| 3 | `scripts/generate_final_articles.py` | Turn draft articles into final production prose. | Final article JSON and Markdown | `issues/{year}/articles/final/story_*.json`, `issues/{year}/articles/final/story_*.md` |
| 4 | `pipeline/generate_issue_page_briefs.py` | Build one page brief per canonical issue page. | Page brief JSON files and manifest | `issues/{year}/layout/page_briefs/page_*.json`, `issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json` |
| 5 | `pipeline/qa_page_briefs.py` | Validate page brief completeness before art-direction handoff. | QA Markdown report | `artifacts/output/{year}/qa/{year}_page_briefs_QA.md` |
| 6 | `pipeline/art_direction_stage.py` | Create page-level art-direction files and illustrator role assignments. | Page art-direction JSON files and assignments manifest | `issues/{year}/art_direction/page_*.json`, `issues/{year}/art_direction/page_assignments.json` |
| 7 | `pipeline/qa_art_direction.py` | Validate page-aware art-direction files. | QA Markdown report | `artifacts/output/{year}/qa/{year}_art_direction_QA.md` |
| 8 | `pipeline/illustration_prompt_stage.py` | Generate one illustration prompt per page. | Prompt text files and prompt manifest | `issues/{year}/art/prompts/page_*.txt`, `issues/{year}/art/image_prompts.json` |
| 9 | `pipeline/qa_art_prompts.py` | Validate prompt structure and required wording. | QA Markdown report | `artifacts/output/{year}/qa/{year}_art_prompt_QA.md` |
| 10 | `scripts/generate_illustrations.py` | Build page images from prompt manifest, using cache/seed logic when available. | Page image PNGs | `issues/{year}/art/pages/page_*.png` |
| 11 | `scripts/build_issue.py` | Rebuild canonical layout HTML pages. | Layout HTML pages and index | `issues/{year}/layout/page_*.html`, `issues/{year}/layout/index.html` |
| 12 | `pipeline/qa_layout.py` | Validate HTML layout against expected structure and page brief content. | QA Markdown report | `artifacts/output/{year}/qa/{year}_layout_QA.md` |
| 13 | `pipeline/qa_press_check.py` | Pre-PDF press check over final HTML pages. | QA Markdown report | `artifacts/output/{year}/qa/{year}_press_check_QA.md` |
| 14 | `tools/magazine_builder/render_browser_pdf.mjs` | Render the HTML layout into a browser PDF. | Final PDF | `issues/{year}/pdf/RetroVerse_{year}.pdf` |

## 3. Real Data Dependency Notes

The orchestrator is linear, but the underlying data flow is not fully linear.

Observed behavior from current code:

- `pipeline/generate_issue_page_briefs.py` does not define page structure from scratch. It calls `pipeline/common.page_records()`, which calls `scripts/magazine_pipeline.build_issue_pages(year)` and turns those already-built page objects into brief JSON.
- `scripts/build_issue.py` later calls `scripts/magazine_pipeline.build_issue_pages(year)` again. It does not read page briefs, art-direction JSON, or prompt files to assemble layout.
- `pipeline/illustration_prompt_stage.py` reads the page brief manifest and page brief JSON files. It does not currently read `issues/{year}/art_direction/page_*.json` or `issues/{year}/art_direction/page_assignments.json`.
- `pipeline/qa_layout.py` is where page briefs re-enter the flow. It compares final HTML pages back to the brief data after layout has already been built.

This means the real architecture is:

- editorial sources and final articles feed `build_issue_pages()`
- page briefs are derived from those page objects
- art direction is derived from page briefs
- prompts are derived from page briefs
- layout is rebuilt from source files plus page image presence, not from the brief/art-direction artifacts

## 4. Shared Asset Reuse Detection

### Current active layout state

Current `issues/1978/layout/page_*.html` files reference page-based art paths such as:

- `../art/pages/page_01.png`
- `../art/pages/page_17.png`
- `../art/pages/page_29.png`

No current `issues/1978/layout/page_*.html` references were found to:

- `department_portrait.png`
- `disco_floor.png`
- `tv_livingroom.png`
- `fake_ad_kit.png`

### Legacy shared-image references still present

The category-based shared asset names still exist in the repository and can still influence runs indirectly.

| Shared asset | Where it is still referenced | Which code touches it | Why multiple pages used it |
|---|---|---|---|
| `department_portrait.png` | `issues/1978/data/issue.json`, `issues/1978/art/departments/department_portrait.png`, `issues/1978/art/feature/department_portrait.png`, `archive/old_runs/issues_1978_preview/page_03_editor.html`, `archive/old_runs/issues_1978_preview/page_10_department_culture.html`, `archive/old_runs/issues_1978_preview/page_21_department_sue.html` | `scripts/index_artwork.py` special-cases it when mapping prompts; `scripts/generate_illustrations.py` can still copy it via `seed_page_job()` if an old layout HTML references it | Older category-based layouts mapped multiple department pages to one shared "department portrait" image instead of one page image per page |
| `disco_floor.png` | `issues/1978/data/issue.json`, `issues/1978/art/feature/disco_floor.png`, `archive/old_runs/issues_1978_preview/page_04_feature_disco.html`, `archive/old_runs/issues_1978_preview/page_13_feature_interview.html` | `scripts/generate_illustrations.py` can seed from old layout HTML image references | Older feature pages reused one shared disco-floor hero image across multiple feature pages |
| `tv_livingroom.png` | `issues/1978/data/issue.json`, `issues/1978/art/feature/tv_livingroom.png`, `archive/old_runs/issues_1978_preview/page_20_feature_tv.html` | `scripts/index_artwork.py` special-cases it; `scripts/generate_illustrations.py` can seed from old layout HTML image references | Older television-oriented pages reused one shared TV living-room hero image |
| `fake_ad_kit.png` | `issues/1978/data/issue.json`, `issues/1978/art/fake_ads/fake_ad_kit.png`, `archive/old_runs/issues_1978_preview/page_14_parody_fake_ad.html` | `scripts/generate_illustrations.py` can seed from old layout HTML image references | Older ad/parody pages reused one shared fake-ad illustration |

### Why reuse can still happen now

The active reuse mechanism is `scripts/generate_illustrations.py`, specifically:

- `should_skip_job()`: if `issues/{year}/art/pages/page_XX.png` already exists, the generator skips that page unless `--overwrite` or `--force` is used.
- `seed_page_job()`: if the page image does not exist, the generator reads the existing layout HTML for that page, finds the first `../art/...` image reference, and copies that file into `issues/{year}/art/pages/page_XX.png`.
- If no prior layout image is found, `seed_page_job()` falls back to `assets/placeholder.png`.

So the current layout is page-based, but the generator still has a backward-looking bridge to category-based assets if old layout HTML is still present.

## 5. Issue Directory Structure for `issues/1978/`

Full tree observed under `issues/1978/`:

```text
issues/1978/
|-- art/
|   |-- collage/
|   |   |-- collage_01.png
|   |   |-- collage_02.png
|   |   |-- collage_03.png
|   |   |-- collage_04.png
|   |   |-- collage_05.png
|   |   |-- collage_06.png
|   |   |-- collage_07.png
|   |   |-- collage_08.png
|   |   `-- collage_09.png
|   |-- comic/
|   |   |-- comic_panel_01.png
|   |   |-- comic_panel_02.png
|   |   |-- comic_panel_03.png
|   |   |-- comic_panel_04.png
|   |   |-- comic_panel_05.png
|   |   `-- comic_panel_06.png
|   |-- cover/
|   |   |-- .DS_Store
|   |   `-- cover_1978.png
|   |-- departments/
|   |   `-- department_portrait.png
|   |-- fake_ads/
|   |   `-- fake_ad_kit.png
|   |-- feature/
|   |   |-- cinema_marquee.png
|   |   |-- department_portrait.png
|   |   |-- disco_floor.png
|   |   |-- feature_placeholder.png
|   |   `-- tv_livingroom.png
|   |-- images/
|   |   |-- .DS_Store
|   |   |-- cinema_marquee.png
|   |   |-- collage_01.png
|   |   |-- collage_02.png
|   |   |-- collage_03.png
|   |   |-- collage_04.png
|   |   |-- collage_05.png
|   |   |-- collage_06.png
|   |   |-- collage_07.png
|   |   |-- collage_08.png
|   |   |-- collage_09.png
|   |   |-- comic_panel_01.png
|   |   |-- comic_panel_02.png
|   |   |-- comic_panel_03.png
|   |   |-- comic_panel_04.png
|   |   |-- comic_panel_05.png
|   |   |-- comic_panel_06.png
|   |   |-- cover_1978.png
|   |   |-- department_portrait.png
|   |   |-- disco_floor.png
|   |   |-- fake_ad_kit.png
|   |   |-- trivia_grid.png
|   |   |-- tv_livingroom.png
|   |   `-- weekend_console.png
|   |-- marginals/
|   |-- pages/
|   |   |-- page_01.png
|   |   |-- page_02.png
|   |   |-- page_03.png
|   |   |-- page_04.png
|   |   |-- page_05.png
|   |   |-- page_06.png
|   |   |-- page_07.png
|   |   |-- page_08.png
|   |   |-- page_09.png
|   |   |-- page_10.png
|   |   |-- page_11.png
|   |   |-- page_12.png
|   |   |-- page_13.png
|   |   |-- page_14.png
|   |   |-- page_15.png
|   |   |-- page_16.png
|   |   |-- page_17.png
|   |   |-- page_18.png
|   |   |-- page_19.png
|   |   |-- page_20.png
|   |   |-- page_21.png
|   |   |-- page_22.png
|   |   |-- page_23.png
|   |   |-- page_24.png
|   |   |-- page_25.png
|   |   |-- page_26.png
|   |   |-- page_27.png
|   |   |-- page_28.png
|   |   |-- page_29.png
|   |   `-- page_30.png
|   |-- parody/
|   |   |-- trivia_grid.png
|   |   `-- weekend_console.png
|   |-- prompts/
|   |   |-- page_01.txt
|   |   |-- page_01_cover.txt
|   |   |-- page_02.txt
|   |   |-- page_02_masthead.txt
|   |   |-- page_03.txt
|   |   |-- page_03_editor_letter.txt
|   |   |-- page_04.txt
|   |   |-- page_04_year_snapshot.txt
|   |   |-- page_05.txt
|   |   |-- page_05_charts_overview.txt
|   |   |-- page_06.txt
|   |   |-- page_06_top_song_1.txt
|   |   |-- page_07.txt
|   |   |-- page_07_top_song_2.txt
|   |   |-- page_08.txt
|   |   |-- page_08_top_song_3.txt
|   |   |-- page_09.txt
|   |   |-- page_09_top_song_4.txt
|   |   |-- page_10.txt
|   |   |-- page_10_top_song_5.txt
|   |   |-- page_11.txt
|   |   |-- page_11_top_song_6.txt
|   |   |-- page_12.txt
|   |   |-- page_12_top_song_7.txt
|   |   |-- page_13.txt
|   |   |-- page_13_top_song_8.txt
|   |   |-- page_14.txt
|   |   |-- page_14_top_song_9.txt
|   |   |-- page_15.txt
|   |   |-- page_15_top_song_10.txt
|   |   |-- page_16.txt
|   |   |-- page_16_movies.txt
|   |   |-- page_17.txt
|   |   |-- page_17_television.txt
|   |   |-- page_18.txt
|   |   |-- page_18_culture.txt
|   |   |-- page_19.txt
|   |   |-- page_19_arcade.txt
|   |   |-- page_20.txt
|   |   |-- page_20_retro_ad.txt
|   |   |-- page_21.txt
|   |   |-- page_21_comic.txt
|   |   |-- page_22.txt
|   |   |-- page_22_puzzle.txt
|   |   |-- page_23.txt
|   |   |-- page_23_letters.txt
|   |   |-- page_24.txt
|   |   |-- page_24_forgotten_hit.txt
|   |   |-- page_25.txt
|   |   |-- page_25_one_hit_wonder.txt
|   |   |-- page_26.txt
|   |   |-- page_26_album_spotlight.txt
|   |   |-- page_27.txt
|   |   |-- page_27_year_timeline.txt
|   |   |-- page_28.txt
|   |   |-- page_28_culture_collage.txt
|   |   |-- page_29.txt
|   |   |-- page_29_retro_ads_page.txt
|   |   |-- page_30.txt
|   |   `-- page_30_chart_top23.txt
|   |-- .DS_Store
|   `-- image_prompts.json
|-- art_direction/
|   |-- page_01_cover.json
|   |-- page_02_masthead.json
|   |-- page_03_editor_letter.json
|   |-- page_04_year_snapshot.json
|   |-- page_05_charts_overview.json
|   |-- page_06_top_song_1.json
|   |-- page_07_top_song_2.json
|   |-- page_08_top_song_3.json
|   |-- page_09_top_song_4.json
|   |-- page_10_top_song_5.json
|   |-- page_11_top_song_6.json
|   |-- page_12_top_song_7.json
|   |-- page_13_top_song_8.json
|   |-- page_14_top_song_9.json
|   |-- page_15_top_song_10.json
|   |-- page_16_movies.json
|   |-- page_17_television.json
|   |-- page_18_culture.json
|   |-- page_19_arcade.json
|   |-- page_20_retro_ad.json
|   |-- page_21_comic.json
|   |-- page_22_puzzle.json
|   |-- page_23_letters.json
|   |-- page_24_forgotten_hit.json
|   |-- page_25_one_hit_wonder.json
|   |-- page_26_album_spotlight.json
|   |-- page_27_year_timeline.json
|   |-- page_28_culture_collage.json
|   |-- page_29_retro_ads_page.json
|   |-- page_30_chart_top23.json
|   `-- page_assignments.json
|-- articles/
|   |-- final/
|   |   |-- story_001.json
|   |   |-- story_001.md
|   |   |-- story_002.json
|   |   |-- story_002.md
|   |   |-- story_003.json
|   |   |-- story_003.md
|   |   |-- story_004.json
|   |   |-- story_004.md
|   |   |-- story_005.json
|   |   |-- story_005.md
|   |   |-- story_006.json
|   |   |-- story_006.md
|   |   |-- story_007.json
|   |   |-- story_007.md
|   |   |-- story_008.json
|   |   |-- story_008.md
|   |   |-- story_009.json
|   |   |-- story_009.md
|   |   |-- story_010.json
|   |   |-- story_010.md
|   |   |-- story_011.json
|   |   |-- story_011.md
|   |   |-- story_012.json
|   |   `-- story_012.md
|   |-- story_001.json
|   |-- story_001.md
|   |-- story_002.json
|   |-- story_002.md
|   |-- story_003.json
|   |-- story_003.md
|   |-- story_004.json
|   |-- story_004.md
|   |-- story_005.json
|   |-- story_005.md
|   |-- story_006.json
|   |-- story_006.md
|   |-- story_007.json
|   |-- story_007.md
|   |-- story_008.json
|   |-- story_008.md
|   |-- story_009.json
|   |-- story_009.md
|   |-- story_010.json
|   |-- story_010.md
|   |-- story_011.json
|   |-- story_011.md
|   |-- story_012.json
|   `-- story_012.md
|-- charts/
|-- data/
|   |-- charts.json
|   |-- editorial.json
|   |-- issue.json
|   |-- movies.json
|   `-- tv.json
|-- layout/
|   |-- art_direction/
|   |   |-- page_01_cover.json
|   |   |-- page_02_masthead.json
|   |   |-- page_03_editor_letter.json
|   |   |-- page_04_year_snapshot.json
|   |   |-- page_05_charts_overview.json
|   |   |-- page_06_top_song_1.json
|   |   |-- page_07_top_song_2.json
|   |   |-- page_08_top_song_3.json
|   |   |-- page_09_top_song_4.json
|   |   |-- page_10_top_song_5.json
|   |   |-- page_11_top_song_6.json
|   |   |-- page_12_top_song_7.json
|   |   |-- page_13_top_song_8.json
|   |   |-- page_14_top_song_9.json
|   |   |-- page_15_top_song_10.json
|   |   |-- page_16_movies.json
|   |   |-- page_17_television.json
|   |   |-- page_18_culture.json
|   |   |-- page_19_arcade.json
|   |   |-- page_20_retro_ad.json
|   |   |-- page_21_comic.json
|   |   |-- page_22_puzzle.json
|   |   |-- page_23_letters.json
|   |   |-- page_24_forgotten_hit.json
|   |   |-- page_25_one_hit_wonder.json
|   |   |-- page_26_album_spotlight.json
|   |   |-- page_27_year_timeline.json
|   |   |-- page_28_culture_collage.json
|   |   |-- page_29_retro_ads_page.json
|   |   `-- page_30_chart_top23.json
|   |-- page_briefs/
|   |   |-- 1978_page_briefs_manifest.json
|   |   |-- page_01_cover.json
|   |   |-- page_02_masthead.json
|   |   |-- page_03_editor_letter.json
|   |   |-- page_04_year_snapshot.json
|   |   |-- page_05_charts_overview.json
|   |   |-- page_06_top_song_1.json
|   |   |-- page_07_top_song_2.json
|   |   |-- page_08_top_song_3.json
|   |   |-- page_09_top_song_4.json
|   |   |-- page_10_top_song_5.json
|   |   |-- page_11_top_song_6.json
|   |   |-- page_12_top_song_7.json
|   |   |-- page_13_top_song_8.json
|   |   |-- page_14_top_song_9.json
|   |   |-- page_15_top_song_10.json
|   |   |-- page_16_movies.json
|   |   |-- page_17_television.json
|   |   |-- page_18_culture.json
|   |   |-- page_19_arcade.json
|   |   |-- page_20_retro_ad.json
|   |   |-- page_21_comic.json
|   |   |-- page_22_puzzle.json
|   |   |-- page_23_letters.json
|   |   |-- page_24_forgotten_hit.json
|   |   |-- page_25_one_hit_wonder.json
|   |   |-- page_26_album_spotlight.json
|   |   |-- page_27_year_timeline.json
|   |   |-- page_28_culture_collage.json
|   |   |-- page_29_retro_ads_page.json
|   |   `-- page_30_chart_top23.json
|   |-- 1978_issue_map.json
|   |-- 1978_issue_map.md
|   |-- 1978_production_targets.json
|   |-- index.html
|   |-- page_01_cover.html
|   |-- page_02_masthead.html
|   |-- page_03_editor_letter.html
|   |-- page_04_year_snapshot.html
|   |-- page_05_charts_overview.html
|   |-- page_06_top_song_1.html
|   |-- page_07_top_song_2.html
|   |-- page_08_top_song_3.html
|   |-- page_09_top_song_4.html
|   |-- page_10_top_song_5.html
|   |-- page_11_top_song_6.html
|   |-- page_12_top_song_7.html
|   |-- page_13_top_song_8.html
|   |-- page_14_top_song_9.html
|   |-- page_15_top_song_10.html
|   |-- page_16_movies.html
|   |-- page_17_television.html
|   |-- page_18_culture.html
|   |-- page_19_arcade.html
|   |-- page_20_retro_ad.html
|   |-- page_21_comic.html
|   |-- page_22_puzzle.html
|   |-- page_23_letters.html
|   |-- page_24_forgotten_hit.html
|   |-- page_25_one_hit_wonder.html
|   |-- page_26_album_spotlight.html
|   |-- page_27_year_timeline.html
|   |-- page_28_culture_collage.html
|   |-- page_29_retro_ads_page.html
|   `-- page_30_chart_top23.html
|-- pdf/
|   |--  .pdf
|   `-- RetroVerse_1978.pdf
|-- songs/
|   |-- 01.md
|   |-- 02.md
|   |-- 03.md
|   |-- 04.md
|   |-- 05.md
|   |-- 06.md
|   |-- 07.md
|   |-- 08.md
|   |-- 09.md
|   `-- 10.md
|-- trace/
|   |-- index.html
|   `-- trace_manifest.json
|-- .DS_Store
|-- ads.md
|-- arcade.md
|-- chart_top23.md
|-- charts_overview.md
|-- comic.md
|-- cover.md
|-- culture.md
|-- editor_letter.md
|-- letters.md
|-- masthead.md
|-- movies.md
|-- puzzle1.md
|-- puzzle2.md
|-- retroverse_1978_pilot.md
`-- television.md
```

## 6. Page Ownership

Current ownership by stage:

- Page briefs: `pipeline/generate_issue_page_briefs.py`
  - real source of page objects: `pipeline/common.page_records()`
  - underlying page builder: `scripts/magazine_pipeline.build_issue_pages(year)`
- Art direction: `pipeline/art_direction_stage.py`
- Illustration prompts: `pipeline/illustration_prompt_stage.py`
- Images: `scripts/generate_illustrations.py`
- Layout HTML files: `scripts/build_issue.py`
  - HTML rendering functions: `scripts/magazine_pipeline.render_layout_page()` and `scripts/magazine_pipeline.render_layout_index()`
- PDF: `tools/magazine_builder/render_browser_pdf.mjs`

## 7. Architecture Conflicts

### Conflict 1: linear orchestration vs non-linear data flow

The orchestrator suggests a strict pipeline:

- briefs
- art direction
- prompts
- images
- layout

The actual code does not work that way.

- Page briefs are generated from already-built page objects.
- Layout is rebuilt later from source files and page image paths, not from page briefs or art-direction files.
- This means the brief/art-direction path is largely descriptive and QA-oriented, not the controlling source for layout.

### Conflict 2: art direction is not an active input to prompt generation

`pipeline/art_direction_stage.py` writes page-specific art-direction JSON files and role assignments, but `pipeline/illustration_prompt_stage.py` does not read them.

Current prompt generation is based on:

- page number
- page slug
- page brief JSON
- article excerpt derived from page brief text blocks

So the art-direction stage is present in orchestration and QA, but its outputs are not currently consumed by the prompt stage.

### Conflict 3: current page-image generation still has a legacy seeding path

`scripts/generate_illustrations.py` has page-based output targets now, but it still contains this backward-looking behavior:

- if `issues/{year}/art/pages/page_XX.png` exists, skip generation
- if it does not exist, inspect the existing layout HTML
- copy the first `../art/...` image used by that layout into `issues/{year}/art/pages/page_XX.png`
- if no layout image exists, copy `assets/placeholder.png`

This is the direct mechanism that can preserve legacy category-based art or placeholder art even in the current page-based pipeline.

### Conflict 4: persistent cache reuse can hide drift

The active image cache is the page-art file itself:

- `issues/{year}/art/pages/page_XX.png`

If that file exists, the generator skips the page unless explicitly forced. This means:

- changed prompts do not necessarily produce changed images
- old page art can survive across runs
- a run can appear successful while preserving stale or seeded artwork

### Conflict 5: legacy artifact families remain beside canonical outputs

Observed side-by-side legacy and current structures:

- current page images: `issues/1978/art/pages/page_*.png`
- legacy category folders still present: `issues/1978/art/feature/`, `issues/1978/art/departments/`, `issues/1978/art/fake_ads/`
- legacy image mirror cache still present: `issues/1978/art/images/`
- current prompt files: `issues/1978/art/prompts/page_01.txt` through `page_30.txt`
- legacy slugged prompt files still present in the same folder: `page_01_cover.txt`, `page_17_television.txt`, and similar
- canonical art-direction folder: `issues/1978/art_direction/`
- duplicate legacy art-direction folder also present inside layout: `issues/1978/layout/art_direction/`
- malformed stray PDF artifact: `issues/1978/pdf/ .pdf`

These are signs of architectural drift rather than a clean single-path artifact model.

### Conflict 6: some repeated imagery still happens within the page model

The current builder uses page-based art paths, but some page templates intentionally repeat the same page image multiple times inside a single page:

- `scripts/magazine_pipeline.py` uses `repeated_page_art_subpaths(year, page_number, tile_count)`
- the collage page therefore repeats the same `art/pages/page_28.png` image across multiple collage tiles

This is not cross-page reuse, but it is repeated-image behavior in the live layout model.

## 8. Actual Pipeline Diagram

### Orchestrator order

```text
pipeline/run_issue_pipeline.py
  -> scripts/generate_year_context.py            [unless --skip-context]
  -> scripts/generate_year_narrative.py
  -> scripts/run_staff_writers.py
  -> scripts/generate_final_articles.py
  -> pipeline/generate_issue_page_briefs.py
  -> pipeline/qa_page_briefs.py
  -> pipeline/art_direction_stage.py
  -> pipeline/qa_art_direction.py
  -> pipeline/illustration_prompt_stage.py
  -> pipeline/qa_art_prompts.py
  -> scripts/generate_illustrations.py
  -> scripts/build_issue.py
  -> pipeline/qa_layout.py
  -> pipeline/qa_press_check.py
  -> tools/magazine_builder/render_browser_pdf.mjs
```

### Real dependency flow

```text
scripts/generate_year_context.py
  -> issues/context/{year}_context.json

scripts/generate_year_narrative.py
  -> issues/plans/{year}_narrative_plan.json

scripts/run_staff_writers.py
  -> issues/{year}/articles/story_*.json|md

scripts/generate_final_articles.py
  -> issues/{year}/articles/final/story_*.json|md

scripts/magazine_pipeline.build_issue_pages(year)
  -> page objects built from issue markdown/data/final articles/page-art paths
  -> used by pipeline/common.page_records()
  -> used by scripts/build_issue.py

pipeline/generate_issue_page_briefs.py
  -> issues/{year}/layout/page_briefs/page_*.json

pipeline/art_direction_stage.py
  -> issues/{year}/art_direction/page_*.json
  -> issues/{year}/art_direction/page_assignments.json
  -> not consumed by scripts/build_issue.py
  -> not currently consumed by pipeline/illustration_prompt_stage.py

pipeline/illustration_prompt_stage.py
  -> issues/{year}/art/prompts/page_*.txt
  -> issues/{year}/art/image_prompts.json

scripts/generate_illustrations.py
  -> issues/{year}/art/pages/page_*.png
  -> if page image is missing, may seed from existing layout HTML image refs

scripts/build_issue.py
  -> scripts/magazine_pipeline.render_layout_page()
  -> scripts/magazine_pipeline.render_layout_index()
  -> issues/{year}/layout/page_*.html
  -> issues/{year}/layout/index.html

pipeline/qa_layout.py
  -> compares final HTML against page brief expectations

pipeline/qa_press_check.py
  -> checks final HTML page count/order/assets

tools/magazine_builder/render_browser_pdf.mjs
  -> issues/{year}/pdf/RetroVerse_{year}.pdf
```

## 9. Summary

The current canonical entrypoint is `pipeline/run_issue_pipeline.py`, and it does execute the issue run in one top-level sequence. The real architecture underneath it is more complicated than the command order suggests.

Most important findings:

- The live layout builder is `scripts/magazine_pipeline.py`, reached through `scripts/build_issue.py`.
- Page briefs are derived from already-built page objects rather than serving as the upstream source for layout.
- Art direction is generated and QA-checked, but prompt generation does not currently consume it.
- The current layout HTML is page-image based, but `scripts/generate_illustrations.py` still contains a legacy seeding path that can copy older shared category assets or placeholders into new page-image slots.
- The `issues/1978/` tree still contains multiple generations of artifacts: page-based art, category-based art, duplicate prompt schemes, duplicate art-direction folders, and a stray malformed PDF artifact.
