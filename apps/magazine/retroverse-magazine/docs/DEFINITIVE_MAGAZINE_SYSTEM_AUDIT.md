# Definitive RetroVerse Magazine System Audit

**Date:** March 17, 2026  
**Project Root:** `~/Sites/retroverse/apps/magazine/retroverse-magazine`  
**Audit Mode:** Read-only. No files were modified.

---

## 1. PURPOSE

This document is the **source of truth** for the current RetroVerse Magazine system. It reflects what actually exists in the repository as of the audit date. Use it to:

- Orient new work without drift
- Resolve conflicts between older docs
- Identify canonical vs deprecated paths
- Plan page-by-page production

---

## 2. CURRENT CANONICAL PROJECT ROOT

```
/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine
```

---

## 3. TOP-LEVEL DIRECTORY MAP

| Directory | Purpose |
|-----------|---------|
| `pipeline/` | Canonical issue pipeline stages and QA gates. Entrypoint: `run_issue_pipeline.py` |
| `scripts/` | Standalone scripts for data, generation, audits, batch runs |
| `workflow/` | Single-page rebuild pipeline (`page_rebuild/`) and workflow configs |
| `prompts/` | LLM/system prompts (minimal: `generate_issue_prompt.md`) |
| `issues/` | Per-year issue content. `issues/context/` = year context JSON; `issues/{year}/` = issue data |
| `issues/context/` | Year context JSON files: `{year}_context.json` (1958–2025) |
| `docs/` | Architecture, runbooks, audits, decisions |
| `artifacts/` | Pipeline logs and QA outputs |
| `charter/` | Editorial charter and personas |
| `templates/` | HTML section templates (`templates/sections/*.html`) |
| `layout-library/` | Layout system: CSS, schemas, layout templates |
| `archive/` | Old runs, prototype pipelines, unused assets |
| `comfy/` | ComfyUI workflow definitions (`artist_render_workflow.json`) |
| `tools/` | Magazine builder, PDF renderer |
| `art-library/` | Shared reusable art (backgrounds, scenes, fake_ads, textures, etc.) |
| `assets/` | Static assets (CSS, placeholder.png) |
| `data/` | `DATA_SOURCES.yaml`, `retroverse_artists.json` |
| `public/` | Public static assets (art-department portraits, etc.) |

---

## 4. CANONICAL DOCUMENTS

| Document | Role |
|----------|------|
| `PROJECT_STATE.md` | Primary spec: editorial staff, issue structure, generation rules, QA stages, canonical directories |
| `charter/retroverse_editorial_charter.md` | Editorial personas, voice, tone |
| `docs/CANONICAL_PIPELINE.md` | Pipeline flow (partially stale; see Section 6) |
| `docs/ARCHITECTURE.md` | Data flow, screen/culture warehouse |
| `ISSUE_STRUCTURE_REPORT.md` | Confirms 30-page structure and build integration |
| `DATA_INVENTORY.md` | Data sources and inventory |
| `data/DATA_SOURCES.yaml` | Canonical data paths |

---

## 5. STALE / CONFLICTING / DUPLICATE DOCUMENTS

| Document | Status | Notes |
|----------|--------|-------|
| `PROJECT_AUDIT.md` | **Stale** | Describes fragmented state from an earlier audit. Paths (e.g. `issues/articles/`, `issues/final/`) have since moved. |
| `MAGAZINE_PIPELINE_AUDIT.md` | **Stale** | Project root wrong (`retroverse-magazine` vs `retroverse/retroverse-magazine`). Directory tree outdated. |
| `PIPELINE_REPAIR_REPORT.md` | **Partially stale** | Says `scripts/magazine_pipeline.py` is canonical CLI; actual canonical entrypoint is `pipeline/run_issue_pipeline.py`. |
| `PIPELINE_REPAIR_IMPLEMENTATION.md` | **Partially implemented** | Describes moves (e.g. `issues/articles/1978` → `issues/1978/articles/`) that appear done; `artifacts/` exists. |
| `PRESS_CHECK_1978.md` | **Historical** | Documents failures at a point in time; many fixes applied since. |
| `docs/CANONICAL_PIPELINE.md` | **Stale** | References `issues/final/{year}/`; actual path is `issues/{year}/articles/final/`. References `output/`; PDF now goes to `issues/{year}/pdf/`. |
| `docs/PROJECT_PIPELINE_REPORT.md` | **Stale** | Describes OpenAI image generation; `generate_illustrations.py` uses ComfyUI only. |

