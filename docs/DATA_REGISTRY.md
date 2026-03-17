# Data Registry

The Data Registry documents all datasets in the RetroVerse repository and their relationships to pipelines and applications. It provides a single source of truth for data locations, ownership, and consumption.

## Purpose

- **Discoverability** — Find where datasets live and who uses them
- **Traceability** — Understand data flow from raw inputs to derived outputs
- **Validation** — Verify paths exist and detect unregistered datasets
- **Onboarding** — Help contributors understand the data layer

## Dataset Schema

Each entry in `data/registry/DATA_REGISTRY.yaml` follows:

```yaml
datasets:
  dataset_id:
    type: raw | derived
    path: relative path in repository
    description: short explanation
    owner_pipeline: pipeline responsible for producing or maintaining it
    inputs:  # optional
      - upstream_dataset_id
    consumers:
      - apps or pipelines that read this dataset
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `raw` = canonical input, never overwritten by pipelines; `derived` = produced by a pipeline |
| `path` | Yes | Repository-relative path (e.g. `data/raw/charts/billboard-hot-100.db`) |
| `description` | Yes | One-line explanation of the dataset |
| `owner_pipeline` | Yes | Pipeline that produces or maintains the dataset |
| `inputs` | No | Upstream registered dataset IDs that feed this dataset |
| `consumers` | Yes | List of apps or pipelines that read this dataset |

## Data Directory Layout

| Directory | Purpose |
|-----------|---------|
| **data/raw** | Canonical raw inputs. Never overwritten by pipelines. Source of truth for external data (charts, VDJ history, IMDb, screen-culture warehouse). |
| **data/derived** | Outputs produced by pipelines. May be regenerated. Includes media-index, cards/1974, culture, year-masters. |
| **data/support** | Supporting datasets used by multiple pipelines (e.g. cultural support CSV, magazine archive harvest). Often hand-curated or produced by support-data pipeline. |
| **data/registry** | Registry metadata and documentation. Contains `DATA_REGISTRY.yaml` and validation outputs. |

## Adding New Datasets

1. Add an entry to `data/registry/DATA_REGISTRY.yaml`:
   - Choose a unique `dataset_id` (snake_case)
   - Set `type` to `raw` or `derived`
   - Use a repository-relative `path`
   - Set `owner_pipeline` to the pipeline that produces/maintains it
   - Optionally add `inputs` for upstream registered datasets
   - List all `consumers` that read it

2. Run validation:
   ```bash
   python3 pipelines/support-data/scripts/validate_registry.py
   ```

3. Update `docs/DATA_REGISTRY.md` if the schema changes.

## How Pipelines Should Reference Datasets

- **Read paths from the registry** — Prefer loading `DATA_REGISTRY.yaml` and resolving paths, rather than hardcoding.
- **Use repository-relative paths** — Resolve from repo root: `Path(__file__).resolve().parents[N] / registry_path`
- **Respect ownership** — Only the `owner_pipeline` should write to a dataset. Consumers read only.

## How Apps Should Consume Derived Data

- **Use published paths** — Apps typically consume data from `apps/web/public/data/` (synced from `data/derived/`) or via API.
- **Do not read raw data directly** — Apps should consume derived or published outputs, not raw inputs.
- **Check the registry** — Before adding a new data dependency, verify the dataset is registered and the path is correct.

## Cultural Datasets

Cultural datasets provide film, television, and media context for magazine generation, cultural pipelines, and chart storytelling.

### IMDb datasets (`data/raw/imdb/`)

IMDb public dataset snapshots (TSV exports) used for film and television metadata enrichment. Ingested by the magazine pipeline to populate movie and TV reference data. Supports year-context generation and cultural event anchoring.

### Screen-culture reference data (`data/raw/screen-culture/`)

Curated cultural datasets for movies, television, and media context. Includes warehouse files (`movies_by_year.json`, `television_by_year.json`, `screen_culture_inventory.json`) that power magazine year-context generation and story anchoring. The magazine app owns and maintains this data.

### Culture derived tables (`data/derived/culture/`)

Normalized cultural reference tables generated from multiple sources by the support-data pipeline. Includes `index/` (cultural week index) and `processed/` (billboard_hot100.csv, magazine_issues.csv, tv_listings.csv, radio_airplay.csv). Feeds apps/web and apps/magazine for cultural context and chart storytelling.

### Year master datasets (`data/derived/year-masters/`)

Yearly cultural summary datasets produced by the support-data pipeline. Includes `retroverse_year_master_1958_2024.json`, year-end CSVs, and related exports. Used for charts, 1974 cards, and magazine generation. Consumed by apps/web, apps/magazine, and pipelines/cards-1974.
