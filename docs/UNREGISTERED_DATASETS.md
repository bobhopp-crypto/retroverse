# Unregistered Datasets

Generated from `data/registry/DATA_REGISTRY.yaml` by `pipelines/support-data/scripts/validate_registry.py`.

This report is advisory only. It does not modify the registry automatically.

## Summary

- Missing registered paths: 0
- Orphan top-level scan paths: 0
- Suggested registry entries: 22
- Ignored transient or backup artifacts: 0

Discovery scans `data/raw` and `data/derived`, ignores obvious transient artifacts, and suggests entries for unregistered child directories or files beneath registered dataset roots.

## Suggested Entries

| Suggested ID | Kind | Suggested Path | Basis |
|---|---|---|---|
| `derived_cards_1974_1974_card_render_report_json` | `file` | `data/derived/cards/1974/1974_card_render_report.json` | unregistered child of registered dataset `cards_1974_dataset` |
| `derived_cards_1974_1974_master_json` | `file` | `data/derived/cards/1974/1974_master.json` | unregistered child of registered dataset `cards_1974_dataset` |
| `derived_cards_1974_1974_weekly_context_json` | `file` | `data/derived/cards/1974/1974_weekly_context.json` | unregistered child of registered dataset `cards_1974_dataset` |
| `derived_cards_1974_1974_weekly_context_md` | `file` | `data/derived/cards/1974/1974_weekly_context.md` | unregistered child of registered dataset `cards_1974_dataset` |
| `derived_cards_1974_1974_weekly_context_parse_report_json` | `file` | `data/derived/cards/1974/1974_weekly_context.parse_report.json` | unregistered child of registered dataset `cards_1974_dataset` |
| `derived_cards_1974_retro_verse_1974_weekly_data_md` | `file` | `data/derived/cards/1974/retro-verse-1974-weekly-data.md` | unregistered child of registered dataset `cards_1974_dataset` |
| `derived_culture_index_dir` | `directory` | `data/derived/culture/index` | unregistered child of registered dataset `culture_derived_dataset` |
| `derived_culture_processed_dir` | `directory` | `data/derived/culture/processed` | unregistered child of registered dataset `culture_derived_dataset` |
| `derived_media_index_at40_dir` | `directory` | `data/derived/media-index/at40` | unregistered child of registered dataset `media_index` |
| `derived_media_index_canonical_dir` | `directory` | `data/derived/media-index/canonical` | unregistered child of registered dataset `media_index` |
| `derived_media_index_decisions_dir` | `directory` | `data/derived/media-index/decisions` | unregistered child of registered dataset `media_index` |
| `derived_media_index_inventory_dir` | `directory` | `data/derived/media-index/inventory` | unregistered child of registered dataset `media_index` |
| `derived_media_index_matching_dir` | `directory` | `data/derived/media-index/matching` | unregistered child of registered dataset `media_index` |
| `derived_media_index_output_dir` | `directory` | `data/derived/media-index/output` | unregistered child of registered dataset `media_index` |
| `derived_year_masters_legacy_dir` | `directory` | `data/derived/year-masters/legacy` | unregistered child of registered dataset `year_master_dataset` |
| `derived_year_masters_logs_dir` | `directory` | `data/derived/year-masters/logs` | unregistered child of registered dataset `year_master_dataset` |
| `derived_year_masters_retroverse_year_end_1958_2024_all_csv` | `file` | `data/derived/year-masters/retroverse_year_end_1958_2024_all.csv` | unregistered child of registered dataset `year_master_dataset` |
| `year_masters_retroverse_year_end_year_csv_family` | `file_family` | `data/derived/year-masters/retroverse_year_end_YYYY.csv` | grouped from 67 matching files under data/derived/year-masters |
| `year_masters_retroverse_year_end_year_top40_csv_family` | `file_family` | `data/derived/year-masters/retroverse_year_end_YYYY_top40.csv` | grouped from 67 matching files under data/derived/year-masters |
| `derived_year_masters_retroverse_year_master_1958_2024_json` | `file` | `data/derived/year-masters/retroverse_year_master_1958_2024.json` | unregistered child of registered dataset `year_master_dataset` |
| `raw_imdb_imdb_dir` | `directory` | `data/raw/imdb/imdb` | unregistered child of registered dataset `imdb_datasets` |
| `raw_screen_culture_screen_culture_dir` | `directory` | `data/raw/screen-culture/screen-culture` | unregistered child of registered dataset `screen_culture_dataset` |

