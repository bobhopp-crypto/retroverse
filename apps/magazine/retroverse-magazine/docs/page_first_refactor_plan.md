# Page-First Refactor Plan

Scope: convert the RetroVerse layout engine from a `build_issue_pages(year)`-driven planner to a page-brief-driven planner, while keeping HTML/PDF rendering inside `scripts/magazine_pipeline.py`.

Primary reference: `docs/build_issue_pages_analysis.md`

## 1. Current Responsibility Map

### What currently defines page order

Current owner:

- `ISSUE_STRUCTURE` in `scripts/magazine_pipeline.py`

What it does:

- hard-codes the full issue sequence
- hard-codes page count
- hard-codes page numbers through `enumerate(ISSUE_STRUCTURE, start=1)` inside `build_issue_pages(year)`

This is editorial planning logic.

### What currently defines page slugs

Current owner:

- `ISSUE_STRUCTURE`
- `build_page(...)`, which writes the slug into `filename` and `story_id`

What it does:

- defines slugs like `cover`, `year_snapshot`, `top_song_1`, `retro_ads_page`
- uses the slug as the stable page identifier throughout the build

This is editorial planning logic up to the point where the slug is already known. Converting a known slug into a filename is rendering/normalization logic.

### What currently selects page templates

Current owner:

- `template_key_for_section(...)`
- `template_path_for_section(...)`
- `assert_canonical_templates_exist()`

Important qualification:

- this code only validates template-file existence
- it does not drive actual runtime page rendering
- the current HTML output is built by `render_issue_panel(...)`, `render_layout_page(...)`, and `render_layout_index(...)`

So template selection is currently a planning/validation artifact, not an active rendering dependency.

### What currently assigns content sources

Current owners:

- `ISSUE_SECTION_CONFIG`
- `STORY_SECTION_CONFIG`
- `build_section_page(...)`
- `build_cover_page(...)`
- `build_issue_markdown_section(...)`
- `build_year_snapshot_page(...)`
- `build_top_song_page(...)`
- `build_story_section_page(...)`
- `build_culture_collage_page(...)`
- `build_retro_ads_page(...)`
- `build_placeholder_page(...)`

What they do:

- map page slugs to markdown filenames
- map story pages to final article files
- derive fallback content from `chart_top23.md`
- derive snapshot/collage content from `data/editorial.json`
- assign page type / layout type
- assign hero image paths and collage image paths
- decide placeholder behavior when content is missing

This entire block is editorial planning logic.

## 2. Conceptual Layer Split

## LAYER A: Editorial Planning Logic

New owner:

- `pipeline/generate_issue_page_briefs.py`

Responsibilities that belong here:

- define the canonical issue order
- define page numbers
- define page slugs
- define page type / structure
- define source files for each page
- resolve final content source for each page
- decide fallback behavior when source content is missing
- assign title, subtitle, byline, story summary, text blocks, sidebar blocks, and data blocks
- assign hero asset and collage assets
- assign whether a page is cover-only, collage-driven, reserve/placeholder, or article-driven
- assign any future `template_key` if templates are going to be real rendering inputs

Design rule:

- page briefs should become the source of truth for what each page is
- the layout engine should stop reconstructing editorial intent from hard-coded slug dispatch

## LAYER B: Rendering Logic

Owner that should remain:

- `scripts/magazine_pipeline.py`

Responsibilities that belong here:

- define the render-side `IssuePage` structure, or its replacement render model
- convert structured page content into HTML and PDF-safe HTML
- resolve relative asset paths for layout mode and PDF mode
- render hero image blocks, collage blocks, marginal galleries, headers, footers, and navigation
- render issue pages and the layout index
- perform rendering-only sanitization and formatting

Design rule:

- the renderer should accept a page brief or a normalized page-spec object
- the renderer should not decide what pages exist
- the renderer should not decide what source file feeds a page
- the renderer should not decide what page type a slug means

## 3. Proposed Refactor

### Phase 1: Make page briefs authoritative

Update `generate_issue_page_briefs.py` so it no longer derives briefs from `page_records(year)`, because `page_records(year)` currently calls `build_issue_pages(year)`.

Instead, move the planning logic into the brief generator:

- move issue sequence ownership from `ISSUE_STRUCTURE` into the brief-generation stage
- move page slug assignment into the brief-generation stage
- move page-type assignment into the brief-generation stage
- move source-file mapping from `ISSUE_SECTION_CONFIG` and `STORY_SECTION_CONFIG` into the brief-generation stage
- move section-specific content synthesis into the brief-generation stage

Required result:

- `issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json` should fully define the issue
- each page brief should contain everything needed to render a page except final image bytes and the final HTML wrapper

### Phase 2: Replace planner dispatch inside `magazine_pipeline.py`

Replace the current flow:

- `build_issue_pages(year)` -> `build_section_page(...)` -> section-specific builders

With a new flow:

- `build_issue_pages(year)` loads the page brief manifest
- it loads each page brief JSON
- it converts each brief into a render-ready page object

At that point, `build_issue_pages(year)` becomes a render-model loader, not an editorial planner.

### Phase 3: Reduce rendering inputs to brief-owned fields