**Conflicts:**

- **Editorial staff names:** `PROJECT_STATE.md` top block lists BJ Lovestreet, A.J. Hunter, Nicole Thomas, Professor Wheeler, Emily Bennet/Charles Cursor, Nick Nitro, Daisy Delgado. Voice profiles reference Bob Jones, Martin Hale, Linda Park, Eve Binet. Charter uses A.J. Hunter, Emily Bennett, Charles Carter, Prof Dick Wheeler, Nicole Thomas, Sue Belmer, Hanna Judge. Treat `PROJECT_STATE.md` + `issues/1978/masthead.md` as canonical for display; charter for persona detail.
- **Article paths:** `docs/CANONICAL_PIPELINE.md` says `issues/final/{year}/`; actual path is `issues/{year}/articles/final/`.

---

## 6. ACTIVE PRODUCTION PIPELINE

**Canonical entrypoint:**

```bash
python3 pipeline/run_issue_pipeline.py --year 1978
```

**Stage order (from `pipeline/run_issue_pipeline.py`):**

1. **Context** — `scripts/generate_year_context.py` → `issues/context/{year}_context.json`
2. **Narrative Planning** — `scripts/generate_year_narrative.py` → `issues/plans/{year}_narrative_plan.json`
3. **Staff Writers** — `scripts/run_staff_writers.py` → `issues/{year}/articles/story_*.json`
4. **Final Articles** — `scripts/generate_final_articles.py` → `issues/{year}/articles/final/story_*.md`
5. **Page Briefs** — `pipeline/generate_issue_page_briefs.py` → `issues/{year}/layout/page_briefs/page_*_*.json`
6. **QA Page Briefs** — `pipeline/qa_page_briefs.py`
7. **Art Direction** — `pipeline/art_direction_stage.py` → `issues/{year}/art_direction/`, `issues/{year}/layout/art_direction/`
8. **QA Art Direction** — `pipeline/qa_art_direction.py`
9. **Illustration Prompts** — `pipeline/illustration_prompt_stage.py` → `issues/{year}/art/prompts/page_*.txt`, `issues/{year}/art/image_prompts.json`
10. **QA Art Prompts** — `pipeline/qa_art_prompts.py`
11. **Illustration Generation** — `scripts/generate_illustrations.py` → `issues/{year}/art/pages/page_*.png` (ComfyUI)
12. **Layout** — `scripts/build_issue.py` → `issues/{year}/layout/page_*.html`, `index.html`
13. **QA Layout** — `pipeline/qa_layout.py`
14. **Press Check** — `pipeline/qa_press_check.py`
15. **PDF** — `node tools/magazine_builder/render_browser_pdf.mjs` → `issues/{year}/pdf/RetroVerse_{year}.pdf`

**Key scripts:**

- `scripts/build_issue.py` — Imports from `magazine_pipeline`; builds HTML from `build_issue_pages(year)`.
- `scripts/magazine_pipeline.py` — Defines `ISSUE_STRUCTURE`, `build_issue_pages()`, `render_layout_page()`, `render_layout_index()`.
- `pipeline/common.py` — Shared helpers, `page_records()`, `ensure_canonical_directories()`.

**Dependencies:** `build_issue_pages(year)` in `magazine_pipeline.py` still owns page order, slugs, and source routing. Page briefs are generated from it; the layout builder does not yet load page briefs as the primary source.

---

## 7. YEAR-CENTRIC DATA AND CONTEXT SOURCES

| Source | Path | Purpose |
|--------|------|---------|
| Year context | `issues/context/{year}_context.json` | Top songs, chart data, cultural context for the year |
| Narrative plan | `issues/plans/{year}_narrative_plan.json` | Story assignments, planning |
| Article drafts | `issues/{year}/articles/story_*.json` | Staff writer outputs |
| Final articles | `issues/{year}/articles/final/story_*.md` | Final prose |
| Issue map | `issues/{year}/layout/1978_issue_map.json` | Page mapping |
| Production targets | `issues/{year}/layout/1978_production_targets.json` | Art/layout targets |
| Markdown sections | `issues/{year}/*.md` (e.g. `cover.md`, `masthead.md`, `charts_overview.md`) | Section copy |
| Chart data | `issues/{year}/chart_top23.md`, `issues/context/{year}_context.json` (top_songs) | Chart content |

