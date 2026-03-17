# Data Registry Implementation Report

Date: 2026-03-13

## Summary

Data Registry created to document datasets and their relationships to pipelines and applications. Documentation and validation tooling added. No code logic or file moves performed.

## Datasets Registered

| dataset_id | type | path | owner_pipeline | consumers |
|------------|------|------|----------------|-----------|
| billboard_hot_100 | raw | data/raw/charts/billboard-hot-100.db | pipelines/support-data | pipelines/cards-1974, pipelines/support-data, apps/web, apps/magazine |
| billboard_200_albums | raw | data/raw/charts/billboard-200-albums-charts.db | pipelines/support-data | pipelines/support-data |
| vdj_history | raw | data/raw/media/vdj_history_full.json | pipelines/media-index | pipelines/media-index |
| imdb_datasets | raw | data/raw/imdb/ | apps/magazine | apps/magazine, pipelines/support-data |
| screen_culture_dataset | raw | data/raw/screen-culture/ | apps/magazine | apps/magazine |
| media_index | derived | data/derived/media-index/ | pipelines/media-index | apps/web |
| cards_1974_dataset | derived | data/derived/cards/1974/ | pipelines/cards-1974 | apps/web, pipelines/cards-1974 |
| culture_derived_dataset | derived | data/derived/culture/ | pipelines/support-data | apps/web, apps/magazine |
| year_master_dataset | derived | data/derived/year-masters/ | pipelines/support-data | apps/web, apps/magazine, pipelines/cards-1974 |

## Pipelines Linked

| Pipeline | Datasets owned | Datasets consumed |
|----------|----------------|-------------------|
| pipelines/support-data | billboard_hot_100, billboard_200_albums, culture_derived_dataset, year_master_dataset | billboard_hot_100, billboard_200_albums, imdb_datasets, culture_derived_dataset, year_master_dataset |
| pipelines/media-index | vdj_history, media_index | vdj_history |
| pipelines/cards-1974 | cards_1974_dataset | billboard_hot_100, cards_1974_dataset, year_master_dataset |
| apps/web | — | media_index, cards_1974_dataset, culture_derived_dataset, year_master_dataset |
| apps/magazine | imdb_datasets, screen_culture_dataset | billboard_hot_100, imdb_datasets, screen_culture_dataset, culture_derived_dataset, year_master_dataset |

## Validation Results

```
Validating Data Registry...
Registry: data/registry/DATA_REGISTRY.yaml
Repo root: <repo>

[OK] All registered paths exist.

[UNREGISTERED] Paths in data/raw not in registry:
  - data/raw/imdb
  - data/raw/screen-culture

[UNREGISTERED] Paths in data/derived not in registry:
  - data/derived/culture
  - data/derived/year-masters
```

All five registered dataset paths exist. Unregistered paths reported for future registry expansion.

## Files Created

| Path | Purpose |
|------|---------|
| data/registry/ | Registry directory |
| data/registry/DATA_REGISTRY.yaml | Canonical dataset registry |
| docs/DATA_REGISTRY.md | Schema, layout, and usage documentation |
| pipelines/support-data/scripts/validate_registry.py | Validation script (report-only) |
| docs/DATA_REGISTRY_IMPLEMENTATION.md | This report |

## Registry Completion

### Newly Registered Datasets (2026-03-13)

| dataset_id | type | path | owner_pipeline | consumers |
|------------|------|------|----------------|-----------|
| imdb_datasets | raw | data/raw/imdb/ | apps/magazine | apps/magazine, pipelines/support-data |
| screen_culture_dataset | raw | data/raw/screen-culture/ | apps/magazine | apps/magazine |
| culture_derived_dataset | derived | data/derived/culture/ | pipelines/support-data | apps/web, apps/magazine |
| year_master_dataset | derived | data/derived/year-masters/ | pipelines/support-data | apps/web, apps/magazine, pipelines/cards-1974 |

### Validation Results (Post-Completion)

```
Validating Data Registry...
Registry: data/registry/DATA_REGISTRY.yaml
Repo root: <repo>

[OK] All registered paths exist. No unregistered datasets reported.
```

- No unregistered datasets remain
- All nine registered paths exist

### Registry Coverage Complete

The registry now fully describes the data layer:

| Category | Datasets |
|----------|----------|
| **Raw** | billboard_hot_100, billboard_200_albums, vdj_history, imdb_datasets, screen_culture_dataset |
| **Derived** | media_index, cards_1974_dataset, culture_derived_dataset, year_master_dataset |
| **Producers** | pipelines/support-data, pipelines/media-index, pipelines/cards-1974, apps/magazine |
| **Consumers** | apps/web, apps/magazine, pipelines/cards-1974, pipelines/support-data |

## Recommendations for Future Datasets

1. **Add data/support** — Consider a `support` type for datasets in `data/support/` (cultural support CSV, magazine archive harvest).
2. **Run validation in CI** — Add `python3 pipelines/support-data/scripts/validate_registry.py` to pre-commit or CI to catch path drift.
3. **Install PyYAML** — For cleaner YAML parsing, add `pyyaml` to `pipelines/support-data` or root requirements. The script includes a fallback parser when PyYAML is absent.
