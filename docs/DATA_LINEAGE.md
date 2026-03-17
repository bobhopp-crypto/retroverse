# Data Lineage

Generated from `data/registry/DATA_REGISTRY.yaml`.

## Summary

- Datasets: 12
- Raw datasets: 5
- Derived datasets: 7
- Pipelines referenced: 3
- Apps referenced: 2
- Graph file: `docs/DATA_LINEAGE_GRAPH.dot`
- SVG file: `docs/DATA_LINEAGE_GRAPH.svg`

The `inputs` field captures only registered internal dataset dependencies. External APIs, manual editorial inputs, and unregistered transient sources are not represented here.

## Raw Datasets

| Dataset | Owner | Consumers | Path |
|---|---|---|---|
| `billboard_200_albums` | `pipelines/support-data` | `pipelines/support-data` | `data/raw/charts/billboard-200-albums-charts.db` |
| `billboard_hot_100` | `pipelines/support-data` | `pipelines/cards-1974, pipelines/support-data, apps/web, apps/magazine` | `data/raw/charts/billboard-hot-100.db` |
| `imdb_datasets` | `apps/magazine` | `apps/magazine, pipelines/support-data` | `data/raw/imdb/` |
| `screen_culture_dataset` | `apps/magazine` | `apps/magazine` | `data/raw/screen-culture/` |
| `vdj_history` | `pipelines/media-index` | `pipelines/media-index` | `data/raw/media/vdj_history_full.json` |

## Derived Datasets

| Dataset | Owner | Inputs | Consumers | Path |
|---|---|---|---|---|
| `cards_1974_dataset` | `pipelines/cards-1974` | none registered | `apps/web, pipelines/cards-1974` | `data/derived/cards/1974/` |
| `culture_derived_dataset` | `pipelines/support-data` | `billboard_hot_100` | `apps/web, apps/magazine` | `data/derived/culture/` |
| `media_index` | `pipelines/media-index` | `vdj_history`, `billboard_hot_100` | `apps/web` | `data/derived/media-index/` |
| `retroverse_support_cultural` | `pipelines/support-data` | none registered | `pipelines/support-data, apps/magazine` | `data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv` |
| `web_public_cards_1974` | `pipelines/cards-1974` | `cards_1974_dataset` | `apps/web, pipelines/cards-1974` | `apps/web/public/cards/1974` |
| `web_public_data` | `apps/web` | `media_index`, `cards_1974_dataset`, `billboard_hot_100`, `billboard_200_albums` | `apps/web, pipelines/media-index, pipelines/cards-1974, pipelines/support-data` | `apps/web/public/data` |
| `year_master_dataset` | `pipelines/support-data` | `billboard_hot_100`, `retroverse_support_cultural` | `apps/web, apps/magazine, pipelines/cards-1974` | `data/derived/year-masters/` |

## Producer And Consumer Map

### `apps/magazine`

- Kind: `app`
- Produces or maintains: `imdb_datasets`, `screen_culture_dataset`
- Consumes: `billboard_hot_100`, `culture_derived_dataset`, `imdb_datasets`, `retroverse_support_cultural`, `screen_culture_dataset`, `year_master_dataset`

### `apps/web`

- Kind: `app`
- Produces or maintains: `web_public_data`
- Consumes: `billboard_hot_100`, `cards_1974_dataset`, `culture_derived_dataset`, `media_index`, `web_public_cards_1974`, `web_public_data`, `year_master_dataset`

### `pipelines/cards-1974`

- Kind: `pipeline`
- Produces or maintains: `cards_1974_dataset`, `web_public_cards_1974`
- Consumes: `billboard_hot_100`, `cards_1974_dataset`, `web_public_cards_1974`, `web_public_data`, `year_master_dataset`

### `pipelines/media-index`

- Kind: `pipeline`
- Produces or maintains: `media_index`, `vdj_history`
- Consumes: `vdj_history`, `web_public_data`

### `pipelines/support-data`

- Kind: `pipeline`
- Produces or maintains: `billboard_200_albums`, `billboard_hot_100`, `culture_derived_dataset`, `retroverse_support_cultural`, `year_master_dataset`
- Consumes: `billboard_200_albums`, `billboard_hot_100`, `imdb_datasets`, `retroverse_support_cultural`, `web_public_data`

## Automatic Lineage Generation

The lineage graph is regenerated automatically at the end of successful runs for the support-data, media-index, and cards-1974 pipeline entrypoints.
The Graphviz DOT file at `docs/DATA_LINEAGE_GRAPH.dot` is the canonical lineage artifact.
The SVG companion at `docs/DATA_LINEAGE_GRAPH.svg` is rendered automatically when Graphviz is installed.

## Graph Rendering

Render or refresh the SVG manually with:

```bash
dot -Tsvg docs/DATA_LINEAGE_GRAPH.dot -o docs/DATA_LINEAGE_GRAPH.svg
```