## Suggested YAML Entries

These entries are suggestions only. Review the path granularity, owners, descriptions, inputs, and consumers before copying them into `DATA_REGISTRY.yaml`.

### `derived_cards_1974_1974_card_render_report_json`

- Kind: `file`
- Suggested path: `data/derived/cards/1974/1974_card_render_report.json`
- Basis: unregistered child of registered dataset `cards_1974_dataset`
- Nearest registered dataset: `cards_1974_dataset`

```yaml
derived_cards_1974_1974_card_render_report_json:
  type: derived
  path: data/derived/cards/1974/1974_card_render_report.json
  description: TODO: describe unregistered file dataset at data/derived/cards/1974/1974_card_render_report.json.
  owner_pipeline: pipelines/cards-1974
  consumers:
    - apps/web
    - pipelines/cards-1974
```

### `derived_cards_1974_1974_master_json`

- Kind: `file`
- Suggested path: `data/derived/cards/1974/1974_master.json`
- Basis: unregistered child of registered dataset `cards_1974_dataset`
- Nearest registered dataset: `cards_1974_dataset`

```yaml
derived_cards_1974_1974_master_json:
  type: derived
  path: data/derived/cards/1974/1974_master.json
  description: TODO: describe unregistered file dataset at data/derived/cards/1974/1974_master.json.
  owner_pipeline: pipelines/cards-1974
  consumers:
    - apps/web
    - pipelines/cards-1974
```

### `derived_cards_1974_1974_weekly_context_json`

- Kind: `file`
- Suggested path: `data/derived/cards/1974/1974_weekly_context.json`
- Basis: unregistered child of registered dataset `cards_1974_dataset`
- Nearest registered dataset: `cards_1974_dataset`

```yaml
derived_cards_1974_1974_weekly_context_json:
  type: derived
  path: data/derived/cards/1974/1974_weekly_context.json
  description: TODO: describe unregistered file dataset at data/derived/cards/1974/1974_weekly_context.json.
  owner_pipeline: pipelines/cards-1974
  consumers:
    - apps/web
    - pipelines/cards-1974
```

### `derived_cards_1974_1974_weekly_context_md`

- Kind: `file`
- Suggested path: `data/derived/cards/1974/1974_weekly_context.md`
- Basis: unregistered child of registered dataset `cards_1974_dataset`
- Nearest registered dataset: `cards_1974_dataset`

```yaml
derived_cards_1974_1974_weekly_context_md:
  type: derived
  path: data/derived/cards/1974/1974_weekly_context.md
  description: TODO: describe unregistered file dataset at data/derived/cards/1974/1974_weekly_context.md.
  owner_pipeline: pipelines/cards-1974
  consumers:
    - apps/web
    - pipelines/cards-1974
```

### `derived_cards_1974_1974_weekly_context_parse_report_json`

- Kind: `file`
- Suggested path: `data/derived/cards/1974/1974_weekly_context.parse_report.json`
- Basis: unregistered child of registered dataset `cards_1974_dataset`
- Nearest registered dataset: `cards_1974_dataset`

```yaml
derived_cards_1974_1974_weekly_context_parse_report_json:
  type: derived
  path: data/derived/cards/1974/1974_weekly_context.parse_report.json
  description: TODO: describe unregistered file dataset at data/derived/cards/1974/1974_weekly_context.parse_report.json.
  owner_pipeline: pipelines/cards-1974
  consumers:
    - apps/web
    - pipelines/cards-1974
```

### `derived_cards_1974_retro_verse_1974_weekly_data_md`

