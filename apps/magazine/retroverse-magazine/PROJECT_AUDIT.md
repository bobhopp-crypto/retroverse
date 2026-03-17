# RetroVerse Magazine Project Audit

## Executive Summary

The true state of the RetroVerse magazine engine is **fragmented**. The project contains **multiple partially overlapping pipelines** rather than one canonical end-to-end magazine builder.

What exists on disk today:

- a **Markdown -> PDF** pipeline
- a separate **JSON/data -> HTML preview/layout** pipeline
- a separate **satirical illustrated HTML** pipeline
- a separate **planning/writer/art-director/final-prose** pipeline

These systems do **not** currently converge on one shared source of truth.

---

## PROJECT STRUCTURE MAP

```text
retroverse-magazine/
├── PROJECT_STATE.md
├── DATA_INVENTORY.md
├── generate_magazine.py                     # standalone satirical HTML builder
├── magazine_template.html
├── requirements.txt
├── data/
│   └── DATA_SOURCES.yaml
├── prompts/
│   └── generate_issue_prompt.md             # empty
├── templates/
│   ├── issue_template.md                    # empty
│   └── page_template.html                   # legacy/unused-looking template
├── assets/
│   └── css/
│       └── magazine.css
├── images/                                  # legacy card-image set used by generate_magazine.py
│   ├── 1978_raw_*.png
│   └── 1978_magazine.jpg
├── output/
│   ├── RetroVerse_1978.html                 # generated standalone HTML artifact
│   └── RetroVerse_1978.pdf                  # generated PDF artifact
├── layout-library/
│   ├── css/layout-library.css
│   ├── docs/
│   ├── schemas/layout_templates.json
│   └── templates/
│       ├── template_back_page.html
│       ├── template_contents.html
│       ├── template_cover.html
│       ├── template_data_page.html
│       ├── template_department_column.html
│       ├── template_feature_spread.html
│       ├── template_grid_collage.html
│       ├── template_narrative_comic.html
│       └── template_visual_parody.html
├── tools/
│   └── magazine_builder/
│       ├── build_issue.py                   # Markdown -> PDF
│       ├── style.css
│       └── template.html
├── scripts/
│   ├── editorial_supervisor.py              # planning pipeline orchestrator
│   ├── generate_year_context.py             # minimal Hot 100 context generator
│   ├── generate_all_year_contexts.py
│   ├── analyze_chart_dynamics.py
│   ├── generate_year_narrative.py
│   ├── run_staff_writers.py
│   ├── run_art_director.py
│   ├── generate_final_articles.py
│   ├── generate_editorial.py                # issue.json/data -> editorial.json
│   ├── generate_art_prompts.py
│   ├── generate_illustrations.py
│   ├── generate_marginals.py
│   ├── build_issue.py                       # issue.json -> preview/layout HTML
│   ├── build_full_issue.py                  # small HTML/art pipeline orchestrator
│   ├── index_artwork.py
│   └── find_art_asset.py
├── art-library/                             # reusable art index + large asset cache
│   ├── art_index.json
│   ├── backgrounds/
│   ├── fake_ads/
│   └── textures/
├── art_library/                             # second, differently named art cache
│   ├── backgrounds/
│   └── scenes/
└── issues/
    ├── context/                             # 68 *_context.json files (1958-2025)
    ├── plans/
    │   └── 1978_narrative_plan.{json,md}
    ├── articles/
    │   └── 1978/story_001..012.{json,md}
    ├── final/
    │   └── 1978/story_001..012.{json,md}
    ├── layout/
    │   ├── 1978_issue_map.{json,md}
    │   └── 1978_production_targets.json
    ├── art/                                 # duplicated shared art tree
    ├── 1978/
    │   ├── cover.md
    │   ├── masthead.md
    │   ├── editor_letter.md
    │   ├── charts_overview.md
    │   ├── songs/01.md ... 10.md
    │   ├── movies.md
    │   ├── television.md
    │   ├── culture.md
    │   ├── letters.md
    │   ├── ads.md
    │   ├── comic.md
    │   ├── arcade.md
    │   ├── puzzle1.md
    │   ├── puzzle2.md
    │   ├── chart_top23.md
    │   ├── retroverse_1978_pilot.md
    │   ├── data/
    │   │   ├── issue.json
    │   │   ├── charts.json
    │   │   ├── movies.json
    │   │   ├── tv.json
    │   │   └── editorial.json
    │   ├── art/
    │   │   ├── collage/
    │   │   ├── comic/
    │   │   ├── cover/
    │   │   ├── departments/
    │   │   ├── fake_ads/
    │   │   ├── feature/
    │   │   ├── marginals/
    │   │   ├── parody/
    │   │   └── image_prompts.json
    │   ├── preview/page_*.html              # generated preview pages
    │   ├── layout/page_*.html               # generated layout pages
    │   └── page_*.html / index.html         # older legacy static issue
    ├── 1979/                                # empty
    └── 1980/                                # empty
```

