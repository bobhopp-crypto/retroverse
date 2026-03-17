# Trunk Stabilization Plan

Date: 2026-03-13

Purpose: convert the repository from a mixed experimental tree into a clear trunk architecture without breaking the current working systems during migration.

## 1. Active Systems That Should Form The Trunk

These are the systems that are currently active enough, coherent enough, or directly wired into root commands to justify keeping them in the supported trunk.

| Trunk system | Current location | Why it belongs in trunk | Proposed target |
|---|---|---|---|
| Web application | root `src/`, `public/`, `api/`, `netlify/`, root Vite/Netlify config | This is the current primary UI and deployment path. | `/apps/web` |
| Media index pipeline | `pipeline/` | This is the current TypeScript ingest/match/index API pipeline used by the root app. | `/pipelines/media-index` |
| Magazine product | `retroverse-magazine/` | This is the only magazine system with active issue content, editorial pipeline, and layout/PDF generation. | `/apps/magazine` |
| 1974 cards pipeline | `tools/1974/` | It is the 1974 pipeline actually wired into root `package.json` (`build:1974`, `render:1974`, `capsule:1974`). | `/pipelines/cards-1974` |
| Support-data builders | currently split across `scripts/` and `retroverse-output/` | These produce chart analytics, year-master data, and support CSVs used by other active systems. | `/pipelines/support-data` |

### Trunk decision notes

- Keep the root web app as the product-facing trunk.
- Keep `pipeline/` as the only supported media pipeline.
- Keep `retroverse-magazine/` as the only supported magazine product.
- Keep `tools/1974/` as the supported card pipeline because it is the one already wired into root commands.
- Treat support-data generation as part of the trunk because it feeds the magazine and deck systems.

## 2. Legacy Experiments, Prototype Apps, And Archived Code

These should not remain in the trunk. They should move under `/archive` once the active systems are relocated.

### Legacy apps

- `retroverse_chart/`
- `retroverse_v0/`
- `public/charts/`

Why archive:

- They duplicate the root `/charts` functionality.
- `retroverse_chart/` and `retroverse_v0/` share a large amount of identical code and assets.
- `public/charts/` is generated output, not a source app.

### Prototype or redundant pipelines

- `tools/src/` and the rest of the scaffolded `tools/` service pipeline
- `retroverse-1974/`
- root legacy harvest pipeline in `scripts/run_full_pipeline.py` plus `harvest_*`, `build_cultural_index.py`, and `pipeline_common.py`
- root one-off 1974 scripts in `scripts/`:
  - `generate_retroverse_1974_week30_top5.py`
  - `generate_at40_week30_rank01.py`
  - `render-week-30-cards.mjs`
  - `render-week-30-illustrated.mjs`
  - `render-1974-playing-card.mjs`
  - `generate_1974_deck.py`
  - `compose_1974_deck.py`
  - `build_multi_year_retroverse_decks.py`

Why archive:

- `tools/src/` duplicates the media pipeline concept but is explicitly documented as a scaffold.
- `retroverse-1974/` overlaps with the currently wired `tools/1974/` path.
- the legacy harvest pipeline writes to a separate `data/processed` / `data/index` model that is not the current root media-pipeline architecture.
- the root one-off 1974 scripts overlap with both `tools/1974/` and `retroverse-1974/`.

### Already archived or historical material

- `retroverse-magazine/archive/`
- `runs/`
- `retroverse-1974/runs/`
- `dist/`
- `dist-pipeline/`
- `.netlify/`
- `retroverse_chart/.next/`
- `retroverse_v0/.next/`

These should remain available for reference, but outside the supported trunk.

## 3. Proposed Stable Top-Level Structure

Target top-level areas:

- `/data`
- `/pipelines`
- `/apps`
- `/archive`
- `/docs`

### Proposed directory layout

```text
/
  apps/
    web/
    magazine/

  pipelines/
    media-index/
    cards-1974/
    support-data/

  data/
    raw/
      charts/
      media/
      screen-culture/
    derived/
      media-index/
      chart-analytics/
      year-masters/
      magazine/
      cards/
    published/
      web/
      magazine/
    support/

  archive/
    apps/
    pipelines/
    artifacts/
    runs/

  docs/
```

### Current-to-target mapping

