# Lineage Automation Report

## Clustering Changes

- `pipelines/support-data/scripts/generate_data_lineage.py` now emits a top-to-bottom Graphviz layout with `rankdir=TB`.
- The DOT graph now uses the requested four clusters:
  - `cluster_raw` labeled `Raw Datasets`
  - `cluster_pipelines` labeled `Pipelines`
  - `cluster_derived` labeled `Derived Datasets`
  - `cluster_apps` labeled `Applications`
- Nodes use a rounded box style by default, with light cluster background colors to improve readability.
- Systems that are neither `pipelines/*` nor `apps/*` remain outside the four primary clusters so the requested layer structure stays explicit.

## Pipeline Hooks Added

- Added shared Python hook helper: `pipelines/support-data/scripts/lineage_hook.py`
- Added shared Node hook helper: `pipelines/lib/lineage-hook.js`
- Added automatic lineage regeneration to these support-data Python entrypoints:
  - `archive_magazine_harvester.py`
  - `build_cultural_index.py`
  - `build_year_master.py`
  - `compute_billboard_stats.py`
  - `generate_magazine_catalog.py`
  - `generate_yearly_magazine_index.py`
  - `harvest_billboard.py`
  - `harvest_magazines.py`
  - `harvest_radio_logs.py`
  - `harvest_tv_listings.py`
  - `init_culture_dataset.py`
  - `merge_magazine_datasets.py`
  - `rebuild_year_master.py`
  - `recover_issue_dates.py`
  - `recover_issue_dates_from_url.py`
  - `run_full_pipeline.py`
  - `rv_year_end_rank.py`
- Added automatic lineage regeneration to these shell entrypoints:
  - `pipelines/support-data/scripts/export-album-summaries.sh`
  - `pipelines/support-data/scripts/export-hot100-summaries.sh`
  - `pipelines/media-index/scripts/sync-index.sh`
- Added automatic lineage regeneration to these JS/TS entrypoints:
  - `pipelines/media-index/scripts/split-video-index-by-decade.mjs`
  - `pipelines/cards-1974/export_weekly_context.ts`
  - `pipelines/cards-1974/render_cards.ts`
- Utility scripts were intentionally not hooked:
  - `pipelines/support-data/scripts/generate_data_lineage.py`
  - `pipelines/support-data/scripts/validate_registry.py`
  - `pipelines/support-data/scripts/pipeline_common.py`

## Graphviz Detection Behavior

- After writing `docs/DATA_LINEAGE_GRAPH.dot`, the generator now attempts to render `docs/DATA_LINEAGE_GRAPH.svg` with `dot -Tsvg`.
- If Graphviz is missing, the script prints installation guidance and leaves the DOT file as the canonical lineage artifact.
- In nested orchestrations, lineage generation is suppressed inside child steps with `RETROVERSE_SKIP_LINEAGE=1`, then regenerated once at the outer entrypoint.

## Verification Results

- `python3 -m py_compile` passed for all modified Python entrypoints and the updated lineage generator.
- `bash -n` passed for the modified shell scripts.
- `node --check` passed for `pipelines/lib/lineage-hook.js` and `pipelines/media-index/scripts/split-video-index-by-decade.mjs`.
- `npx tsc --noEmit --pretty false --skipLibCheck --moduleResolution node16 --module node16 --target ES2022 --types node pipelines/cards-1974/export_weekly_context.ts pipelines/cards-1974/render_cards.ts` passed.
- `python3 pipelines/support-data/scripts/generate_data_lineage.py` completed successfully.
- Verified artifacts:
  - `docs/DATA_LINEAGE_GRAPH.dot`
  - `docs/DATA_LINEAGE_GRAPH.svg`
  - `docs/DATA_LINEAGE.md`
