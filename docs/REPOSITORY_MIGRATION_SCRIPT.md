# Repository Migration Script

This document is a planning simulation only. It does not execute any moves.

## Scope

The target stabilized layout is:

- `/data`
- `/pipelines`
- `/apps`
- `/archive`
- `/docs`

This migration preserves the current trunk while separating active systems from experiments and generated clutter.

## Assumptions

- The active trunk remains:
  - the root web app
  - the TypeScript media-index pipeline
  - the magazine product
  - the `tools/1974` cards pipeline
  - the support-data builders
- `raw-data/billboard-hot-100.db` remains the canonical Billboard Hot 100 source during transition.
- The long-term canonical location becomes `data/raw/charts/billboard-hot-100.db`.
- A temporary compatibility alias at `raw-data/billboard-hot-100.db` should remain until all active consumers are updated.
- Repo-control files such as root `package.json`, root `README.md`, root `.gitignore`, and future workspace config are intentionally left at the repo root in this first migration pass.
- Local caches and generated directories such as `node_modules/`, `.next/`, `.venv/`, `__pycache__/`, `.DS_Store`, and SQLite sidecars should not be treated as canonical source during the move.

## Exact Move Map

### Into `/apps`

#### `/apps/web`

- `src/`
- `api/`
- `netlify/`
- `index.html`
- `public/`, except `public/charts/`
- `tools/autoUpdate.ts`

#### `/apps/magazine`

- `retroverse-magazine/`

### Into `/pipelines`

#### `/pipelines/media-index`

- `pipeline/`
- `scripts/sync-index.sh`
- `scripts/split-video-index-by-decade.mjs`
- `tools/analyze_playcounts.py`
- `tools/api-selftest.mjs`
- `tools/api-selftest.ts`

#### `/pipelines/cards-1974`

- `tools/1974/`

#### `/pipelines/support-data`

- `scripts/archive_magazine_harvester.py`
- `scripts/build_cultural_index.py`
- `scripts/build_year_master.py`
- `scripts/compute_billboard_stats.py`
- `scripts/export-album-summaries.sh`
- `scripts/export-hot100-summaries.sh`
- `scripts/generate_magazine_catalog.py`
- `scripts/generate_yearly_magazine_index.py`
- `scripts/harvest_billboard.py`
- `scripts/harvest_magazines.py`
- `scripts/harvest_radio_logs.py`
- `scripts/harvest_tv_listings.py`
- `scripts/init_culture_dataset.py`
- `scripts/merge_magazine_datasets.py`
- `scripts/pipeline_common.py`
- `scripts/rebuild_year_master.py`
- `scripts/recover_issue_dates.py`
- `scripts/recover_issue_dates_from_url.py`
- `scripts/run_full_pipeline.py`
- `scripts/rv_year_end_rank.py`
- `retroverse-output/build_retroverse_support_1958_2024.py`
- `retroverse-output/README.md`
- `retroverse-output/requirements.txt`

### Into `/data`

#### Canonical raw data

- `raw-data/billboard-hot-100.db` -> `data/raw/charts/billboard-hot-100.db`
- `raw-data/billboard-200-albums-charts.db` -> `data/raw/charts/billboard-200-albums-charts.db`
- `raw-data/vdj_history_full.json` -> `data/raw/media/vdj_history_full.json`
- `raw-data/imdb/` -> `data/raw/imdb/`
- `raw-data/screen-culture/` -> `data/raw/screen-culture/`

#### Existing in-repo derived data to normalize inside `/data`

- `data/1974_card_render_report.json` -> `data/derived/cards/1974/1974_card_render_report.json`
- `data/1974_master.json` -> `data/derived/cards/1974/1974_master.json`
- `data/1974_weekly_context.json` -> `data/derived/cards/1974/1974_weekly_context.json`
- `data/1974_weekly_context.md` -> `data/derived/cards/1974/1974_weekly_context.md`
- `data/1974_weekly_context.parse_report.json` -> `data/derived/cards/1974/1974_weekly_context.parse_report.json`
- `data/retro-verse-1974-weekly-data.md` -> `data/derived/cards/1974/retro-verse-1974-weekly-data.md`
- `data/index/` -> `data/derived/culture/index/`
- `data/processed/` -> `data/derived/culture/processed/`

