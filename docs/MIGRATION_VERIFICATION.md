# Repository Migration Verification

Date: 2026-03-13

**Status: Pre-migration verification. Do NOT execute moves yet.**

---

## 1. Canonical Dataset Verification

### raw-data/billboard-hot-100.db

| Check | Result |
|-------|--------|
| Exists | **YES** |
| Path | `/Users/bobhopp/Sites/retroverse/raw-data/billboard-hot-100.db` |
| Size | ~51.9 MB |
| Sidecars | `billboard-hot-100.db-shm`, `billboard-hot-100.db-wal` (SQLite WAL; exclude from git) |

### raw-data/ contents (verified)

| Item | Status |
|------|--------|
| billboard-hot-100.db | Present |
| billboard-200-albums-charts.db | Present |
| vdj_history_full.json | Present |
| imdb/ | Present |
| screen-culture/ | Present |

**Note:** `pipeline.config.json` references `raw-data/charts/`, `raw-data/playlists/`, `raw-data/videos/`, `raw-data/youtube-reference.json` — these do not exist in the current tree. Migration does not move them.

---

## 2. Migration Script Review

### Critical issues

1. **Compatibility alias contradiction**  
   Plan says: "keep raw-data/billboard-hot-100.db as a temporary compatibility alias until all active consumers are updated."  
   Script does: `git mv raw-data/billboard-hot-100.db data/raw/charts/billboard-hot-100.db` (full move, no alias).  
   **Action:** Either add a symlink after the move, or update all consumers before the move.

2. **git mv glob patterns**  
   `git mv retroverse-output/retroverse_year_end_[0-9][0-9][0-9][0-9].csv` — bash expands the glob before `git mv`; each file is moved individually. Works.  
   Same for `cultural_events_{1976,...,1981}.json` and `year_end_top_40_{1976,...,1981}.json`.

3. **Move order dependency**  
   - Must move `public/charts` before `public` (script does this).
   - Must extract support-data scripts from `scripts/` before `git mv scripts archive/...`.
   - Must extract from `retroverse-output/` before archiving `retroverse-output/decks`.
   - Must move `tools/1974`, `tools/analyze_playcounts.py`, etc. before `git mv tools archive/...`.

4. **sync-index.sh ROOT_DIR**  
   Uses `$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)`. After move to `pipelines/media-index/scripts/`, `..` = `pipelines/media-index/`, not repo root. **Will break.**

5. **export-hot100-summaries.sh, export-album-summaries.sh**  
   Same pattern. After move to `pipelines/support-data/scripts/`, `..` = `pipelines/support-data/`. **Will break.**

6. **split-video-index-by-decade.mjs**  
   Uses `path.resolve(__dirname, '..')`. After move to `pipelines/media-index/scripts/`, rootDir = `pipelines/media-index/`. Called by sync-index.sh with `DEST_FILE`; may need path updates.

7. **retroverse-output directory**  
   Script moves individual files out but does not remove or archive the empty `retroverse-output/` directory. Recommend adding `rmdir retroverse-output` or `git rm -r retroverse-output` after moves (if empty).

---

## 3. Commit Plan for Repository Restructure

### Phase A: Path updates first (recommended)

1. **Commit 1: Centralize data paths**  
   - Add repo-level `data-paths.json` or equivalent.  
   - Update `pipeline.config.json` to use config-driven paths.  
   - Repoint magazine `generate_year_context.py` from `retroverse-data/.../source_billboard_hot_100.db` to `raw-data/billboard-hot-100.db`.  
   - Verify trunk still works.

2. **Commit 2: Create target layout (empty dirs)**  
   - `mkdir -p apps/web pipelines/media-index pipelines/cards-1974 pipelines/support-data data/raw data/derived archive/apps archive/pipelines archive/artifacts archive/docs docs`  
   - Add `.gitkeep` if needed.  
   - No moves yet.

3. **Commit 3: Move apps**  
   - `apps/web/`, `apps/magazine/`  
   - Update `package.json`, `vite.config.ts`, `netlify.toml`, `tsconfig.*.json` to new paths.

4. **Commit 4: Move pipelines**  
   - `pipelines/media-index/`, `pipelines/cards-1974/`, `pipelines/support-data/`  
   - Update all pipeline configs and script path resolution.

5. **Commit 5: Move data**  
   - `data/raw/`, `data/derived/`, `data/support/`  
   - Add compatibility symlink for `raw-data/billboard-hot-100.db` if needed.

6. **Commit 6: Archive**  
   - `archive/apps/`, `archive/pipelines/`, `archive/artifacts/`, `archive/docs/`  
   - Update `.gitignore` for new layout.

7. **Commit 7: Docs and cleanup**  
   - Move docs, remove compatibility symlinks, final verification.

### Phase B: Big-bang (alternative)

