# Repository Architecture Audit

Generated: 2026-03-14 15:47:57
Repository root: `/Users/bobhopp/Sites/retroverse`

Observed root layout uses the migrated `apps/`, `data/`, `pipelines/`, and `archive/` structure.

## Repository Tree

```text
retroverse/
├── .netlify/
│   ├── functions/
│   │   ├── billboard.zip
│   │   └── manifest.json
│   ├── functions-internal/
│   ├── v1/
│   │   └── functions/
│   └── netlify.toml
├── .tmp.drivedownload/
├── .tmp.driveupload/
│   └── 199168
├── .vscode/
│   └── tasks.json
├── apps/
│   ├── magazine/
│   │   ├── retroverse-magazine/
│   │   │   ├── .cursor/
│   │   │   ├── archive/
│   │   │   ├── art-library/
│   │   │   ├── artifacts/
│   │   │   ├── assets/
│   │   │   ├── charter/
│   │   │   ├── data/
│   │   │   ├── docs/
│   │   │   ├── INSPECT_1978_IMAGES/
│   │   │   ├── issues/
│   │   │   ├── layout-library/
│   │   │   ├── logs/
│   │   │   ├── pipeline/
│   │   │   ├── prompts/
│   │   │   ├── scripts/
│   │   │   ├── templates/
│   │   │   ├── tools/
│   │   │   ├── workflow/
│   │   │   ├── .DS_Store
│   │   │   ├── .env
│   │   │   ├── .gitignore
│   │   │   ├── DATA_INVENTORY.md
│   │   │   ├── ISSUE_STRUCTURE_REPORT.md
│   │   │   ├── MAGAZINE_PIPELINE_AUDIT.md
│   │   │   ├── magazine_template.html
│   │   │   ├── name
│   │   │   ├── PIPELINE_REPAIR_IMPLEMENTATION.md
│   │   │   ├── PIPELINE_REPAIR_REPORT.md
│   │   │   ├── PRESS_CHECK_1978.md
│   │   │   ├── PROJECT_AUDIT.md
│   │   │   ├── PROJECT_STATE.md
│   │   │   └── requirements.txt
│   │   └── .DS_Store
│   └── web/
│       ├── api/
│       │   └── server.ts
│       ├── dist/
│       │   ├── 1974/
│       │   ├── assets/
│       │   ├── cards/
│       │   ├── data/
│       │   ├── images/
│       │   ├── magazine/
│       │   ├── .DS_Store
│       │   ├── _redirects
│       │   ├── index.html
│       │   ├── thumbnail-placeholder.svg
│       │   └── vite.svg
│       ├── netlify/
│       │   └── functions/
│       ├── public/
│       │   ├── 1974/
│       │   ├── cards/
│       │   ├── data/
│       │   ├── images/
│       │   ├── magazine/
│       │   ├── .DS_Store
│       │   ├── _redirects
│       │   ├── thumbnail-placeholder.svg
│       │   └── vite.svg
│       ├── src/
│       │   ├── assets/
│       │   ├── components/
│       │   ├── config/
│       │   ├── context/
│       │   ├── data/
│       │   ├── design/
│       │   ├── hooks/
│       │   ├── lib/
│       │   ├── pages/
│       │   ├── state/
│       │   ├── theme/
│       │   ├── .DS_Store
│       │   ├── App.css
│       │   ├── App.tsx
│       │   ├── index.css
│       │   └── main.tsx
│       ├── tools/
│       │   └── autoUpdate.ts
│       └── index.html
├── archive/
│   ├── apps/
│   │   ├── public-charts/
│   │   │   ├── _next/
│   │   │   ├── _not-found/
│   │   │   ├── data/
│   │   │   ├── 404.html
│   │   │   ├── __next.__PAGE__.txt
│   │   │   ├── __next._full.txt
│   │   │   ├── __next._head.txt
│   │   │   ├── __next._index.txt
│   │   │   ├── __next._tree.txt
│   │   │   ├── _not-found.html
│   │   │   ├── _not-found.txt
│   │   │   ├── apple-icon.png
│   │   │   ├── icon-dark-32x32.png
│   │   │   ├── icon-light-32x32.png
│   │   │   ├── icon.svg
│   │   │   ├── index.html
│   │   │   ├── index.txt
│   │   │   ├── placeholder-logo.png
│   │   │   ├── placeholder-logo.svg
│   │   │   ├── placeholder-user.jpg
│   │   │   ├── placeholder.jpg
│   │   │   └── placeholder.svg
│   │   ├── retroverse_chart/
│   │   │   ├── .next/
│   │   │   ├── app/
│   │   │   ├── charts/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── lib/
│   │   │   ├── public/
│   │   │   ├── scripts/
│   │   │   ├── styles/
│   │   │   ├── .gitignore
│   │   │   ├── components.json
│   │   │   ├── next-env.d.ts
│   │   │   ├── next.config.mjs
│   │   │   ├── package-lock.json
│   │   │   ├── package.json
│   │   │   ├── pnpm-lock.yaml
│   │   │   ├── postcss.config.mjs
│   │   │   └── tsconfig.json
│   │   └── retroverse_v0/
│   │       ├── .next/
│   │       ├── app/
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── lib/
│   │       ├── public/
│   │       ├── styles/
│   │       ├── .gitignore
│   │       ├── components.json
│   │       ├── export_billboard_json.py
│   │       ├── next-env.d.ts
│   │       ├── next.config.mjs
│   │       ├── package-lock.json
│   │       ├── package.json
│   │       ├── pnpm-lock.yaml
│   │       ├── postcss.config.mjs
│   │       └── tsconfig.json
│   ├── artifacts/
│   │   ├── artifacts-remainder/
│   │   │   ├── .DS_Store
│   │   │   └── .pipeline_alive
│   │   ├── dist/
│   │   │   ├── 1974/
│   │   │   ├── assets/
│   │   │   ├── cards/
│   │   │   ├── charts/
│   │   │   ├── data/
│   │   │   ├── images/
│   │   │   ├── magazine/
│   │   │   ├── .DS_Store
│   │   │   ├── _redirects
│   │   │   ├── index.html
│   │   │   ├── thumbnail-placeholder.svg
│   │   │   └── vite.svg
│   │   ├── dist-pipeline/
│   │   │   ├── config/
│   │   │   ├── ingest/
│   │   │   ├── modules/
│   │   │   ├── scripts/
│   │   │   ├── utils/
│   │   │   ├── index.d.ts
│   │   │   ├── index.js
│   │   │   ├── server.d.ts
│   │   │   ├── server.js
│   │   │   ├── types.d.ts
│   │   │   └── types.js
│   │   ├── logs/
│   │   │   └── pipeline.log
│   │   ├── retroverse-output-decks/
│   │   │   ├── 1974/
│   │   │   ├── 1975/
│   │   │   ├── 1976/
│   │   │   ├── 1977/
│   │   │   └── 1978/
│   │   ├── retroverse-output-remainder/
│   │   │   ├── .venv/
│   │   │   └── .DS_Store
│   │   ├── retroverse-support-remainder/
│   │   ├── runs/
│   │   │   ├── deck_1974/
│   │   │   ├── deck_1974_partial_3/
│   │   │   ├── deck_1975/
│   │   │   ├── deck_1975_partial_8/
│   │   │   ├── deck_1976_diamonds/
│   │   │   ├── deck_1977_spades/
│   │   │   ├── deck_1978_hearts/
│   │   │   ├── deck_1978_hearts_partial_A/
│   │   │   ├── deck_1978_hearts_partial_A-2-3/
│   │   │   ├── deck_1978_hearts_partial_A-2-3-4/
│   │   │   ├── deck_1978_hearts_partial_A-2-3-4-5/
│   │   │   ├── deck_1979_clubs/
│   │   │   ├── deck_1980_diamonds/
│   │   │   └── deck_1981_spades/
│   │   ├── and
│   │   ├── dsm_webstack_repair.sh
│   │   ├── history_collect.py
│   │   ├── minimal
│   │   ├── readable
│   │   └── remains
│   ├── docs/
│   │   └── Journal/
│   │       ├── rv_journal.md
│   │       └── rv_journal.md alias
│   └── pipelines/
│       ├── legacy-root-scripts/
│       │   ├── build_multi_year_retroverse_decks.py
│       │   ├── compose_1974_deck.py
│       │   ├── dsm-web-stack-forensics.sh
│       │   ├── fix_1978_magazine.py
│       │   ├── generate-artist-gravity.js
│       │   ├── generate-artist-timelines.js
│       │   ├── generate_1974_deck.py
│       │   ├── generate_at40_week30_rank01.py
│       │   ├── generate_retroverse_1974_week30_top5.py
│       │   ├── render-1974-playing-card.mjs
│       │   ├── render-week-30-cards.mjs
│       │   └── render-week-30-illustrated.mjs
│       ├── retroverse-1974/
│       │   ├── .venv/
│       │   ├── data/
│       │   ├── out/
│       │   ├── pipeline/
│       │   ├── runs/
│       │   ├── .DS_Store
│       │   ├── .env.example
│       │   ├── README.md
│       │   └── requirements.txt
│       ├── retroverse-data/
│       │   └── databases/
│       └── tools-legacy/
│           ├── media-normalization/
│           ├── sample-data/
│           ├── src/
│           ├── .DS_Store
│           ├── faststart_mp4.scpt
│           ├── faststart_mp4.sh
│           ├── package.json
│           ├── pipeline.config.json
│           ├── README.md
│           ├── tierMapping.test.ts
│           └── tsconfig.json
├── data/
│   ├── derived/
│   │   ├── cards/
│   │   │   └── 1974/
│   │   ├── culture/
│   │   │   ├── index/
│   │   │   └── processed/
│   │   ├── media-index/
│   │   │   ├── at40/
│   │   │   ├── canonical/
│   │   │   ├── decisions/
│   │   │   ├── inventory/
│   │   │   ├── matching/
│   │   │   └── output/
│   │   └── year-masters/
│   │       ├── legacy/
│   │       ├── logs/
│   │       ├── retroverse_year_end_1958.csv
│   │       ├── retroverse_year_end_1958_2024_all.csv
│   │       ├── retroverse_year_end_1958_top40.csv
│   │       ├── retroverse_year_end_1959.csv
│   │       ├── retroverse_year_end_1959_top40.csv
│   │       ├── retroverse_year_end_1960.csv
│   │       ├── retroverse_year_end_1960_top40.csv
│   │       ├── retroverse_year_end_1961.csv
│   │       ├── retroverse_year_end_1961_top40.csv
│   │       ├── retroverse_year_end_1962.csv
│   │       ├── retroverse_year_end_1962_top40.csv
│   │       ├── retroverse_year_end_1963.csv
│   │       ├── retroverse_year_end_1963_top40.csv
│   │       ├── retroverse_year_end_1964.csv
│   │       ├── retroverse_year_end_1964_top40.csv
│   │       ├── retroverse_year_end_1965.csv
│   │       ├── retroverse_year_end_1965_top40.csv
│   │       ├── retroverse_year_end_1966.csv
│   │       ├── retroverse_year_end_1966_top40.csv
│   │       ├── retroverse_year_end_1967.csv
│   │       ├── retroverse_year_end_1967_top40.csv
│   │       ├── retroverse_year_end_1968.csv
│   │       ├── retroverse_year_end_1968_top40.csv
│   │       ├── retroverse_year_end_1969.csv
│   │       ├── retroverse_year_end_1969_top40.csv
│   │       ├── retroverse_year_end_1970.csv
│   │       ├── retroverse_year_end_1970_top40.csv
│   │       ├── retroverse_year_end_1971.csv
│   │       ├── retroverse_year_end_1971_top40.csv
│   │       ├── retroverse_year_end_1972.csv
│   │       ├── retroverse_year_end_1972_top40.csv
│   │       ├── retroverse_year_end_1973.csv
│   │       ├── retroverse_year_end_1973_top40.csv
│   │       ├── retroverse_year_end_1974.csv
│   │       ├── retroverse_year_end_1974_top40.csv
│   │       ├── retroverse_year_end_1975.csv
│   │       ├── retroverse_year_end_1975_top40.csv
│   │       ├── retroverse_year_end_1976.csv
│   │       ├── retroverse_year_end_1976_top40.csv
│   │       ├── retroverse_year_end_1977.csv
│   │       ├── retroverse_year_end_1977_top40.csv
│   │       ├── retroverse_year_end_1978.csv
│   │       ├── retroverse_year_end_1978_top40.csv
│   │       ├── retroverse_year_end_1979.csv
│   │       ├── retroverse_year_end_1979_top40.csv
│   │       ├── retroverse_year_end_1980.csv
│   │       ├── retroverse_year_end_1980_top40.csv
│   │       ├── retroverse_year_end_1981.csv
│   │       ├── retroverse_year_end_1981_top40.csv
│   │       ├── retroverse_year_end_1982.csv
│   │       ├── retroverse_year_end_1982_top40.csv
│   │       ├── retroverse_year_end_1983.csv
│   │       ├── retroverse_year_end_1983_top40.csv
│   │       ├── retroverse_year_end_1984.csv
│   │       ├── retroverse_year_end_1984_top40.csv
│   │       ├── retroverse_year_end_1985.csv
│   │       ├── retroverse_year_end_1985_top40.csv
│   │       ├── retroverse_year_end_1986.csv
│   │       ├── retroverse_year_end_1986_top40.csv
│   │       ├── retroverse_year_end_1987.csv
│   │       ├── retroverse_year_end_1987_top40.csv
│   │       ├── retroverse_year_end_1988.csv
│   │       ├── retroverse_year_end_1988_top40.csv
│   │       ├── retroverse_year_end_1989.csv
│   │       ├── retroverse_year_end_1989_top40.csv
│   │       ├── retroverse_year_end_1990.csv
│   │       ├── retroverse_year_end_1990_top40.csv
│   │       ├── retroverse_year_end_1991.csv
│   │       ├── retroverse_year_end_1991_top40.csv
│   │       ├── retroverse_year_end_1992.csv
│   │       ├── retroverse_year_end_1992_top40.csv
│   │       ├── retroverse_year_end_1993.csv
│   │       ├── retroverse_year_end_1993_top40.csv
│   │       ├── retroverse_year_end_1994.csv
│   │       ├── retroverse_year_end_1994_top40.csv
│   │       ├── retroverse_year_end_1995.csv
│   │       ├── retroverse_year_end_1995_top40.csv
│   │       ├── retroverse_year_end_1996.csv
│   │       ├── retroverse_year_end_1996_top40.csv
│   │       ├── retroverse_year_end_1997.csv
│   │       ├── retroverse_year_end_1997_top40.csv
│   │       ├── retroverse_year_end_1998.csv
│   │       ├── retroverse_year_end_1998_top40.csv
│   │       ├── retroverse_year_end_1999.csv
│   │       ├── retroverse_year_end_1999_top40.csv
│   │       ├── retroverse_year_end_2000.csv
│   │       ├── retroverse_year_end_2000_top40.csv
│   │       ├── retroverse_year_end_2001.csv
│   │       ├── retroverse_year_end_2001_top40.csv
│   │       ├── retroverse_year_end_2002.csv
│   │       ├── retroverse_year_end_2002_top40.csv
│   │       ├── retroverse_year_end_2003.csv
│   │       ├── retroverse_year_end_2003_top40.csv
│   │       ├── retroverse_year_end_2004.csv
│   │       ├── retroverse_year_end_2004_top40.csv
│   │       ├── retroverse_year_end_2005.csv
│   │       ├── retroverse_year_end_2005_top40.csv
│   │       ├── retroverse_year_end_2006.csv
│   │       ├── retroverse_year_end_2006_top40.csv
│   │       ├── retroverse_year_end_2007.csv
│   │       ├── retroverse_year_end_2007_top40.csv
│   │       ├── retroverse_year_end_2008.csv
│   │       ├── retroverse_year_end_2008_top40.csv
│   │       ├── retroverse_year_end_2009.csv
│   │       ├── retroverse_year_end_2009_top40.csv
│   │       ├── retroverse_year_end_2010.csv
│   │       ├── retroverse_year_end_2010_top40.csv
│   │       ├── retroverse_year_end_2011.csv
│   │       ├── retroverse_year_end_2011_top40.csv
│   │       ├── retroverse_year_end_2012.csv
│   │       ├── retroverse_year_end_2012_top40.csv
│   │       ├── retroverse_year_end_2013.csv
│   │       ├── retroverse_year_end_2013_top40.csv
│   │       ├── retroverse_year_end_2014.csv
│   │       ├── retroverse_year_end_2014_top40.csv
│   │       ├── retroverse_year_end_2015.csv
│   │       ├── retroverse_year_end_2015_top40.csv
│   │       ├── retroverse_year_end_2016.csv
│   │       ├── retroverse_year_end_2016_top40.csv
│   │       ├── retroverse_year_end_2017.csv
│   │       ├── retroverse_year_end_2017_top40.csv
│   │       ├── retroverse_year_end_2018.csv
│   │       ├── retroverse_year_end_2018_top40.csv
│   │       ├── retroverse_year_end_2019.csv
│   │       ├── retroverse_year_end_2019_top40.csv
│   │       ├── retroverse_year_end_2020.csv
│   │       ├── retroverse_year_end_2020_top40.csv
│   │       ├── retroverse_year_end_2021.csv
│   │       ├── retroverse_year_end_2021_top40.csv
│   │       ├── retroverse_year_end_2022.csv
│   │       ├── retroverse_year_end_2022_top40.csv
│   │       ├── retroverse_year_end_2023.csv
│   │       ├── retroverse_year_end_2023_top40.csv
│   │       ├── retroverse_year_end_2024.csv
│   │       ├── retroverse_year_end_2024_top40.csv
│   │       └── retroverse_year_master_1958_2024.json
│   ├── raw/
│   │   ├── charts/
│   │   │   ├── billboard-200-albums-charts.db
│   │   │   └── billboard-hot-100.db
│   │   ├── imdb/
│   │   │   └── imdb/
│   │   ├── media/
│   │   │   └── vdj_history_full.json
│   │   └── screen-culture/
│   │       └── screen-culture/
│   ├── registry/
│   │   └── DATA_REGISTRY.yaml
│   └── support/
│       ├── magazine/
│       │   ├── albums/
│       │   ├── archive/
│       │   ├── cultural-events/
│       │   └── year-end-top40/
│       └── retroverse/
│           └── retroverse_support_cultural_1958_2024_top10.csv
├── dist-pipeline/
│   ├── config/
│   │   ├── loadConfig.d.ts
│   │   └── loadConfig.js
│   ├── ingest/
│   │   ├── historyIngest.d.ts
│   │   ├── historyIngest.js
│   │   ├── historyParser.d.ts
│   │   ├── historyParser.js
│   │   ├── historyStats.d.ts
│   │   └── historyStats.js
│   ├── modules/
│   │   ├── exportBillboardJson.d.ts
│   │   ├── exportBillboardJson.js
│   │   ├── extractCue8.d.ts
│   │   ├── extractCue8.js
│   │   ├── fuzzyMatch.d.ts
│   │   ├── fuzzyMatch.js
│   │   ├── historyIngest.d.ts
│   │   ├── historyIngest.js
│   │   ├── matchCharts.d.ts
│   │   ├── matchCharts.js
│   │   ├── mp4Metadata.d.ts
│   │   ├── mp4Metadata.js
│   │   ├── parseVdj.d.ts
│   │   ├── parseVdj.js
│   │   ├── playlistParser.d.ts
│   │   ├── playlistParser.js
│   │   ├── r2Publisher.d.ts
│   │   ├── r2Publisher.js
│   │   ├── retentionScore.d.ts
│   │   ├── retentionScore.js
│   │   ├── rewriteIndexFromExisting.d.ts
│   │   ├── rewriteIndexFromExisting.js
│   │   ├── thumbnailGenerator.d.ts
│   │   ├── thumbnailGenerator.js
│   │   ├── thumbnailIntent.d.ts
│   │   ├── thumbnailIntent.js
│   │   ├── tierCutoffs.d.ts
│   │   ├── tierCutoffs.js
│   │   ├── vdjIngest.d.ts
│   │   ├── vdjIngest.js
│   │   ├── youtubeReconciliation.d.ts
│   │   └── youtubeReconciliation.js
│   ├── scripts/
│   │   ├── run-history-ingest.d.ts
│   │   ├── run-history-ingest.js
│   │   ├── run.d.ts
│   │   └── run.js
│   ├── utils/
│   │   ├── fs.d.ts
│   │   ├── fs.js
│   │   ├── logger.d.ts
│   │   ├── logger.js
│   │   ├── matchDecisions.d.ts
│   │   ├── matchDecisions.js
│   │   ├── pathNormalize.d.ts
│   │   ├── pathNormalize.js
│   │   ├── searchChart.d.ts
│   │   ├── searchChart.js
│   │   ├── thumbnail.d.ts
│   │   └── thumbnail.js
│   ├── index.d.ts
│   ├── index.js
│   ├── server.d.ts
│   ├── server.js
│   ├── types.d.ts
│   └── types.js
├── docs/
│   ├── DATA_INVENTORY.md
│   ├── DATA_LINEAGE.md
│   ├── DATA_LINEAGE_GRAPH.dot
│   ├── DATA_LINEAGE_GRAPH.svg
│   ├── DATA_REGISTRY.md
│   ├── DATA_REGISTRY_IMPLEMENTATION.md
│   ├── DSM_WEBSTACK_RECOVERY.md
│   ├── LINEAGE_AUTOMATION_REPORT.md
│   ├── MIGRATION_EXECUTION_REPORT.md
│   ├── MIGRATION_VERIFICATION.md
│   ├── REGISTRY_PIPELINE_INTEGRATION.md
│   ├── REPO_ARCHITECTURE_AUDIT.md
│   ├── REPOSITORY_ARCHITECTURE_AUDIT.md
│   ├── REPOSITORY_MIGRATION_SCRIPT.md
│   ├── RetroVerse Wheel Specification.md
│   ├── TRUNK_STABILIZATION_PLAN.md
│   ├── TRUNK_STABILIZATION_REPORT.md
│   └── UNREGISTERED_DATASETS.md
├── pipelines/
│   ├── cards-1974/
│   │   ├── card.css
│   │   ├── card_template.html
│   │   ├── export_weekly_context.ts
│   │   └── render_cards.ts
│   ├── lib/
│   │   ├── lineage-hook.js
│   │   └── registry-loader.js
│   ├── media-index/
│   │   ├── pipeline/
│   │   │   ├── config/
│   │   │   ├── history/
│   │   │   ├── ingest/
│   │   │   ├── logs/
│   │   │   ├── modules/
│   │   │   ├── output/
│   │   │   ├── scripts/
│   │   │   ├── utils/
│   │   │   ├── index.ts
│   │   │   ├── match-inspector.html
│   │   │   ├── README.md
│   │   │   ├── server.ts
│   │   │   └── types.ts
│   │   ├── scripts/
│   │   │   ├── split-video-index-by-decade.mjs
│   │   │   └── sync-index.sh
│   │   └── tools/
│   │       ├── analyze_playcounts.py
│   │       ├── api-selftest.mjs
│   │       └── api-selftest.ts
│   └── support-data/
│       ├── lib/
│       │   └── registry_loader.py
│       ├── scripts/
│       │   ├── archive_magazine_harvester.py
│       │   ├── build_cultural_index.py
│       │   ├── build_year_master.py
│       │   ├── compute_billboard_stats.py
│       │   ├── export-album-summaries.sh
│       │   ├── export-hot100-summaries.sh
│       │   ├── generate_data_lineage.py
│       │   ├── generate_magazine_catalog.py
│       │   ├── generate_yearly_magazine_index.py
│       │   ├── harvest_billboard.py
│       │   ├── harvest_magazines.py
│       │   ├── harvest_radio_logs.py
│       │   ├── harvest_tv_listings.py
│       │   ├── init_culture_dataset.py
│       │   ├── lineage_hook.py
│       │   ├── merge_magazine_datasets.py
│       │   ├── pipeline_common.py
│       │   ├── rebuild_year_master.py
│       │   ├── recover_issue_dates.py
│       │   ├── recover_issue_dates_from_url.py
│       │   ├── run_full_pipeline.py
│       │   ├── rv_year_end_rank.py
│       │   └── validate_registry.py
│       ├── build_retroverse_support_1958_2024.py
│       ├── README.md
│       └── requirements.txt
├── raw-data/
│   ├── billboard-hot-100.db
│   ├── billboard-hot-100.db-shm
│   └── billboard-hot-100.db-wal
├── scripts/
│   └── audit_repo_architecture.py
├── .DS_Store
├── .env
├── .gitignore
├── 11.11.1
├── eslint.config.js
├── netlify.toml
├── package-lock.json
├── package.json
├── pipeline.config.json
├── postcss.config.js
├── PROJECT_DOCUMENTATION_INDEX.md
├── README.md
├── retroverse@0.0.0
├── RETROVERSE_PLATFORM_STATE.md
├── tailwind.config.js
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
├── tsconfig.pipeline.json
├── tsx
└── vite.config.ts
```