#### Media-index outputs

- `artifacts/canonical/` -> `data/derived/media-index/canonical/`
- `artifacts/decisions/` -> `data/derived/media-index/decisions/`
- `artifacts/matching/` -> `data/derived/media-index/matching/`
- `artifacts/output/` -> `data/derived/media-index/output/`
- `r2_inventory.json` -> `data/derived/media-index/inventory/r2_inventory.json`
- `r2_thumbs.json` -> `data/derived/media-index/inventory/r2_thumbs.json`

#### Support-data outputs

- `retroverse-output/retroverse_year_end_YYYY.csv` -> `data/derived/year-masters/`
- `retroverse-output/retroverse_year_end_YYYY_top40.csv` -> `data/derived/year-masters/`
- `retroverse-output/retroverse_year_end_1958_2024_all.csv` -> `data/derived/year-masters/retroverse_year_end_1958_2024_all.csv`
- `retroverse-output/retroverse_year_master_1958_2024.json` -> `data/derived/year-masters/retroverse_year_master_1958_2024.json`
- `retroverse-output/master_1978_1981.json` -> `data/derived/year-masters/legacy/master_1978_1981.json`
- `retroverse-output/retroverse_support_cultural_1958_2024_top10.log` -> `data/derived/year-masters/logs/retroverse_support_cultural_1958_2024_top10.log`
- `retroverse-support/retroverse_support_cultural_1958_2024_top10.csv` -> `data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv`

#### Top-level support files

- `albums_1978_sample.csv` -> `data/support/magazine/albums/albums_1978_sample.csv`
- `cultural_events_1976.json` -> `data/support/magazine/cultural-events/cultural_events_1976.json`
- `cultural_events_1977.json` -> `data/support/magazine/cultural-events/cultural_events_1977.json`
- `cultural_events_1978.json` -> `data/support/magazine/cultural-events/cultural_events_1978.json`
- `cultural_events_1979.json` -> `data/support/magazine/cultural-events/cultural_events_1979.json`
- `cultural_events_1980.json` -> `data/support/magazine/cultural-events/cultural_events_1980.json`
- `cultural_events_1981.json` -> `data/support/magazine/cultural-events/cultural_events_1981.json`
- `year_end_top_40_1976.json` -> `data/support/magazine/year-end-top40/year_end_top_40_1976.json`
- `year_end_top_40_1977.json` -> `data/support/magazine/year-end-top40/year_end_top_40_1977.json`
- `year_end_top_40_1978.json` -> `data/support/magazine/year-end-top40/year_end_top_40_1978.json`
- `year_end_top_40_1979.json` -> `data/support/magazine/year-end-top40/year_end_top_40_1979.json`
- `year_end_top_40_1980.json` -> `data/support/magazine/year-end-top40/year_end_top_40_1980.json`
- `year_end_top_40_1981.json` -> `data/support/magazine/year-end-top40/year_end_top_40_1981.json`
- `MAGAZINE_ARCHIVE_HARVEST.csv` -> `data/support/magazine/archive/MAGAZINE_ARCHIVE_HARVEST.csv`
- `MAGAZINE_ARCHIVE_HARVEST.csv.bak` -> `data/support/magazine/archive/MAGAZINE_ARCHIVE_HARVEST.csv.bak`
- `MAGAZINE_CULTURAL_SIGNALS.json` -> `data/support/magazine/archive/MAGAZINE_CULTURAL_SIGNALS.json`
- `MAGAZINE_ISSUE_MANIFEST.csv` -> `data/support/magazine/archive/MAGAZINE_ISSUE_MANIFEST.csv`
- `MAGAZINE_ISSUE_MANIFEST_DATED.csv` -> `data/support/magazine/archive/MAGAZINE_ISSUE_MANIFEST_DATED.csv`
- `MAGAZINE_MASTER_ARCHIVE.csv` -> `data/support/magazine/archive/MAGAZINE_MASTER_ARCHIVE.csv`
- `MAGAZINE_MASTER_INDEX.csv` -> `data/support/magazine/archive/MAGAZINE_MASTER_INDEX.csv`
- `MAGAZINE_METADATA_SAMPLE.json` -> `data/support/magazine/archive/MAGAZINE_METADATA_SAMPLE.json`
- `MAGAZINE_YEAR_INDEX.csv` -> `data/support/magazine/archive/MAGAZINE_YEAR_INDEX.csv`