Single large commit with all moves + path updates. Higher risk; harder to bisect.

---

## 4. Exact git mv Operations (by phase)

### Phase 1: Apps

```bash
# Create structure
mkdir -p apps/web/tools apps/magazine

# Web app
git mv src apps/web/src
git mv api apps/web/api
git mv netlify apps/web/netlify
git mv index.html apps/web/index.html
git mv tools/autoUpdate.ts apps/web/tools/autoUpdate.ts

# Archive charts before moving public
git mv public/charts archive/apps/public-charts
git mv public apps/web/public

# Magazine
git mv retroverse-magazine apps/magazine
```

### Phase 2: Pipelines

```bash
mkdir -p pipelines/media-index/scripts pipelines/media-index/tools
mkdir -p pipelines/cards-1974
mkdir -p pipelines/support-data/scripts

# Media-index
git mv pipeline pipelines/media-index
git mv scripts/sync-index.sh pipelines/media-index/scripts/sync-index.sh
git mv scripts/split-video-index-by-decade.mjs pipelines/media-index/scripts/split-video-index-by-decade.mjs
git mv tools/analyze_playcounts.py pipelines/media-index/tools/analyze_playcounts.py
git mv tools/api-selftest.mjs pipelines/media-index/tools/api-selftest.mjs
git mv tools/api-selftest.ts pipelines/media-index/tools/api-selftest.ts

# Cards
git mv tools/1974 pipelines/cards-1974

# Support-data (individual files)
git mv scripts/archive_magazine_harvester.py pipelines/support-data/scripts/
git mv scripts/build_cultural_index.py pipelines/support-data/scripts/
git mv scripts/build_year_master.py pipelines/support-data/scripts/
git mv scripts/compute_billboard_stats.py pipelines/support-data/scripts/
git mv scripts/export-album-summaries.sh pipelines/support-data/scripts/
git mv scripts/export-hot100-summaries.sh pipelines/support-data/scripts/
git mv scripts/generate_magazine_catalog.py pipelines/support-data/scripts/
git mv scripts/generate_yearly_magazine_index.py pipelines/support-data/scripts/
git mv scripts/harvest_billboard.py pipelines/support-data/scripts/
git mv scripts/harvest_magazines.py pipelines/support-data/scripts/
git mv scripts/harvest_radio_logs.py pipelines/support-data/scripts/
git mv scripts/harvest_tv_listings.py pipelines/support-data/scripts/
git mv scripts/init_culture_dataset.py pipelines/support-data/scripts/
git mv scripts/merge_magazine_datasets.py pipelines/support-data/scripts/
git mv scripts/pipeline_common.py pipelines/support-data/scripts/
git mv scripts/rebuild_year_master.py pipelines/support-data/scripts/
git mv scripts/recover_issue_dates.py pipelines/support-data/scripts/
git mv scripts/recover_issue_dates_from_url.py pipelines/support-data/scripts/
git mv scripts/run_full_pipeline.py pipelines/support-data/scripts/
git mv scripts/rv_year_end_rank.py pipelines/support-data/scripts/
git mv retroverse-output/build_retroverse_support_1958_2024.py pipelines/support-data/
git mv retroverse-output/README.md pipelines/support-data/
git mv retroverse-output/requirements.txt pipelines/support-data/
```

### Phase 3: Data