### Generation Scripts By Function

- Context/data: `generate_year_context.py`, `analyze_chart_dynamics.py`, `generate_all_year_contexts.py`
- Planning/writing: `generate_year_narrative.py`, `run_staff_writers.py`, `run_art_director.py`, `generate_final_articles.py`, `editorial_supervisor.py`
- Issue-data/content: `generate_editorial.py`
- Art: `generate_art_prompts.py`, `generate_illustrations.py`, `generate_marginals.py`, `index_artwork.py`, `find_art_asset.py`
- Builders: `scripts/build_issue.py`, `tools/magazine_builder/build_issue.py`, `generate_magazine.py`, `build_full_issue.py`

---

## PIPELINE STATUS

| Component | Status | Audit Result |
| --- | --- | --- |
| Context generation system | PARTIAL | 68 context JSON files exist, but the current generator writes only a minimal Hot 100 schema while downstream planning/final prose expects richer fields such as albums, sonic profile, movies, television, and `context_sources`. |
| Article generation system | PARTIAL | Narrative plan, draft article, and final article generators exist and produce `issues/articles/1978` and `issues/final/1978`, but the active builders do not consume those outputs. |
| Illustration generation system | PARTIAL | Prompt generation, image generation, marginal generation, and artwork indexing all exist. Artwork files are present, but the preview/layout builder mostly shows file paths instead of rendering the images. |
| Magazine builder | PARTIAL | Three separate builders exist, but there is no single canonical builder that consumes the planning pipeline outputs and emits the final issue. |
| Output artifacts | EXISTS | `output/RetroVerse_1978.html`, `output/RetroVerse_1978.pdf`, `issues/1978/preview/`, and `issues/1978/layout/` all exist, but they are produced by different systems. |

### Key Break In The Pipeline

The biggest structural break is:

`context/plans/articles/final prose` -> **not connected** -> `preview/layout/PDF builders`

The planning pipeline writes:

- `issues/plans/1978_narrative_plan.json`
- `issues/articles/1978/story_001..012.{json,md}`
- `issues/final/1978/story_001..012.{json,md}`
- `issues/layout/1978_issue_map.{json,md}`
- `issues/layout/1978_production_targets.json`

But the HTML/PDF issue builders instead read:

- `issues/1978/data/issue.json`
- `issues/1978/data/charts.json`
- `issues/1978/data/movies.json`
- `issues/1978/data/tv.json`
- `issues/1978/data/editorial.json`
- `issues/1978/*.md`

Those are two different content models.

---

## ILLUSTRATION SYSTEM STATUS

### Located Artwork Assets

- `issues/1978/art/` contains **29 files**
- `issues/art/` contains **28 files** and appears to be a duplicate/shared copy
- `images/` contains **18 files** used by the older `generate_magazine.py` pipeline
- `art-library/` contains **71 indexed reusable assets**
- `art_library/` contains **2 additional assets** in a second differently named library

### Prompt Files

- `issues/1978/art/image_prompts.json`
- `issues/art/image_prompts.json` (duplicate copy)

### Art Generation Scripts

- `scripts/generate_art_prompts.py`
- `scripts/generate_illustrations.py`
- `scripts/generate_marginals.py`
- `scripts/index_artwork.py`
- `scripts/find_art_asset.py`

### Builder Integration Reality

- `scripts/build_issue.py` reads `art_filename` values from `issues/1978/data/issue.json`
- for most page types, it renders those assets as `<code>../art/...png</code>` text, not as actual `<img>` elements
- the only real image tags in that builder are the marginal gag injections
- `tools/magazine_builder/build_issue.py` does not load the issue art tree at all
- `generate_magazine.py` is the only builder that clearly renders actual image tags for page art, and it uses the separate `images/1978_raw_*.png` set

### Important Style Mismatch

The project rules say to avoid MAD imitation, but:

- `scripts/generate_illustrations.py`
- `scripts/generate_marginals.py`

still hard-code MAD-style language in the art prompts. The illustration pipeline does not match the current editorial rule set.