- Kind: `file`
- Suggested path: `data/derived/cards/1974/retro-verse-1974-weekly-data.md`
- Basis: unregistered child of registered dataset `cards_1974_dataset`
- Nearest registered dataset: `cards_1974_dataset`

```yaml
derived_cards_1974_retro_verse_1974_weekly_data_md:
  type: derived
  path: data/derived/cards/1974/retro-verse-1974-weekly-data.md
  description: TODO: describe unregistered file dataset at data/derived/cards/1974/retro-verse-1974-weekly-data.md.
  owner_pipeline: pipelines/cards-1974
  consumers:
    - apps/web
    - pipelines/cards-1974
```

### `derived_culture_index_dir`

- Kind: `directory`
- Suggested path: `data/derived/culture/index`
- Basis: unregistered child of registered dataset `culture_derived_dataset`
- Nearest registered dataset: `culture_derived_dataset`

```yaml
derived_culture_index_dir:
  type: derived
  path: data/derived/culture/index
  description: TODO: describe unregistered directory dataset at data/derived/culture/index.
  owner_pipeline: pipelines/support-data
  inputs:
    - billboard_hot_100
  consumers:
    - apps/web
    - apps/magazine
```

### `derived_culture_processed_dir`

- Kind: `directory`
- Suggested path: `data/derived/culture/processed`
- Basis: unregistered child of registered dataset `culture_derived_dataset`
- Nearest registered dataset: `culture_derived_dataset`

```yaml
derived_culture_processed_dir:
  type: derived
  path: data/derived/culture/processed
  description: TODO: describe unregistered directory dataset at data/derived/culture/processed.
  owner_pipeline: pipelines/support-data
  inputs:
    - billboard_hot_100
  consumers:
    - apps/web
    - apps/magazine
```

### `derived_media_index_at40_dir`

- Kind: `directory`
- Suggested path: `data/derived/media-index/at40`
- Basis: unregistered child of registered dataset `media_index`
- Nearest registered dataset: `media_index`

```yaml
derived_media_index_at40_dir:
  type: derived
  path: data/derived/media-index/at40
  description: TODO: describe unregistered directory dataset at data/derived/media-index/at40.
  owner_pipeline: pipelines/media-index
  inputs:
    - vdj_history
    - billboard_hot_100
  consumers:
    - apps/web
```

### `derived_media_index_canonical_dir`

- Kind: `directory`
- Suggested path: `data/derived/media-index/canonical`
- Basis: unregistered child of registered dataset `media_index`
- Nearest registered dataset: `media_index`

```yaml
derived_media_index_canonical_dir:
  type: derived
  path: data/derived/media-index/canonical
  description: TODO: describe unregistered directory dataset at data/derived/media-index/canonical.
  owner_pipeline: pipelines/media-index
  inputs:
    - vdj_history
    - billboard_hot_100
  consumers:
    - apps/web
```

### `derived_media_index_decisions_dir`

- Kind: `directory`
- Suggested path: `data/derived/media-index/decisions`
- Basis: unregistered child of registered dataset `media_index`
- Nearest registered dataset: `media_index`

```yaml
derived_media_index_decisions_dir:
  type: derived
  path: data/derived/media-index/decisions
  description: TODO: describe unregistered directory dataset at data/derived/media-index/decisions.
  owner_pipeline: pipelines/media-index
  inputs:
    - vdj_history
    - billboard_hot_100
  consumers:
    - apps/web
```

### `derived_media_index_inventory_dir`

- Kind: `directory`
- Suggested path: `data/derived/media-index/inventory`
- Basis: unregistered child of registered dataset `media_index`
- Nearest registered dataset: `media_index`

```yaml
derived_media_index_inventory_dir:
  type: derived
  path: data/derived/media-index/inventory
  description: TODO: describe unregistered directory dataset at data/derived/media-index/inventory.
  owner_pipeline: pipelines/media-index
  inputs:
    - vdj_history
    - billboard_hot_100
  consumers:
    - apps/web
```