```bash
mkdir -p data/raw/charts data/raw/media data/raw/imdb data/raw/screen-culture
mkdir -p data/derived/cards/1974 data/derived/culture data/derived/media-index/inventory
mkdir -p data/derived/year-masters/legacy data/derived/year-masters/logs
mkdir -p data/support/retroverse data/support/magazine/albums
mkdir -p data/support/magazine/cultural-events data/support/magazine/year-end-top40
mkdir -p data/support/magazine/archive

# Raw
git mv raw-data/billboard-hot-100.db data/raw/charts/billboard-hot-100.db
git mv raw-data/billboard-200-albums-charts.db data/raw/charts/billboard-200-albums-charts.db
git mv raw-data/vdj_history_full.json data/raw/media/vdj_history_full.json
git mv raw-data/imdb data/raw/imdb
git mv raw-data/screen-culture data/raw/screen-culture

# Derived (cards, culture)
git mv data/1974_card_render_report.json data/derived/cards/1974/
git mv data/1974_master.json data/derived/cards/1974/
git mv data/1974_weekly_context.json data/derived/cards/1974/
git mv data/1974_weekly_context.md data/derived/cards/1974/
git mv data/1974_weekly_context.parse_report.json data/derived/cards/1974/
git mv data/retro-verse-1974-weekly-data.md data/derived/cards/1974/
git mv data/index data/derived/culture/
git mv data/processed data/derived/culture/

# Media-index artifacts
git mv artifacts/canonical data/derived/media-index/
git mv artifacts/decisions data/derived/media-index/
git mv artifacts/matching data/derived/media-index/
git mv artifacts/output data/derived/media-index/
git mv r2_inventory.json data/derived/media-index/inventory/
git mv r2_thumbs.json data/derived/media-index/inventory/

# Year-masters (use loop for glob)
for f in retroverse-output/retroverse_year_end_*.csv retroverse-output/retroverse_year_end_*_top40.csv; do
  [ -f "$f" ] && git mv "$f" data/derived/year-masters/
done
git mv retroverse-output/retroverse_year_end_1958_2024_all.csv data/derived/year-masters/
git mv retroverse-output/retroverse_year_master_1958_2024.json data/derived/year-masters/
git mv retroverse-output/master_1978_1981.json data/derived/year-masters/legacy/
git mv retroverse-output/retroverse_support_cultural_1958_2024_top10.log data/derived/year-masters/logs/
git mv retroverse-support/retroverse_support_cultural_1958_2024_top10.csv data/support/retroverse/

# Support files
git mv albums_1978_sample.csv data/support/magazine/albums/
for f in cultural_events_{1976,1977,1978,1979,1980,1981}.json; do
  [ -f "$f" ] && git mv "$f" data/support/magazine/cultural-events/
done
for f in year_end_top_40_{1976,1977,1978,1979,1980,1981}.json; do
  [ -f "$f" ] && git mv "$f" data/support/magazine/year-end-top40/
done
git mv MAGAZINE_ARCHIVE_HARVEST.csv data/support/magazine/archive/
git mv MAGAZINE_ARCHIVE_HARVEST.csv.bak data/support/magazine/archive/
git mv MAGAZINE_CULTURAL_SIGNALS.json data/support/magazine/archive/
git mv MAGAZINE_ISSUE_MANIFEST.csv data/support/magazine/archive/
git mv MAGAZINE_ISSUE_MANIFEST_DATED.csv data/support/magazine/archive/
git mv MAGAZINE_MASTER_ARCHIVE.csv data/support/magazine/archive/
git mv MAGAZINE_MASTER_INDEX.csv data/support/magazine/archive/
git mv MAGAZINE_METADATA_SAMPLE.json data/support/magazine/archive/
git mv MAGAZINE_YEAR_INDEX.csv data/support/magazine/archive/
```

### Phase 4: Docs

```bash
git mv DATA_INVENTORY.md docs/
git mv DSM_WEBSTACK_RECOVERY.md docs/
git mv "RetroVerse Wheel Specification.md" docs/
```

### Phase 5: Archive

```bash
git mv retroverse_chart archive/apps/
git mv retroverse_v0 archive/apps/
git mv retroverse-1974 archive/pipelines/
git mv retroverse-data archive/pipelines/
git mv scripts archive/pipelines/legacy-root-scripts
git mv tools archive/pipelines/tools-legacy
git mv dist archive/artifacts/
git mv dist-pipeline archive/artifacts/
git mv runs archive/artifacts/
git mv logs archive/artifacts/ 2>/dev/null || true
git mv retroverse-output/decks archive/artifacts/retroverse-output-decks
git mv history_collect.py archive/artifacts/
git mv dsm_webstack_repair.sh archive/artifacts/
git mv and archive/artifacts/ 2>/dev/null || true
git mv minimal archive/artifacts/ 2>/dev/null || true
git mv readable archive/artifacts/ 2>/dev/null || true
git mv remains archive/artifacts/ 2>/dev/null || true
git mv Journal archive/docs/ 2>/dev/null || true
```

---

## 5. Scripts That Will Break (Path Changes)

### Trunk scripts (must fix before/with migration)