The renderer should read from page briefs for:

- `page_number`
- `page_slug`
- `page_type`
- `title`
- `subtitle`
- `writer.byline`
- `text_blocks`
- `sidebar_blocks`
- `layout_requirements.structure`
- `layout_requirements.hero_asset`
- `layout_requirements.collage_assets`

The renderer may still read files indirectly, but only through paths explicitly declared in the brief.

### Phase 4: Keep HTML/PDF assembly intact

Keep these rendering functions inside `magazine_pipeline.py`:

- `markdown_to_html(...)` if markdown block rendering remains part of rendering
- `sanitize_render_text(...)`
- `layout_asset_path(...)`
- `pdf_asset_path(...)`
- `hero_image_html(...)`
- `collage_html(...)`
- `marginal_gallery_html(...)`
- `render_masthead(...)`
- `render_issue_panel(...)`
- `render_layout_page(...)`
- `render_layout_index(...)`
- `render_pdf_document(...)`

These are rendering concerns, not planning concerns.

## 4. What Code Moves

Move from `scripts/magazine_pipeline.py` into `pipeline/generate_issue_page_briefs.py` or supporting planning helpers:

- `ISSUE_STRUCTURE`
- `ISSUE_SECTION_CONFIG`
- `STORY_SECTION_CONFIG`
- `load_chart_top23_rows(...)` if it continues to exist only to synthesize editorial page content
- `build_cover_page(...)`
- `build_issue_markdown_section(...)`
- `build_year_snapshot_page(...)`
- `build_top_song_page(...)`
- `build_story_section_page(...)`
- `build_culture_collage_page(...)`
- `build_retro_ads_page(...)`
- the editorial portions of `build_placeholder_page(...)`
- the editorial routing logic in `build_section_page(...)`

Move from `pipeline/common.py`:

- `page_records(year)` should stop calling `build_issue_pages(year)` and instead load the brief manifest directly

Move conceptually, even if helper functions are split differently:

- slug-to-source-file mapping
- slug-to-page-type mapping
- story-id-to-page mapping
- content fallback rules
- asset-assignment planning rules

## 5. What Code Stays

Keep in `scripts/magazine_pipeline.py`:

- `IssuePage`
- `build_page(...)` or its equivalent render-model constructor
- rendering helpers that format already-decided content
- asset path conversion helpers
- HTML wrapper generation
- navigation generation
- layout index generation
- PDF document rendering helpers

Keep as render-only helpers if still useful:

- `markdown_to_html(...)`
- `extract_title_byline_and_body(...)` only if briefs continue to carry markdown blobs instead of structured text blocks
- `strip_leading_headings(...)` only if briefs continue to carry raw markdown

Keep in `pipeline/generate_issue_page_briefs.py` after expansion:

- all logic that decides what content goes on a page
- all logic that determines what the page is supposed to look like structurally

## 6. What Code Should Be Deleted

Delete after the page-brief-driven path is fully in place:

- the hard-coded editorial dispatcher pattern in `build_section_page(...)`
- the current use of `page_records(year)` as a wrapper around `build_issue_pages(year)`
- any duplicate slug-routing logic that survives in both the brief generator and the renderer

Delete from `magazine_pipeline.py` once replaced by brief-owned data:

- `ISSUE_STRUCTURE`
- `ISSUE_SECTION_CONFIG`
- `STORY_SECTION_CONFIG`
- `build_cover_page(...)`
- `build_issue_markdown_section(...)`
- `build_year_snapshot_page(...)`
- `build_top_song_page(...)`
- `build_story_section_page(...)`
- `build_culture_collage_page(...)`
- `build_retro_ads_page(...)`

Delete or replace depending on whether templates become real:

- `template_key_for_section(...)`
- `template_path_for_section(...)`
- `assert_canonical_templates_exist()`

Delete them if:

- the renderer continues using only `render_issue_panel(...)` and CSS classes

Replace them with brief validation if:

- a future renderer actually consumes a `template_key` field from page briefs

Delete render-time editorial placeholders once briefs become complete:

- reserve-page synthesis that exists only because source selection still happens in the renderer

## 7. Recommended Target Shape

Desired control flow:

```text
generate_issue_page_briefs.py
  -> defines canonical issue sequence
  -> defines slugs, page types, sources, assets, and text blocks
  -> writes page brief manifest + page brief JSON files

magazine_pipeline.build_issue_pages(year)
  -> loads manifest
  -> loads each page brief
  -> converts brief data into IssuePage objects

build_issue.py
  -> renders IssuePage objects to HTML
```

In that shape:

- planning happens once
- rendering consumes the plan
- QA can validate the same brief contract the renderer actually uses
- the current duplicated planner-inside-renderer architecture disappears

## 8. Bottom Line

The core change is not “rewrite `build_issue_pages(year)`.” The core change is:

- remove editorial decision-making from the layout engine
- make page briefs the single source of truth for page identity and page content
- reduce `magazine_pipeline.py` to a renderer that consumes already-planned pages

If that boundary is held, the renderer becomes simpler, QA becomes more meaningful, and downstream stages stop depending on a layout builder that is secretly also acting as the issue planner.