### `derived_media_index_matching_dir`

- Kind: `directory`
- Suggested path: `data/derived/media-index/matching`
- Basis: unregistered child of registered dataset `media_index`
- Nearest registered dataset: `media_index`

```yaml
derived_media_index_matching_dir:
  type: derived
  path: data/derived/media-index/matching
  description: TODO: describe unregistered directory dataset at data/derived/media-index/matching.
  owner_pipeline: pipelines/media-index
  inputs:
    - vdj_history
    - billboard_hot_100
  consumers:
    - apps/web
```

### `derived_media_index_output_dir`

- Kind: `directory`
- Suggested path: `data/derived/media-index/output`
- Basis: unregistered child of registered dataset `media_index`
- Nearest registered dataset: `media_index`

```yaml
derived_media_index_output_dir:
  type: derived
  path: data/derived/media-index/output
  description: TODO: describe unregistered directory dataset at data/derived/media-index/output.
  owner_pipeline: pipelines/media-index
  inputs:
    - vdj_history
    - billboard_hot_100
  consumers:
    - apps/web
```

### `derived_year_masters_legacy_dir`

- Kind: `directory`
- Suggested path: `data/derived/year-masters/legacy`
- Basis: unregistered child of registered dataset `year_master_dataset`
- Nearest registered dataset: `year_master_dataset`

```yaml
derived_year_masters_legacy_dir:
  type: derived
  path: data/derived/year-masters/legacy
  description: TODO: describe unregistered directory dataset at data/derived/year-masters/legacy.
  owner_pipeline: pipelines/support-data
  inputs:
    - billboard_hot_100
    - retroverse_support_cultural
  consumers:
    - apps/web
    - apps/magazine
    - pipelines/cards-1974
```

### `derived_year_masters_logs_dir`

- Kind: `directory`
- Suggested path: `data/derived/year-masters/logs`
- Basis: unregistered child of registered dataset `year_master_dataset`
- Nearest registered dataset: `year_master_dataset`

```yaml
derived_year_masters_logs_dir:
  type: derived
  path: data/derived/year-masters/logs
  description: TODO: describe unregistered directory dataset at data/derived/year-masters/logs.
  owner_pipeline: pipelines/support-data
  inputs:
    - billboard_hot_100
    - retroverse_support_cultural
  consumers:
    - apps/web
    - apps/magazine
    - pipelines/cards-1974
```

### `derived_year_masters_retroverse_year_end_1958_2024_all_csv`

- Kind: `file`
- Suggested path: `data/derived/year-masters/retroverse_year_end_1958_2024_all.csv`
- Basis: unregistered child of registered dataset `year_master_dataset`
- Nearest registered dataset: `year_master_dataset`

```yaml
derived_year_masters_retroverse_year_end_1958_2024_all_csv:
  type: derived
  path: data/derived/year-masters/retroverse_year_end_1958_2024_all.csv
  description: TODO: describe unregistered file dataset at data/derived/year-masters/retroverse_year_end_1958_2024_all.csv.
  owner_pipeline: pipelines/support-data
  inputs:
    - billboard_hot_100
    - retroverse_support_cultural
  consumers:
    - apps/web
    - apps/magazine
    - pipelines/cards-1974
```

### `year_masters_retroverse_year_end_year_csv_family`

- Kind: `file_family`
- Suggested path: `data/derived/year-masters/retroverse_year_end_YYYY.csv`
- Basis: grouped from 67 matching files under data/derived/year-masters
- Nearest registered dataset: `year_master_dataset`
- Matching paths grouped: 67

Matched paths:
- `data/derived/year-masters/retroverse_year_end_1958.csv`
- `data/derived/year-masters/retroverse_year_end_1959.csv`
- `data/derived/year-masters/retroverse_year_end_1960.csv`
- `data/derived/year-masters/retroverse_year_end_1961.csv`
- `data/derived/year-masters/retroverse_year_end_1962.csv`
- `data/derived/year-masters/retroverse_year_end_1963.csv`
- `data/derived/year-masters/retroverse_year_end_1964.csv`
- `data/derived/year-masters/retroverse_year_end_1965.csv`
- `data/derived/year-masters/retroverse_year_end_1966.csv`
- `data/derived/year-masters/retroverse_year_end_1967.csv`
- `data/derived/year-masters/retroverse_year_end_1968.csv`
- `data/derived/year-masters/retroverse_year_end_1969.csv`
- ... 55 more