### Into `/archive`

#### `/archive/apps`

- `retroverse_chart/`
- `retroverse_v0/`
- `public/charts/`

#### `/archive/pipelines`

- `retroverse-1974/`
- `retroverse-data/`
- remaining root `scripts/` after trunk support-data and media-index moves
- remaining `tools/` after trunk cards/media-index/web-tool moves

Representative archive-bound files left behind after the trunk moves:

- `scripts/build_multi_year_retroverse_decks.py`
- `scripts/compose_1974_deck.py`
- `scripts/dsm-web-stack-forensics.sh`
- `scripts/fix_1978_magazine.py`
- `scripts/generate-artist-gravity.js`
- `scripts/generate-artist-timelines.js`
- `scripts/generate_1974_deck.py`
- `scripts/generate_at40_week30_rank01.py`
- `scripts/generate_retroverse_1974_week30_top5.py`
- `scripts/render-1974-playing-card.mjs`
- `scripts/render-week-30-cards.mjs`
- `scripts/render-week-30-illustrated.mjs`
- `tools/README.md`
- `tools/package.json`
- `tools/pipeline.config.json`
- `tools/tsconfig.json`
- `tools/tierMapping.test.ts`
- `tools/src/`
- `tools/media-normalization/`
- `tools/sample-data/`
- `tools/faststart_mp4.scpt`
- `tools/faststart_mp4.sh`

#### `/archive/artifacts`

- `dist/`
- `dist-pipeline/`
- `runs/`
- `logs/`
- `retroverse-output/decks/`
- `history_collect.py`
- `dsm_webstack_repair.sh`
- stray root files `and`, `minimal`, `readable`, `remains`

#### `/archive/docs`

- `Journal/`

### Into `/docs`

- `DATA_INVENTORY.md`
- `DSM_WEBSTACK_RECOVERY.md`
- `RetroVerse Wheel Specification.md`

## Proposed Migration Script

This is an illustrative script. Do not run it as-is until the path-update items in the next section are prepared.