---

## ISSUE 1978 ANALYSIS

### What Exists In `issues/1978/`

There are **three different 1978 issue representations**:

1. Markdown issue package for the PDF builder
2. Legacy root `page_*.html` issue set
3. Generated `preview/` and `layout/` issue sets

Counts:

- root HTML pages: **24**
- preview HTML pages: **24**
- layout HTML pages: **24**

There are no missing numbered HTML pages, but the page sets are not identical.

### Root HTML vs Generated Preview Filename Drift

These page names differ between the root issue folder and the generated preview/layout output:

- `page_07_parody_media.html` vs `page_07_parody_console.html`
- `page_11_parody_weekend.html` vs `page_11_parody_planner.html`
- `page_15_comic_nightshift.html` vs `page_15_comic_night.html`
- `page_19_data_music_pulse.html` vs `page_19_data_music.html`
- `page_20_feature_television.html` vs `page_20_feature_tv.html`
- `page_21_department_letters.html` vs `page_21_department_sue.html`
- `page_22_parody_trends.html` vs `page_22_parody_trend.html`

This confirms the project is carrying at least two separate 1978 HTML issue versions.

### Markdown Issue Package Check

Required components in the Markdown/PDF package:

- Cover: YES (`cover.md`)
- Masthead: YES (`masthead.md`)
- Editor letter: YES (`editor_letter.md`)
- Charts overview: YES (`charts_overview.md`)
- Song features: YES (`songs/01.md` through `songs/10.md`)
- Culture page: YES (`culture.md`)
- Chart page: YES (`chart_top23.md`)

Incomplete Markdown pages:

- `ads.md`
- `comic.md`
- `arcade.md`
- `puzzle1.md`
- `puzzle2.md`

Markdown placeholder count in the 1978 package: **5**

Also important:

- Markdown issue files: **15**
- Markdown image references: **0**

So the PDF source package is text-only at present.

### Preview/Layout Issue Quality

Generated preview/layout pages are more visually structured than the Markdown package, but still partial:

- preview placeholder hits: **11**
- layout placeholder hits: **11**
- legacy root issue placeholder hits: **77**

### Page-Level Problems In The Generated Preview/Layout

- Multiple feature pages reuse the **same single feature body** from `issues/1978/data/editorial.json`
  - affected pages: page 04, 05, 13, 16, 20
- Multiple collage pages reuse the **same single collage tile set**
  - page 17 ignores its own page-specific `collage_tiles` and renders the page-06 style tile set
- The comic page ignores the page-specific panel list in `issue.json` and instead uses the shared comic block from `editorial.json`
- Most art is referenced only as text/code, not rendered

### Illustration References Inside The 1978 Issue

Main references in `issues/1978/data/issue.json` point to assets such as:

- `cover/cover_1978.png`
- `feature/disco_floor.png`
- `feature/cinema_marquee.png`
- `feature/tv_livingroom.png`
- `feature/feature_placeholder.png`
- `parody/weekend_console.png`
- `parody/fake_ad_kit.png`
- `parody/trivia_grid.png`
- `parody/parody_placeholder.png`
- `collage/collage_01..09.png`

But in the generated preview/layout HTML these usually appear as code blocks, not actual image renders.

---

## MAGAZINE BUILDER STATUS

### Builder A: `scripts/build_issue.py`

Status: PARTIAL

What it loads:

- `issues/1978/data/issue.json`
- `issues/1978/data/charts.json`
- `issues/1978/data/movies.json`
- `issues/1978/data/tv.json`
- `issues/1978/data/editorial.json`
- `issues/1978/art/image_prompts.json`
- layout templates from `layout-library/templates/`

What it outputs:

- `issues/1978/preview/page_*.html`
- `issues/1978/layout/page_*.html`
- `issues/1978/preview/index.html`

Image support:

- partial only
- main art is usually printed as file-path text inside the page chrome
- marginals are true image embeds

Placeholder behavior:

- placeholder text passes through into final pages
- placeholder art files such as `feature_placeholder.png` and `parody_placeholder.png` are used directly

Structural problem:

- this builder does **not** consume `issues/articles/1978` or `issues/final/1978`

### Builder B: `tools/magazine_builder/build_issue.py`

Status: PARTIAL

What it loads:

- a fixed `PAGE_ORDER` of 24 Markdown files from `issues/<year>/`

What it outputs:

- `output/RetroVerse_<year>.pdf`

Image support:

