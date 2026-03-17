# build_issue_pages(year) Analysis

Target function: `scripts/magazine_pipeline.build_issue_pages(year)`

## Full Function Definition

```python
def build_issue_pages(year: int) -> list[IssuePage]:
    assert_canonical_templates_exist()
    top23_rows = load_chart_top23_rows(year)
    return [
        build_section_page(year, page_number, section_key, top23_rows)
        for page_number, section_key in enumerate(ISSUE_STRUCTURE, start=1)
    ]
```

## What the Function Actually Does

`build_issue_pages(year)` is only a thin orchestrator.

It does three things:

1. validates that section template files exist via `assert_canonical_templates_exist()`
2. loads Top 23 chart rows from `chart_top23.md`
3. walks the hard-coded `ISSUE_STRUCTURE` list and delegates each page to `build_section_page(...)`

Almost all real page construction logic lives outside this function.

## Where Key Decisions Are Defined

### Page order

Defined in `ISSUE_STRUCTURE` in [scripts/magazine_pipeline.py](/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/magazine_pipeline.py#L40).

That list hard-codes the full 30-page issue order:

- `cover`
- `masthead`
- `editor_letter`
- `year_snapshot`
- `charts_overview`
- `top_song_1` through `top_song_10`
- `movies`
- `television`
- `culture`
- `arcade`
- `retro_ad`
- `comic`
- `puzzle`
- `letters`
- `forgotten_hit`
- `one_hit_wonder`
- `album_spotlight`
- `year_timeline`
- `culture_collage`
- `retro_ads_page`
- `chart_top23`

### Page slugs like `top_song_1`

Those are also defined directly in `ISSUE_STRUCTURE` at [scripts/magazine_pipeline.py](/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/magazine_pipeline.py#L40).

They are then propagated as `section_key` through:

- `build_issue_pages(...)`
- `build_section_page(...)`
- `build_page(...)`

`build_page(...)` stores the slug in two places:

- `filename = f"page_{page_number:02d}_{section_key}.html"`
- `story_id = section_key`

See [scripts/magazine_pipeline.py](/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/magazine_pipeline.py#L436).

### Page types

Defined in several places:

- `ISSUE_SECTION_CONFIG` assigns `layout_type` for markdown-backed sections at [scripts/magazine_pipeline.py](/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/magazine_pipeline.py#L73)
- `STORY_SECTION_CONFIG` assigns `layout_type` for final-article-backed sections at [scripts/magazine_pipeline.py](/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/magazine_pipeline.py#L144)
- `build_cover_page(...)`, `build_year_snapshot_page(...)`, `build_top_song_page(...)`, `build_culture_collage_page(...)`, and `build_retro_ads_page(...)` hard-code additional page types in their own return paths
- `build_placeholder_page(...)` synthesizes reserve-page types when source content is missing

### Page templates

Template mapping is defined by:

- `template_key_for_section(...)` at [scripts/magazine_pipeline.py](/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/magazine_pipeline.py#L220)
- `template_path_for_section(...)` at [scripts/magazine_pipeline.py](/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/magazine_pipeline.py#L226)

Special case:

- any slug starting with `top_song_` maps to template key `top_song`

Important finding:

- `build_issue_pages(year)` does **not** actually select or load those template files for rendering
- it only calls `assert_canonical_templates_exist()` to verify the files exist
- the runtime page object is built by `build_section_page(...)` and `build_page_from_markdown(...)`, not by reading `templates/sections/*.html`

So template files are validated here, but not actively consumed here.

## Routing Logic

The real dispatcher is `build_section_page(...)` at [scripts/magazine_pipeline.py](/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/magazine_pipeline.py#L834).

It routes each `section_key` like this:

- `cover` -> `build_cover_page(...)`
- keys in `ISSUE_SECTION_CONFIG` -> `build_issue_markdown_section(...)`
- `year_snapshot` -> `build_year_snapshot_page(...)`
- keys starting with `top_song_` -> `build_top_song_page(...)`
- keys in `STORY_SECTION_CONFIG` -> `build_story_section_page(...)`
- `culture_collage` -> `build_culture_collage_page(...)`
- `retro_ads_page` -> `build_retro_ads_page(...)`
- `one_hit_wonder` -> placeholder page
- everything else -> generic placeholder page

## All Page Types Generated

For the current 1978 issue, `build_issue_pages(1978)` returns these layout types:

- `cover`
- `department masthead`
- `department letter`
- `snapshot page`
- `chart overview`
- `top song page`
- `screen feature`
- `department feature`
- `ad page`
- `comic page`
- `puzzle page`
- `department letters`
- `feature story`
- `one_hit_wonder reserve page`
- `timeline page`
- `collage page`
- `ad roundup`
- `chart page`

Page-by-page mapping for 1978:

| Page | Slug | Layout type |
|---|---|---|
| 01 | `cover` | `cover` |
| 02 | `masthead` | `department masthead` |
| 03 | `editor_letter` | `department letter` |
| 04 | `year_snapshot` | `snapshot page` |
| 05 | `charts_overview` | `chart overview` |
| 06-15 | `top_song_1` .. `top_song_10` | `top song page` |
| 16 | `movies` | `screen feature` |
| 17 | `television` | `screen feature` |
| 18 | `culture` | `department feature` |
| 19 | `arcade` | `department feature` |
| 20 | `retro_ad` | `ad page` |
| 21 | `comic` | `comic page` |
| 22 | `puzzle` | `puzzle page` |
| 23 | `letters` | `department letters` |
| 24 | `forgotten_hit` | `feature story` |
| 25 | `one_hit_wonder` | `one_hit_wonder reserve page` |
| 26 | `album_spotlight` | `feature story` |
| 27 | `year_timeline` | `timeline page` |
| 28 | `culture_collage` | `collage page` |
| 29 | `retro_ads_page` | `ad roundup` |
| 30 | `chart_top23` | `chart page` |

## Inputs It Reads

### Markdown

Yes. This is the primary content input.

Read paths include:

- `issues/{year}/cover.md`
- `issues/{year}/masthead.md`
- `issues/{year}/editor_letter.md`
- `issues/{year}/charts_overview.md`
- `issues/{year}/movies.md`
- `issues/{year}/television.md`
- `issues/{year}/culture.md`
- `issues/{year}/arcade.md`
- `issues/{year}/ads.md`
- `issues/{year}/comic.md`
- `issues/{year}/puzzle1.md`
- `issues/{year}/letters.md`
- `issues/{year}/chart_top23.md`
- `issues/{year}/songs/01.md` through `songs/10.md`
- `issues/{year}/articles/final/story_*.md` for story sections

The relevant loaders are:

- `load_text_if_exists(...)`
- `issue_markdown_path(...)`
- `final_year_dir(...)`
- `build_issue_markdown_section(...)`
- `build_top_song_page(...)`
- `build_story_section_page(...)`

### Charts

Yes, but only through Markdown.

`build_issue_pages(year)` reads chart data via:

- `load_chart_top23_rows(year)`
- which parses `issues/{year}/chart_top23.md`

This chart input is used for:

- the cover deck line
- the year snapshot quick signals
- top song fallback pages when `songs/NN.md` is missing

It does **not** read `issues/{year}/charts/*.json` or any database directly.

### Article JSON

No, not in the current code path.

Story sections read:

- `issues/{year}/articles/final/story_*.md`

They do **not** read:

- `issues/{year}/articles/final/story_*.json`

So the layout builder currently depends on final article Markdown, not final article JSON.

### Prompts

No.

`build_issue_pages(year)` does not read:

- illustration prompt text files
- `issues/{year}/art/image_prompts.json`
- art-direction JSON
- page-brief JSON

Those artifacts are outside this function’s current input model.

### Images

Yes, but only as path existence checks and asset subpath selection.

It reads image-related state from:

- `issues/{year}/art/pages/page_XX.png` via `page_art_subpath(...)`
- `assets/placeholder.png` via `page_art_or_placeholder_subpath(...)`
- `issues/{year}/art/collage/*.png` via `subpaths_from_folder(...)`
- `issues/{year}/art/marginals/*.png` via `choose_marginal_subpaths(...)`

Important nuance:

- it does not open image bytes or inspect image contents
- it only decides which image path should be attached to the `IssuePage`

## What `build_issue_pages(year)` Does Not Read

These artifacts exist elsewhere in the pipeline but are not used here:

- page briefs in `issues/{year}/layout/page_briefs/`
- art direction in `issues/{year}/art_direction/`
- illustration prompts in `issues/{year}/art/prompts/`
- prompt manifest in `issues/{year}/art/image_prompts.json`
- final article JSON in `issues/{year}/articles/final/*.json`

## What Should Instead Come From Page Briefs

If page briefs are intended to be the controlling layout contract, these parts should come from page briefs instead of being hard-coded or re-derived here:

### 1. Page order and page numbering

Currently:

- hard-coded in `ISSUE_STRUCTURE`
- page numbers are assigned by `enumerate(ISSUE_STRUCTURE, start=1)`

Should come from page briefs:

- page sequence
- page number
- page slug

### 2. Page type / layout type

Currently:

- hard-coded across `ISSUE_SECTION_CONFIG`
- `STORY_SECTION_CONFIG`
- individual builder functions
- placeholder logic

Should come from page briefs:

- `page_type`
- `layout_requirements.structure`

### 3. Hero and collage asset assignments

Currently:

- `page_art_or_placeholder_subpath(year, page_number)`
- `repeated_page_art_subpaths(...)`
- section-specific folder rules

Should come from page briefs:

- `layout_requirements.hero_asset`
- `layout_requirements.collage_assets`

### 4. Page-specific rendering intent

Currently:

- inferred from section key and helper choice
- e.g. `top_song_*` becomes `top song page`
- `retro_ads_page` becomes `ad roundup`
- `one_hit_wonder` becomes a reserve page

Should come from page briefs:

- explicit page intent
- expected page structure
- required content zones

### 5. Sidebar/data block expectations

Currently:

- extracted ad hoc from markdown sections like `## Data Snapshot`
- assembled from `editorial.json` for `year_snapshot`
- repeated from collage/ad helper logic

Should come from page briefs:

- declared sidebar blocks
- declared data blocks
- page-specific structured handoff metadata

## What Should Still Stay Outside Page Briefs

Not everything belongs in a page brief.

These should remain source inputs rather than brief-owned content:

- article body copy from source markdown or final article markdown
- chart facts from the chart source
- image files themselves
- placeholder fallback assets

Page briefs should describe the layout contract, not replace source editorial data.

## Bottom Line

`build_issue_pages(year)` is not a layout planner. It is a thin adapter over:

- `ISSUE_STRUCTURE`
- section config dictionaries
- markdown loaders
- image-path helpers
- the `build_section_page(...)` dispatcher

The function currently ignores the page-brief layer entirely. If page briefs are meant to be canonical, then page order, slug, layout type, and asset assignments should move from hard-coded builder logic into the brief data model, and `build_issue_pages(year)` should consume that contract instead of reconstructing it.
