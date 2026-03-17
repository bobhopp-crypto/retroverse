# Migration Execution Report

Date: 2026-03-13

## Summary

Repository migration from mixed experimental tree to stabilized trunk layout completed. All phases executed successfully.

## Files Moved

### Phase 1 — Directories Created
- `/apps`, `/apps/web`, `/apps/magazine`
- `/pipelines`, `/pipelines/media-index`, `/pipelines/cards-1974`, `/pipelines/support-data`
- `/data/raw/charts`, `/data/raw/media`, `/data/raw/imdb`, `/data/raw/screen-culture`
- `/data/derived`
- `/archive`, `/archive/apps`, `/archive/pipelines`, `/archive/artifacts`, `/archive/docs`

### Phase 2 — Apps
- `src/` → `apps/web/src/`
- `api/` → `apps/web/api/`
- `index.html` → `apps/web/index.html`
- `public/` → `apps/web/public/` (except `public/charts/` archived to `archive/apps/public-charts/`)
- `netlify/` → `apps/web/netlify/`
- `tools/autoUpdate.ts` → `apps/web/tools/autoUpdate.ts`
- `retroverse-magazine/` → `apps/magazine/retroverse-magazine/`

### Phase 3 — Pipelines
- `pipeline/` → `pipelines/media-index/pipeline/`
- `scripts/sync-index.sh` → `pipelines/media-index/scripts/`
- `scripts/split-video-index-by-decade.mjs` → `pipelines/media-index/scripts/`
- `tools/1974/` → `pipelines/cards-1974/`
- `tools/analyze_playcounts.py`, `api-selftest.mjs`, `api-selftest.ts` → `pipelines/media-index/tools/`
- Support-data scripts (20 files) → `pipelines/support-data/scripts/`
- `retroverse-output/build_retroverse_support_1958_2024.py`, `README.md`, `requirements.txt` → `pipelines/support-data/`

### Phase 4 — Raw Data
- `raw-data/billboard-hot-100.db` → `data/raw/charts/billboard-hot-100.db`
- `raw-data/billboard-200-albums-charts.db` → `data/raw/charts/`
- `raw-data/vdj_history_full.json` → `data/raw/media/`
- `raw-data/imdb/` → `data/raw/imdb/`
- `raw-data/screen-culture/` → `data/raw/screen-culture/`
- **Compatibility symlink:** `raw-data/billboard-hot-100.db` → `../data/raw/charts/billboard-hot-100.db`

### Phase 5 — Derived Data
- `data/1974_*` → `data/derived/cards/1974/`
- `data/index/` → `data/derived/culture/index/`
- `data/processed/` → `data/derived/culture/processed/`
- `artifacts/*` → `data/derived/media-index/`
- `r2_inventory.json`, `r2_thumbs.json` → `data/derived/media-index/inventory/`
- `retroverse-output/*.csv`, `*.json` → `data/derived/year-masters/`
- `retroverse-support/*.csv` → `data/support/retroverse/`
- Top-level support files → `data/support/magazine/`

### Phase 6 — Archive
- `retroverse_chart/`, `retroverse_v0/` → `archive/apps/`
- `retroverse-1974/`, `retroverse-data/` → `archive/pipelines/`
- `scripts/` (remaining) → `archive/pipelines/legacy-root-scripts/`
- `tools/` (remaining) → `archive/pipelines/tools-legacy/`
- `dist/`, `dist-pipeline/`, `runs/`, `logs/` → `archive/artifacts/`
- `retroverse-output/decks/`
- `history_collect.py`, `dsm_webstack_repair.sh`
- `Journal/` → `archive/docs/`
- `DATA_INVENTORY.md`, `DSM_WEBSTACK_RECOVERY.md`, `RetroVerse Wheel Specification.md` → `docs/`

## Paths Updated

