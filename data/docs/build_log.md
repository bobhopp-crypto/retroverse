# Master dataset build log

## Last run

- **When:** 2026-03-24 (see `data/master/retroverse_master.json` → `meta.generated_at_utc`)
- **Command:** `npm run build:master` (runs `tsx scripts/build_master_dataset.ts`)
- **Exit:** success
- **Duration (approx.):** ~115s on this machine (dominated by full scans of Billboard 200 `albums` + `acoustic_features` SQLite tables)

## Outputs

| Artifact | Path |
|----------|------|
| Schema inventory | `data/docs/schema_inventory.json` |
| Normalized JSON Schemas | `data/normalized/*.schema.json` |
| Master dataset | `data/master/retroverse_master.json` |

## Sources wired into the master builder

| Role | Path |
|------|------|
| Hot 100 export (latest mtime) | `data/derived/media-index/canonical/billboard_run_*.json` |
| VDJ library export (latest mtime) | `data/derived/media-index/canonical/vdj_library_run_*.json` |
| Year master | `data/derived/year-masters/retroverse_year_master_1958_2024.json` |
| Billboard 200 + acoustic features | `data/raw/charts/billboard-200-albums-charts.db` |
| Movies / TV (slimmed records) | `data/raw/screen-culture/screen-culture/warehouse/movies_master.json`, `television_master.json` |

## Matching rules

- **VDJ → Hot 100:** normalized `artist|title` exact match first; otherwise Fuse.js on the Hot 100 subset that shares the same two-letter normalized artist prefix (keeps fuzzy search fast). No full-catalog Fuse pass per video.
- **Songs → acoustic features:** normalized `artist|song` key against `acoustic_features`.
- **Songs → album attach:** best `albums` row per normalized artist (latest `date` string) among rows whose artist appears in the merged song set.
- **Movies / TV:** large `provenance` trees are omitted; top-level display/search fields are kept.

## Schema inventory

Generated with `npm run inventory:schema` (`tsx scripts/inventory_schema.ts`). Repeated pipeline files (e.g. many `billboard_run_*.json` with identical shape) are collapsed into one entry with a glob `path` and a note.

## Stats snapshot (see JSON for live numbers)

From the last successful build, `stats` included roughly: ~32k unified songs, ~8.7k VDJ videos, ~21k album rows (filtered to known artists), ~669 movies, ~646 TV rows, and VDJ↔Hot100 matches in the low thousands (exact + prefix-bucket fuzzy).