## Canonical Directory Validation

| Directory | Status | Observed Equivalent(s) |
|---|---|---|
| retroverse-data | Missing | data, raw-data |
| retroverse-magazine | Missing | apps/magazine/retroverse-magazine |
| retroverse-hub | Missing | apps/web |
| retroverse-games | Missing | — |
| scripts | Present | pipelines/support-data/scripts, pipelines/media-index/scripts |

Missing canonical directories: retroverse-data, retroverse-magazine, retroverse-hub, retroverse-games

## Experimental Directories

| Path | Matched Token(s) |
|---|---|
| .netlify/v1 | v1 |
| .tmp.drivedownload | tmp |
| .tmp.driveupload | tmp |
| apps/magazine/retroverse-magazine/archive/old_runs | old |
| apps/magazine/retroverse-magazine/archive/old_runs/prototype_pipelines | prototype |
| apps/magazine/retroverse-magazine/archive/unused_assets | unused |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/pydantic/v1 | v1 |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/sniffio/_tests | test |
| archive/pipelines/retroverse-1974/out/1974/authentic_print_1974_v1 | v1 |
| archive/pipelines/retroverse-1974/out/1974/cinematic_painterly_1974_v1 | v1 |
| archive/pipelines/retroverse-1974/runs/2026-02-26_w30_top3_authentic_print_1974_v1_720x1280 | v1 |
| archive/pipelines/retroverse-1974/runs/2026-02-26_w30_top3_cinematic_painterly_1974_v1_720x1280 | v1 |
| archive/pipelines/retroverse-1974/runs/2026-02-26_w30_top3_era_1969_1974_v1_720x1280 | v1 |