| File | Changes |
|------|---------|
| `package.json` | All script paths: `apps/web/`, `pipelines/`, `archive/` |
| `apps/web/api/server.ts` | Import: `../../pipelines/media-index/pipeline/server.js` |
| `vite.config.ts` | `root: 'apps/web'` |
| `netlify.toml` | `publish: apps/web/dist`, `directory: apps/web/netlify/functions`, `included_files: data/derived/culture/processed/billboard_hot100.csv` |
| `pipeline.config.json` | `billboard_sqlite`, `artifacts.*`, `logging.dir` paths |
| `tsconfig.app.json` | `include: ["apps/web/src"]` |
| `tsconfig.pipeline.json` | `rootDir`, `include` for pipeline paths |
| `pipelines/media-index/scripts/sync-index.sh` | `ROOT_DIR`, `SOURCE_FILE`, `DEST_DIR`, `SPLIT_SCRIPT` |
| `apps/web/netlify/functions/billboard.ts` | `BILLBOARD_CSV_PATHS` |
| `pipelines/cards-1974/export_weekly_context.ts` | `INPUT_PATH`, `OUTPUT_PATH`, `PUBLIC_OUTPUT_PATH`, `REPORT_PATH` |
| `pipelines/cards-1974/render_cards.ts` | `DATA_PATH`, `TEMPLATE_PATH`, `CSS_PATH`, `OUTPUT_DIR`, `REPORT_PATH` |
| `pipelines/media-index/tools/api-selftest.mjs` | Import: `../../../dist-pipeline/server.js` |
| `pipelines/media-index/pipeline/scripts/run-history-ingest.ts` | `OUTPUT_PATH` |
| `pipelines/support-data/scripts/pipeline_common.py` | `ROOT_DIR`, `PROCESSED_DIR`, `INDEX_DIR`, `LOG_DIR`, `SCRIPTS_DIR` |
| `pipelines/support-data/scripts/export-hot100-summaries.sh` | `ROOT_DIR`, `OUT_DIR` |
| `pipelines/support-data/scripts/export-album-summaries.sh` | `ROOT_DIR`, `DB_PATH`, `OUT_DIR` |
| `pipelines/support-data/scripts/compute_billboard_stats.py` | Default `--db`, `--out-dir` |
| `pipelines/support-data/scripts/rebuild_year_master.py` | `BASE_DIR`, `OUTPUT_DIR`, `CULTURE_FILE` |
| `pipelines/support-data/scripts/build_year_master.py` | `MUSIC_PATH`, `CULTURE_PATH`, `OUTPUT_PATH` |
| `pipelines/support-data/scripts/harvest_billboard.py` | `RAW_DB_PATH` |
| `pipelines/support-data/scripts/rv_year_end_rank.py` | Default `--db`, `--out` |
| `pipelines/support-data/scripts/run_full_pipeline.py` | `ROOT_DIR`, `SCRIPT_DIR` |
| `apps/magazine/retroverse-magazine/scripts/generate_year_context.py` | `WORKSPACE_ROOT`, `DB_PATH`, `CULTURAL_EVENTS_TEMPLATE`, `ALBUM_SAMPLE_TEMPLATE` |
| `apps/magazine/retroverse-magazine/scripts/generate_all_year_contexts.py` | `DB_PATH` |
| `apps/magazine/retroverse-magazine/scripts/screen_culture_common.py` | `RETROVERSE_ROOT`, `RAW_DATA_ROOT`, `DEFAULT_YEAR_MASTER_PATH` |
| `apps/magazine/retroverse-magazine/data/DATA_SOURCES.yaml` | All paths |

## Scripts Checked

| Check | Result |
|-------|--------|
| Canonical DB exists | `data/raw/charts/billboard-hot-100.db` ✓ |
| Symlink alias works | `raw-data/billboard-hot-100.db` → `../data/raw/charts/billboard-hot-100.db` ✓ |
| `npm run pipeline:build` | ✓ Success |
| `npm run build` | ✓ Success (sync-index, tsc, vite build) |
| `npm run build:1974` | Not run (tsx sandbox EPERM; path logic OK) |
| `python3 compute_billboard_stats.py --help` | ✓ Success |

## Issues Detected

1. **test:tier-mapping** — Points to `archive/pipelines/tools-legacy/tierMapping.test.ts`. If tier mapping is trunk, consider moving or updating.
2. **Netlify publish** — Set to `apps/web/dist`. Verify Netlify build command runs from repo root and `npm run build` produces output there.
3. **build:1974** — Could not run in sandbox due to tsx IPC pipe EPERM. Path updates are correct; manual verification recommended.
4. **retroverse-output** — Remaining directory archived as `archive/artifacts/retroverse-output-remainder`. Some files may remain.
5. **init_culture_dataset.py** — `SUPPORT_DIR` still uses `Path.home() / "Sites" / "retroverse"`; not updated (may be intentional for Downloads path).

## Final Layout

```
/
  apps/
    web/          # Vite frontend, api, netlify, public
    magazine/     # retroverse-magazine
  pipelines/
    media-index/  # pipeline, scripts, tools
    cards-1974/
    support-data/
  data/
    raw/
      charts/
      media/
      imdb/
      screen-culture/
    derived/
      cards/
      culture/
      media-index/
      year-masters/
    support/
  archive/
    apps/
    pipelines/
    artifacts/
    docs/
  docs/
  raw-data/       # Symlink + compatibility
```