```bash
# create target top-level directories
mkdir -p apps/web/tools
mkdir -p pipelines
mkdir -p pipelines/support-data/scripts pipelines/support-data
mkdir -p data/raw data/raw/charts data/raw/media
mkdir -p data/derived/cards/1974
mkdir -p data/derived/culture
mkdir -p data/derived/media-index/inventory
mkdir -p data/derived/year-masters/legacy data/derived/year-masters/logs
mkdir -p data/support/retroverse
mkdir -p data/support/magazine/albums
mkdir -p data/support/magazine/cultural-events
mkdir -p data/support/magazine/year-end-top40
mkdir -p data/support/magazine/archive
mkdir -p archive/apps archive/pipelines archive/artifacts archive/docs
mkdir -p docs

# apps
git mv src apps/web/src
git mv api apps/web/api
git mv netlify apps/web/netlify
git mv index.html apps/web/index.html
git mv tools/autoUpdate.ts apps/web/tools/autoUpdate.ts

# archive the legacy static charts app before moving the rest of public/
git mv public/charts archive/apps/public-charts
git mv public apps/web/public

git mv retroverse-magazine apps/magazine

# pipelines: media-index
git mv pipeline pipelines/media-index
mkdir -p pipelines/media-index/scripts pipelines/media-index/tools
git mv scripts/sync-index.sh pipelines/media-index/scripts/sync-index.sh
git mv scripts/split-video-index-by-decade.mjs pipelines/media-index/scripts/split-video-index-by-decade.mjs
git mv tools/analyze_playcounts.py pipelines/media-index/tools/analyze_playcounts.py
git mv tools/api-selftest.mjs pipelines/media-index/tools/api-selftest.mjs
git mv tools/api-selftest.ts pipelines/media-index/tools/api-selftest.ts

# pipelines: cards
git mv tools/1974 pipelines/cards-1974

# pipelines: support-data
git mv scripts/archive_magazine_harvester.py pipelines/support-data/scripts/archive_magazine_harvester.py
git mv scripts/build_cultural_index.py pipelines/support-data/scripts/build_cultural_index.py
git mv scripts/build_year_master.py pipelines/support-data/scripts/build_year_master.py
git mv scripts/compute_billboard_stats.py pipelines/support-data/scripts/compute_billboard_stats.py
git mv scripts/export-album-summaries.sh pipelines/support-data/scripts/export-album-summaries.sh
git mv scripts/export-hot100-summaries.sh pipelines/support-data/scripts/export-hot100-summaries.sh
git mv scripts/generate_magazine_catalog.py pipelines/support-data/scripts/generate_magazine_catalog.py
git mv scripts/generate_yearly_magazine_index.py pipelines/support-data/scripts/generate_yearly_magazine_index.py
git mv scripts/harvest_billboard.py pipelines/support-data/scripts/harvest_billboard.py
git mv scripts/harvest_magazines.py pipelines/support-data/scripts/harvest_magazines.py
git mv scripts/harvest_radio_logs.py pipelines/support-data/scripts/harvest_radio_logs.py
git mv scripts/harvest_tv_listings.py pipelines/support-data/scripts/harvest_tv_listings.py
git mv scripts/init_culture_dataset.py pipelines/support-data/scripts/init_culture_dataset.py
git mv scripts/merge_magazine_datasets.py pipelines/support-data/scripts/merge_magazine_datasets.py
git mv scripts/pipeline_common.py pipelines/support-data/scripts/pipeline_common.py
git mv scripts/rebuild_year_master.py pipelines/support-data/scripts/rebuild_year_master.py
git mv scripts/recover_issue_dates.py pipelines/support-data/scripts/recover_issue_dates.py
git mv scripts/recover_issue_dates_from_url.py pipelines/support-data/scripts/recover_issue_dates_from_url.py
git mv scripts/run_full_pipeline.py pipelines/support-data/scripts/run_full_pipeline.py
git mv scripts/rv_year_end_rank.py pipelines/support-data/scripts/rv_year_end_rank.py
git mv retroverse-output/build_retroverse_support_1958_2024.py pipelines/support-data/build_retroverse_support_1958_2024.py
git mv retroverse-output/README.md pipelines/support-data/README.md
git mv retroverse-output/requirements.txt pipelines/support-data/requirements.txt

# data: canonical raw data
git mv raw-data/billboard-hot-100.db data/raw/charts/billboard-hot-100.db
git mv raw-data/billboard-200-albums-charts.db data/raw/charts/billboard-200-albums-charts.db
git mv raw-data/vdj_history_full.json data/raw/media/vdj_history_full.json
git mv raw-data/imdb data/raw/imdb
git mv raw-data/screen-culture data/raw/screen-culture

# keep a temporary compatibility alias after the move
# raw-data/billboard-hot-100.db -> data/raw/charts/billboard-hot-100.db
# do not retire the compatibility path until all active consumers are updated

# data: normalize current in-repo data
git mv data/1974_card_render_report.json data/derived/cards/1974/1974_card_render_report.json
git mv data/1974_master.json data/derived/cards/1974/1974_master.json
git mv data/1974_weekly_context.json data/derived/cards/1974/1974_weekly_context.json
git mv data/1974_weekly_context.md data/derived/cards/1974/1974_weekly_context.md
git mv data/1974_weekly_context.parse_report.json data/derived/cards/1974/1974_weekly_context.parse_report.json
git mv data/retro-verse-1974-weekly-data.md data/derived/cards/1974/retro-verse-1974-weekly-data.md
git mv data/index data/derived/culture/index
git mv data/processed data/derived/culture/processed

# data: media-index artifacts
git mv artifacts/canonical data/derived/media-index/canonical
git mv artifacts/decisions data/derived/media-index/decisions
git mv artifacts/matching data/derived/media-index/matching
git mv artifacts/output data/derived/media-index/output
git mv r2_inventory.json data/derived/media-index/inventory/r2_inventory.json
git mv r2_thumbs.json data/derived/media-index/inventory/r2_thumbs.json

# data: support-data outputs
git mv retroverse-output/retroverse_year_end_[0-9][0-9][0-9][0-9].csv data/derived/year-masters/
git mv retroverse-output/retroverse_year_end_[0-9][0-9][0-9][0-9]_top40.csv data/derived/year-masters/
git mv retroverse-output/retroverse_year_end_1958_2024_all.csv data/derived/year-masters/retroverse_year_end_1958_2024_all.csv
git mv retroverse-output/retroverse_year_master_1958_2024.json data/derived/year-masters/retroverse_year_master_1958_2024.json
git mv retroverse-output/master_1978_1981.json data/derived/year-masters/legacy/master_1978_1981.json
git mv retroverse-output/retroverse_support_cultural_1958_2024_top10.log data/derived/year-masters/logs/retroverse_support_cultural_1958_2024_top10.log
git mv retroverse-support/retroverse_support_cultural_1958_2024_top10.csv data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv

# data: top-level support files
git mv albums_1978_sample.csv data/support/magazine/albums/albums_1978_sample.csv
git mv cultural_events_{1976,1977,1978,1979,1980,1981}.json data/support/magazine/cultural-events/
git mv year_end_top_40_{1976,1977,1978,1979,1980,1981}.json data/support/magazine/year-end-top40/
git mv MAGAZINE_ARCHIVE_HARVEST.csv data/support/magazine/archive/MAGAZINE_ARCHIVE_HARVEST.csv
git mv MAGAZINE_ARCHIVE_HARVEST.csv.bak data/support/magazine/archive/MAGAZINE_ARCHIVE_HARVEST.csv.bak
git mv MAGAZINE_CULTURAL_SIGNALS.json data/support/magazine/archive/MAGAZINE_CULTURAL_SIGNALS.json
git mv MAGAZINE_ISSUE_MANIFEST.csv data/support/magazine/archive/MAGAZINE_ISSUE_MANIFEST.csv
git mv MAGAZINE_ISSUE_MANIFEST_DATED.csv data/support/magazine/archive/MAGAZINE_ISSUE_MANIFEST_DATED.csv
git mv MAGAZINE_MASTER_ARCHIVE.csv data/support/magazine/archive/MAGAZINE_MASTER_ARCHIVE.csv
git mv MAGAZINE_MASTER_INDEX.csv data/support/magazine/archive/MAGAZINE_MASTER_INDEX.csv
git mv MAGAZINE_METADATA_SAMPLE.json data/support/magazine/archive/MAGAZINE_METADATA_SAMPLE.json
git mv MAGAZINE_YEAR_INDEX.csv data/support/magazine/archive/MAGAZINE_YEAR_INDEX.csv

# docs
git mv DATA_INVENTORY.md docs/DATA_INVENTORY.md
git mv DSM_WEBSTACK_RECOVERY.md docs/DSM_WEBSTACK_RECOVERY.md
git mv "RetroVerse Wheel Specification.md" "docs/RetroVerse Wheel Specification.md"

# archive: legacy apps and pipelines
git mv retroverse_chart archive/apps/retroverse_chart
git mv retroverse_v0 archive/apps/retroverse_v0
git mv retroverse-1974 archive/pipelines/retroverse-1974
git mv retroverse-data archive/pipelines/retroverse-data

# archive: move the remainder of scripts/ and tools/ after trunk extractions
git mv scripts archive/pipelines/legacy-root-scripts
git mv tools archive/pipelines/tools-legacy

# archive: generated and historical material
git mv dist archive/artifacts/dist
git mv dist-pipeline archive/artifacts/dist-pipeline
git mv runs archive/artifacts/runs
git mv logs archive/artifacts/logs
git mv retroverse-output/decks archive/artifacts/retroverse-output-decks
git mv history_collect.py archive/artifacts/history_collect.py
git mv dsm_webstack_repair.sh archive/artifacts/dsm_webstack_repair.sh
git mv and archive/artifacts/and
git mv minimal archive/artifacts/minimal
git mv readable archive/artifacts/readable
git mv remains archive/artifacts/remains
git mv Journal archive/docs/Journal
```