| Current path | Target path | Notes |
|---|---|---|
| root app files (`src/`, `public/`, `api/`, `netlify/`, root app config) | `/apps/web/` | Preserve behavior first; move only after paths are centralized. |
| `pipeline/` | `/pipelines/media-index/` | This becomes the only supported media pipeline. |
| `tools/1974/` | `/pipelines/cards-1974/` | Keep as the supported trunk card pipeline. |
| `retroverse-magazine/` | `/apps/magazine/` | Move whole product first; do not split its internals during the first stabilization pass. |
| support-data scripts from `scripts/` and `retroverse-output/` | `/pipelines/support-data/` | Includes chart analytics, summary exports, year-master builders, and cultural support generation. |
| `raw-data/` | `/data/raw/` | Canonical raw inputs. |
| `artifacts/output/`, `artifacts/canonical/`, `artifacts/matching/` | `/data/derived/media-index/` | Current media-pipeline outputs. |
| `retroverse-output/` | `/data/derived/year-masters/` | Consolidated year-end / year-master outputs. |
| `retroverse-support/` | `/data/support/` | Support CSVs and closely related support artifacts. |
| `retroverse_chart/`, `retroverse_v0/`, `public/charts/` | `/archive/apps/` | Legacy chart products. |
| `tools/src/`, legacy root `scripts/`, `retroverse-1974/` | `/archive/pipelines/` | Archive unless explicitly reactivated later. |
| `dist/`, `dist-pipeline/`, `.netlify/`, `runs/`, `retroverse-1974/runs/` | `/archive/artifacts/` or `/archive/runs/` | Generated history, not trunk source. |

## 4. Single Canonical Billboard Hot 100 Dataset

### Recommended canonical source

Use the contents of:

- `raw-data/billboard-hot-100.db`

as the single canonical Billboard Hot 100 source.

### Why this dataset should win

1. It already serves the root web app and the root TypeScript media/chart pipeline.
2. It is the dataset most heavily used by active root scripts.
3. The magazine project already documents it as canonical in `retroverse-magazine/data/DATA_SOURCES.yaml`, even though one magazine script still points elsewhere.
4. The competing alternatives are clearly duplicates or local copies:
   - `retroverse-data/databases/source_billboard_hot_100.db` is only used by magazine context scripts.
   - `retroverse-1974/data/db/billboard-hot-100.db` is a copied local DB inside a legacy/parallel pipeline.

### Target path in the stabilized tree

Long-term canonical path:

- `/data/raw/charts/billboard-hot-100.db`

Short-term migration rule:

- keep `raw-data/billboard-hot-100.db` as the compatibility path until all consumers are migrated
- then retire `retroverse-data/databases/source_billboard_hot_100.db`
- then retire `retroverse-1974/data/db/billboard-hot-100.db` or keep it only as archived historical material

## 5. Pipelines That Depend On The Canonical Billboard Dataset

### Active trunk consumers

| Pipeline/system | Current files consuming the dataset | Current status |
|---|---|---|
| Web app chart/API layer | `pipeline/server.ts`, `pipeline/modules/exportBillboardJson.ts` | Active trunk |
| Support-data analytics/export pipeline | `scripts/compute_billboard_stats.py`, `scripts/export-hot100-summaries.sh`, `scripts/harvest_billboard.py`, `scripts/rv_year_end_rank.py` | Active supporting pipeline |
| Magazine context pipeline | `retroverse-magazine/scripts/generate_year_context.py`, `retroverse-magazine/scripts/generate_all_year_contexts.py` | Active trunk, but currently pointed at the duplicate DB |

### Legacy or archive-bound consumers

| Pipeline/system | Current files consuming the dataset or a copy | Archive status |
|---|---|---|
| Legacy 1974 scripts | `scripts/generate_retroverse_1974_week30_top5.py`, `scripts/render-week-30-cards.mjs`, `scripts/render-week-30-illustrated.mjs`, `scripts/generate_at40_week30_rank01.py` | Archive unless reactivated |
| Legacy chart app exporters | `retroverse_chart/scripts/export_billboard_json.py`, `retroverse_v0/export_billboard_json.py` | Archive |
| `retroverse-1974` batch engine | uses local copy at `retroverse-1974/data/db/billboard-hot-100.db` | Archive unless chosen as the official cards pipeline |

### Important distinction

The current supported `tools/1974/` pipeline does not directly hit the Billboard DB. It consumes `data/1974_weekly_context.{md,json}`. That means it should remain in trunk, but its upstream context-generation inputs should still trace back to the canonical DB through a reproducible data-build step.

## 6. Migration Plan

The migration should preserve the current trunk while steadily moving experiments out of the way. The order below is designed to avoid breaking the working root app.

### Phase 0. Freeze the trunk definition

Declare these as the only supported systems:

- web app
- media index pipeline
- magazine product
- current `tools/1974` cards pipeline
- support-data builders

Everything else becomes either archive material or optional future reactivation work.

### Phase 1. Make the data layer explicit before moving code