- only implicit Markdown image support through `markdown` + WeasyPrint
- no explicit art loading from `issues/<year>/art/`
- current 1978 Markdown source has **0** image references, so the PDF path is effectively text-only

Placeholder behavior:

- placeholder Markdown is rendered as-is

Dependency gap:

- `requirements.txt` only lists `openai` and `python-dotenv`
- the PDF builder also needs `markdown` and `weasyprint`

### Builder C: `generate_magazine.py`

Status: PARTIAL

What it loads:

- `images/1978_raw_*.png`
- `year_end_top_40_<year>.json` if available
- `magazine_template.html`

What it outputs:

- `output/RetroVerse_1978.html`

Image support:

- real `<img>` rendering is present here

Problem:

- this is a separate satirical/placeholder magazine engine, not connected to the planning pipeline or the `issues/1978/data` pipeline

### Orchestrators

There are also two different orchestration layers:

- `scripts/build_full_issue.py`
  - runs `generate_editorial.py` -> `generate_art_prompts.py` -> `generate_illustrations.py` -> `generate_marginals.py` -> `scripts/build_issue.py`
- `scripts/editorial_supervisor.py`
  - runs context checks, chart dynamics, narrative plan, staff drafts, art-director outputs, and final prose
  - does **not** build the preview, HTML issue, or PDF

So even the orchestrators are split across two disconnected workflows.

---

## REDUNDANT SYSTEMS

### 1. Multiple Magazine Builders

- `scripts/build_issue.py`
- `tools/magazine_builder/build_issue.py`
- `generate_magazine.py`

These produce different artifacts from different source models.

### 2. Multiple Orchestration Paths

- `scripts/build_full_issue.py`
- `scripts/editorial_supervisor.py`
- `scripts/generate_year_range.py`

They do not drive the same pipeline end to end.

### 3. Multiple Article Sources

- `issues/1978/*.md` and `issues/1978/songs/*.md`
- `issues/articles/1978/*.md`
- `issues/final/1978/*.md`
- `issues/1978/retroverse_1978_pilot.md`
- synthetic copy embedded by `generate_magazine.py`

There is no single canonical article source.

### 4. Multiple 1978 HTML Issue Variants

- root `issues/1978/page_*.html`
- generated `issues/1978/preview/page_*.html`
- generated `issues/1978/layout/page_*.html`

### 5. Duplicate Art Trees

- `issues/1978/art/`
- `issues/art/`

### 6. Duplicate Art Libraries

- `art-library/`
- `art_library/`

These are not used consistently. `generate_illustrations.py` writes/reuses `art_library`, while `index_artwork.py` indexes `art-library`.

### 7. Conflicting Editorial Metadata

The planning pipeline and issue-data pipeline do not even share one staff model:

- `PROJECT_STATE.md` staff includes Daisy Delgado, Nicole Thomas, Professor Wheeler, Lola Vance
- `issues/1978/data/issue.json` credits Hanna Judge, Kevin Casey, Bennett & Carter, Prof Dick Wheeler

This is another sign that two pipelines evolved separately.

---

## MISSING COMPONENTS

- A single canonical issue schema shared by planning, art, and layout
- A context generator that matches downstream expectations
- A builder that consumes `issues/final/<year>` article outputs
- Real image embedding across the preview/layout pipeline
- A single authoritative 1978 issue source
- Completed non-placeholder Markdown pages for ads, comic, arcade, and puzzle sections
- A populated issue-generation path for years beyond 1978
- Consistent dependency declaration for `markdown` and `weasyprint`
- Any evidence that `1978_issue_map.json` / `1978_production_targets.json` drive page layout generation

---

## RECOMMENDED NEXT ACTION

Before adding features, pick and enforce **one canonical pipeline**:

1. Adopt one source of truth for article content.
   Best candidate: `issues/final/<year>` plus `issues/layout/<year>_production_targets.json`.

2. Replace or repair `generate_year_context.py` so it emits the rich schema that the planning/final-prose pipeline expects.

3. Retire or archive the non-canonical builders and duplicate asset trees:
   `generate_magazine.py`, root `issues/1978/page_*.html`, one of `art-library` / `art_library`, and one of `issues/1978/art` / `issues/art`.

4. Rebuild the canonical builder so it:
   - reads final article outputs
   - reads visual briefs / production targets
   - embeds actual images
   - emits both HTML and PDF from the same page model

Until that is done, the RetroVerse magazine engine should be treated as **a set of prototypes, not a single production pipeline**.