**Context schema:** `issues/context/{year}_context.json` includes `year`, `top_songs`, and other chart/cultural fields. Generated by `generate_year_context.py` and enriched by `analyze_chart_dynamics.py`.

---

## 8. DEFINITIVE PAGE STRUCTURE

**Source:** `scripts/magazine_pipeline.py` → `ISSUE_STRUCTURE`

**30-page order:**

| # | Section | # | Section |
|---|---------|---|---------|
| 1 | cover | 16 | movies |
| 2 | masthead | 17 | television |
| 3 | editor_letter | 18 | culture |
| 4 | year_snapshot | 19 | arcade |
| 5 | charts_overview | 20 | retro_ad |
| 6 | top_song_1 | 21 | comic |
| 7 | top_song_2 | 22 | puzzle |
| 8 | top_song_3 | 23 | letters |
| 9 | top_song_4 | 24 | forgotten_hit |
| 10 | top_song_5 | 25 | one_hit_wonder |
| 11 | top_song_6 | 26 | album_spotlight |
| 12 | top_song_7 | 27 | year_timeline |
| 13 | top_song_8 | 28 | culture_collage |
| 14 | top_song_9 | 29 | retro_ads_page |
| 15 | top_song_10 | 30 | chart_top23 |

**Layout outputs:** `issues/1978/layout/page_01_cover.html` … `page_30_chart_top23.html`, `index.html`.

**Final page:** Always `chart_top23` (page 30).

---

## 9. ROLE REGISTRY (WRITERS / EDITORS / ARTISTS)

**Source:** `PROJECT_STATE.md`, `issues/1978/masthead.md`, `charter/retroverse_editorial_charter.md`, `data/retroverse_artists.json`

### Editorial staff (display)

| Role | Name | Source |
|------|------|--------|
| Editor-in-Chief | BJ Lovestreet | masthead.md, PROJECT_STATE |
| Charts Editor | Nicole Thomas | masthead.md, PROJECT_STATE |
| Music Features Editor | Bob Jones | masthead.md, PROJECT_STATE |
| Film Editor | Martin Hale | masthead.md, PROJECT_STATE |
| Television Editor | Linda Park | masthead.md, PROJECT_STATE |
| Culture & Lifestyle Editor | Eve Binet | masthead.md, PROJECT_STATE |
| Humor Editor | Nick Nitro | masthead.md, PROJECT_STATE |
| Art Director | Daisy Delgado | masthead.md, PROJECT_STATE |

### Charter personas (voice detail)

| Persona | Role | Source |
|---------|------|--------|
| B.J. Lovestreet | Editor-in-Chief | charter |
| A.J. Hunter | Music Editor | charter |
| Emily Bennett, Charles Carter | Film & TV Critics | charter |
| Prof Dick Wheeler | Culture & Trends | charter |
| Nicole Thomas | Charts Narrator | charter |
| Sue Belmer | Advice Column "Sue Says" | charter |
| Hanna Judge | Art Director | charter |

### Art department (illustrators)

| Role | Source |
|------|--------|
| COVER_ARTIST | pipeline/common.py ILLUSTRATION_STUDIO |
| EDITORIAL_SCENE_ARTIST | pipeline/common.py |
| INFOGRAPHIC_ARTIST | pipeline/common.py |
| COMIC_ARTIST | pipeline/common.py |
| SPOT_ARTIST | pipeline/common.py |

**Artist registry:** `data/retroverse_artists.json` — Celia Marsh, Lennox Vale, etc., with departments, style traits, self_portrait_prompt, reference_scene_prompts.

---

## 10. PROMPT AND ART GENERATION SOURCES

| Source | Path | Purpose |
|--------|------|---------|
| Page briefs | `issues/{year}/layout/page_briefs/page_*_*.json` | Per-page editorial brief |
| Art direction | `issues/{year}/art_direction/page_*_*.json` | Per-page art direction |
| Illustration prompts | `issues/{year}/art/prompts/page_*.txt` | Prompt text for each page |
| Image prompts manifest | `issues/{year}/art/image_prompts.json` | Maps page_number, page_slug, prompt_path, image_path |
| Artist prompts | `artist_prompts.txt` (root) | Legacy/standalone prompts |

