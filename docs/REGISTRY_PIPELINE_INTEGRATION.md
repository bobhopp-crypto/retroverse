# Registry Pipeline Integration

## Summary

Implemented registry-aware dataset resolution across the targeted pipeline surfaces without changing pipeline logic.

The integration now resolves dataset paths from:

- `data/registry/DATA_REGISTRY.yaml`

and falls back to the prior repository-relative path when a registry entry is missing.

## Added Helpers

### Python

- `pipelines/support-data/lib/registry_loader.py`

Exports:

- `load_registry()`
- `get_dataset_path(dataset_id, fallback=None)`

Behavior:

- loads `data/registry/DATA_REGISTRY.yaml`
- caches the parsed registry
- resolves repository-relative dataset paths to absolute paths
- uses the provided fallback when the registry file or dataset entry is missing

### Node

- `pipelines/lib/registry-loader.js`

Exports:

- `loadRegistry()`
- `getDatasetPath(datasetId, fallback = null)`

Behavior:

- reads the same registry file
- resolves absolute paths for Node/TS pipeline scripts
- falls back to the previous path when an entry is missing

## Registry Entries Added

Added the dataset IDs required by the target scripts:

- `retroverse_support_cultural`
  - `data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv`
- `web_public_data`
  - `apps/web/public/data`
- `web_public_cards_1974`
  - `apps/web/public/cards/1974`

## Updated Files

### Registry

- `data/registry/DATA_REGISTRY.yaml`

### Support-Data

- `pipelines/support-data/lib/registry_loader.py`
- `pipelines/support-data/build_retroverse_support_1958_2024.py`
- `pipelines/support-data/scripts/pipeline_common.py`
- `pipelines/support-data/scripts/validate_registry.py`
- `pipelines/support-data/scripts/compute_billboard_stats.py`
- `pipelines/support-data/scripts/harvest_billboard.py`
- `pipelines/support-data/scripts/run_full_pipeline.py`
- `pipelines/support-data/scripts/build_year_master.py`
- `pipelines/support-data/scripts/rebuild_year_master.py`
- `pipelines/support-data/scripts/init_culture_dataset.py`
- `pipelines/support-data/scripts/rv_year_end_rank.py`
- `pipelines/support-data/scripts/export-hot100-summaries.sh`
- `pipelines/support-data/scripts/export-album-summaries.sh`

### Media-Index Scripts

- `pipelines/media-index/scripts/split-video-index-by-decade.mjs`
- `pipelines/media-index/scripts/sync-index.sh`

### Cards-1974

- `pipelines/cards-1974/export_weekly_context.ts`
- `pipelines/cards-1974/render_cards.ts`

### Shared Node Helper

- `pipelines/lib/registry-loader.js`

## Path Resolution Changes

### Support-Data

Registry-backed lookups now cover:

- canonical Billboard Hot 100 SQLite DB
- canonical Billboard 200 albums SQLite DB
- culture-derived root
- year-master root
- retroverse support cultural CSV
- canonical raw-data root protection in `run_full_pipeline.py`

`pipeline_common.py` now derives shared culture/raw paths from the registry, so scripts that already depended on it inherit registry-aware resolution automatically.

### Media-Index Scripts

Registry-backed lookups now cover:

- media-index derived root
- published web data root

This affects:

- the source `video-index.json` used by sync
- the default publish destination
- the default source for decade splitting

### Cards-1974

Registry-backed lookups now cover:

- the 1974 cards dataset root
- the published 1974 web data directory
- the published 1974 card image directory

Template and CSS paths were left unchanged because they are pipeline code assets, not datasets.

## Fallback Behavior

Fallback behavior was added in all lookup paths:

- If `DATA_REGISTRY.yaml` is missing, the helper returns the provided legacy path.
- If a dataset entry is missing, the helper returns the provided legacy path.
- If no fallback is supplied, the helper raises an error.

This keeps the pipeline behavior stable while shifting path ownership to the registry.

## Verification

The following checks were run successfully:

- `python3 -m py_compile` on the updated Python helper and support-data Python scripts
- `python3 pipelines/support-data/scripts/validate_registry.py`
  - result: `[OK] All registered paths exist. No unregistered datasets reported.`
- `bash -n` on:
  - `pipelines/support-data/scripts/export-hot100-summaries.sh`
  - `pipelines/support-data/scripts/export-album-summaries.sh`
  - `pipelines/media-index/scripts/sync-index.sh`
- `node --check` on:
  - `pipelines/lib/registry-loader.js`
  - `pipelines/media-index/scripts/split-video-index-by-decade.mjs`
- `npx tsc --noEmit --module nodenext --moduleResolution nodenext --target ES2022` on:
  - `pipelines/cards-1974/export_weekly_context.ts`
  - `pipelines/cards-1974/render_cards.ts`

## Notes

- No transformation logic was changed.
- Only dataset path resolution was centralized.
- The remaining hardcoded path literals in the updated files are fallback values used only when the registry cannot supply the dataset path.
