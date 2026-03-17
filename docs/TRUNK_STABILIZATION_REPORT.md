# Trunk Stabilization Report

Date: 2026-03-13

## Directory Verification

| Path | Status |
|------|--------|
| `/apps/web` | ✓ Exists |
| `/apps/magazine/retroverse-magazine` | ✓ Exists |
| `/pipelines/media-index` | ✓ Exists |
| `/pipelines/cards-1974` | ✓ Exists |
| `/pipelines/support-data` | ✓ Exists |
| `/data/raw` | ✓ Exists |
| `/data/derived` | ✓ Exists |
| `/archive` | ✓ Exists |
| `/docs` | ✓ Exists |

## Dataset Verification

| Check | Result |
|-------|--------|
| Canonical DB | ✓ `data/raw/charts/billboard-hot-100.db` exists |
| Symlink alias | ✓ `raw-data/billboard-hot-100.db` → `../data/raw/charts/billboard-hot-100.db` |
| Symlink resolves | ✓ File readable via symlink |

## Scripts Checked

| Script | Status |
|--------|--------|
| `pipelines/media-index/scripts/sync-index.sh` | ✓ ROOT_DIR uses `../../..` to repo root; paths correct |
| `pipelines/media-index/scripts/split-video-index-by-decade.mjs` | ✓ Receives paths from sync-index.sh; no changes needed |
| `pipelines/cards-1974/export_weekly_context.ts` | ✓ Paths use `data/derived/cards/1974/`, `apps/web/public/` |
| `pipelines/cards-1974/render_cards.ts` | ✓ Paths use `data/derived/cards/1974/`, `pipelines/cards-1974/`, `apps/web/public/` |
| `pipelines/support-data/scripts/compute_billboard_stats.py` | ✓ Default paths correct |
| `apps/magazine/retroverse-magazine/scripts/run_staff_writers.py` | ✓ Path corrected |
| `apps/magazine/retroverse-magazine/scripts/generate_year_range.py` | ✓ Path corrected |
| `apps/magazine/retroverse-magazine/scripts/ingest_imdb_datasets.py` | ✓ Paths corrected |

## Paths Corrected

| File | Change |
|------|--------|
| `apps/magazine/retroverse-magazine/scripts/run_staff_writers.py` | `WAREHOUSE_ROOT` → `data/raw/screen-culture/warehouse` |
| `apps/magazine/retroverse-magazine/scripts/generate_year_range.py` | `WAREHOUSE_ROOT` → `data/raw/screen-culture/warehouse` |
| `apps/magazine/retroverse-magazine/scripts/ingest_imdb_datasets.py` | `IMDB_ROOT` → `data/raw/imdb`, `SCREEN_CULTURE_REFERENCE_ROOT` → `data/raw/screen-culture/reference` |

## Pipelines Tested

| Pipeline | Result |
|----------|--------|
| `npm run dev` | ✓ Vite starts on http://localhost:5173/ |
| `npm run build` | ✓ sync-index, tsc, vite build succeed |
| `npm run build:1974` | ✓ 52 weekly rows exported (tsx requires non-sandbox env) |
| `npm run render:1974` | ⚠ Playwright Chromium not installed; path logic OK |
| `python3 compute_billboard_stats.py --help` | ✓ Runs successfully |

## Build Results

| Command | Exit | Notes |
|---------|------|-------|
| `npm install` | 0 | Up to date |
| `npm run dev` | 0 | Vite ready |
| `npm run build` | 0 | Full build succeeds |
| `npm run build:1974` | 0 | Succeeds outside sandbox |
| `npm run render:1974` | 1 | Playwright browser missing |

## Unresolved Issues

1. **render:1974** — Requires `npx playwright install chromium`. Not a path issue.
2. **story_*.json in issues/1978/articles/** — Contain hardcoded `raw-data/screen-culture/warehouse` paths. Treated as data artifacts; not modified per "do not modify datasets" rule. If magazine pipeline reads these at runtime, consider a follow-up to update or the symlink may suffice for `raw-data` references.
3. **Documentation** — `PROJECT_STATE.md`, `PIPELINE_REPAIR_IMPLEMENTATION.md`, `MAGAZINE_PIPELINE_AUDIT.md`, `SCREEN_CULTURE_DATA_AUDIT.md` still reference old paths. Documentation only; no runtime impact.

## Repository Stability

**Core commands succeed:**

- `npm run dev` ✓
- `npm run build` ✓
- `npm run build:1974` ✓

**Trunk is stable.** Remaining items are environment setup (Playwright) and documentation updates.