**Prompt flow:** `illustration_prompt_stage.py` reads page briefs and art direction, writes `art/prompts/page_*.txt` and updates `image_prompts.json`. `generate_illustrations.py` reads `image_prompts.json` and `prompt_path` files.

**Note:** Some prompts still contain "MAD Magazine caricature influence" (e.g. `page_06.txt`), which conflicts with PROJECT_STATE rule to avoid MAD imitation.

---

## 11. WHAT TO USE GOING FORWARD

| Use | Path |
|-----|------|
| Pipeline entrypoint | `pipeline/run_issue_pipeline.py --year {year}` |
| Page structure | `scripts/magazine_pipeline.py` → `ISSUE_STRUCTURE` |
| Layout builder | `scripts/build_issue.py` |
| PDF renderer | `node tools/magazine_builder/render_browser_pdf.mjs` |
| Year context | `issues/context/{year}_context.json` |
| Final articles | `issues/{year}/articles/final/story_*.md` |
| Section markdown | `issues/{year}/*.md` |
| Art output | `issues/{year}/art/pages/page_*.png` |
| Layout output | `issues/{year}/layout/page_*.html` |
| PDF output | `issues/{year}/pdf/RetroVerse_{year}.pdf` |
| Single image (OpenAI) | `scripts/generate_image.py` (standalone) |
| Marginal gags (OpenAI) | `scripts/generate_marginals.py` |

---

## 12. WHAT TO STOP USING

| Do not use | Reason |
|------------|--------|
| `scripts/magazine_pipeline.py` as CLI | Use `pipeline/run_issue_pipeline.py` instead |
| `scripts/build_full_issue.py` | Archived; use pipeline |
| `scripts/build_magazine.py` | Archived |
| `archive/old_runs/prototype_pipelines/generate_magazine.py` | Archived prototype |
| `issues/1978/preview/` | Old preview pipeline; layout is canonical |
| `issues/art/` | Duplicate; use `issues/{year}/art/` |
| `output/` for PDF | PDF now in `issues/{year}/pdf/` |
| `docs/CANONICAL_PIPELINE.md` paths | Stale; use this audit |
| `PROJECT_AUDIT.md` / `MAGAZINE_PIPELINE_AUDIT.md` for current state | Stale |

---

## 13. PAGE-BY-PAGE PRODUCTION PLAN

1. **Context:** Ensure `issues/context/{year}_context.json` exists and is complete.
2. **Planning:** Run narrative + staff writers + final articles.
3. **Page briefs:** Run `pipeline/generate_issue_page_briefs.py`; check `issues/{year}/layout/page_briefs/`.
4. **Art direction:** Run `pipeline/art_direction_stage.py`; check `issues/{year}/art_direction/`.
5. **Prompts:** Run `pipeline/illustration_prompt_stage.py`; check `issues/{year}/art/prompts/`.
6. **Illustrations:** Run `scripts/generate_illustrations.py` (requires ComfyUI) or use `scripts/generate_image.py` for single images via OpenAI.
7. **Layout:** Run `scripts/build_issue.py`; inspect `issues/{year}/layout/`.
8. **PDF:** Run `render_browser_pdf.mjs`; output in `issues/{year}/pdf/`.

**Single-page workflow:** `workflow/page_rebuild/rebuild_single_page.py` for one-page rebuild with QA.

---

## 14. OPEN QUESTIONS / MISSING LINKS

1. **Image generation:** `generate_illustrations.py` uses ComfyUI only. No OpenAI fallback. ComfyUI must be running at `COMFYUI_BASE_URL`. For OpenAI-only: use `generate_image.py` (single) or `generate_marginals.py` (marginals).
2. **Page briefs vs build:** `build_issue_pages(year)` still drives layout; page briefs are derived from it, not consumed by the renderer. Page-first refactor (see `docs/page_first_refactor_plan.md`) is planned but not done.
3. **MAD style in prompts:** Some `art/prompts/page_*.txt` still reference MAD; PROJECT_STATE says avoid MAD imitation. Needs prompt cleanup.
4. **Staff name alignment:** Charter uses Hanna Judge, A.J. Hunter, etc.; masthead uses Daisy Delgado, Bob Jones, etc. Decide canonical roster.
5. **`issues/articles/` vs `issues/{year}/articles/`:** PIPELINE_REPAIR_IMPLEMENTATION moved to per-year; verify no scripts still expect global `issues/articles/`.