## Orphan Artifacts

Artifact heuristic checks `png`, `jpg`, `jpeg`, `json`, `csv`, and `pdf` files outside expected artifact containers (archive, artifacts, assets, data, images, issues, output, public, raw-data, runs).

| Path | Size (bytes) |
|---|---|
| .netlify/functions/manifest.json | 355 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_magazine.jpg | 5038772 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_02.png | 4006682 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_03.png | 4080931 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_04.png | 4401075 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_05.png | 3755716 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_06.png | 3933444 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_07.png | 4045624 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_08.png | 4030765 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_09.png | 3632860 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_10.png | 3445193 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_A.png | 4588514 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_J.png | 3936812 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_K.png | 4456000 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_Q.png | 3862213 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_R1.png | 4010406 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_R2.png | 3867091 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_R3.png | 4046029 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/1978_raw_R4.png | 3620626 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/back_page_1978.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_1970s_mad_printing_cover_1970s_1978.png | 3210794 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_10.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_11.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_12.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_13.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_14.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_2.png | 2711021 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_3.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_4.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_5.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_6.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_7.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_8.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/background_cover_neon_city_nightlife_retro_1978_9.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/cinema_marquee.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_01.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_02.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_03.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_04.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_05.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_06.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_07.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_08.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/collage_09.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/comic_panel_01.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/comic_panel_02.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/comic_panel_03.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/comic_panel_04.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/comic_panel_05.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/comic_panel_06.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/cover_1978.png | 2726660 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/department_portrait.png | 2820075 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/disco_floor.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_10.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_11.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_12.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_13.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_14.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_15.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_16.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_17.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_18.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_19.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_2.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_20.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_21.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_22.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_23.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_24.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_25.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_26.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_27.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_28.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_3.png | 1757 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_4.png | 1756 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_5.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_6.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_7.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_8.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_gadget_advertisement_art_chrome_retro_1978_9.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/fake_ad_kit.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/feature_placeholder.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/parody_placeholder.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/scene_1970s_mad_printing_movie_1970s_1978.png | 2942645 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_10.png | 2576244 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_11.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_12.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_13.png | 2866941 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_14.png | 2866941 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_15.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_16.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_17.png | 2866941 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_18.png | 2866941 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_19.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_2.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_20.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_21.png | 2820075 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_22.png | 2820075 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_23.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_24.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_25.png | 2820075 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_26.png | 2820075 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_27.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_28.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_3.png | 1757 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_4.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_5.png | 2576244 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_6.png | 2576244 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_7.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_8.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/texture_cultural_bustling_night_street_retro_1978_9.png | 2576244 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/trivia_grid.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/tv_livingroom.png | 1758 |
| apps/magazine/retroverse-magazine/INSPECT_1978_IMAGES/weekend_console.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/art_index.json | 56581 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_10.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_11.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_12.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_13.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_14.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_2.png | 2711021 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_3.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_4.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_5.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_6.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_7.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_8.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_9.png | 2726660 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978.png | 3456621 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_10.png | 1799218 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_2.png | 4047393 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_3.png | 3604039 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_4.png | 4006827 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_5.png | 3640539 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_6.png | 4056931 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_7.png | 2132270 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_8.png | 1916562 |
| apps/magazine/retroverse-magazine/art-library/backgrounds/background_retroverse_page_brief_target_1970s_1978_9.png | 1914632 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_10.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_11.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_12.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_13.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_14.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_15.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_16.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_17.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_18.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_19.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_2.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_20.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_21.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_22.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_23.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_24.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_25.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_26.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_27.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_28.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_3.png | 1757 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_4.png | 1756 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_5.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_6.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_7.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_8.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_9.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978.png | 3030960 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_10.png | 1482575 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_11.png | 1700188 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_12.png | 1873939 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_13.png | 1584225 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_14.png | 1166523 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_15.png | 1377956 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_16.png | 1716001 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_17.png | 1465450 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_2.png | 2820153 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_3.png | 3799625 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_4.png | 2776102 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_5.png | 3296492 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_6.png | 1706830 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_7.png | 1630710 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_8.png | 1811845 |
| apps/magazine/retroverse-magazine/art-library/scenes/scene_retroverse_page_brief_target_1970s_1978_9.png | 1754739 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_10.png | 2576244 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_11.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_12.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_13.png | 2866941 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_14.png | 2866941 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_15.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_16.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_17.png | 2866941 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_18.png | 2866941 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_19.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_2.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_20.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_21.png | 2820075 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_22.png | 2820075 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_23.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_24.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_25.png | 2820075 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_26.png | 2820075 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_27.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_28.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_3.png | 1757 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_4.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_5.png | 2576244 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_6.png | 2576244 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_7.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_8.png | 1758 |
| apps/magazine/retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_9.png | 2576244 |
| apps/magazine/retroverse-magazine/layout-library/schemas/layout_templates.json | 8756 |
| apps/magazine/retroverse-magazine/workflow/page_rebuild/page_brief_schema.json | 8511 |
| apps/web/dist/cards/1974/playing-card-week30-ace.png | 426038 |
| apps/web/dist/cards/1974/week-01.png | 945077 |
| apps/web/dist/cards/1974/week-02.png | 779035 |
| apps/web/dist/cards/1974/week-03.png | 530594 |
| apps/web/dist/cards/1974/week-04.png | 950086 |
| apps/web/dist/cards/1974/week-05.png | 782077 |
| apps/web/dist/cards/1974/week-06.png | 534770 |
| apps/web/dist/cards/1974/week-07.png | 949755 |
| apps/web/dist/cards/1974/week-08.png | 781015 |
| apps/web/dist/cards/1974/week-09.png | 532372 |
| apps/web/dist/cards/1974/week-10.png | 945856 |
| apps/web/dist/cards/1974/week-11.png | 776055 |
| apps/web/dist/cards/1974/week-12.png | 535478 |
| apps/web/dist/cards/1974/week-13.png | 946994 |
| apps/web/dist/cards/1974/week-14.png | 779304 |
| apps/web/dist/cards/1974/week-15.png | 541183 |
| apps/web/dist/cards/1974/week-16.png | 953002 |
| apps/web/dist/cards/1974/week-17.png | 778955 |
| apps/web/dist/cards/1974/week-18.png | 530567 |
| apps/web/dist/cards/1974/week-19.png | 944924 |
| apps/web/dist/cards/1974/week-20.png | 779957 |
| apps/web/dist/cards/1974/week-21.png | 529304 |
| apps/web/dist/cards/1974/week-22.png | 950276 |
| apps/web/dist/cards/1974/week-23.png | 786001 |
| apps/web/dist/cards/1974/week-24.png | 538809 |
| apps/web/dist/cards/1974/week-25.png | 945658 |
| apps/web/dist/cards/1974/week-26.png | 781459 |
| apps/web/dist/cards/1974/week-27.png | 532776 |
| apps/web/dist/cards/1974/week-28.png | 947671 |
| apps/web/dist/cards/1974/week-29.png | 780267 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-01.png | 1877953 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-02.png | 1848946 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-03.png | 1861823 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-04.png | 1853329 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-05.png | 1860862 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-06.png | 1848294 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-07.png | 1871376 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-08.png | 1859601 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-09.png | 1854470 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-10.png | 1867770 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-11.png | 1856593 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-12.png | 1869724 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-13.png | 1858159 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-14.png | 1857412 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-15.png | 1859593 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-16.png | 1868115 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-17.png | 1846944 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-18.png | 1858005 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-19.png | 1858180 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-20.png | 1852258 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-21.png | 1855519 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-22.png | 1853420 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-23.png | 1865795 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-24.png | 1853836 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-25.png | 1843341 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-26.png | 1842039 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-27.png | 1866186 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-28.png | 1862815 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-29.png | 1853865 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-30.png | 1844962 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-31.png | 1838281 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-32.png | 1872950 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-33.png | 1868457 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-34.png | 1859234 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-35.png | 1839134 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-36.png | 1860073 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-37.png | 1857955 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-38.png | 1874478 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-39.png | 1863578 |
| apps/web/dist/cards/1974/week-30-illustrated/week-30-rank-40.png | 1858358 |
| apps/web/dist/cards/1974/week-30.png | 530891 |
| apps/web/dist/cards/1974/week-30/week-30-rank-01.png | 1005923 |
| apps/web/dist/cards/1974/week-30/week-30-rank-02.png | 879107 |
| apps/web/dist/cards/1974/week-30/week-30-rank-03.png | 866725 |
| apps/web/dist/cards/1974/week-30/week-30-rank-04.png | 876548 |
| apps/web/dist/cards/1974/week-30/week-30-rank-05.png | 869990 |
| apps/web/dist/cards/1974/week-30/week-30-rank-06.png | 869080 |
| apps/web/dist/cards/1974/week-30/week-30-rank-07.png | 867396 |
| apps/web/dist/cards/1974/week-30/week-30-rank-08.png | 869511 |
| apps/web/dist/cards/1974/week-30/week-30-rank-09.png | 874421 |
| apps/web/dist/cards/1974/week-30/week-30-rank-10.png | 873018 |
| apps/web/dist/cards/1974/week-30/week-30-rank-11.png | 870325 |
| apps/web/dist/cards/1974/week-30/week-30-rank-12.png | 862300 |
| apps/web/dist/cards/1974/week-30/week-30-rank-13.png | 866214 |
| apps/web/dist/cards/1974/week-30/week-30-rank-14.png | 872646 |
| apps/web/dist/cards/1974/week-30/week-30-rank-15.png | 868237 |
| apps/web/dist/cards/1974/week-30/week-30-rank-16.png | 870237 |
| apps/web/dist/cards/1974/week-30/week-30-rank-17.png | 860470 |
| apps/web/dist/cards/1974/week-30/week-30-rank-18.png | 870938 |
| apps/web/dist/cards/1974/week-30/week-30-rank-19.png | 860260 |
| apps/web/dist/cards/1974/week-30/week-30-rank-20.png | 866189 |
| apps/web/dist/cards/1974/week-30/week-30-rank-21.png | 867852 |
| apps/web/dist/cards/1974/week-30/week-30-rank-22.png | 864332 |
| apps/web/dist/cards/1974/week-30/week-30-rank-23.png | 870722 |
| apps/web/dist/cards/1974/week-30/week-30-rank-24.png | 862415 |
| apps/web/dist/cards/1974/week-30/week-30-rank-25.png | 887143 |
| apps/web/dist/cards/1974/week-30/week-30-rank-26.png | 884605 |
| apps/web/dist/cards/1974/week-30/week-30-rank-27.png | 865551 |
| apps/web/dist/cards/1974/week-30/week-30-rank-28.png | 863433 |
| apps/web/dist/cards/1974/week-30/week-30-rank-29.png | 876455 |
| apps/web/dist/cards/1974/week-30/week-30-rank-30.png | 870627 |
| apps/web/dist/cards/1974/week-30/week-30-rank-31.png | 896930 |
| apps/web/dist/cards/1974/week-30/week-30-rank-32.png | 857298 |
| apps/web/dist/cards/1974/week-30/week-30-rank-33.png | 865079 |
| apps/web/dist/cards/1974/week-30/week-30-rank-34.png | 868020 |
| apps/web/dist/cards/1974/week-30/week-30-rank-35.png | 889482 |
| apps/web/dist/cards/1974/week-30/week-30-rank-36.png | 860491 |
| apps/web/dist/cards/1974/week-30/week-30-rank-37.png | 862511 |
| apps/web/dist/cards/1974/week-30/week-30-rank-38.png | 867547 |
| apps/web/dist/cards/1974/week-30/week-30-rank-39.png | 868663 |
| apps/web/dist/cards/1974/week-30/week-30-rank-40.png | 864034 |
| apps/web/dist/cards/1974/week-31.png | 947611 |
| apps/web/dist/cards/1974/week-32.png | 782184 |
| apps/web/dist/cards/1974/week-33.png | 535819 |
| apps/web/dist/cards/1974/week-34.png | 950505 |
| apps/web/dist/cards/1974/week-35.png | 783759 |
| apps/web/dist/cards/1974/week-36.png | 531019 |
| apps/web/dist/cards/1974/week-37.png | 956016 |
| apps/web/dist/cards/1974/week-38.png | 780923 |
| apps/web/dist/cards/1974/week-39.png | 534768 |
| apps/web/dist/cards/1974/week-40.png | 948475 |
| apps/web/dist/cards/1974/week-41.png | 781055 |
| apps/web/dist/cards/1974/week-42.png | 532364 |
| apps/web/dist/cards/1974/week-43.png | 948711 |
| apps/web/dist/cards/1974/week-44.png | 807102 |
| apps/web/dist/cards/1974/week-45.png | 540439 |
| apps/web/dist/cards/1974/week-46.png | 942757 |
| apps/web/dist/cards/1974/week-47.png | 777214 |
| apps/web/dist/cards/1974/week-48.png | 531473 |
| apps/web/dist/cards/1974/week-49.png | 945619 |
| apps/web/dist/cards/1974/week-50.png | 780108 |
| apps/web/dist/cards/1974/week-51.png | 529803 |
| apps/web/dist/cards/1974/week-52.png | 945388 |