| Script | Current path assumption | New location | Fix |
|--------|-------------------------|--------------|-----|
| `package.json` scripts | `src/`, `api/`, `pipeline/`, `tools/1974/`, `scripts/`, `tools/` | Various | Update all script paths |
| `api/server.ts` | `../pipeline/server.js` | `../pipelines/media-index/server.js` | Update import |
| `vite.config.ts` | root = cwd | root = `apps/web` | Add `root: 'apps/web'` |
| `netlify.toml` | `dist`, `data/processed/billboard_hot100.csv` | `apps/web/dist`?, `data/derived/culture/processed/` | Update publish dir, included_files |
| `netlify/functions/billboard.ts` | `data/processed/billboard_hot100.csv` | `data/derived/culture/processed/billboard_hot100.csv` | Update path |
| `pipeline.config.json` | All absolute paths | `data/raw/charts/`, `artifacts` → `data/derived/media-index/` | Full path rewrite |
| `scripts/sync-index.sh` | ROOT_DIR = script dir `..` | In pipelines/media-index/scripts | Use repo root (e.g. `../../..` or env) |
| `scripts/split-video-index-by-decade.mjs` | rootDir = `__dirname/..` | In pipelines/media-index/scripts | Use repo root |
| `scripts/export-hot100-summaries.sh` | ROOT_DIR = script dir `..` | In pipelines/support-data/scripts | Use repo root |
| `scripts/export-album-summaries.sh` | Same | Same | Same |
| `tools/1974/export_weekly_context.ts` | `data/`, `public/` | `data/derived/cards/1974/`, `apps/web/public/` | Update paths |
| `tools/1974/render_cards.ts` | `data/`, `tools/1974/`, `public/` | Same | Same |
| `tools/api-selftest.mjs` | `../dist-pipeline/server.js` | In pipelines/media-index/tools | `../dist-pipeline` still correct |
| `scripts/compute_billboard_stats.py` | `raw-data/`, `artifacts/output/billboard` | `data/raw/charts/`, `data/derived/media-index/output/billboard` | Update paths |
| `scripts/build_year_master.py` | `../retroverse-output`, `../retroverse-support` | `../data/derived/year-masters`, `../data/support/retroverse` | Update paths |
| `scripts/rebuild_year_master.py` | Same | Same | Same |
| `scripts/harvest_billboard.py` | `raw-data/billboard-hot-100.db`, `data/processed` | `data/raw/charts/`, `data/derived/culture/processed` | Update paths |
| `scripts/rv_year_end_rank.py` | `raw-data/`, `retroverse-output` | `data/raw/charts/`, `data/derived/year-masters` | Update paths |
| `retroverse-magazine/scripts/generate_year_context.py` | `retroverse-data/.../source_billboard_hot_100.db` | `data/raw/charts/billboard-hot-100.db` | Update DB path |
| `retroverse-magazine/scripts/generate_all_year_contexts.py` | Same | Same | Same |
| `retroverse-magazine/scripts/screen_culture_common.py` | `retroverse-output/`, `raw-data/` | `data/derived/year-masters/`, `data/raw/` | Update paths |
| `retroverse-magazine/data/DATA_SOURCES.yaml` | All paths | All paths | Full rewrite |

### Archive scripts (will break if reactivated)

- `scripts/generate_1974_deck.py`
- `scripts/build_multi_year_retroverse_decks.py`
- `scripts/compose_1974_deck.py`
- `scripts/generate_at40_week30_rank01.py`
- `scripts/generate_retroverse_1974_week30_top5.py`
- `scripts/render-1974-playing-card.mjs`
- `scripts/render-week-30-cards.mjs`
- `scripts/render-week-30-illustrated.mjs`
- `retroverse_chart/scripts/export_billboard_json.py`
- `retroverse_v0/export_billboard_json.py`

### Config files

- `tsconfig.app.json` — may reference `src/`
- `tsconfig.node.json` — may reference `tools/`
- `tsconfig.pipeline.json` — references `pipeline/`

---

## 6. Final Migration Checklist

### Pre-migration

- [ ] Confirm `raw-data/billboard-hot-100.db` exists and is canonical
- [ ] Decide: compatibility symlink for `raw-data/billboard-hot-100.db` or update all consumers first
- [ ] Create `docs/MIGRATION_VERIFICATION.md` (this file)
- [ ] Branch: `git checkout -b migration/trunk-stabilization`
- [ ] Ensure working tree is clean

### Path-update prep (before or with moves)

- [ ] Add repo-root resolution helper (e.g. `REPO_ROOT` env or `scripts/find-repo-root.sh`)
- [ ] Update `scripts/sync-index.sh`, `export-hot100-summaries.sh`, `export-album-summaries.sh` to use repo root
- [ ] Update `retroverse-magazine` scripts to use `data/raw/charts/billboard-hot-100.db`
- [ ] Update `pipeline.config.json` to use config-driven or repo-relative paths

### Execution order

1. [ ] Phase 1: Apps (git mv + config updates)
2. [ ] Phase 2: Pipelines (git mv + config updates)
3. [ ] Phase 3: Data (git mv)
4. [ ] Phase 4: Docs (git mv)
5. [ ] Phase 5: Archive (git mv)

### Post-migration verification

- [ ] `npm run dev` — web app starts
- [ ] `npm run api` — API starts
- [ ] `npm run build` — build succeeds
- [ ] `npm run build:1974` — cards pipeline runs
- [ ] `npm run billboard:stats` — support-data script runs
- [ ] Magazine pipeline runs (from `apps/magazine/`)
- [ ] Netlify build succeeds (or document known deploy path changes)

### Cleanup

- [ ] Remove `raw-data/` if fully migrated (or keep symlink)
- [ ] Update `.gitignore` for new layout
- [ ] Update root `README.md` with new structure
- [ ] Add `docs/REPOSITORY_MAP.md` describing trunk vs archive
