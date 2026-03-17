# Repository Architecture Audit

Date: 2026-03-13

Scope: static audit of the repository filesystem, script/config entrypoints, local import graphs, and data-path references. No files were modified other than this report.

High-level findings:

- The repository has one current root product (`src/` + `pipeline/` + Netlify/Vite) plus at least five parallel or legacy products still checked in.
- Architecture drift is mostly caused by duplicated pipelines, checked-in build artifacts, and machine-specific path assumptions.
- Two competing Billboard Hot 100 databases are treated as authoritative by different subsystems.
- No circular dependencies were detected in static local-import scans of the TS/JS trees (`src/`, `pipeline/`, `api/`, `tools/src/`, `retroverse_chart/`, `retroverse_v0/`) or the Python CLI trees (`retroverse-magazine`, `retroverse-1974`).

## PROJECT STRUCTURE

### Major directories and purpose

| Path | Purpose | Status |
|---|---|---|
| `src/` | Current React/Vite frontend for charts, video library, analytics, set builder, tools, and magazine reader routes. | Active |
| `api/` | Thin wrapper over the TypeScript pipeline HTTP server. | Active but redundant |
| `pipeline/` | Current TypeScript media pipeline and HTTP API for VDJ ingest, playlist parsing, metadata extraction, matching, thumbnails, history ingest, and publishing. | Active |
| `scripts/` | Mixed Python/JS/shell utilities: legacy cultural harvest pipeline, Billboard exports, year-master builders, 1974/deck generators, and repair utilities. | Mixed active + legacy |
| `tools/1974/` | Lightweight current 1974 card-context export and rendering workflow used by root `package.json`. | Active |
| `tools/src/` | Separate TypeScript “tools pipeline” scaffold with placeholder stages and its own service layer. | Experimental / redundant |
| `artifacts/` | Current generated pipeline snapshots, matching outputs, decisions, and `video-index.json`. | Generated output |
| `data/` | Local intermediate/processed datasets, including legacy cultural harvest outputs and 1974 working files. | Generated / working data |
| `raw-data/` | Canonical raw ingest inputs currently checked into the repo: chart DBs, VDJ history JSON, IMDb TSVs, screen-culture warehouse files. | Canonical raw data |
| `public/` | Published static assets and frontend-consumable JSON; also contains legacy exported charts bundle under `public/charts/`. | Mixed active + generated legacy |
| `retroverse-magazine/` | Separate Python-heavy magazine project with editorial pipeline, screen-culture warehouse tooling, layout generation, PDF build, and issue assets. | Active but structurally divergent |
| `retroverse-1974/` | Separate illustrated artifact engine with YAML-driven batch pipeline and historical run outputs. | Active niche pipeline / overlaps root 1974 work |
| `retroverse-output/` | Derived multi-year year-end CSV/JSON outputs plus support-data generator. | Canonical derived data |
| `retroverse-support/` | Cultural support CSV consumed by year-master builders. | Canonical support data |
| `retroverse-data/` | Additional database store; contains `source_billboard_hot_100.db` used by magazine context generation. | Competing canonical source |
| `retroverse_chart/` | Standalone Next.js charts app variant with its own build and export script. | Legacy / archived-in-place |
| `retroverse_v0/` | Older standalone Next.js app variant sharing most of the same UI scaffold as `retroverse_chart/`. | Legacy / archived-in-place |
| `runs/` | Historical deck/render run outputs. | Generated historical output |
| `retroverse-1974/runs/` | Historical run outputs for the separate 1974 engine. | Generated historical output |
| `dist/`, `dist-pipeline/`, `.netlify/`, `retroverse_chart/.next/`, `retroverse_v0/.next/` | Checked-in build artifacts. | Generated output that should not be treated as source |
| `retroverse-magazine/archive/` | Archived prototype pipelines, deprecated builders, and unused assets. | Archived experiments |