## Duplicate Pipelines

### generate_issue*

- `apps/magazine/retroverse-magazine/pipeline/generate_issue_art_direction.py`
- `apps/magazine/retroverse-magazine/pipeline/generate_issue_art_prompts.py`
- `apps/magazine/retroverse-magazine/pipeline/generate_issue_page_briefs.py`

### build_issue*

- `apps/magazine/retroverse-magazine/scripts/build_issue.py`
- `apps/magazine/retroverse-magazine/tools/magazine_builder/build_issue.py`

## Markdown Inventory

Total Markdown files: `120`

| Path | Size (bytes) | Last Modified |
|---|---|---|
| PROJECT_DOCUMENTATION_INDEX.md | 49243 | 2026-03-14 14:10:18 |
| README.md | 3124 | 2026-02-04 11:37:33 |
| RETROVERSE_PLATFORM_STATE.md | 4064 | 2026-03-14 15:32:45 |
| apps/magazine/retroverse-magazine/.cursor/rules/.cursor/rules/.cursor/rules/tasks.md | 709 | 2026-03-13 17:54:06 |
| apps/magazine/retroverse-magazine/.cursor/rules/.cursor/rules/architecture.md | 1390 | 2026-03-13 17:53:40 |
| apps/magazine/retroverse-magazine/.cursor/rules/project.md | 1826 | 2026-03-13 17:43:43 |
| apps/magazine/retroverse-magazine/DATA_INVENTORY.md | 167174 | 2026-03-12 11:07:50 |
| apps/magazine/retroverse-magazine/ISSUE_STRUCTURE_REPORT.md | 2552 | 2026-03-12 23:32:09 |
| apps/magazine/retroverse-magazine/MAGAZINE_PIPELINE_AUDIT.md | 48078 | 2026-03-13 12:52:06 |
| apps/magazine/retroverse-magazine/PIPELINE_REPAIR_IMPLEMENTATION.md | 4212 | 2026-03-13 13:22:10 |
| apps/magazine/retroverse-magazine/PIPELINE_REPAIR_REPORT.md | 3619 | 2026-03-12 23:07:07 |
| apps/magazine/retroverse-magazine/PRESS_CHECK_1978.md | 5905 | 2026-03-12 22:33:04 |
| apps/magazine/retroverse-magazine/PROJECT_AUDIT.md | 18292 | 2026-03-12 21:43:32 |
| apps/magazine/retroverse-magazine/PROJECT_STATE.md | 28947 | 2026-03-13 13:53:31 |
| apps/magazine/retroverse-magazine/artifacts/logs/year_generation_summary.md | 650 | 2026-03-12 15:57:22 |
| apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_art_direction_QA.md | 5201 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_art_prompt_QA.md | 3098 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_layout_QA.md | 3506 | 2026-03-13 13:54:36 |
| apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_page_briefs_QA.md | 5865 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_press_check_QA.md | 1123 | 2026-03-13 13:54:36 |
| apps/magazine/retroverse-magazine/charter/retroverse_editorial_charter.md | 4317 | 2026-03-12 18:52:16 |
| apps/magazine/retroverse-magazine/docs/ARCHITECTURE.md | 2356 | 2026-03-12 12:10:45 |
| apps/magazine/retroverse-magazine/docs/CANONICAL_PIPELINE.md | 1496 | 2026-03-12 22:08:47 |
| apps/magazine/retroverse-magazine/docs/PROJECT_PIPELINE_REPORT.md | 66974 | 2026-03-13 16:06:08 |
| apps/magazine/retroverse-magazine/docs/SCREEN_CULTURE_DATA_AUDIT.md | 3339 | 2026-03-12 15:57:22 |
| apps/magazine/retroverse-magazine/docs/SCREEN_CULTURE_WAREHOUSE_AUDIT.md | 19855 | 2026-03-12 14:52:52 |
| apps/magazine/retroverse-magazine/issues/1978/ads.md | 119 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/arcade.md | 127 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_001.md | 6718 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_002.md | 3821 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_003.md | 2251 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_004.md | 2935 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_005.md | 2949 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_006.md | 6859 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_007.md | 4249 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_008.md | 2728 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_009.md | 2388 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_010.md | 4217 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_011.md | 1598 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/final/story_012.md | 3446 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_001.md | 1842 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_002.md | 1627 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_003.md | 1637 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_004.md | 1577 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_005.md | 1575 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_006.md | 1710 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_007.md | 1622 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_008.md | 1806 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_009.md | 1887 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_010.md | 1734 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_011.md | 1526 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/articles/story_012.md | 1502 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/issues/1978/chart_top23.md | 1723 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/charts_overview.md | 1378 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/comic.md | 111 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/cover.md | 1035 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/culture.md | 1099 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/editor_letter.md | 1441 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/layout/1978_issue_map.md | 4166 | 2026-03-13 13:22:51 |
| apps/magazine/retroverse-magazine/issues/1978/letters.md | 1003 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/masthead.md | 545 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/movies.md | 1125 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/puzzle1.md | 102 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/puzzle2.md | 102 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/retroverse_1978_pilot.md | 10545 | 2026-03-11 13:27:57 |
| apps/magazine/retroverse-magazine/issues/1978/songs/01.md | 788 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/02.md | 670 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/03.md | 708 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/04.md | 672 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/05.md | 705 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/06.md | 674 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/07.md | 623 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/08.md | 636 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/09.md | 624 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/songs/10.md | 645 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/1978/television.md | 964 | 2026-03-12 21:07:35 |
| apps/magazine/retroverse-magazine/issues/plans/1978_narrative_plan.md | 13240 | 2026-03-13 13:54:35 |
| apps/magazine/retroverse-magazine/layout-library/docs/page_rhythm_guide.md | 3408 | 2026-03-11 17:23:22 |
| apps/magazine/retroverse-magazine/layout-library/docs/retroverse_layout_library.md | 6637 | 2026-03-11 17:23:01 |
| apps/magazine/retroverse-magazine/prompts/generate_issue_prompt.md | 0 | 2026-03-11 13:24:23 |
| apps/magazine/retroverse-magazine/templates/issue_template.md | 0 | 2026-03-11 13:24:23 |
| apps/magazine/retroverse-magazine/workflow/page_rebuild/README.md | 1107 | 2026-03-13 12:21:13 |
| apps/magazine/retroverse-magazine/workflow/page_rebuild/SINGLE_PAGE_REBUILD_REPORT.md | 3026 | 2026-03-13 12:22:14 |
| apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_art_direction_QA.md | 1537 | 2026-03-13 12:21:50 |
| apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_art_prompt_QA.md | 752 | 2026-03-13 12:21:50 |
| apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_layout_QA.md | 841 | 2026-03-13 12:21:50 |
| apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_page_brief_QA.md | 1274 | 2026-03-13 12:21:50 |
| archive/artifacts/retroverse-output-remainder/.venv/lib/python3.12/site-packages/idna-3.11.dist-info/licenses/LICENSE.md | 1541 | 2026-02-26 23:33:19 |
| archive/artifacts/retroverse-output-remainder/.venv/lib/python3.12/site-packages/soupsieve-2.8.3.dist-info/licenses/LICENSE.md | 1096 | 2026-02-26 23:33:19 |
| archive/docs/Journal/rv_journal.md | 193288 | 2026-03-07 00:12:03 |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/httpcore-1.0.9.dist-info/licenses/LICENSE.md | 1518 | 2026-02-25 15:58:31 |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/httpx-0.28.1.dist-info/licenses/LICENSE.md | 1508 | 2026-02-25 15:58:31 |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/idna-3.11.dist-info/licenses/LICENSE.md | 1541 | 2026-02-25 15:58:31 |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/openai/resources/conversations/api.md | 3047 | 2026-02-25 15:58:31 |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/openai/resources/realtime/api.md | 5162 | 2026-02-25 15:58:31 |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/openai/resources/responses/api.md | 6462 | 2026-02-25 15:58:31 |
| archive/pipelines/retroverse-1974/.venv/lib/python3.12/site-packages/openai/resources/webhooks/api.md | 610 | 2026-02-25 15:58:31 |
| archive/pipelines/retroverse-1974/README.md | 758 | 2026-02-25 12:48:12 |
| archive/pipelines/tools-legacy/README.md | 3663 | 2026-02-04 11:07:21 |
| archive/pipelines/tools-legacy/media-normalization/README.md | 915 | 2026-02-13 09:36:21 |
| data/derived/cards/1974/1974_weekly_context.md | 4365 | 2026-02-24 22:28:25 |
| data/derived/cards/1974/retro-verse-1974-weekly-data.md | 3777 | 2026-02-25 09:26:26 |
| docs/DATA_INVENTORY.md | 9639 | 2026-03-10 14:03:59 |
| docs/DATA_LINEAGE.md | 4113 | 2026-03-13 21:56:44 |
| docs/DATA_REGISTRY.md | 4952 | 2026-03-14 14:01:21 |
| docs/DATA_REGISTRY_IMPLEMENTATION.md | 4971 | 2026-03-14 14:01:21 |
| docs/DSM_WEBSTACK_RECOVERY.md | 3834 | 2026-03-13 17:54:35 |
| docs/LINEAGE_AUTOMATION_REPORT.md | 3314 | 2026-03-13 21:44:24 |
| docs/MIGRATION_EXECUTION_REPORT.md | 7263 | 2026-03-14 14:01:21 |
| docs/MIGRATION_VERIFICATION.md | 16836 | 2026-03-14 14:01:21 |
| docs/REGISTRY_PIPELINE_INTEGRATION.md | 4858 | 2026-03-13 19:59:10 |
| docs/REPOSITORY_ARCHITECTURE_AUDIT.md | 29711 | 2026-03-13 18:09:17 |
| docs/REPOSITORY_MIGRATION_SCRIPT.md | 22053 | 2026-03-13 18:45:59 |
| docs/REPO_ARCHITECTURE_AUDIT.md | 74062 | 2026-03-14 15:47:41 |
| docs/RetroVerse Wheel Specification.md | 601 | 2026-02-12 13:55:31 |
| docs/TRUNK_STABILIZATION_PLAN.md | 13767 | 2026-03-13 18:30:58 |
| docs/TRUNK_STABILIZATION_REPORT.md | 3716 | 2026-03-14 14:01:21 |
| docs/UNREGISTERED_DATASETS.md | 19350 | 2026-03-13 20:13:21 |
| pipelines/media-index/pipeline/README.md | 2521 | 2026-02-04 09:09:50 |
| pipelines/support-data/README.md | 1290 | 2026-02-26 23:32:34 |

## Platform State File Check

- PASS: `RETROVERSE_PLATFORM_STATE.md` found at `RETROVERSE_PLATFORM_STATE.md`

## Magazine State File Check

- FAIL: requested path `retroverse-magazine/PROJECT_STATE.md` is missing.
- NOTE: migrated equivalent found at `apps/magazine/retroverse-magazine/PROJECT_STATE.md`

## Summary

- Missing canonical directories: `4`
- Experimental directories flagged: `13`
- Orphan artifacts flagged: `350`
- Duplicate pipeline families: `2`
- Markdown files inventoried: `120`
- Root appears to be a migrated RetroVerse layout rather than the older flat module layout.
- Requested magazine state path is absent, but a migrated equivalent exists under `apps/magazine/retroverse-magazine/PROJECT_STATE.md`.