## Canonical Billboard Dataset Handling

The migration should treat the Billboard database in two stages:

1. Update active consumers to resolve the Billboard DB through config or a data-source mapping layer.
2. Move `raw-data/billboard-hot-100.db` to `data/raw/charts/billboard-hot-100.db`.
3. Keep `raw-data/billboard-hot-100.db` as a temporary compatibility alias until all active paths are rewritten.

Active consumers that must follow the canonical DB:

- `pipeline.config.json`
- `pipelines/support-data/scripts/compute_billboard_stats.py`
- `pipelines/support-data/scripts/export-hot100-summaries.sh`
- `pipelines/support-data/scripts/harvest_billboard.py`
- `pipelines/support-data/scripts/rv_year_end_rank.py`
- `apps/magazine/scripts/generate_year_context.py`
- `apps/magazine/scripts/generate_all_year_contexts.py`
- `apps/magazine/data/DATA_SOURCES.yaml`

## Scripts And Configs That Need Path Updates After The Move

### Repo control plane

- `package.json`
  - every script that currently references `src/`, `api/`, `pipeline/`, `tools/1974/`, `scripts/`, or `tools/`
- `vite.config.ts`
- `tsconfig.app.json`
- `tsconfig.node.json`
- `tsconfig.pipeline.json`
- `netlify.toml`
- `pipeline.config.json`