### Configuration files affecting builds or pipelines

| Path | Effect |
|---|---|
| `package.json` | Root command surface for Vite app, API wrapper, TypeScript pipeline, and current `tools/1974` commands. |
| `netlify.toml` | Netlify build command, publish dir, function bundling, and app/chart/magazine redirects. |
| `pipeline.config.json` | Runtime contract for the root media pipeline; defines source locations, artifact paths, matching thresholds, thumbnail settings, and R2 settings. |
| `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `tsconfig.pipeline.json` | Compiler boundaries; `tsconfig.pipeline.json` emits `dist-pipeline/`. |
| `vite.config.ts` | Root frontend build and `/media` proxy behavior. |
| `tailwind.config.js`, `postcss.config.js`, `eslint.config.js` | Root frontend styling/lint configuration. |
| `tools/package.json`, `tools/pipeline.config.json`, `tools/tsconfig.json` | Separate scaffolded tools pipeline config surface. |
| `retroverse_chart/package.json`, `retroverse_chart/next.config.mjs`, `retroverse_chart/postcss.config.mjs`, `retroverse_chart/tsconfig.json` | Standalone charts app build/export settings. |
| `retroverse_v0/package.json`, `retroverse_v0/next.config.mjs`, `retroverse_v0/postcss.config.mjs`, `retroverse_v0/tsconfig.json` | Older standalone app build settings. |
| `retroverse-magazine/requirements.txt`, `retroverse-magazine/.env`, `retroverse-magazine/data/DATA_SOURCES.yaml` | Magazine runtime dependencies, secrets, and canonical data-path map. |
| `retroverse-1974/requirements.txt`, `retroverse-1974/.env.example`, `retroverse-1974/pipeline/config/*.yaml` | 1974 batch engine dependencies and run definitions. |
| `public/1974/.env` | Alternate env location used by `scripts/generate_at40_week30_rank01.py`. |

## PIPELINE INVENTORY

### 1. Root web app and deploy path

| Pipeline | Entry points | Notes |
|---|---|---|
| Root Vite app | `src/`, `package.json` (`dev`, `build`, `preview:built`), `vite.config.ts`, `netlify.toml` | This is the current trunk UI. |
| API wrapper | `api/server.ts`, `package.json` (`api`) | Only delegates to `pipeline/server.ts`; does not add independent business logic. |
| Netlify billboard function | `netlify/functions/billboard.ts` | Separate read-only API path built from `data/processed/billboard_hot100.csv`; deploy-specific, not the same data path as the root pipeline server. |

### 2. Root TypeScript media pipeline

Active implementation in `pipeline/`:

- Orchestration: `pipeline/index.ts`, `pipeline/server.ts`, `pipeline/config/loadConfig.ts`, `pipeline/types.ts`
- CLI entrypoints: `pipeline/scripts/run.ts`, `pipeline/scripts/run-history-ingest.ts`
- Core stages: `vdjIngest.ts`, `playlistParser.ts`, `mp4Metadata.ts`, `youtubeReconciliation.ts`, `fuzzyMatch.ts`, `thumbnailGenerator.ts`, `r2Publisher.ts`, `parseVdj.ts`, `thumbnailIntent.ts`, `extractCue8.ts`, `matchCharts.ts`, `exportBillboardJson.ts`, `historyIngest.ts`, `retentionScore.ts`, `rewriteIndexFromExisting.ts`, `tierCutoffs.ts`
- History helpers: `pipeline/ingest/historyIngest.ts`, `historyParser.ts`, `historyStats.ts`
- Shared utils: `pipeline/utils/fs.ts`, `logger.ts`, `matchDecisions.ts`, `pathNormalize.ts`, `searchChart.ts`, `thumbnail.ts`
- Extra side script: `pipeline/history/extract_vdj_history.py`
- Supporting prompt helper: `pipeline/scripts/song_premise_generator.py`

### 3. Legacy cultural harvest/data-index pipeline in `scripts/`

This is a separate Python pipeline, distinct from `pipeline/`, that writes `data/processed/` and `data/index/`:

- Orchestrator: `scripts/run_full_pipeline.py`
- Shared helpers: `scripts/pipeline_common.py`
- Harvesters: `harvest_billboard.py`, `harvest_magazines.py`, `harvest_tv_listings.py`, `harvest_radio_logs.py`
- Index builder: `build_cultural_index.py`
- Repair/catalog utilities around the same data family: `recover_issue_dates.py`, `recover_issue_dates_from_url.py`, `merge_magazine_datasets.py`, `generate_magazine_catalog.py`, `generate_yearly_magazine_index.py`, `archive_magazine_harvester.py`, `fix_1978_magazine.py`

### 4. Billboard export and master-data utilities

- Analytics/export: `scripts/compute_billboard_stats.py`, `scripts/export-hot100-summaries.sh`, `scripts/export-album-summaries.sh`, `scripts/rv_year_end_rank.py`
- Master-data builders: `scripts/build_year_master.py`, `scripts/rebuild_year_master.py`, `scripts/init_culture_dataset.py`
- Consumers/outputs: `artifacts/output/billboard/*.json`, `retroverse-output/*.csv`, `retroverse-output/retroverse_year_master_1958_2024.json`, `retroverse-support/*.csv`

### 5. Current lightweight 1974 card pipeline

Wired into root `package.json` via `build:1974`, `render:1974`, and `capsule:1974`:

- `tools/1974/export_weekly_context.ts`
- `tools/1974/render_cards.ts`
- Shared template assets: `tools/1974/card_template.html`, `tools/1974/card.css`

### 6. Legacy 1974 / deck generation experiments in root `scripts/`

- Week-30 extraction/rendering: `generate_retroverse_1974_week30_top5.py`, `generate_at40_week30_rank01.py`, `render-week-30-cards.mjs`, `render-week-30-illustrated.mjs`, `render-1974-playing-card.mjs`
- Single-year / multi-year deck generation: `generate_1974_deck.py`, `compose_1974_deck.py`, `build_multi_year_retroverse_decks.py`

These overlap heavily with both `tools/1974/` and `retroverse-1974/`.

### 7. Separate `retroverse-1974` illustrated artifact engine

- CLI orchestration: `retroverse-1974/pipeline/scripts/rv_run_batch.py`
- Stages: `rv_extract_spine.py`, `rv_build_prompts.py`, `rv_select_ambient.py`, `rv_render_images.py`, `rv_validate_outputs.py`, `rv_runtime.py`
- Run configs: `retroverse-1974/pipeline/config/*.yaml`

### 8. RetroVerse Magazine canonical issue pipeline

Core build path actually present in the tree:

- Orchestrator: `retroverse-magazine/pipeline/run_issue_pipeline.py`
- Context/planning/editorial: `scripts/generate_year_context.py`, `generate_year_narrative.py`, `run_staff_writers.py`, `generate_final_articles.py`, `editorial_supervisor.py`
- Page brief / art direction / QA: `pipeline/generate_issue_page_briefs.py`, `qa_page_briefs.py`, `art_direction_stage.py`, `qa_art_direction.py`, `illustration_prompt_stage.py`, `qa_art_prompts.py`, `qa_layout.py`, `qa_press_check.py`
- Layout/PDF: `scripts/build_issue.py`, `tools/magazine_builder/build_issue.py`, `tools/magazine_builder/render_browser_pdf.mjs`
- Art generation helpers: `generate_art_prompts.py`, `generate_illustrations.py`, `generate_marginals.py`, `find_art_asset.py`, `index_artwork.py`

### 9. RetroVerse Magazine data-warehouse support pipeline

- Screen-culture warehouse and enrichment: `build_screen_culture_warehouse.py`, `build_movies_dataset.py`, `build_television_dataset.py`, `ingest_imdb_datasets.py`, `enrich_tmdb_metadata.py`, `enrich_omdb_metadata.py`, `screen_culture_common.py`
- Audit/reporting utilities: `audit_hot100_db.py`, `audit_billboard200_db.py`, `audit_screen_culture_data.py`, `audit_screen_culture_warehouse.py`, `analyze_chart_dynamics.py`, `update_data_inventory.py`, `print_daily_refresh_instructions.py`

### 10. RetroVerse Magazine experimental page-rebuild workflow

`retroverse-magazine/workflow/page_rebuild/` contains a second page-brief/art-direction/layout QA flow:

- `rebuild_single_page.py`
- `build_mock_page.py`
- `generate_page_brief.py`
- `generate_art_direction.py`
- `generate_page_art_prompt.py`
- `qa_page_brief.py`
- `qa_art_direction.py`
- `qa_art_prompt.py`
- `qa_layout.py`
- `common.py`

This is an experiment/prototype, not a distinct canonical production pipeline.

### 11. Archived standalone charts apps

- `retroverse_chart/scripts/export_billboard_json.py`
- `retroverse_v0/export_billboard_json.py`

Both belong to older Next.js products that duplicate root chart functionality.

### 12. Separate `tools/` scaffold pipeline

This is a second, incomplete TypeScript pipeline concept:

- `tools/src/index.ts`
- `tools/src/config/*`
- `tools/src/pipeline/*`
- `tools/src/parsers/*`
- `tools/src/normalize/*`
- `tools/src/match/*`
- `tools/src/thumbnails/*`
- `tools/src/publish/*`
- `tools/src/services/*`

`tools/README.md` explicitly describes it as a scaffold with placeholder logic.

## DATA SOURCES

### Canonical or effectively canonical data locations

| Path | Role | Current consumers | Notes |
|---|---|---|---|
| `raw-data/billboard-hot-100.db` | Primary Billboard Hot 100 relational source for the root app/pipeline. | `pipeline/server.ts`, `pipeline/modules/exportBillboardJson.ts`, `scripts/compute_billboard_stats.py`, `scripts/export-hot100-summaries.sh`, several 1974 scripts | This is the strongest chart source in the root project. |
| `retroverse-data/databases/source_billboard_hot_100.db` | Alternate Billboard Hot 100 DB used by magazine context generation. | `retroverse-magazine/scripts/generate_year_context.py`, `generate_all_year_contexts.py` | Conflicts with the root source of truth. Pick one canonical DB. |
| `raw-data/billboard-200-albums-charts.db` | Billboard 200 albums DB. | `scripts/export-album-summaries.sh`, magazine `DATA_SOURCES.yaml`, future chart logic | Canonical album source. |
| `raw-data/screen-culture/warehouse/{movies_by_year.json,television_by_year.json,movies_master.json,television_master.json,screen_culture_inventory.json,screen_culture.db}` | Canonical screen/culture warehouse. | Magazine year context, writer assignment, year-range generation, warehouse audits | This is the most coherent canonical dataset in the magazine subsystem. |
| `raw-data/vdj_history_full.json` | Raw VDJ history snapshot. | `pipeline/ingest/historyIngest.ts`, `pipeline/scripts/run-history-ingest.ts` | Repo-local history ingest source. |
| External `~/Library/Application Support/VirtualDJ/database.xml` | Live VDJ library XML. | Root TypeScript pipeline | Required by `pipeline.config.json`; not versioned in repo. |
| External `~/Library/CloudStorage/Dropbox/VIDEO` | Canonical media root assumed by path normalization and media URL derivation. | `pipeline/utils/pathNormalize.ts`, `pipeline/server.ts`, `tools/src/services/routes/pipelineRoutes.ts` | Currently missing on this machine; hardcoded in multiple places. |
| `retroverse-output/retroverse_year_end_1958_2024_all.csv` | Consolidated year-end chart export. | `scripts/build_year_master.py` | Derived, but treated as canonical input by master builders. |
| `retroverse-output/retroverse_year_master_1958_2024.json` | Consolidated year master JSON. | Deck generators, magazine docs, other derived scripts | Canonical derived master dataset. |
| `retroverse-support/retroverse_support_cultural_1958_2024_top10.csv` | Cultural support CSV. | `scripts/rebuild_year_master.py` | Canonical support dataset. |
| `artifacts/output/video-index.json` | Canonical current video index output. | Root frontend via sync to `public/data`, matching tools | Strongest current source for video library UI. |
| `public/data/video-index*.json` | Published frontend copies of the video index. | Root Vite frontend | Derived from `artifacts/output/video-index.json`; should not be primary source. |
| `data/processed/billboard_hot100.csv` | Deploy-time CSV for Netlify function. | `netlify/functions/billboard.ts` | Derived from chart DB; canonical only for the Netlify edge/API path. |
| `data/1974_weekly_context.{md,json}` | Current lightweight 1974 card input. | `tools/1974/*`, some legacy render scripts | Current 1974 root pipeline data. |
| `retroverse-magazine/issues/context/*.json` | Magazine year context artifacts. | Magazine editorial and layout scripts | Build artifact, but treated as canonical factual packet by the magazine subsystem. |
| `retroverse-magazine/issues/{year}/articles/final/` | Final magazine article source. | `retroverse-magazine/scripts/build_issue.py`, PDF builder via shared pipeline helpers | Actual canonical article location, despite stale docs claiming `issues/final/{year}`. |
| `retroverse-magazine/issues/{year}/layout/` | Magazine HTML/layout outputs and production-target data. | Magazine PDF/render steps | Actual canonical layout location, despite stale docs claiming `issues/layout/{year}_*.json`. |

### Canonical data-source conflicts

- Root chart code prefers `raw-data/billboard-hot-100.db`.
- Magazine context generation prefers `retroverse-data/databases/source_billboard_hot_100.db`.
- Magazine `DATA_SOURCES.yaml` claims the canonical Hot 100 path is `/Users/bobhopp/Sites/retroverse/raw-data/billboard-hot-100.db`, but `generate_year_context.py` does not use that file.
- Root media pipeline treats `artifacts/output/video-index.json` as canonical output, while deploy/API paths also depend on `data/processed/billboard_hot100.csv`.

## REDUNDANT COMPONENTS

| Component(s) | Why redundant | Recommendation |
|---|---|---|
| `retroverse_chart/`, `retroverse_v0/`, `public/charts/`, and root `/charts` route in `src/pages/ChartsPage.tsx` | Multiple chart UIs coexist. `retroverse_chart` and `retroverse_v0` share 74 identical relative file paths, including 57 shared `components/ui/*` files and 10 identical public assets. `public/charts/` is a generated export of the standalone charts app. | Keep one chart UI. Archive the others under a clear legacy folder. |
| `pipeline/` vs `tools/src/` | Both describe a media-ingest/match/thumbnail/publish pipeline. `tools/README.md` says the `tools/` version is only a scaffold, but it also duplicates path/media logic and even imports from `src/lib/media/thumbnail.js`. | Keep `pipeline/` as the only media pipeline. Archive or delete `tools/src/`. |
| `pipeline/` vs `dist-pipeline/` | `dist-pipeline/` is compiled output of `pipeline/`, but it is checked in and contains a second copy of the implementation. | Treat `dist-pipeline/` as build artifact only; remove from trunk source ownership. |
| `api/server.ts` vs `pipeline/server.ts` | `api/server.ts` is only a wrapper around `pipeline/server.ts`. | Either collapse into one entrypoint or document the wrapper as purely compatibility glue. |
| `raw-data/billboard-hot-100.db` vs `retroverse-data/databases/source_billboard_hot_100.db` | Two databases act as authoritative Hot 100 sources for different subsystems. | Pick one canonical DB and migrate all consumers. |
| `tools/1974/`, root `scripts/*1974*`, and `retroverse-1974/` | Three separate 1974/deck pipelines overlap: lightweight card renderer, several legacy root experiments, and a dedicated batch engine. | Choose one official 1974/deck pipeline and archive the rest. |
| `retroverse-magazine/scripts/build_issue.py` + `retroverse-magazine/tools/magazine_builder/build_issue.py` + `retroverse-magazine/workflow/page_rebuild/` | There is a canonical HTML builder, a canonical PDF builder, and a second page-rebuild prototype that repeats brief/art/QA stages. | Keep the orchestrated canonical path; move `workflow/page_rebuild/` to `experiments/` or archive. |
| `retroverse-magazine/archive/old_runs/`, `archive/unused_assets/`, `runs/`, `retroverse-1974/runs/`, `dist/`, `.netlify/` | Historical outputs and experiments are mixed with active source. | Move generated/history-only material behind a clear archive boundary. |

### Dead code / archived experiments already visible

- `retroverse-magazine/archive/old_runs/deprecated_build_full_issue.py`
- `retroverse-magazine/archive/old_runs/deprecated_build_magazine.py`
- `retroverse-magazine/archive/old_runs/prototype_pipelines/`
- `retroverse_chart/`
- `retroverse_v0/`
- `public/charts/`
- `runs/`
- `retroverse-1974/runs/`
- `dist/`
- `dist-pipeline/`
- `.netlify/`

## UNUSED SCRIPTS

These scripts have no meaningful in-repo callers or are only mentioned in inventory docs, not by active commands.

| Script | Why it appears unused |
|---|---|
| `scripts/generate-artist-gravity.js` | No `package.json` script, no in-repo callers found, and its output directory `public/data/artist-gravity/` is already populated. |
| `scripts/generate-artist-timelines.js` | Same status as `generate-artist-gravity.js`; depends on already-generated gravity data and is not wired into builds. |
| `scripts/render-1974-playing-card.mjs` | No callers found; overlaps with `tools/1974/render_cards.ts` and larger deck-generation scripts. |
| `retroverse_chart/scripts/export_billboard_json.py` | Only referenced in inventory documentation; belongs to an archived standalone charts app. |
| `retroverse_v0/export_billboard_json.py` | Same as above for the older standalone app. |
| `tools/api-selftest.ts` | Shadowed by `tools/api-selftest.mjs`, which is the file actually invoked by root `package.json`. |
| `tools/faststart_mp4.scpt` | No in-repo references found; shell-based `tools/faststart_mp4.sh` exists separately. |
| `scripts/fix_1978_magazine.py` | No callers found beyond inventory docs; appears to be a one-off repair script. |
| `scripts/recover_issue_dates.py` | No callers found beyond inventory docs; appears to be a one-off repair script. |
| `scripts/recover_issue_dates_from_url.py` | No callers found beyond inventory docs; appears to be a one-off repair script. |
| `scripts/generate_magazine_catalog.py` | No callers found beyond inventory docs; appears to be a standalone catalog utility. |
| `scripts/generate_yearly_magazine_index.py` | No callers found beyond inventory docs; appears to be a standalone catalog utility. |

## LIKELY FAILURE POINTS

1. Root media pipeline is not reproducible from the repository alone.
   - `pipeline.config.json` points at missing repo-local inputs: `raw-data/charts/billboard.json`, `raw-data/charts/at40.json`, `raw-data/playlists/`, `raw-data/videos/`, and `raw-data/youtube-reference.json`.
   - The same config expects external `database.xml` and Dropbox media roots.
   - `/Users/bobhopp/Library/CloudStorage/Dropbox/VIDEO` is currently missing, but the path is hardcoded in `pipeline/utils/pathNormalize.ts`, `pipeline/server.ts`, and `tools/src/services/routes/pipelineRoutes.ts`.

2. Root API startup inherits config failure immediately.
   - `pipeline/index.ts` loads `pipeline.config.json` at import time.
   - `pipeline/server.ts` imports `runStep` from `pipeline/index.ts`.
   - `api/server.ts` imports `pipeline/server.ts`.
   - Result: `npm run api`, `npm run pipeline:run`, and `npm run pipeline:serve` all fail early when config paths are invalid.

3. Machine-specific absolute paths are widespread.
   - Examples: `scripts/rebuild_year_master.py`, `scripts/init_culture_dataset.py`, `retroverse-output/build_retroverse_support_1958_2024.py`, `retroverse-magazine/scripts/generate_year_range.py`, `run_staff_writers.py`, `ingest_imdb_datasets.py`, `update_data_inventory.py`, `pipeline/utils/pathNormalize.ts`.
   - This prevents portability, CI reproducibility, and contributor onboarding.

4. Several scripts are cwd-sensitive instead of file-relative.
   - `scripts/build_year_master.py` uses `../retroverse-output` and `../retroverse-support` relative to current working directory; `python3 scripts/build_year_master.py` from repo root resolves outside the repo.
   - `retroverse-magazine/scripts/generate_all_year_contexts.py` uses `../../retroverse-data/...` and runs `python3 generate_year_context.py` without setting `cwd`.
   - `tools/1974/export_weekly_context.ts`, `tools/1974/render_cards.ts`, `scripts/render-week-30-cards.mjs`, `scripts/render-week-30-illustrated.mjs`, and `scripts/render-1974-playing-card.mjs` all assume `process.cwd()` is the repo root.

5. Magazine documentation and filesystem reality diverge.
   - `retroverse-magazine/docs/CANONICAL_PIPELINE.md` still refers to `issues/final/{year}/` and `issues/layout/{year}_production_targets.json`.
   - Actual code and files use `issues/{year}/articles/final/` and `issues/{year}/layout/`.
   - This is a real operational risk because scripts, docs, and human workflow do not agree on canonical paths.

6. Magazine year-context generation has uneven data coverage.
   - `retroverse-magazine/scripts/generate_year_context.py` expects `albums_{year}_sample.csv`; only `albums_1978_sample.csv` exists.
   - Root `cultural_events_*.json` files exist only for 1976-1981, but contexts are generated for 1958-2025.
   - Most years therefore have partial culture/album enrichment even though context files exist.

7. Legacy build artifacts can be mistaken for source of truth.
   - `dist-pipeline/` can drift from `pipeline/`.
   - `public/charts/` can be mistaken for the active charts frontend even though the root app already serves `/charts`.
   - `.netlify/`, `.next/`, and `dist/` are checked in alongside source.

8. Some scripts require prior generated artifacts rather than source.
   - `tools/api-selftest.mjs` imports `../dist-pipeline/server.js`, so it depends on a prior pipeline build instead of current source.
   - `scripts/generate-artist-timelines.js` depends on pre-existing `public/data/artist-gravity/*.json`.

9. Several pipelines depend on external services or local tools without one canonical environment contract.
   - Harvesters in `scripts/*.py` and `retroverse-output/build_retroverse_support_1958_2024.py` require network access.
   - 1974 and magazine image/PDF stages need `OPENAI_API_KEY`, Playwright/Chromium, and in some cases WeasyPrint system libraries.
   - Thumbnail generation requires `ffmpeg`.

10. One script already points at a missing local file right now.
   - `scripts/init_culture_dataset.py` expects `~/Downloads/retroverse_support_cultural_1958_2024_top10.csv`, which is currently absent.

11. Circular dependency risk is low at the code-import level.
   - Static local-import scans found no circular dependencies in the current TS/JS or Python entrypoint trees.
   - Structural instability is coming from duplicate pipelines and path/config drift, not module cycles.

## ARCHITECTURE RECOMMENDATION

Stabilize the repository around one explicit trunk and treat everything else as either a workspace package or an archive.

1. Declare the supported trunk products.
   - Keep the root Vite app as the primary web UI.
   - Keep `pipeline/` as the only supported media ingest/index pipeline.
   - Keep `retroverse-magazine/` as the only supported magazine project.
   - Pick exactly one supported 1974/deck pipeline: either `tools/1974/` or `retroverse-1974/`.

2. Move legacy products behind an archive boundary.
   - Archive `retroverse_chart/`, `retroverse_v0/`, `public/charts/`, `tools/src/`, root one-off 1974 experiment scripts, and deprecated magazine builders.
   - Keep them for reference only under `archive/legacy-products/` or a similarly named directory.

3. Establish one canonical data map at the repo root.
   - Create one authoritative source manifest for all raw, derived, and published datasets.
   - Pick one Billboard Hot 100 DB path and migrate every consumer to it.
   - Define a clear split such as `data/raw/`, `data/derived/`, and `data/published/`.

4. Remove hardcoded machine paths from source.
   - Centralize path resolution in one config layer per active project.
   - Replace `/Users/bobhopp/...` and `Path.home()/Sites/retroverse` with env/config values.
   - Stop hardcoding the Dropbox VIDEO root in source code.

5. Collapse duplicate pipeline logic.
   - Decommission `tools/src/` in favor of `pipeline/`.
   - Merge the duplicate chart export scripts into one maintained exporter.
   - Merge 1974/deck generation into one parameterized pipeline rather than keeping `tools/1974`, root experiment scripts, and `retroverse-1974` all live at once.

6. Separate source from generated artifacts.
   - Treat `dist/`, `dist-pipeline/`, `.next/`, `.netlify/`, `public/charts/`, `runs/`, PDFs, and render outputs as generated.
   - Move long-lived historical outputs to `artifacts/` or `archive/`.
   - Reduce the chance that contributors edit compiled/exported material by mistake.

7. Replace ad hoc script discovery with explicit entrypoints.
   - Every supported workflow should be callable from a documented root command surface.
   - Manual-only or one-off repair scripts should either be archived or labeled `manual/one-off`.
   - A workspace layout such as `apps/`, `packages/`, `projects/`, and `archive/` would make ownership much clearer.

8. Repair documentation so it matches the tree.
   - Replace the root `README.md` Vite template with an actual repo map.
   - Update magazine docs to match `issues/{year}/articles/final/` and `issues/{year}/layout/`.
   - Document which pipelines are active, deprecated, experimental, or archived.

9. Add structural guardrails.
   - Add CI checks for missing configured paths, duplicate canonical data definitions, and stale generated artifacts.
   - Add a path/schema validator that fails fast but reports all missing prerequisites in one place.
   - Add a lightweight repository manifest describing active products, archive zones, and canonical data sources.

### Recommended target trunk layout

One workable end state:

- `apps/web/` for the current Vite frontend and deploy config
- `packages/media-pipeline/` for `pipeline/`
- `projects/magazine/` for `retroverse-magazine/`
- `projects/cards/` for the single chosen 1974/deck pipeline
- `data/raw/`, `data/derived/`, `data/published/`
- `archive/` for `retroverse_chart/`, `retroverse_v0/`, historical runs, deprecated builders, and experimental prototypes

### Near-term stabilization order

1. Fix `pipeline.config.json` and remove hardcoded media roots from code.
2. Choose one canonical Billboard Hot 100 database and migrate all consumers.
3. Pick the official charts UI and official 1974/deck pipeline; archive the rest.
4. Move generated artifacts and legacy apps behind an archive boundary.
5. Replace the root README and add a repo-level source-of-truth manifest for products, configs, and data paths.
