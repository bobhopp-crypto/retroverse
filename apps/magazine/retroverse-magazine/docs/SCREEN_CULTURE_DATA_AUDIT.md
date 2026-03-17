# Screen & Culture Data Audit

Overall coverage status: INCOMPLETE

## Thresholds

- Movies: >= 10
- Television: >= 15
- Cultural events: >= 8

## Source Detection

- `cultural_events_glob` (json_glob): `/Users/bobhopp/Sites/retroverse/cultural_events_1976.json` [targets: cultural_events]
- `cultural_events_glob` (json_glob): `/Users/bobhopp/Sites/retroverse/cultural_events_1977.json` [targets: cultural_events]
- `cultural_events_glob` (json_glob): `/Users/bobhopp/Sites/retroverse/cultural_events_1978.json` [targets: cultural_events]
- `cultural_events_glob` (json_glob): `/Users/bobhopp/Sites/retroverse/cultural_events_1979.json` [targets: cultural_events]
- `cultural_events_glob` (json_glob): `/Users/bobhopp/Sites/retroverse/cultural_events_1980.json` [targets: cultural_events]
- `cultural_events_glob` (json_glob): `/Users/bobhopp/Sites/retroverse/cultural_events_1981.json` [targets: cultural_events]
- `screen_culture_inventory` (json): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/screen_culture_inventory.json` [targets: cultural_events]
- `screen_culture_movies_by_year` (json): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/movies_by_year.json` [targets: cultural_events, movies]
- `screen_culture_movies_master` (json): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/movies_master.json` [targets: cultural_events, movies]
- `screen_culture_root_dir` (directory): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/movies_by_year.json` [targets: cultural_events]
- `screen_culture_root_dir` (directory): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/movies_master.json` [targets: cultural_events]
- `screen_culture_root_dir` (directory): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/screen_culture.db` [targets: cultural_events]
- `screen_culture_root_dir` (directory): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/screen_culture_inventory.json` [targets: cultural_events]
- `screen_culture_root_dir` (directory): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/television_by_year.json` [targets: cultural_events]
- `screen_culture_root_dir` (directory): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/television_master.json` [targets: cultural_events]
- `screen_culture_television_by_year` (json): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/television_by_year.json` [targets: cultural_events, television]
- `screen_culture_television_master` (json): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/television_master.json` [targets: cultural_events, television]
- `screen_culture_warehouse_db` (sqlite): `/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/warehouse/screen_culture.db` [targets: cultural_events]
- `year_master_json` (json): `/Users/bobhopp/Sites/retroverse/retroverse-output/retroverse_year_master_1958_2024.json` [targets: cultural_events, movies, television]

## Per-Year Counts

### Year: 1978

- Movies: 11 (OK)
- Television: 14 (LOW)
- Cultural events: 10 (OK)

Recommendation: Expand television for this year.

## Coverage Warnings

- Year 1978: below threshold for television

## Dataset Gaps

- Coverage remains incomplete for at least one required category/year.