### Web app and API

- `api/server.ts`
  - `../pipeline/server.js` must become the new media-index path
- `netlify/functions/billboard.ts`
  - currently expects `data/processed/billboard_hot100.csv`
- any import or asset references inside `src/` that assume root-relative `public/` or `api/`

### Media-index pipeline

- `pipeline/config/loadConfig.ts`
- `pipeline/index.ts`
- `pipeline/server.ts`
- `pipeline/modules/exportBillboardJson.ts`
- `pipeline/modules/r2Publisher.ts`
- `scripts/sync-index.sh`
- `scripts/split-video-index-by-decade.mjs`
- `tools/api-selftest.mjs`

### Support-data pipeline

- `scripts/build_year_master.py`
- `scripts/rebuild_year_master.py`
- `scripts/compute_billboard_stats.py`
- `scripts/export-album-summaries.sh`
- `scripts/export-hot100-summaries.sh`
- `scripts/harvest_billboard.py`
- `scripts/run_full_pipeline.py`
- `scripts/rv_year_end_rank.py`
- `retroverse-output/build_retroverse_support_1958_2024.py`

These currently assume root-relative `raw-data/`, `retroverse-output/`, or `scripts/`.

### Magazine product

- `retroverse-magazine/scripts/generate_year_context.py`
  - currently points at `retroverse-data/databases/source_billboard_hot_100.db`
- `retroverse-magazine/scripts/generate_all_year_contexts.py`
  - same duplicate DB path
- `retroverse-magazine/scripts/screen_culture_common.py`
  - currently points at `retroverse-output/retroverse_year_master_1958_2024.json`
- `retroverse-magazine/scripts/update_data_inventory.py`
- `retroverse-magazine/data/DATA_SOURCES.yaml`

### Cards pipeline

- `tools/1974/export_weekly_context.ts`
- `tools/1974/render_cards.ts`

These should be updated to read the normalized `data/derived/cards/1974/` paths rather than the current flat `data/` layout.

### Archive-only consumers

These do not need to block trunk stabilization, but they will break if reactivated without path rewrites:

- `scripts/generate_1974_deck.py`
- `scripts/build_multi_year_retroverse_decks.py`
- `scripts/compose_1974_deck.py`
- `scripts/generate_at40_week30_rank01.py`
- `scripts/generate_retroverse_1974_week30_top5.py`
- `scripts/render-1974-playing-card.mjs`
- `scripts/render-week-30-cards.mjs`
- `scripts/render-week-30-illustrated.mjs`
- `retroverse_v0/export_billboard_json.py`
- legacy references embedded in `retroverse_chart/`, `retroverse_v0/`, and `retroverse-1974/`

## Notes On Non-Source Directories

The migration script intentionally avoids trying to preserve local dependency caches and generated build state as trunk source:

- `node_modules/`
- `.next/`
- `.venv/`
- `__pycache__/`
- `.netlify/`
- SQLite sidecars such as `raw-data/billboard-hot-100.db-shm` and `raw-data/billboard-hot-100.db-wal`

These should be recreated or discarded after the tree is stabilized.

## Recommended Execution Order

1. Update active path consumers to read the canonical Billboard DB via config.
2. Move active app and pipeline source directories into `/apps` and `/pipelines`.
3. Normalize the data layer into `/data`.
4. Move legacy apps, pipelines, and generated history into `/archive`.
5. Move top-level documentation into `/docs`.
6. Add a new root workspace manifest and updated build/deploy config in a follow-up change.
