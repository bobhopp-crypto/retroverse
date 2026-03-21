# RetroVerse Data Discovery Report

**Generated:** 2026-03-21  
**Purpose:** Map all structured data related to Billboard charts, albums, cultural data, and year context.

---

## 1. ALL DATA SOURCES FOUND

### Chart Data (Billboard Hot 100)

| Path | Type | Description | Years |
|------|------|-------------|-------|
| `data/raw/charts/billboard-hot-100.db` | SQLite | **PRIMARY** — Weekly Hot 100 charts | 1958–present |
| `archive/pipelines/retroverse-data/databases/source_billboard_hot_100.db` | SQLite | Legacy duplicate (avoid) | — |
| `archive/pipelines/retroverse-1974/data/db/billboard-hot-100.db` | SQLite | 1974 cards pipeline copy | — |
| `apps/web/public/data/charts/[year].json` | JSON | Per-year top 100 songs (artist, title, peak, weeks) | **1958–2024** ✅ |
| `data/derived/media-index/output/billboard/top_songs_by_year.json` | JSON | Aggregated top songs by year | 1958+ |
| `data/derived/media-index/output/billboard/year_stats.json` | JSON | Per-year stats (counts, etc.) | 1958+ |
| `data/derived/year-masters/retroverse_year_master_1958_2024.json` | JSON | Consolidated year master (top 40 + metadata) | 1958–2024 |

### Album Data (Billboard 200)

| Path | Type | Description |
|------|------|-------------|
| `data/raw/charts/billboard-200-albums-charts.db` | SQLite | Billboard 200 album charts |
| `apps/web/public/data/albums/[year].json` | JSON | Per-year album data | 1958–2024 |

### Cultural Data (Movies, TV, Events)

| Path | Type | Description | Years |
|------|------|-------------|-------|
| `data/raw/screen-culture/screen-culture/warehouse/movies_master.json` | JSON | Movies master records | — |
| `data/raw/screen-culture/screen-culture/warehouse/movies_by_year.json` | JSON | Movies grouped by year | — |
| `data/raw/screen-culture/screen-culture/warehouse/television_master.json` | JSON | TV master records | — |
| `data/raw/screen-culture/screen-culture/warehouse/television_by_year.json` | JSON | TV grouped by year | — |
| `data/support/magazine/cultural-events/cultural_events_[year].json` | JSON | Cultural events by year | **1976–1981** (partial) |
| `data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv` | CSV | Curated cultural support | 1958–2024 |
| `data/support/magazine/academy_awards.json` | JSON | Academy Awards | — |
| `data/support/magazine/year-end-top40/year_end_top_40_[year].json` | JSON | Year-end Top 40 | **1976–1981** (partial) |

### Year Context (Magazine)

| Path | Type | Description | Years |
|------|------|-------------|-------|
| `apps/magazine/retroverse-magazine/issues/context/[year]_context.json` | JSON | Rich year context (top_songs, movies, tv, events) | **1958–2025** (68 files) |

### Other Derived

| Path | Type | Description |
|------|------|-------------|
| `data/derived/culture/index/cultural_datasets.db` | SQLite | Cultural index |
| `data/derived/media-index/canonical/billboard_run_*.json` | JSON | Media-index billboard runs |
| `apps/web/public/data/artist-gravity/[year].json` | JSON | Artist gravity by year |

---

## 2. IDENTIFIED SOURCE OF TRUTH

### Chart Data

**Primary:** `data/raw/charts/billboard-hot-100.db`

- Weekly Billboard Hot 100 (1958–present)
- Schema: `charts` or `event`/`event_entry`/`work`/`person` (depending on DB version)
- Referenced by: `data/registry/DATA_REGISTRY.yaml`

### Cultural Data

**Primary:** `data/raw/screen-culture/screen-culture/warehouse/`

- `movies_by_year.json` — movies grouped by year
- `television_by_year.json` — TV grouped by year
- Supplement: `data/support/magazine/cultural-events/` (partial coverage)

---

## 3. PIPELINE TRACE

### Per-Year Chart Files → `apps/web/public/data/charts/[year].json`

**Script:** `pipelines/support-data/scripts/export-hot100-summaries.sh`

**Flow:**
1. Reads `data/raw/charts/billboard-hot-100.db`
2. For each year (default 1958–2024):
   - SQL: `GROUP BY artist, title` → min(rank) as peak, count(*) as weeks
   - ORDER BY peak, LIMIT 100
3. Writes `apps/web/public/data/charts/{year}.json`
4. Uses `web_public_data` path from registry

**Run:**
```bash
cd /Users/bobhopp/Sites/retroverse
bash pipelines/support-data/scripts/export-hot100-summaries.sh 1958 2024
```

### Year Context → `issues/context/[year]_context.json`

**Script:** `apps/magazine/retroverse-magazine/scripts/generate_year_context.py`

**Flow:**
1. Reads billboard-hot-100.db
2. Builds top_songs (score-based ranking)
3. Loads movies from `issues/{year}/data/movies.json` or screen culture
4. Loads TV from `issues/{year}/data/tv.json` or screen culture
5. Loads cultural_events from `data/support/magazine/cultural-events/cultural_events_{year}.json`
6. Writes `issues/context/{year}_context.json`

**Batch:** `generate_all_year_contexts.py` iterates DB years and calls `generate_year_context.py`

### Year Master → `data/derived/year-masters/retroverse_year_master_1958_2024.json`

**Script:** `pipelines/support-data/scripts/rebuild_year_master.py` or `build_year_master.py`

**Flow:** Builds consolidated top-40 dataset from Hot 100 + cultural support CSV.

### Media-Index Billboard Stats

**Script:** `pipelines/support-data/scripts/compute_billboard_stats.py`

**Outputs:** `data/derived/media-index/output/billboard/` (year_stats, top_songs_by_year, etc.)

---

## 4. TARGET OUTPUT: `apps/web/public/data/charts/[year].json`

### Status: ✅ FILES ALREADY EXIST

| Check | Result |
|-------|--------|
| Path | `apps/web/public/data/charts/` |
| Years | **1958–2024** (67 files) |
| Structure | `[{artist, title, peak, weeks}, ...]` |
| Generated by | `export-hot100-summaries.sh` |

**Sample (1983):**
```json
[
  {"artist":"Billy Joel","title":"Tell Her About It","peak":1,"weeks":18},
  {"artist":"Bonnie Tyler","title":"Total Eclipse Of The Heart","peak":1,"weeks":25},
  ...
]
```

---

## 5. COVERAGE SUMMARY

| Dataset | Path | Years | Complete |
|---------|------|-------|----------|
| Per-year charts | `apps/web/public/data/charts/[year].json` | 1958–2024 | ✅ Yes |
| Year context | `issues/context/[year]_context.json` | 1958–2025 | ✅ Yes |
| Year master | `retroverse_year_master_1958_2024.json` | 1958–2024 | ✅ Yes |
| Cultural events | `cultural_events_[year].json` | 1976–1981 | ⚠️ Partial |
| Year-end Top 40 | `year_end_top_40_[year].json` | 1976–1981 | ⚠️ Partial |
| Movies/TV | screen culture warehouse | Multi-year | ✅ Yes |

---

## 6. NO SCRIPT NEEDED

Per-year chart files **already exist** at the target path. Use:

```bash
# Regenerate if needed
bash pipelines/support-data/scripts/export-hot100-summaries.sh 1958 2024
```

---

## 7. FINAL OUTPUT PATH

**Primary:** `apps/web/public/data/charts/[year].json` for years **1958–2024** (67 files)

All files present. No `scripts/build_year_data.py` required.