```yaml
year_masters_retroverse_year_end_year_csv_family:
  type: derived
  path: data/derived/year-masters/retroverse_year_end_YYYY.csv
  description: TODO: describe unregistered file family at data/derived/year-masters/retroverse_year_end_YYYY.csv (67 matching files discovered).
  owner_pipeline: pipelines/support-data
  inputs:
    - billboard_hot_100
    - retroverse_support_cultural
  consumers:
    - apps/web
    - apps/magazine
    - pipelines/cards-1974
```

### `year_masters_retroverse_year_end_year_top40_csv_family`

- Kind: `file_family`
- Suggested path: `data/derived/year-masters/retroverse_year_end_YYYY_top40.csv`
- Basis: grouped from 67 matching files under data/derived/year-masters
- Nearest registered dataset: `year_master_dataset`
- Matching paths grouped: 67

Matched paths:
- `data/derived/year-masters/retroverse_year_end_1958_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1959_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1960_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1961_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1962_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1963_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1964_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1965_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1966_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1967_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1968_top40.csv`
- `data/derived/year-masters/retroverse_year_end_1969_top40.csv`
- ... 55 more

```yaml
year_masters_retroverse_year_end_year_top40_csv_family:
  type: derived
  path: data/derived/year-masters/retroverse_year_end_YYYY_top40.csv
  description: TODO: describe unregistered file family at data/derived/year-masters/retroverse_year_end_YYYY_top40.csv (67 matching files discovered).
  owner_pipeline: pipelines/support-data
  inputs:
    - billboard_hot_100
    - retroverse_support_cultural
  consumers:
    - apps/web
    - apps/magazine
    - pipelines/cards-1974
```

### `derived_year_masters_retroverse_year_master_1958_2024_json`

- Kind: `file`
- Suggested path: `data/derived/year-masters/retroverse_year_master_1958_2024.json`
- Basis: unregistered child of registered dataset `year_master_dataset`
- Nearest registered dataset: `year_master_dataset`

```yaml
derived_year_masters_retroverse_year_master_1958_2024_json:
  type: derived
  path: data/derived/year-masters/retroverse_year_master_1958_2024.json
  description: TODO: describe unregistered file dataset at data/derived/year-masters/retroverse_year_master_1958_2024.json.
  owner_pipeline: pipelines/support-data
  inputs:
    - billboard_hot_100
    - retroverse_support_cultural
  consumers:
    - apps/web
    - apps/magazine
    - pipelines/cards-1974
```

### `raw_imdb_imdb_dir`

- Kind: `directory`
- Suggested path: `data/raw/imdb/imdb`
- Basis: unregistered child of registered dataset `imdb_datasets`
- Nearest registered dataset: `imdb_datasets`

```yaml
raw_imdb_imdb_dir:
  type: raw
  path: data/raw/imdb/imdb
  description: TODO: describe unregistered directory dataset at data/raw/imdb/imdb.
  owner_pipeline: apps/magazine
  consumers:
    - apps/magazine
    - pipelines/support-data
```

### `raw_screen_culture_screen_culture_dir`

- Kind: `directory`
- Suggested path: `data/raw/screen-culture/screen-culture`
- Basis: unregistered child of registered dataset `screen_culture_dataset`
- Nearest registered dataset: `screen_culture_dataset`

```yaml
raw_screen_culture_screen_culture_dir:
  type: raw
  path: data/raw/screen-culture/screen-culture
  description: TODO: describe unregistered directory dataset at data/raw/screen-culture/screen-culture.
  owner_pipeline: apps/magazine
  consumers:
    - apps/magazine
```