1. Create the target `/data` layout in the design docs first:
   - `/data/raw/charts/`
   - `/data/raw/media/`
   - `/data/raw/screen-culture/`
   - `/data/derived/`
   - `/data/published/`
   - `/data/support/`
2. Define `raw-data/billboard-hot-100.db` as the canonical Hot 100 source.
3. Add one repo-level path manifest for canonical inputs/outputs.
4. Redirect magazine context generation off `retroverse-data/databases/source_billboard_hot_100.db` and onto the canonical dataset.
5. Mark all duplicate DB copies as compatibility-only until the migration is complete.

Outcome:

- the data layer becomes explicit before any code is moved
- reproducibility no longer depends on hidden duplicate DBs

### Phase 2. Consolidate supported pipelines under `/pipelines`

Move or plan these as supported:

- `pipeline/` -> `/pipelines/media-index/`
- `tools/1974/` -> `/pipelines/cards-1974/`
- support-data builders -> `/pipelines/support-data/`

Support-data builders to keep:

- `scripts/compute_billboard_stats.py`
- `scripts/export-hot100-summaries.sh`
- `scripts/export-album-summaries.sh`
- `scripts/harvest_billboard.py`
- `scripts/rv_year_end_rank.py`
- `scripts/build_year_master.py`
- `scripts/rebuild_year_master.py`
- `retroverse-output/build_retroverse_support_1958_2024.py`

Migration note:

- do not move the old `scripts/` directory wholesale into `/pipelines`
- extract only the supported builders
- send the rest to `/archive/pipelines/legacy-root-scripts/`

### Phase 3. Move supported products under `/apps`

Move or plan these as supported:

- current root web app -> `/apps/web/`
- `retroverse-magazine/` -> `/apps/magazine/`

Important rule:

- move `retroverse-magazine/` as a whole first
- do not split its `scripts/`, `pipeline/`, `issues/`, and `tools/` internals during the first move
- first make it a clean app boundary, then refactor internals later

Outcome:

- the trunk gets a clear app boundary without forcing immediate magazine-internal surgery

### Phase 4. Archive experiments and generated clutter

Move these into `/archive`:

- `/archive/apps/`
  - `retroverse_chart/`
  - `retroverse_v0/`
  - `public/charts/`
- `/archive/pipelines/`
  - `tools/src/`
  - `retroverse-1974/`
  - unsupported root `scripts/`
- `/archive/artifacts/`
  - `dist/`
  - `dist-pipeline/`
  - `.netlify/`
  - `.next/` outputs if kept
- `/archive/runs/`
  - `runs/`
  - `retroverse-1974/runs/`

Outcome:

- the top-level tree stops mixing active source with legacy products and generated output

### Phase 5. Make pipelines reproducible

Reproducibility requirements for the stabilized trunk:

1. All supported pipelines must use repo-relative canonical data paths under `/data`.
2. No supported pipeline may hardcode `/Users/bobhopp/...`.
3. All required inputs must be declared in one config or manifest.
4. Every supported pipeline must have one documented entrypoint.
5. Generated outputs must write into `/data/derived` or `/data/published`, not into ambiguous ad hoc locations.

Concrete fixes needed:

- remove machine-specific DB and warehouse paths from magazine scripts
- remove hardcoded Dropbox VIDEO root from media pipeline code
- replace cwd-sensitive path logic with file-relative or manifest-based path resolution
- stop relying on `dist-pipeline/` as the source of truth for tools like `tools/api-selftest.mjs`

### Phase 6. Clean up documentation and command surface

1. Replace the root Vite template `README.md` with a real repository map.
2. Keep the architecture docs in `/docs`.
3. Document exactly:
   - which systems are trunk
   - which systems are archive
   - which dataset is canonical
   - which commands are supported

## 7. Final Recommended Trunk Shape

If stabilization is successful, the repository should read conceptually like this:

```text
/
  apps/
    web/
    magazine/

  pipelines/
    media-index/
    cards-1974/
    support-data/

  data/
    raw/
    derived/
    published/
    support/

  archive/
    apps/
    pipelines/
    artifacts/
    runs/

  docs/
```

## 8. Recommended Execution Order

1. Declare `raw-data/billboard-hot-100.db` the canonical Hot 100 source.
2. Repoint magazine context generation to that DB.
3. Define the `/data`, `/pipelines`, `/apps`, `/archive`, `/docs` layout in repo docs.
4. Extract supported builders into `/pipelines`.
5. Move supported products into `/apps`.
6. Archive all legacy apps, legacy pipelines, and generated artifacts.
7. Remove duplicate DB copies after compatibility shims are no longer needed.

This order preserves the working trunk first, then simplifies the repository around it.
