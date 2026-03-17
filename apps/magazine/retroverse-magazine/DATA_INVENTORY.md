# RetroVerse Data Inventory

## Project Structure

| Area | Relative Path | Status |
|---|---|---|
| Magazine workspace | `retroverse-magazine` | exists |
| Raw datasets | `raw-data` | exists |
| RetroVerse output | `retroverse-output` | exists |
| Billboard analytics | `artifacts/output/billboard` | exists |
| Public data bundles | `public/data` | exists |

## Canonical Data Sources

| Source Key | Config Path | Status | Type | Required | Description |
|---|---|---|---|---|---|
| `billboard_200` | `/Users/bobhopp/Sites/retroverse/raw-data/billboard-200-albums-charts.db` | exists (raw-data/billboard-200-albums-charts.db) | `sqlite` | `true` | Weekly Billboard 200 album charts |
| `billboard_hot_100` | `/Users/bobhopp/Sites/retroverse/raw-data/billboard-hot-100.db` | exists (raw-data/billboard-hot-100.db) | `sqlite` | `true` | Weekly Billboard Hot 100 charts (1958–present) |
| `billboard_stats_dir` | `../artifacts/output/billboard` | exists (artifacts/output/billboard) | `directory` | `false` | Derived Billboard analytics |
| `cultural_events_glob` | `../cultural_events_*.json` | 6 match(es) | `json_glob` | `false` | Cultural event datasets by year or topic |
| `public_data_dir` | `../public/data` | exists (public/data) | `directory` | `false` | Front-end ready data bundles |
| `retroverse_output_dir` | `../retroverse-output` | exists (retroverse-output) | `directory` | `false` | Generated RetroVerse output datasets |
| `vdj_history_json` | `../raw-data/vdj_history_full.json` | exists (raw-data/vdj_history_full.json) | `json` | `false` | Personal DJ history dataset |
| `year_end_top_40_glob` | `../year_end_top_40_*.json` | 6 match(es) | `json_glob` | `false` | Year-end Top 40 exports |
| `year_master_json` | `../retroverse-output/retroverse_year_master_1958_2024.json` | exists (retroverse-output/retroverse_year_master_1958_2024.json) | `json` | `false` | Consolidated year master dataset |

## Data Files

| File | Relative Path | Type | Purpose |
|---|---|---|---|
| `DATA_INVENTORY.md` | `DATA_INVENTORY.md` | `markdown` | Project documentation. |
| `MAGAZINE_ARCHIVE_HARVEST.csv` | `MAGAZINE_ARCHIVE_HARVEST.csv` | `csv` | Structured project dataset or configuration. |
| `MAGAZINE_CULTURAL_SIGNALS.json` | `MAGAZINE_CULTURAL_SIGNALS.json` | `json` | Structured project dataset or configuration. |
| `MAGAZINE_ISSUE_MANIFEST.csv` | `MAGAZINE_ISSUE_MANIFEST.csv` | `csv` | Structured project dataset or configuration. |
| `MAGAZINE_ISSUE_MANIFEST_DATED.csv` | `MAGAZINE_ISSUE_MANIFEST_DATED.csv` | `csv` | Structured project dataset or configuration. |
| `MAGAZINE_MASTER_ARCHIVE.csv` | `MAGAZINE_MASTER_ARCHIVE.csv` | `csv` | Structured project dataset or configuration. |
| `MAGAZINE_MASTER_INDEX.csv` | `MAGAZINE_MASTER_INDEX.csv` | `csv` | Structured project dataset or configuration. |
| `MAGAZINE_METADATA_SAMPLE.json` | `MAGAZINE_METADATA_SAMPLE.json` | `json` | Structured project dataset or configuration. |
| `MAGAZINE_YEAR_INDEX.csv` | `MAGAZINE_YEAR_INDEX.csv` | `csv` | Structured project dataset or configuration. |
| `albums_1978_sample.csv` | `albums_1978_sample.csv` | `csv` | Structured project dataset or configuration. |
| `billboard_run_1770237987209.json` | `artifacts/canonical/billboard_run_1770237987209.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770238068474.json` | `artifacts/canonical/billboard_run_1770238068474.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770238116087.json` | `artifacts/canonical/billboard_run_1770238116087.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770238860587.json` | `artifacts/canonical/billboard_run_1770238860587.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770239424933.json` | `artifacts/canonical/billboard_run_1770239424933.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770239575757.json` | `artifacts/canonical/billboard_run_1770239575757.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770239599578.json` | `artifacts/canonical/billboard_run_1770239599578.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770239804132.json` | `artifacts/canonical/billboard_run_1770239804132.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770240367324.json` | `artifacts/canonical/billboard_run_1770240367324.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770241214624.json` | `artifacts/canonical/billboard_run_1770241214624.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770323993208.json` | `artifacts/canonical/billboard_run_1770323993208.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770337670503.json` | `artifacts/canonical/billboard_run_1770337670503.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770485989469.json` | `artifacts/canonical/billboard_run_1770485989469.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770493928350.json` | `artifacts/canonical/billboard_run_1770493928350.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770494011925.json` | `artifacts/canonical/billboard_run_1770494011925.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770494216030.json` | `artifacts/canonical/billboard_run_1770494216030.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_1770494287612.json` | `artifacts/canonical/billboard_run_1770494287612.json` | `json` | Structured project dataset or configuration. |
| `billboard_run_decision_demo.json` | `artifacts/canonical/billboard_run_decision_demo.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770237684687.json` | `artifacts/canonical/vdj_library_run_1770237684687.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770237987209.json` | `artifacts/canonical/vdj_library_run_1770237987209.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770238068474.json` | `artifacts/canonical/vdj_library_run_1770238068474.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770238116087.json` | `artifacts/canonical/vdj_library_run_1770238116087.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770238860587.json` | `artifacts/canonical/vdj_library_run_1770238860587.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770239424933.json` | `artifacts/canonical/vdj_library_run_1770239424933.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770239575757.json` | `artifacts/canonical/vdj_library_run_1770239575757.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770239599578.json` | `artifacts/canonical/vdj_library_run_1770239599578.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770239804132.json` | `artifacts/canonical/vdj_library_run_1770239804132.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770240367324.json` | `artifacts/canonical/vdj_library_run_1770240367324.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770241214624.json` | `artifacts/canonical/vdj_library_run_1770241214624.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770323993208.json` | `artifacts/canonical/vdj_library_run_1770323993208.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770328005927.json` | `artifacts/canonical/vdj_library_run_1770328005927.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770337670503.json` | `artifacts/canonical/vdj_library_run_1770337670503.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770485989469.json` | `artifacts/canonical/vdj_library_run_1770485989469.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770493928350.json` | `artifacts/canonical/vdj_library_run_1770493928350.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770494011925.json` | `artifacts/canonical/vdj_library_run_1770494011925.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770494216030.json` | `artifacts/canonical/vdj_library_run_1770494216030.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_1770494287612.json` | `artifacts/canonical/vdj_library_run_1770494287612.json` | `json` | Structured project dataset or configuration. |
| `vdj_library_run_decision_demo.json` | `artifacts/canonical/vdj_library_run_decision_demo.json` | `json` | Structured project dataset or configuration. |
| `match_decisions.json` | `artifacts/decisions/match_decisions.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770238068474.json` | `artifacts/matching/chart_matches_run_1770238068474.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770238116087.json` | `artifacts/matching/chart_matches_run_1770238116087.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770239424933.json` | `artifacts/matching/chart_matches_run_1770239424933.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770239804132.json` | `artifacts/matching/chart_matches_run_1770239804132.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770240367324.json` | `artifacts/matching/chart_matches_run_1770240367324.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770241214624.json` | `artifacts/matching/chart_matches_run_1770241214624.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770323993208.json` | `artifacts/matching/chart_matches_run_1770323993208.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770337670503.json` | `artifacts/matching/chart_matches_run_1770337670503.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770485989469.json` | `artifacts/matching/chart_matches_run_1770485989469.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770493928350.json` | `artifacts/matching/chart_matches_run_1770493928350.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770494011925.json` | `artifacts/matching/chart_matches_run_1770494011925.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770494216030.json` | `artifacts/matching/chart_matches_run_1770494216030.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_1770494287612.json` | `artifacts/matching/chart_matches_run_1770494287612.json` | `json` | Structured project dataset or configuration. |
| `chart_matches_run_decision_demo.json` | `artifacts/matching/chart_matches_run_decision_demo.json` | `json` | Structured project dataset or configuration. |
| `artist_totals.json` | `artifacts/output/billboard/artist_totals.json` | `json` | Derived Billboard analytics and summary outputs. |
| `top_songs_by_year.json` | `artifacts/output/billboard/top_songs_by_year.json` | `json` | Derived Billboard analytics and summary outputs. |
| `weeks_at_number_one.json` | `artifacts/output/billboard/weeks_at_number_one.json` | `json` | Derived Billboard analytics and summary outputs. |
| `year_stats.json` | `artifacts/output/billboard/year_stats.json` | `json` | Derived Billboard analytics and summary outputs. |
| `history-index.json` | `artifacts/output/history-index.json` | `json` | Structured project dataset or configuration. |
| `tier-cutoffs.json` | `artifacts/output/tier-cutoffs.json` | `json` | Structured project dataset or configuration. |
| `vdj_history_flat.json` | `artifacts/output/vdj_history_flat.json` | `json` | Structured project dataset or configuration. |
| `video-index.json` | `artifacts/output/video-index.json` | `json` | Structured project dataset or configuration. |
| `cultural_events_1976.json` | `cultural_events_1976.json` | `json` | Cultural events, film, and TV context by year. |
| `cultural_events_1977.json` | `cultural_events_1977.json` | `json` | Cultural events, film, and TV context by year. |
| `cultural_events_1978.json` | `cultural_events_1978.json` | `json` | Cultural events, film, and TV context by year. |
| `cultural_events_1979.json` | `cultural_events_1979.json` | `json` | Cultural events, film, and TV context by year. |
| `cultural_events_1980.json` | `cultural_events_1980.json` | `json` | Cultural events, film, and TV context by year. |
| `cultural_events_1981.json` | `cultural_events_1981.json` | `json` | Cultural events, film, and TV context by year. |
| `1974_card_render_report.json` | `data/1974_card_render_report.json` | `json` | Structured project dataset or configuration. |
| `1974_master.json` | `data/1974_master.json` | `json` | Structured project dataset or configuration. |
| `1974_weekly_context.json` | `data/1974_weekly_context.json` | `json` | Structured project dataset or configuration. |
| `1974_weekly_context.md` | `data/1974_weekly_context.md` | `markdown` | Project documentation. |
| `1974_weekly_context.parse_report.json` | `data/1974_weekly_context.parse_report.json` | `json` | Structured project dataset or configuration. |
| `cultural_week_index.csv` | `data/index/cultural_week_index.csv` | `csv` | Structured project dataset or configuration. |
| `billboard_hot100.csv` | `data/processed/billboard_hot100.csv` | `csv` | Structured project dataset or configuration. |
| `magazine_issues.csv` | `data/processed/magazine_issues.csv` | `csv` | Structured project dataset or configuration. |
| `radio_airplay.csv` | `data/processed/radio_airplay.csv` | `csv` | Structured project dataset or configuration. |
| `tv_listings.csv` | `data/processed/tv_listings.csv` | `csv` | Structured project dataset or configuration. |
| `retro-verse-1974-weekly-data.md` | `data/retro-verse-1974-weekly-data.md` | `markdown` | Project documentation. |
| `package-lock.json` | `package-lock.json` | `json` | Structured project dataset or configuration. |
| `package.json` | `package.json` | `json` | Structured project dataset or configuration. |
| `pipeline.config.json` | `pipeline.config.json` | `json` | Structured project dataset or configuration. |
| `_clientMiddlewareManifest.json` | `public/charts/_next/static/RewpAnZ1rE4dEZKgoGHpB/_clientMiddlewareManifest.json` | `json` | Structured project dataset or configuration. |
| `billboard_hot_100.json` | `public/charts/data/billboard_hot_100.json` | `json` | Structured project dataset or configuration. |
| `1974_master.json` | `public/data/1974_master.json` | `json` | Structured project dataset or configuration. |
| `1974_weekly_context.json` | `public/data/1974_weekly_context.json` | `json` | Structured project dataset or configuration. |
| `1960.json` | `public/data/albums/1960.json` | `json` | Structured project dataset or configuration. |
| `1961.json` | `public/data/albums/1961.json` | `json` | Structured project dataset or configuration. |
| `1962.json` | `public/data/albums/1962.json` | `json` | Structured project dataset or configuration. |
| `1963.json` | `public/data/albums/1963.json` | `json` | Structured project dataset or configuration. |
| `1964.json` | `public/data/albums/1964.json` | `json` | Structured project dataset or configuration. |
| `1965.json` | `public/data/albums/1965.json` | `json` | Structured project dataset or configuration. |
| `1966.json` | `public/data/albums/1966.json` | `json` | Structured project dataset or configuration. |
| `1967.json` | `public/data/albums/1967.json` | `json` | Structured project dataset or configuration. |
| `1968.json` | `public/data/albums/1968.json` | `json` | Structured project dataset or configuration. |
| `1969.json` | `public/data/albums/1969.json` | `json` | Structured project dataset or configuration. |
| `1970.json` | `public/data/albums/1970.json` | `json` | Structured project dataset or configuration. |
| `1971.json` | `public/data/albums/1971.json` | `json` | Structured project dataset or configuration. |
| `1972.json` | `public/data/albums/1972.json` | `json` | Structured project dataset or configuration. |
| `1973.json` | `public/data/albums/1973.json` | `json` | Structured project dataset or configuration. |
| `1974.json` | `public/data/albums/1974.json` | `json` | Structured project dataset or configuration. |
| `1975.json` | `public/data/albums/1975.json` | `json` | Structured project dataset or configuration. |
| `1976.json` | `public/data/albums/1976.json` | `json` | Structured project dataset or configuration. |
| `1977.json` | `public/data/albums/1977.json` | `json` | Structured project dataset or configuration. |
| `1978.json` | `public/data/albums/1978.json` | `json` | Structured project dataset or configuration. |
| `1979.json` | `public/data/albums/1979.json` | `json` | Structured project dataset or configuration. |
| `1980.json` | `public/data/albums/1980.json` | `json` | Structured project dataset or configuration. |
| `1981.json` | `public/data/albums/1981.json` | `json` | Structured project dataset or configuration. |
| `1982.json` | `public/data/albums/1982.json` | `json` | Structured project dataset or configuration. |
| `1983.json` | `public/data/albums/1983.json` | `json` | Structured project dataset or configuration. |
| `1984.json` | `public/data/albums/1984.json` | `json` | Structured project dataset or configuration. |
| `1985.json` | `public/data/albums/1985.json` | `json` | Structured project dataset or configuration. |
| `1986.json` | `public/data/albums/1986.json` | `json` | Structured project dataset or configuration. |
| `1987.json` | `public/data/albums/1987.json` | `json` | Structured project dataset or configuration. |
| `1988.json` | `public/data/albums/1988.json` | `json` | Structured project dataset or configuration. |
| `1989.json` | `public/data/albums/1989.json` | `json` | Structured project dataset or configuration. |
| `1990.json` | `public/data/albums/1990.json` | `json` | Structured project dataset or configuration. |
| `1991.json` | `public/data/albums/1991.json` | `json` | Structured project dataset or configuration. |
| `1992.json` | `public/data/albums/1992.json` | `json` | Structured project dataset or configuration. |
| `1993.json` | `public/data/albums/1993.json` | `json` | Structured project dataset or configuration. |
| `1994.json` | `public/data/albums/1994.json` | `json` | Structured project dataset or configuration. |
| `1995.json` | `public/data/albums/1995.json` | `json` | Structured project dataset or configuration. |
| `1996.json` | `public/data/albums/1996.json` | `json` | Structured project dataset or configuration. |
| `1997.json` | `public/data/albums/1997.json` | `json` | Structured project dataset or configuration. |
| `1998.json` | `public/data/albums/1998.json` | `json` | Structured project dataset or configuration. |
| `1999.json` | `public/data/albums/1999.json` | `json` | Structured project dataset or configuration. |
| `2000.json` | `public/data/albums/2000.json` | `json` | Structured project dataset or configuration. |
| `2001.json` | `public/data/albums/2001.json` | `json` | Structured project dataset or configuration. |
| `2002.json` | `public/data/albums/2002.json` | `json` | Structured project dataset or configuration. |
| `2003.json` | `public/data/albums/2003.json` | `json` | Structured project dataset or configuration. |
| `2004.json` | `public/data/albums/2004.json` | `json` | Structured project dataset or configuration. |
| `2005.json` | `public/data/albums/2005.json` | `json` | Structured project dataset or configuration. |
| `2006.json` | `public/data/albums/2006.json` | `json` | Structured project dataset or configuration. |
| `2007.json` | `public/data/albums/2007.json` | `json` | Structured project dataset or configuration. |
| `2008.json` | `public/data/albums/2008.json` | `json` | Structured project dataset or configuration. |
| `2009.json` | `public/data/albums/2009.json` | `json` | Structured project dataset or configuration. |
| `2010.json` | `public/data/albums/2010.json` | `json` | Structured project dataset or configuration. |
| `2011.json` | `public/data/albums/2011.json` | `json` | Structured project dataset or configuration. |
| `2012.json` | `public/data/albums/2012.json` | `json` | Structured project dataset or configuration. |
| `2013.json` | `public/data/albums/2013.json` | `json` | Structured project dataset or configuration. |
| `2014.json` | `public/data/albums/2014.json` | `json` | Structured project dataset or configuration. |
| `2015.json` | `public/data/albums/2015.json` | `json` | Structured project dataset or configuration. |
| `2016.json` | `public/data/albums/2016.json` | `json` | Structured project dataset or configuration. |
| `2017.json` | `public/data/albums/2017.json` | `json` | Structured project dataset or configuration. |
| `2018.json` | `public/data/albums/2018.json` | `json` | Structured project dataset or configuration. |
| `2019.json` | `public/data/albums/2019.json` | `json` | Structured project dataset or configuration. |
| `2020.json` | `public/data/albums/2020.json` | `json` | Structured project dataset or configuration. |
| `2021.json` | `public/data/albums/2021.json` | `json` | Structured project dataset or configuration. |
| `2022.json` | `public/data/albums/2022.json` | `json` | Structured project dataset or configuration. |
| `2023.json` | `public/data/albums/2023.json` | `json` | Structured project dataset or configuration. |
| `2024.json` | `public/data/albums/2024.json` | `json` | Structured project dataset or configuration. |
| `1958.json` | `public/data/artist-gravity/1958.json` | `json` | Structured project dataset or configuration. |
| `1959.json` | `public/data/artist-gravity/1959.json` | `json` | Structured project dataset or configuration. |
| `1960.json` | `public/data/artist-gravity/1960.json` | `json` | Structured project dataset or configuration. |
| `1961.json` | `public/data/artist-gravity/1961.json` | `json` | Structured project dataset or configuration. |
| `1962.json` | `public/data/artist-gravity/1962.json` | `json` | Structured project dataset or configuration. |
| `1963.json` | `public/data/artist-gravity/1963.json` | `json` | Structured project dataset or configuration. |
| `1964.json` | `public/data/artist-gravity/1964.json` | `json` | Structured project dataset or configuration. |
| `1965.json` | `public/data/artist-gravity/1965.json` | `json` | Structured project dataset or configuration. |
| `1966.json` | `public/data/artist-gravity/1966.json` | `json` | Structured project dataset or configuration. |
| `1967.json` | `public/data/artist-gravity/1967.json` | `json` | Structured project dataset or configuration. |
| `1968.json` | `public/data/artist-gravity/1968.json` | `json` | Structured project dataset or configuration. |
| `1969.json` | `public/data/artist-gravity/1969.json` | `json` | Structured project dataset or configuration. |
| `1970.json` | `public/data/artist-gravity/1970.json` | `json` | Structured project dataset or configuration. |
| `1971.json` | `public/data/artist-gravity/1971.json` | `json` | Structured project dataset or configuration. |
| `1972.json` | `public/data/artist-gravity/1972.json` | `json` | Structured project dataset or configuration. |
| `1973.json` | `public/data/artist-gravity/1973.json` | `json` | Structured project dataset or configuration. |
| `1974.json` | `public/data/artist-gravity/1974.json` | `json` | Structured project dataset or configuration. |
| `1975.json` | `public/data/artist-gravity/1975.json` | `json` | Structured project dataset or configuration. |
| `1976.json` | `public/data/artist-gravity/1976.json` | `json` | Structured project dataset or configuration. |
| `1977.json` | `public/data/artist-gravity/1977.json` | `json` | Structured project dataset or configuration. |
| `1978.json` | `public/data/artist-gravity/1978.json` | `json` | Structured project dataset or configuration. |
| `1979.json` | `public/data/artist-gravity/1979.json` | `json` | Structured project dataset or configuration. |
| `1980.json` | `public/data/artist-gravity/1980.json` | `json` | Structured project dataset or configuration. |
| `1981.json` | `public/data/artist-gravity/1981.json` | `json` | Structured project dataset or configuration. |
| `1982.json` | `public/data/artist-gravity/1982.json` | `json` | Structured project dataset or configuration. |
| `1983.json` | `public/data/artist-gravity/1983.json` | `json` | Structured project dataset or configuration. |
| `1984.json` | `public/data/artist-gravity/1984.json` | `json` | Structured project dataset or configuration. |
| `1985.json` | `public/data/artist-gravity/1985.json` | `json` | Structured project dataset or configuration. |
| `1986.json` | `public/data/artist-gravity/1986.json` | `json` | Structured project dataset or configuration. |
| `1987.json` | `public/data/artist-gravity/1987.json` | `json` | Structured project dataset or configuration. |
| `1988.json` | `public/data/artist-gravity/1988.json` | `json` | Structured project dataset or configuration. |
| `1989.json` | `public/data/artist-gravity/1989.json` | `json` | Structured project dataset or configuration. |
| `1990.json` | `public/data/artist-gravity/1990.json` | `json` | Structured project dataset or configuration. |
| `1991.json` | `public/data/artist-gravity/1991.json` | `json` | Structured project dataset or configuration. |
| `1992.json` | `public/data/artist-gravity/1992.json` | `json` | Structured project dataset or configuration. |
| `1993.json` | `public/data/artist-gravity/1993.json` | `json` | Structured project dataset or configuration. |
| `1994.json` | `public/data/artist-gravity/1994.json` | `json` | Structured project dataset or configuration. |
| `1995.json` | `public/data/artist-gravity/1995.json` | `json` | Structured project dataset or configuration. |
| `1996.json` | `public/data/artist-gravity/1996.json` | `json` | Structured project dataset or configuration. |
| `1997.json` | `public/data/artist-gravity/1997.json` | `json` | Structured project dataset or configuration. |
| `1998.json` | `public/data/artist-gravity/1998.json` | `json` | Structured project dataset or configuration. |
| `1999.json` | `public/data/artist-gravity/1999.json` | `json` | Structured project dataset or configuration. |
| `2000.json` | `public/data/artist-gravity/2000.json` | `json` | Structured project dataset or configuration. |
| `2001.json` | `public/data/artist-gravity/2001.json` | `json` | Structured project dataset or configuration. |
| `2002.json` | `public/data/artist-gravity/2002.json` | `json` | Structured project dataset or configuration. |
| `2003.json` | `public/data/artist-gravity/2003.json` | `json` | Structured project dataset or configuration. |
| `2004.json` | `public/data/artist-gravity/2004.json` | `json` | Structured project dataset or configuration. |
| `2005.json` | `public/data/artist-gravity/2005.json` | `json` | Structured project dataset or configuration. |
| `2006.json` | `public/data/artist-gravity/2006.json` | `json` | Structured project dataset or configuration. |
| `2007.json` | `public/data/artist-gravity/2007.json` | `json` | Structured project dataset or configuration. |
| `2008.json` | `public/data/artist-gravity/2008.json` | `json` | Structured project dataset or configuration. |
| `2009.json` | `public/data/artist-gravity/2009.json` | `json` | Structured project dataset or configuration. |
| `2010.json` | `public/data/artist-gravity/2010.json` | `json` | Structured project dataset or configuration. |
| `2011.json` | `public/data/artist-gravity/2011.json` | `json` | Structured project dataset or configuration. |
| `2012.json` | `public/data/artist-gravity/2012.json` | `json` | Structured project dataset or configuration. |
| `2013.json` | `public/data/artist-gravity/2013.json` | `json` | Structured project dataset or configuration. |
| `2014.json` | `public/data/artist-gravity/2014.json` | `json` | Structured project dataset or configuration. |
| `2015.json` | `public/data/artist-gravity/2015.json` | `json` | Structured project dataset or configuration. |
| `2016.json` | `public/data/artist-gravity/2016.json` | `json` | Structured project dataset or configuration. |
| `2017.json` | `public/data/artist-gravity/2017.json` | `json` | Structured project dataset or configuration. |
| `2018.json` | `public/data/artist-gravity/2018.json` | `json` | Structured project dataset or configuration. |
| `2019.json` | `public/data/artist-gravity/2019.json` | `json` | Structured project dataset or configuration. |
| `2020.json` | `public/data/artist-gravity/2020.json` | `json` | Structured project dataset or configuration. |
| `2021.json` | `public/data/artist-gravity/2021.json` | `json` | Structured project dataset or configuration. |
| `2022.json` | `public/data/artist-gravity/2022.json` | `json` | Structured project dataset or configuration. |
| `2023.json` | `public/data/artist-gravity/2023.json` | `json` | Structured project dataset or configuration. |
| `2024.json` | `public/data/artist-gravity/2024.json` | `json` | Structured project dataset or configuration. |
| `artist-timelines.json` | `public/data/artist-timelines.json` | `json` | Structured project dataset or configuration. |
| `1958.json` | `public/data/charts/1958.json` | `json` | Structured project dataset or configuration. |
| `1959.json` | `public/data/charts/1959.json` | `json` | Structured project dataset or configuration. |
| `1960.json` | `public/data/charts/1960.json` | `json` | Structured project dataset or configuration. |
| `1961.json` | `public/data/charts/1961.json` | `json` | Structured project dataset or configuration. |
| `1962.json` | `public/data/charts/1962.json` | `json` | Structured project dataset or configuration. |
| `1963.json` | `public/data/charts/1963.json` | `json` | Structured project dataset or configuration. |
| `1964.json` | `public/data/charts/1964.json` | `json` | Structured project dataset or configuration. |
| `1965.json` | `public/data/charts/1965.json` | `json` | Structured project dataset or configuration. |
| `1966.json` | `public/data/charts/1966.json` | `json` | Structured project dataset or configuration. |
| `1967.json` | `public/data/charts/1967.json` | `json` | Structured project dataset or configuration. |
| `1968.json` | `public/data/charts/1968.json` | `json` | Structured project dataset or configuration. |
| `1969.json` | `public/data/charts/1969.json` | `json` | Structured project dataset or configuration. |
| `1970.json` | `public/data/charts/1970.json` | `json` | Structured project dataset or configuration. |
| `1971.json` | `public/data/charts/1971.json` | `json` | Structured project dataset or configuration. |
| `1972.json` | `public/data/charts/1972.json` | `json` | Structured project dataset or configuration. |
| `1973.json` | `public/data/charts/1973.json` | `json` | Structured project dataset or configuration. |
| `1974.json` | `public/data/charts/1974.json` | `json` | Structured project dataset or configuration. |
| `1975.json` | `public/data/charts/1975.json` | `json` | Structured project dataset or configuration. |
| `1976.json` | `public/data/charts/1976.json` | `json` | Structured project dataset or configuration. |
| `1977.json` | `public/data/charts/1977.json` | `json` | Structured project dataset or configuration. |
| `1978.json` | `public/data/charts/1978.json` | `json` | Structured project dataset or configuration. |
| `1979.json` | `public/data/charts/1979.json` | `json` | Structured project dataset or configuration. |
| `1980.json` | `public/data/charts/1980.json` | `json` | Structured project dataset or configuration. |
| `1981.json` | `public/data/charts/1981.json` | `json` | Structured project dataset or configuration. |
| `1982.json` | `public/data/charts/1982.json` | `json` | Structured project dataset or configuration. |
| `1983.json` | `public/data/charts/1983.json` | `json` | Structured project dataset or configuration. |
| `1984.json` | `public/data/charts/1984.json` | `json` | Structured project dataset or configuration. |
| `1985.json` | `public/data/charts/1985.json` | `json` | Structured project dataset or configuration. |
| `1986.json` | `public/data/charts/1986.json` | `json` | Structured project dataset or configuration. |
| `1987.json` | `public/data/charts/1987.json` | `json` | Structured project dataset or configuration. |
| `1988.json` | `public/data/charts/1988.json` | `json` | Structured project dataset or configuration. |
| `1989.json` | `public/data/charts/1989.json` | `json` | Structured project dataset or configuration. |
| `1990.json` | `public/data/charts/1990.json` | `json` | Structured project dataset or configuration. |
| `1991.json` | `public/data/charts/1991.json` | `json` | Structured project dataset or configuration. |
| `1992.json` | `public/data/charts/1992.json` | `json` | Structured project dataset or configuration. |
| `1993.json` | `public/data/charts/1993.json` | `json` | Structured project dataset or configuration. |
| `1994.json` | `public/data/charts/1994.json` | `json` | Structured project dataset or configuration. |
| `1995.json` | `public/data/charts/1995.json` | `json` | Structured project dataset or configuration. |
| `1996.json` | `public/data/charts/1996.json` | `json` | Structured project dataset or configuration. |
| `1997.json` | `public/data/charts/1997.json` | `json` | Structured project dataset or configuration. |
| `1998.json` | `public/data/charts/1998.json` | `json` | Structured project dataset or configuration. |
| `1999.json` | `public/data/charts/1999.json` | `json` | Structured project dataset or configuration. |
| `2000.json` | `public/data/charts/2000.json` | `json` | Structured project dataset or configuration. |
| `2001.json` | `public/data/charts/2001.json` | `json` | Structured project dataset or configuration. |
| `2002.json` | `public/data/charts/2002.json` | `json` | Structured project dataset or configuration. |
| `2003.json` | `public/data/charts/2003.json` | `json` | Structured project dataset or configuration. |
| `2004.json` | `public/data/charts/2004.json` | `json` | Structured project dataset or configuration. |
| `2005.json` | `public/data/charts/2005.json` | `json` | Structured project dataset or configuration. |
| `2006.json` | `public/data/charts/2006.json` | `json` | Structured project dataset or configuration. |
| `2007.json` | `public/data/charts/2007.json` | `json` | Structured project dataset or configuration. |
| `2008.json` | `public/data/charts/2008.json` | `json` | Structured project dataset or configuration. |
| `2009.json` | `public/data/charts/2009.json` | `json` | Structured project dataset or configuration. |
| `2010.json` | `public/data/charts/2010.json` | `json` | Structured project dataset or configuration. |
| `2011.json` | `public/data/charts/2011.json` | `json` | Structured project dataset or configuration. |
| `2012.json` | `public/data/charts/2012.json` | `json` | Structured project dataset or configuration. |
| `2013.json` | `public/data/charts/2013.json` | `json` | Structured project dataset or configuration. |
| `2014.json` | `public/data/charts/2014.json` | `json` | Structured project dataset or configuration. |
| `2015.json` | `public/data/charts/2015.json` | `json` | Structured project dataset or configuration. |
| `2016.json` | `public/data/charts/2016.json` | `json` | Structured project dataset or configuration. |
| `2017.json` | `public/data/charts/2017.json` | `json` | Structured project dataset or configuration. |
| `2018.json` | `public/data/charts/2018.json` | `json` | Structured project dataset or configuration. |
| `2019.json` | `public/data/charts/2019.json` | `json` | Structured project dataset or configuration. |
| `2020.json` | `public/data/charts/2020.json` | `json` | Structured project dataset or configuration. |
| `2021.json` | `public/data/charts/2021.json` | `json` | Structured project dataset or configuration. |
| `2022.json` | `public/data/charts/2022.json` | `json` | Structured project dataset or configuration. |
| `2023.json` | `public/data/charts/2023.json` | `json` | Structured project dataset or configuration. |
| `2024.json` | `public/data/charts/2024.json` | `json` | Structured project dataset or configuration. |
| `history-index.json` | `public/data/history-index.json` | `json` | Structured project dataset or configuration. |
| `magazine-year-index.json` | `public/data/magazine-year-index.json` | `json` | Structured project dataset or configuration. |
| `video-index-1920s.json` | `public/data/video-index-1920s.json` | `json` | Structured project dataset or configuration. |
| `video-index-1930s.json` | `public/data/video-index-1930s.json` | `json` | Structured project dataset or configuration. |
| `video-index-1940s.json` | `public/data/video-index-1940s.json` | `json` | Structured project dataset or configuration. |
| `video-index-1950s.json` | `public/data/video-index-1950s.json` | `json` | Structured project dataset or configuration. |
| `video-index-1960s.json` | `public/data/video-index-1960s.json` | `json` | Structured project dataset or configuration. |
| `video-index-1970s.json` | `public/data/video-index-1970s.json` | `json` | Structured project dataset or configuration. |
| `video-index-1980s.json` | `public/data/video-index-1980s.json` | `json` | Structured project dataset or configuration. |
| `video-index-1990s.json` | `public/data/video-index-1990s.json` | `json` | Structured project dataset or configuration. |
| `video-index-2000s.json` | `public/data/video-index-2000s.json` | `json` | Structured project dataset or configuration. |
| `video-index-2010s.json` | `public/data/video-index-2010s.json` | `json` | Structured project dataset or configuration. |
| `video-index-2020s.json` | `public/data/video-index-2020s.json` | `json` | Structured project dataset or configuration. |
| `video-index.json` | `public/data/video-index.json` | `json` | Structured project dataset or configuration. |
| `r2_inventory.json` | `r2_inventory.json` | `json` | Structured project dataset or configuration. |
| `r2_thumbs.json` | `r2_thumbs.json` | `json` | Structured project dataset or configuration. |
| `vdj_history_full.json` | `raw-data/vdj_history_full.json` | `json` | Structured project dataset or configuration. |
| `context_1974.json` | `retroverse-1974/data/libraries/context_1974.json` | `json` | Structured project dataset or configuration. |
| `weeks_1974_minimal.csv` | `retroverse-1974/data/weeks/weeks_1974_minimal.csv` | `csv` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R01_annie-s-song__john-denver.render.json` | `retroverse-1974/out/1974/authentic_print_1974_v1/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R01_annie-s-song__john-denver.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `retroverse-1974/out/1974/authentic_print_1974_v1/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.render.json` | `retroverse-1974/out/1974/authentic_print_1974_v1/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R01_annie-s-song__john-denver.json` | `retroverse-1974/out/1974/authentic_print_1974_v1/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R01_annie-s-song__john-denver.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `retroverse-1974/out/1974/authentic_print_1974_v1/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.json` | `retroverse-1974/out/1974/authentic_print_1974_v1/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R01_annie-s-song__john-denver.render.json` | `retroverse-1974/out/1974/cinematic_painterly_1974_v1/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R01_annie-s-song__john-denver.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `retroverse-1974/out/1974/cinematic_painterly_1974_v1/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.render.json` | `retroverse-1974/out/1974/cinematic_painterly_1974_v1/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R01_annie-s-song__john-denver.json` | `retroverse-1974/out/1974/cinematic_painterly_1974_v1/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R01_annie-s-song__john-denver.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `retroverse-1974/out/1974/cinematic_painterly_1974_v1/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.json` | `retroverse-1974/out/1974/cinematic_painterly_1974_v1/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R01_annie-s-song__john-denver.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R01_annie-s-song__john-denver.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R03_rock-and-roll-heaven__the-righteous-brothers.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R03_rock-and-roll-heaven__the-righteous-brothers.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R04_rock-your-baby__george-mccrae.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R04_rock-your-baby__george-mccrae.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R05_rikki-don-t-lose-that-number__steely-dan.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R05_rikki-don-t-lose-that-number__steely-dan.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R06_feel-like-makin-love__roberta-flack.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R06_feel-like-makin-love__roberta-flack.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R07_the-air-that-i-breathe__the-hollies.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R07_the-air-that-i-breathe__the-hollies.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R08_rock-the-boat__the-hues-corporation.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R08_rock-the-boat__the-hues-corporation.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R09_please-come-to-boston__dave-loggins.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R09_please-come-to-boston__dave-loggins.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R10_call-on-me__chicago.render.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/logs/1974_W29_1974-07-27_R10_call-on-me__chicago.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R01_annie-s-song__john-denver.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R01_annie-s-song__john-denver.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R03_rock-and-roll-heaven__the-righteous-brothers.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R03_rock-and-roll-heaven__the-righteous-brothers.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R04_rock-your-baby__george-mccrae.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R04_rock-your-baby__george-mccrae.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R05_rikki-don-t-lose-that-number__steely-dan.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R05_rikki-don-t-lose-that-number__steely-dan.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R06_feel-like-makin-love__roberta-flack.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R06_feel-like-makin-love__roberta-flack.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R07_the-air-that-i-breathe__the-hollies.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R07_the-air-that-i-breathe__the-hollies.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R08_rock-the-boat__the-hues-corporation.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R08_rock-the-boat__the-hues-corporation.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R09_please-come-to-boston__dave-loggins.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R09_please-come-to-boston__dave-loggins.json` | `json` | Structured project dataset or configuration. |
| `1974_W29_1974-07-27_R10_call-on-me__chicago.json` | `retroverse-1974/out/1974/week_29_1974-07-22_1974-07-28/top10/meta/1974_W29_1974-07-27_R10_call-on-me__chicago.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R01_annie-s-song__john-denver.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R01_annie-s-song__john-denver.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R04_rikki-don-t-lose-that-number__steely-dan.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R04_rikki-don-t-lose-that-number__steely-dan.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R05_the-night-chicago-died__paper-lace.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R05_the-night-chicago-died__paper-lace.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R06_the-air-that-i-breathe__the-hollies.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R06_the-air-that-i-breathe__the-hollies.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R07_rock-and-roll-heaven__the-righteous-brothers.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R07_rock-and-roll-heaven__the-righteous-brothers.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R08_please-come-to-boston__dave-loggins.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R08_please-come-to-boston__dave-loggins.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R09_call-on-me__chicago.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R09_call-on-me__chicago.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R10_sideshow__blue-magic.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/logs/1974_W30_1974-08-03_R10_sideshow__blue-magic.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R01_annie-s-song__john-denver.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R01_annie-s-song__john-denver.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R04_rikki-don-t-lose-that-number__steely-dan.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R04_rikki-don-t-lose-that-number__steely-dan.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R05_the-night-chicago-died__paper-lace.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R05_the-night-chicago-died__paper-lace.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R06_the-air-that-i-breathe__the-hollies.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R06_the-air-that-i-breathe__the-hollies.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R07_rock-and-roll-heaven__the-righteous-brothers.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R07_rock-and-roll-heaven__the-righteous-brothers.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R08_please-come-to-boston__dave-loggins.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R08_please-come-to-boston__dave-loggins.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R09_call-on-me__chicago.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R09_call-on-me__chicago.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R10_sideshow__blue-magic.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top10/meta/1974_W30_1974-08-03_R10_sideshow__blue-magic.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R01_annie-s-song__john-denver.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R01_annie-s-song__john-denver.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.render.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top3/logs/1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R01_annie-s-song__john-denver.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R01_annie-s-song__john-denver.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R02_don-t-let-the-sun-go-down-on-me__elton-john.json` | `json` | Structured project dataset or configuration. |
| `1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.json` | `retroverse-1974/out/1974/week_30_1974-07-29_1974-08-04/top3/meta/1974_W30_1974-08-03_R03_feel-like-makin-love__roberta-flack.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R01_feel-like-makin-love__roberta-flack.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R01_feel-like-makin-love__roberta-flack.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R02_the-night-chicago-died__paper-lace.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R02_the-night-chicago-died__paper-lace.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R03_annie-s-song__john-denver.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R03_annie-s-song__john-denver.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R04_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R04_don-t-let-the-sun-go-down-on-me__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R05_please-come-to-boston__dave-loggins.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R05_please-come-to-boston__dave-loggins.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R06_call-on-me__chicago.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R06_call-on-me__chicago.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R07_waterloo__abba.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R07_waterloo__abba.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R08_sideshow__blue-magic.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R08_sideshow__blue-magic.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R09_wildwood-weed__jim-stafford.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R09_wildwood-weed__jim-stafford.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R10_tell-me-something-good__rufus.render.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/logs/1974_W31_1974-08-10_R10_tell-me-something-good__rufus.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R01_feel-like-makin-love__roberta-flack.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R01_feel-like-makin-love__roberta-flack.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R02_the-night-chicago-died__paper-lace.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R02_the-night-chicago-died__paper-lace.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R03_annie-s-song__john-denver.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R03_annie-s-song__john-denver.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R04_don-t-let-the-sun-go-down-on-me__elton-john.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R04_don-t-let-the-sun-go-down-on-me__elton-john.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R05_please-come-to-boston__dave-loggins.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R05_please-come-to-boston__dave-loggins.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R06_call-on-me__chicago.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R06_call-on-me__chicago.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R07_waterloo__abba.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R07_waterloo__abba.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R08_sideshow__blue-magic.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R08_sideshow__blue-magic.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R09_wildwood-weed__jim-stafford.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R09_wildwood-weed__jim-stafford.json` | `json` | Structured project dataset or configuration. |
| `1974_W31_1974-08-10_R10_tell-me-something-good__rufus.json` | `retroverse-1974/out/1974/week_31_1974-08-05_1974-08-11/top10/meta/1974_W31_1974-08-10_R10_tell-me-something-good__rufus.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R01_the-night-chicago-died__paper-lace.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R01_the-night-chicago-died__paper-lace.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R02_feel-like-makin-love__roberta-flack.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R02_feel-like-makin-love__roberta-flack.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R03_you-re-having-my-baby__paul-anka.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R03_you-re-having-my-baby__paul-anka.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R04_tell-me-something-good__rufus.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R04_tell-me-something-good__rufus.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R05_please-come-to-boston__dave-loggins.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R05_please-come-to-boston__dave-loggins.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R06_call-on-me__chicago.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R06_call-on-me__chicago.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R07_waterloo__abba.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R07_waterloo__abba.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R08_wildwood-weed__jim-stafford.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R08_wildwood-weed__jim-stafford.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R09_i-m-leaving-it-all-up-to-you__donny.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R09_i-m-leaving-it-all-up-to-you__donny.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R10_sideshow__blue-magic.render.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/logs/1974_W32_1974-08-17_R10_sideshow__blue-magic.render.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R01_the-night-chicago-died__paper-lace.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R01_the-night-chicago-died__paper-lace.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R02_feel-like-makin-love__roberta-flack.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R02_feel-like-makin-love__roberta-flack.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R03_you-re-having-my-baby__paul-anka.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R03_you-re-having-my-baby__paul-anka.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R04_tell-me-something-good__rufus.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R04_tell-me-something-good__rufus.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R05_please-come-to-boston__dave-loggins.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R05_please-come-to-boston__dave-loggins.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R06_call-on-me__chicago.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R06_call-on-me__chicago.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R07_waterloo__abba.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R07_waterloo__abba.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R08_wildwood-weed__jim-stafford.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R08_wildwood-weed__jim-stafford.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R09_i-m-leaving-it-all-up-to-you__donny.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R09_i-m-leaving-it-all-up-to-you__donny.json` | `json` | Structured project dataset or configuration. |
| `1974_W32_1974-08-17_R10_sideshow__blue-magic.json` | `retroverse-1974/out/1974/week_32_1974-08-12_1974-08-18/top10/meta/1974_W32_1974-08-17_R10_sideshow__blue-magic.json` | `json` | Structured project dataset or configuration. |
| `pipeline_1974_w29_w32_top10.yaml` | `retroverse-1974/pipeline/config/pipeline_1974_w29_w32_top10.yaml` | `yaml` | Structured project dataset or configuration. |
| `pipeline_1974_w30_top3_authentic_print_1974_v1_720x1280.yaml` | `retroverse-1974/pipeline/config/pipeline_1974_w30_top3_authentic_print_1974_v1_720x1280.yaml` | `yaml` | Structured project dataset or configuration. |
| `pipeline_1974_w30_top3_cinematic_painterly_1974_v1_720x1280.yaml` | `retroverse-1974/pipeline/config/pipeline_1974_w30_top3_cinematic_painterly_1974_v1_720x1280.yaml` | `yaml` | Structured project dataset or configuration. |
| `pipeline_1974_w30_top3_era_1969_1974_v1_720x1280.yaml` | `retroverse-1974/pipeline/config/pipeline_1974_w30_top3_era_1969_1974_v1_720x1280.yaml` | `yaml` | Structured project dataset or configuration. |
| `ambient.csv` | `retroverse-1974/runs/2026-02-25_w29-w32_top10/ambient.csv` | `csv` | Structured project dataset or configuration. |
| `batch_log.csv` | `retroverse-1974/runs/2026-02-25_w29-w32_top10/batch_log.csv` | `csv` | Structured project dataset or configuration. |
| `run_config_resolved.json` | `retroverse-1974/runs/2026-02-25_w29-w32_top10/run_config_resolved.json` | `json` | Structured project dataset or configuration. |
| `schema_detection.json` | `retroverse-1974/runs/2026-02-25_w29-w32_top10/schema_detection.json` | `json` | Structured project dataset or configuration. |
| `spine.csv` | `retroverse-1974/runs/2026-02-25_w29-w32_top10/spine.csv` | `csv` | Structured project dataset or configuration. |
| `summary.json` | `retroverse-1974/runs/2026-02-25_w29-w32_top10/summary.json` | `json` | Structured project dataset or configuration. |
| `validation_report.json` | `retroverse-1974/runs/2026-02-25_w29-w32_top10/validation_report.json` | `json` | Structured project dataset or configuration. |
| `ambient.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_authentic_print_1974_v1_720x1280/ambient.csv` | `csv` | Structured project dataset or configuration. |
| `batch_log.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_authentic_print_1974_v1_720x1280/batch_log.csv` | `csv` | Structured project dataset or configuration. |
| `run_config_resolved.json` | `retroverse-1974/runs/2026-02-26_w30_top3_authentic_print_1974_v1_720x1280/run_config_resolved.json` | `json` | Structured project dataset or configuration. |
| `schema_detection.json` | `retroverse-1974/runs/2026-02-26_w30_top3_authentic_print_1974_v1_720x1280/schema_detection.json` | `json` | Structured project dataset or configuration. |
| `spine.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_authentic_print_1974_v1_720x1280/spine.csv` | `csv` | Structured project dataset or configuration. |
| `summary.json` | `retroverse-1974/runs/2026-02-26_w30_top3_authentic_print_1974_v1_720x1280/summary.json` | `json` | Structured project dataset or configuration. |
| `validation_report.json` | `retroverse-1974/runs/2026-02-26_w30_top3_authentic_print_1974_v1_720x1280/validation_report.json` | `json` | Structured project dataset or configuration. |
| `ambient.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_cinematic_painterly_1974_v1_720x1280/ambient.csv` | `csv` | Structured project dataset or configuration. |
| `batch_log.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_cinematic_painterly_1974_v1_720x1280/batch_log.csv` | `csv` | Structured project dataset or configuration. |
| `run_config_resolved.json` | `retroverse-1974/runs/2026-02-26_w30_top3_cinematic_painterly_1974_v1_720x1280/run_config_resolved.json` | `json` | Structured project dataset or configuration. |
| `schema_detection.json` | `retroverse-1974/runs/2026-02-26_w30_top3_cinematic_painterly_1974_v1_720x1280/schema_detection.json` | `json` | Structured project dataset or configuration. |
| `spine.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_cinematic_painterly_1974_v1_720x1280/spine.csv` | `csv` | Structured project dataset or configuration. |
| `summary.json` | `retroverse-1974/runs/2026-02-26_w30_top3_cinematic_painterly_1974_v1_720x1280/summary.json` | `json` | Structured project dataset or configuration. |
| `validation_report.json` | `retroverse-1974/runs/2026-02-26_w30_top3_cinematic_painterly_1974_v1_720x1280/validation_report.json` | `json` | Structured project dataset or configuration. |
| `ambient.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_era_1969_1974_v1_720x1280/ambient.csv` | `csv` | Structured project dataset or configuration. |
| `batch_log.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_era_1969_1974_v1_720x1280/batch_log.csv` | `csv` | Structured project dataset or configuration. |
| `run_config_resolved.json` | `retroverse-1974/runs/2026-02-26_w30_top3_era_1969_1974_v1_720x1280/run_config_resolved.json` | `json` | Structured project dataset or configuration. |
| `schema_detection.json` | `retroverse-1974/runs/2026-02-26_w30_top3_era_1969_1974_v1_720x1280/schema_detection.json` | `json` | Structured project dataset or configuration. |
| `spine.csv` | `retroverse-1974/runs/2026-02-26_w30_top3_era_1969_1974_v1_720x1280/spine.csv` | `csv` | Structured project dataset or configuration. |
| `summary.json` | `retroverse-1974/runs/2026-02-26_w30_top3_era_1969_1974_v1_720x1280/summary.json` | `json` | Structured project dataset or configuration. |
| `validation_report.json` | `retroverse-1974/runs/2026-02-26_w30_top3_era_1969_1974_v1_720x1280/validation_report.json` | `json` | Structured project dataset or configuration. |
| `DATA_INVENTORY.md` | `retroverse-magazine/DATA_INVENTORY.md` | `markdown` | Project documentation. |
| `art_index.json` | `retroverse-magazine/art-library/art_index.json` | `json` | Shared RetroVerse magazine artwork asset. |
| `retroverse_editorial_charter.md` | `retroverse-magazine/charter/retroverse_editorial_charter.md` | `markdown` | Project documentation. |
| `DATA_SOURCES.yaml` | `retroverse-magazine/data/DATA_SOURCES.yaml` | `yaml` | Structured project dataset or configuration. |
| `image_prompts.json` | `retroverse-magazine/issues/1978/art/image_prompts.json` | `json` | Issue-level artwork asset. |
| `charts.json` | `retroverse-magazine/issues/1978/data/charts.json` | `json` | Issue-specific source or generated page content. |
| `editorial.json` | `retroverse-magazine/issues/1978/data/editorial.json` | `json` | Issue-specific source or generated page content. |
| `issue.json` | `retroverse-magazine/issues/1978/data/issue.json` | `json` | Issue-specific source or generated page content. |
| `movies.json` | `retroverse-magazine/issues/1978/data/movies.json` | `json` | Issue-specific source or generated page content. |
| `tv.json` | `retroverse-magazine/issues/1978/data/tv.json` | `json` | Issue-specific source or generated page content. |
| `image_prompts.json` | `retroverse-magazine/issues/art/image_prompts.json` | `json` | Issue-level artwork asset. |
| `1978_context.json` | `retroverse-magazine/issues/context/1978_context.json` | `json` | Generated issue context artifact. |
| `example_context_1978.json` | `retroverse-magazine/issues/context/example_context_1978.json` | `json` | Generated issue context artifact. |
| `layout_templates.json` | `retroverse-magazine/layout-library/schemas/layout_templates.json` | `json` | Structured project dataset or configuration. |
| `master_1978_1981.json` | `retroverse-output/master_1978_1981.json` | `json` | Structured project dataset or configuration. |
| `retroverse_year_end_1958.csv` | `retroverse-output/retroverse_year_end_1958.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1958_2024_all.csv` | `retroverse-output/retroverse_year_end_1958_2024_all.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1958_top40.csv` | `retroverse-output/retroverse_year_end_1958_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1959.csv` | `retroverse-output/retroverse_year_end_1959.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1959_top40.csv` | `retroverse-output/retroverse_year_end_1959_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1960.csv` | `retroverse-output/retroverse_year_end_1960.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1960_top40.csv` | `retroverse-output/retroverse_year_end_1960_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1961.csv` | `retroverse-output/retroverse_year_end_1961.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1961_top40.csv` | `retroverse-output/retroverse_year_end_1961_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1962.csv` | `retroverse-output/retroverse_year_end_1962.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1962_top40.csv` | `retroverse-output/retroverse_year_end_1962_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1963.csv` | `retroverse-output/retroverse_year_end_1963.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1963_top40.csv` | `retroverse-output/retroverse_year_end_1963_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1964.csv` | `retroverse-output/retroverse_year_end_1964.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1964_top40.csv` | `retroverse-output/retroverse_year_end_1964_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1965.csv` | `retroverse-output/retroverse_year_end_1965.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1965_top40.csv` | `retroverse-output/retroverse_year_end_1965_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1966.csv` | `retroverse-output/retroverse_year_end_1966.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1966_top40.csv` | `retroverse-output/retroverse_year_end_1966_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1967.csv` | `retroverse-output/retroverse_year_end_1967.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1967_top40.csv` | `retroverse-output/retroverse_year_end_1967_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1968.csv` | `retroverse-output/retroverse_year_end_1968.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1968_top40.csv` | `retroverse-output/retroverse_year_end_1968_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1969.csv` | `retroverse-output/retroverse_year_end_1969.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1969_top40.csv` | `retroverse-output/retroverse_year_end_1969_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1970.csv` | `retroverse-output/retroverse_year_end_1970.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1970_top40.csv` | `retroverse-output/retroverse_year_end_1970_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1971.csv` | `retroverse-output/retroverse_year_end_1971.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1971_top40.csv` | `retroverse-output/retroverse_year_end_1971_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1972.csv` | `retroverse-output/retroverse_year_end_1972.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1972_top40.csv` | `retroverse-output/retroverse_year_end_1972_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1973.csv` | `retroverse-output/retroverse_year_end_1973.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1973_top40.csv` | `retroverse-output/retroverse_year_end_1973_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1974.csv` | `retroverse-output/retroverse_year_end_1974.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1974_top40.csv` | `retroverse-output/retroverse_year_end_1974_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1975.csv` | `retroverse-output/retroverse_year_end_1975.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1975_top40.csv` | `retroverse-output/retroverse_year_end_1975_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1976.csv` | `retroverse-output/retroverse_year_end_1976.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1976_top40.csv` | `retroverse-output/retroverse_year_end_1976_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1977.csv` | `retroverse-output/retroverse_year_end_1977.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1977_top40.csv` | `retroverse-output/retroverse_year_end_1977_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1978.csv` | `retroverse-output/retroverse_year_end_1978.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1978_top40.csv` | `retroverse-output/retroverse_year_end_1978_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1979.csv` | `retroverse-output/retroverse_year_end_1979.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1979_top40.csv` | `retroverse-output/retroverse_year_end_1979_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1980.csv` | `retroverse-output/retroverse_year_end_1980.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1980_top40.csv` | `retroverse-output/retroverse_year_end_1980_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1981.csv` | `retroverse-output/retroverse_year_end_1981.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1981_top40.csv` | `retroverse-output/retroverse_year_end_1981_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1982.csv` | `retroverse-output/retroverse_year_end_1982.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1982_top40.csv` | `retroverse-output/retroverse_year_end_1982_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1983.csv` | `retroverse-output/retroverse_year_end_1983.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1983_top40.csv` | `retroverse-output/retroverse_year_end_1983_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1984.csv` | `retroverse-output/retroverse_year_end_1984.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1984_top40.csv` | `retroverse-output/retroverse_year_end_1984_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1985.csv` | `retroverse-output/retroverse_year_end_1985.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1985_top40.csv` | `retroverse-output/retroverse_year_end_1985_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1986.csv` | `retroverse-output/retroverse_year_end_1986.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1986_top40.csv` | `retroverse-output/retroverse_year_end_1986_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1987.csv` | `retroverse-output/retroverse_year_end_1987.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1987_top40.csv` | `retroverse-output/retroverse_year_end_1987_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1988.csv` | `retroverse-output/retroverse_year_end_1988.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1988_top40.csv` | `retroverse-output/retroverse_year_end_1988_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1989.csv` | `retroverse-output/retroverse_year_end_1989.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1989_top40.csv` | `retroverse-output/retroverse_year_end_1989_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1990.csv` | `retroverse-output/retroverse_year_end_1990.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1990_top40.csv` | `retroverse-output/retroverse_year_end_1990_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1991.csv` | `retroverse-output/retroverse_year_end_1991.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1991_top40.csv` | `retroverse-output/retroverse_year_end_1991_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1992.csv` | `retroverse-output/retroverse_year_end_1992.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1992_top40.csv` | `retroverse-output/retroverse_year_end_1992_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1993.csv` | `retroverse-output/retroverse_year_end_1993.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1993_top40.csv` | `retroverse-output/retroverse_year_end_1993_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1994.csv` | `retroverse-output/retroverse_year_end_1994.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1994_top40.csv` | `retroverse-output/retroverse_year_end_1994_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1995.csv` | `retroverse-output/retroverse_year_end_1995.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1995_top40.csv` | `retroverse-output/retroverse_year_end_1995_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1996.csv` | `retroverse-output/retroverse_year_end_1996.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1996_top40.csv` | `retroverse-output/retroverse_year_end_1996_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1997.csv` | `retroverse-output/retroverse_year_end_1997.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1997_top40.csv` | `retroverse-output/retroverse_year_end_1997_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1998.csv` | `retroverse-output/retroverse_year_end_1998.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1998_top40.csv` | `retroverse-output/retroverse_year_end_1998_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1999.csv` | `retroverse-output/retroverse_year_end_1999.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_1999_top40.csv` | `retroverse-output/retroverse_year_end_1999_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2000.csv` | `retroverse-output/retroverse_year_end_2000.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2000_top40.csv` | `retroverse-output/retroverse_year_end_2000_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2001.csv` | `retroverse-output/retroverse_year_end_2001.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2001_top40.csv` | `retroverse-output/retroverse_year_end_2001_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2002.csv` | `retroverse-output/retroverse_year_end_2002.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2002_top40.csv` | `retroverse-output/retroverse_year_end_2002_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2003.csv` | `retroverse-output/retroverse_year_end_2003.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2003_top40.csv` | `retroverse-output/retroverse_year_end_2003_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2004.csv` | `retroverse-output/retroverse_year_end_2004.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2004_top40.csv` | `retroverse-output/retroverse_year_end_2004_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2005.csv` | `retroverse-output/retroverse_year_end_2005.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2005_top40.csv` | `retroverse-output/retroverse_year_end_2005_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2006.csv` | `retroverse-output/retroverse_year_end_2006.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2006_top40.csv` | `retroverse-output/retroverse_year_end_2006_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2007.csv` | `retroverse-output/retroverse_year_end_2007.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2007_top40.csv` | `retroverse-output/retroverse_year_end_2007_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2008.csv` | `retroverse-output/retroverse_year_end_2008.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2008_top40.csv` | `retroverse-output/retroverse_year_end_2008_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2009.csv` | `retroverse-output/retroverse_year_end_2009.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2009_top40.csv` | `retroverse-output/retroverse_year_end_2009_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2010.csv` | `retroverse-output/retroverse_year_end_2010.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2010_top40.csv` | `retroverse-output/retroverse_year_end_2010_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2011.csv` | `retroverse-output/retroverse_year_end_2011.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2011_top40.csv` | `retroverse-output/retroverse_year_end_2011_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2012.csv` | `retroverse-output/retroverse_year_end_2012.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2012_top40.csv` | `retroverse-output/retroverse_year_end_2012_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2013.csv` | `retroverse-output/retroverse_year_end_2013.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2013_top40.csv` | `retroverse-output/retroverse_year_end_2013_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2014.csv` | `retroverse-output/retroverse_year_end_2014.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2014_top40.csv` | `retroverse-output/retroverse_year_end_2014_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2015.csv` | `retroverse-output/retroverse_year_end_2015.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2015_top40.csv` | `retroverse-output/retroverse_year_end_2015_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2016.csv` | `retroverse-output/retroverse_year_end_2016.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2016_top40.csv` | `retroverse-output/retroverse_year_end_2016_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2017.csv` | `retroverse-output/retroverse_year_end_2017.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2017_top40.csv` | `retroverse-output/retroverse_year_end_2017_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2018.csv` | `retroverse-output/retroverse_year_end_2018.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2018_top40.csv` | `retroverse-output/retroverse_year_end_2018_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2019.csv` | `retroverse-output/retroverse_year_end_2019.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2019_top40.csv` | `retroverse-output/retroverse_year_end_2019_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2020.csv` | `retroverse-output/retroverse_year_end_2020.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2020_top40.csv` | `retroverse-output/retroverse_year_end_2020_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2021.csv` | `retroverse-output/retroverse_year_end_2021.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2021_top40.csv` | `retroverse-output/retroverse_year_end_2021_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2022.csv` | `retroverse-output/retroverse_year_end_2022.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2022_top40.csv` | `retroverse-output/retroverse_year_end_2022_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2023.csv` | `retroverse-output/retroverse_year_end_2023.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2023_top40.csv` | `retroverse-output/retroverse_year_end_2023_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2024.csv` | `retroverse-output/retroverse_year_end_2024.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_end_2024_top40.csv` | `retroverse-output/retroverse_year_end_2024_top40.csv` | `csv` | Structured project dataset or configuration. |
| `retroverse_year_master_1958_2024.json` | `retroverse-output/retroverse_year_master_1958_2024.json` | `json` | Consolidated year master JSON for multi-year issue context. |
| `retroverse_support_cultural_1958_2024_top10.csv` | `retroverse-support/retroverse_support_cultural_1958_2024_top10.csv` | `csv` | Structured project dataset or configuration. |
| `_clientMiddlewareManifest.json` | `retroverse_chart/charts/_next/static/PjAafFw4ZFSUe4qFS5UXU/_clientMiddlewareManifest.json` | `json` | Structured project dataset or configuration. |
| `billboard_hot_100.json` | `retroverse_chart/charts/data/billboard_hot_100.json` | `json` | Structured project dataset or configuration. |
| `components.json` | `retroverse_chart/components.json` | `json` | Structured project dataset or configuration. |
| `package-lock.json` | `retroverse_chart/package-lock.json` | `json` | Structured project dataset or configuration. |
| `package.json` | `retroverse_chart/package.json` | `json` | Structured project dataset or configuration. |
| `pnpm-lock.yaml` | `retroverse_chart/pnpm-lock.yaml` | `yaml` | Structured project dataset or configuration. |
| `billboard_hot_100.json` | `retroverse_chart/public/data/billboard_hot_100.json` | `json` | Structured project dataset or configuration. |
| `tsconfig.json` | `retroverse_chart/tsconfig.json` | `json` | Structured project dataset or configuration. |
| `components.json` | `retroverse_v0/components.json` | `json` | Structured project dataset or configuration. |
| `package-lock.json` | `retroverse_v0/package-lock.json` | `json` | Structured project dataset or configuration. |
| `package.json` | `retroverse_v0/package.json` | `json` | Structured project dataset or configuration. |
| `pnpm-lock.yaml` | `retroverse_v0/pnpm-lock.yaml` | `yaml` | Structured project dataset or configuration. |
| `billboard_hot_100.json` | `retroverse_v0/public/data/billboard_hot_100.json` | `json` | Structured project dataset or configuration. |
| `tsconfig.json` | `retroverse_v0/tsconfig.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_10_then-came-you__dionne-warwicke.render.json` | `runs/deck_1974/logs/1974_deck_10_then-came-you__dionne-warwicke.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_2_come-and-get-your-love__redbone.render.json` | `runs/deck_1974/logs/1974_deck_2_come-and-get-your-love__redbone.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_3_bennie-and-the-jets__elton-john.render.json` | `runs/deck_1974/logs/1974_deck_3_bennie-and-the-jets__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_4_the-way-we-were__barbra-streisand.render.json` | `runs/deck_1974/logs/1974_deck_4_the-way-we-were__barbra-streisand.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_5_seasons-in-the-sun__terry-jacks.render.json` | `runs/deck_1974/logs/1974_deck_5_seasons-in-the-sun__terry-jacks.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_6_you-make-me-feel-brand-new__the-stylistics.render.json` | `runs/deck_1974/logs/1974_deck_6_you-make-me-feel-brand-new__the-stylistics.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_7_midnight-at-the-oasis__maria-muldaur.render.json` | `runs/deck_1974/logs/1974_deck_7_midnight-at-the-oasis__maria-muldaur.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_8_jungle-boogie__kool.render.json` | `runs/deck_1974/logs/1974_deck_8_jungle-boogie__kool.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_9_one-hell-of-a-woman__mac-davis.render.json` | `runs/deck_1974/logs/1974_deck_9_one-hell-of-a-woman__mac-davis.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_A_dancing-machine__jackson-5.render.json` | `runs/deck_1974/logs/1974_deck_A_dancing-machine__jackson-5.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_J_ranks_11_20.render.json` | `runs/deck_1974/logs/1974_deck_J_ranks_11_20.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_K_ranks_31_40.render.json` | `runs/deck_1974/logs/1974_deck_K_ranks_31_40.render.json` | `json` | Structured project dataset or configuration. |
| `1974_deck_Q_ranks_21_30.render.json` | `runs/deck_1974/logs/1974_deck_Q_ranks_21_30.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1974/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1974_deck_3_bennie-and-the-jets__elton-john.render.json` | `runs/deck_1974_partial_3/logs/1974_deck_3_bennie-and-the-jets__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1974_partial_3/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1975_deck_10_fame__david-bowie.render.json` | `runs/deck_1975/logs/1975_deck_10_fame__david-bowie.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_2_feelings__morris-albert.render.json` | `runs/deck_1975/logs/1975_deck_2_feelings__morris-albert.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_3_philadelphia-freedom__the-elton-john-band.render.json` | `runs/deck_1975/logs/1975_deck_3_philadelphia-freedom__the-elton-john-band.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_4_love-will-keep-us-together__the-captain.render.json` | `runs/deck_1975/logs/1975_deck_4_love-will-keep-us-together__the-captain.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_5_i-m-sorry__john-denver.render.json` | `runs/deck_1975/logs/1975_deck_5_i-m-sorry__john-denver.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_6_ballroom-blitz__sweet.render.json` | `runs/deck_1975/logs/1975_deck_6_ballroom-blitz__sweet.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_7_before-the-next-teardrop-falls__freddy-fender.render.json` | `runs/deck_1975/logs/1975_deck_7_before-the-next-teardrop-falls__freddy-fender.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_8_shining-star__earth-wind.render.json` | `runs/deck_1975/logs/1975_deck_8_shining-star__earth-wind.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_9_one-of-these-nights__eagles.render.json` | `runs/deck_1975/logs/1975_deck_9_one-of-these-nights__eagles.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_A_rhinestone-cowboy__glen-campbell.render.json` | `runs/deck_1975/logs/1975_deck_A_rhinestone-cowboy__glen-campbell.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_J_ranks_11_20.render.json` | `runs/deck_1975/logs/1975_deck_J_ranks_11_20.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_K_ranks_31_40.render.json` | `runs/deck_1975/logs/1975_deck_K_ranks_31_40.render.json` | `json` | Structured project dataset or configuration. |
| `1975_deck_Q_ranks_21_30.render.json` | `runs/deck_1975/logs/1975_deck_Q_ranks_21_30.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1975/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1975_deck_8_shining-star__earth-wind.render.json` | `runs/deck_1975_partial_8/logs/1975_deck_8_shining-star__earth-wind.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1975_partial_8/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1976_raw_10_misty-blue__dorothy-moore.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_10_misty-blue__dorothy-moore.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_2_love-is-alive__gary-wright.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_2_love-is-alive__gary-wright.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_3_play-that-funky-music__wild-cherry.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_3_play-that-funky-music__wild-cherry.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_4_kiss-and-say-goodbye__the-manhattans.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_4_kiss-and-say-goodbye__the-manhattans.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_5_sara-smile__daryl-hall-undefined-john-oates.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_5_sara-smile__daryl-hall-undefined-john-oates.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_6_i-d-really-love-to-see-you-tonight__england-dan.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_6_i-d-really-love-to-see-you-tonight__england-dan.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_7_shake-shake-shake-shake-your-booty__kc-and-the-sunshine-band.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_7_shake-shake-shake-shake-your-booty__kc-and-the-sunshine-band.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_8_december-1963-oh-what-a-night__the-4-seasons.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_8_december-1963-oh-what-a-night__the-4-seasons.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_9_disco-duck-part-i__rick-dees.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_9_disco-duck-part-i__rick-dees.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_A_a-fifth-of-beethoven__walter-murphy.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_A_a-fifth-of-beethoven__walter-murphy.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_J_ranks_11_20.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_J_ranks_11_20.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_K_ranks_31_40.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_K_ranks_31_40.render.json` | `json` | Structured project dataset or configuration. |
| `1976_raw_Q_ranks_21_30.render.json` | `runs/deck_1976_diamonds/logs/1976_raw_Q_ranks_21_30.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1976_diamonds/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1977_raw_10_nobody-does-it-better__carly-simon.render.json` | `runs/deck_1977_spades/logs/1977_raw_10_nobody-does-it-better__carly-simon.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_2_best-of-my-love__the-emotions.render.json` | `runs/deck_1977_spades/logs/1977_raw_2_best-of-my-love__the-emotions.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_3_evergreen-love-theme-from-a-star-is-born__barbra-streisand.render.json` | `runs/deck_1977_spades/logs/1977_raw_3_evergreen-love-theme-from-a-star-is-born__barbra-streisand.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_4_angel-in-your-arms__hot.render.json` | `runs/deck_1977_spades/logs/1977_raw_4_angel-in-your-arms__hot.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_5_boogie-nights__heatwave.render.json` | `runs/deck_1977_spades/logs/1977_raw_5_boogie-nights__heatwave.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_6_your-love-has-lifted-me-higher-and-higher__rita-coolidge.render.json` | `runs/deck_1977_spades/logs/1977_raw_6_your-love-has-lifted-me-higher-and-higher__rita-coolidge.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_7_you-light-up-my-life__debby-boone.render.json` | `runs/deck_1977_spades/logs/1977_raw_7_you-light-up-my-life__debby-boone.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_8_don-t-leave-me-this-way__thelma-houston.render.json` | `runs/deck_1977_spades/logs/1977_raw_8_don-t-leave-me-this-way__thelma-houston.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_9_undercover-angel__alan-o-day.render.json` | `runs/deck_1977_spades/logs/1977_raw_9_undercover-angel__alan-o-day.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_A_i-just-want-to-be-your-everything__andy-gibb.render.json` | `runs/deck_1977_spades/logs/1977_raw_A_i-just-want-to-be-your-everything__andy-gibb.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_J_ranks_11_20.render.json` | `runs/deck_1977_spades/logs/1977_raw_J_ranks_11_20.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_K_ranks_31_40.render.json` | `runs/deck_1977_spades/logs/1977_raw_K_ranks_31_40.render.json` | `json` | Structured project dataset or configuration. |
| `1977_raw_Q_ranks_21_30.render.json` | `runs/deck_1977_spades/logs/1977_raw_Q_ranks_21_30.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1977_spades/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1978_raw_10_i-love-the-nightlife-disco-round__alicia-bridges.render.json` | `runs/deck_1978_hearts/logs/1978_raw_10_i-love-the-nightlife-disco-round__alicia-bridges.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_10_i-love-the-nightlife__alicia-bridges.render.json` | `runs/deck_1978_hearts/logs/1978_raw_10_i-love-the-nightlife__alicia-bridges.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_2_shadow-dancing__andy-gibb.render.json` | `runs/deck_1978_hearts/logs/1978_raw_2_shadow-dancing__andy-gibb.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_3_hot-child-in-the-city__nick-gilder.render.json` | `runs/deck_1978_hearts/logs/1978_raw_3_hot-child-in-the-city__nick-gilder.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_4_kiss-you-all-over__exile.render.json` | `runs/deck_1978_hearts/logs/1978_raw_4_kiss-you-all-over__exile.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_5_night-fever__bee-gees.render.json` | `runs/deck_1978_hearts/logs/1978_raw_5_night-fever__bee-gees.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_6_boogie-oogie-oogie__a-taste-of-honey.render.json` | `runs/deck_1978_hearts/logs/1978_raw_6_boogie-oogie-oogie__a-taste-of-honey.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_7_lay-down-sally__eric-clapton.render.json` | `runs/deck_1978_hearts/logs/1978_raw_7_lay-down-sally__eric-clapton.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_8_you-re-the-one-that-i-want__john-travolta-olivia-newton-john.render.json` | `runs/deck_1978_hearts/logs/1978_raw_8_you-re-the-one-that-i-want__john-travolta-olivia-newton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_8_you-re-the-one-that-i-want__john-travolta.render.json` | `runs/deck_1978_hearts/logs/1978_raw_8_you-re-the-one-that-i-want__john-travolta.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_9_love-is-thicker-than-water__andy-gibb.render.json` | `runs/deck_1978_hearts/logs/1978_raw_9_love-is-thicker-than-water__andy-gibb.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_A_stayin-alive__bee-gees.render.json` | `runs/deck_1978_hearts/logs/1978_raw_A_stayin-alive__bee-gees.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_J_ranks_11_20.render.json` | `runs/deck_1978_hearts/logs/1978_raw_J_ranks_11_20.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_J_sultans-of-swing__dire-straits.render.json` | `runs/deck_1978_hearts/logs/1978_raw_J_sultans-of-swing__dire-straits.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_K_baker-street__gerry-rafferty.render.json` | `runs/deck_1978_hearts/logs/1978_raw_K_baker-street__gerry-rafferty.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_K_ranks_31_40.render.json` | `runs/deck_1978_hearts/logs/1978_raw_K_ranks_31_40.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_Q_ranks_21_30.render.json` | `runs/deck_1978_hearts/logs/1978_raw_Q_ranks_21_30.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_Q_roll-with-the-changes__reo-speedwagon.render.json` | `runs/deck_1978_hearts/logs/1978_raw_Q_roll-with-the-changes__reo-speedwagon.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_R1_recap-11-20__top-40-recap.render.json` | `runs/deck_1978_hearts/logs/1978_raw_R1_recap-11-20__top-40-recap.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_R2_recap-21-30__top-40-recap.render.json` | `runs/deck_1978_hearts/logs/1978_raw_R2_recap-21-30__top-40-recap.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_R3_recap-31-40__top-40-recap.render.json` | `runs/deck_1978_hearts/logs/1978_raw_R3_recap-31-40__top-40-recap.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_R4_1978-year-overview__retroverse-editorial-desk.render.json` | `runs/deck_1978_hearts/logs/1978_raw_R4_1978-year-overview__retroverse-editorial-desk.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1978_hearts/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1978_raw_2_shadow-dancing__andy-gibb.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4-5/logs/1978_raw_2_shadow-dancing__andy-gibb.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_3_hot-child-in-the-city__nick-gilder.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4-5/logs/1978_raw_3_hot-child-in-the-city__nick-gilder.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_4_kiss-you-all-over__exile.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4-5/logs/1978_raw_4_kiss-you-all-over__exile.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_5_night-fever__bee-gees.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4-5/logs/1978_raw_5_night-fever__bee-gees.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_A_stayin-alive__bee-gees.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4-5/logs/1978_raw_A_stayin-alive__bee-gees.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1978_hearts_partial_A-2-3-4-5/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1978_raw_2_shadow-dancing__andy-gibb.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4/logs/1978_raw_2_shadow-dancing__andy-gibb.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_3_hot-child-in-the-city__nick-gilder.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4/logs/1978_raw_3_hot-child-in-the-city__nick-gilder.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_4_kiss-you-all-over__exile.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4/logs/1978_raw_4_kiss-you-all-over__exile.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_A_stayin-alive__bee-gees.render.json` | `runs/deck_1978_hearts_partial_A-2-3-4/logs/1978_raw_A_stayin-alive__bee-gees.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1978_hearts_partial_A-2-3-4/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1978_raw_2_shadow-dancing__andy-gibb.render.json` | `runs/deck_1978_hearts_partial_A-2-3/logs/1978_raw_2_shadow-dancing__andy-gibb.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_3_hot-child-in-the-city__nick-gilder.render.json` | `runs/deck_1978_hearts_partial_A-2-3/logs/1978_raw_3_hot-child-in-the-city__nick-gilder.render.json` | `json` | Structured project dataset or configuration. |
| `1978_raw_A_stayin-alive__bee-gees.render.json` | `runs/deck_1978_hearts_partial_A-2-3/logs/1978_raw_A_stayin-alive__bee-gees.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1978_hearts_partial_A-2-3/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1978_raw_A_stayin-alive__bee-gees.render.json` | `runs/deck_1978_hearts_partial_A/logs/1978_raw_A_stayin-alive__bee-gees.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1978_hearts_partial_A/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1979_raw_10_reunited__peaches.render.json` | `runs/deck_1979_clubs/logs/1979_raw_10_reunited__peaches.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_2_i-will-survive__gloria-gaynor.render.json` | `runs/deck_1979_clubs/logs/1979_raw_2_i-will-survive__gloria-gaynor.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_3_hot-stuff__donna-summer.render.json` | `runs/deck_1979_clubs/logs/1979_raw_3_hot-stuff__donna-summer.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_4_i-ll-never-love-this-way-again__dionne-warwick.render.json` | `runs/deck_1979_clubs/logs/1979_raw_4_i-ll-never-love-this-way-again__dionne-warwick.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_5_pop-muzik__m.render.json` | `runs/deck_1979_clubs/logs/1979_raw_5_pop-muzik__m.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_6_my-sharona__the-knack.render.json` | `runs/deck_1979_clubs/logs/1979_raw_6_my-sharona__the-knack.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_7_da-ya-think-i-m-sexy__rod-stewart.render.json` | `runs/deck_1979_clubs/logs/1979_raw_7_da-ya-think-i-m-sexy__rod-stewart.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_8_rise__herb-alpert.render.json` | `runs/deck_1979_clubs/logs/1979_raw_8_rise__herb-alpert.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_9_bad-girls__donna-summer.render.json` | `runs/deck_1979_clubs/logs/1979_raw_9_bad-girls__donna-summer.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_A_sad-eyes__robert-john.render.json` | `runs/deck_1979_clubs/logs/1979_raw_A_sad-eyes__robert-john.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_J_ranks_11_20.render.json` | `runs/deck_1979_clubs/logs/1979_raw_J_ranks_11_20.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_K_ranks_31_40.render.json` | `runs/deck_1979_clubs/logs/1979_raw_K_ranks_31_40.render.json` | `json` | Structured project dataset or configuration. |
| `1979_raw_Q_ranks_21_30.render.json` | `runs/deck_1979_clubs/logs/1979_raw_Q_ranks_21_30.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1979_clubs/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1980_raw_10_little-jeannie__elton-john.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_10_little-jeannie__elton-john.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_2_upside-down__diana-ross.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_2_upside-down__diana-ross.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_3_another-brick-in-the-wall-part-ii__pink-floyd.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_3_another-brick-in-the-wall-part-ii__pink-floyd.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_4_another-one-bites-the-dust__queen.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_4_another-one-bites-the-dust__queen.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_5_all-out-of-love__air-supply.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_5_all-out-of-love__air-supply.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_6_it-s-still-rock-and-roll-to-me__billy-joel.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_6_it-s-still-rock-and-roll-to-me__billy-joel.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_7_crazy-little-thing-called-love__queen.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_7_crazy-little-thing-called-love__queen.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_8_coming-up-live-at-glasgow__paul-mccartney-and-wings.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_8_coming-up-live-at-glasgow__paul-mccartney-and-wings.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_9_the-rose__bette-midler.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_9_the-rose__bette-midler.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_A_call-me__blondie.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_A_call-me__blondie.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_J_ranks_11_20.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_J_ranks_11_20.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_K_ranks_31_40.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_K_ranks_31_40.render.json` | `json` | Structured project dataset or configuration. |
| `1980_raw_Q_ranks_21_30.render.json` | `runs/deck_1980_diamonds/logs/1980_raw_Q_ranks_21_30.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1980_diamonds/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `1981_raw_10_arthur-s-theme-best-that-you-can-do__christopher-cross.render.json` | `runs/deck_1981_spades/logs/1981_raw_10_arthur-s-theme-best-that-you-can-do__christopher-cross.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_2_bette-davis-eyes__kim-carnes.render.json` | `runs/deck_1981_spades/logs/1981_raw_2_bette-davis-eyes__kim-carnes.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_3_endless-love__diana-ross.render.json` | `runs/deck_1981_spades/logs/1981_raw_3_endless-love__diana-ross.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_4_queen-of-hearts__juice-newton.render.json` | `runs/deck_1981_spades/logs/1981_raw_4_queen-of-hearts__juice-newton.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_5_theme-from-greatest-american-hero-believe-it-or-not__joey-scarbury.render.json` | `runs/deck_1981_spades/logs/1981_raw_5_theme-from-greatest-american-hero-believe-it-or-not__joey-scarbury.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_6_being-with-you__smokey-robinson.render.json` | `runs/deck_1981_spades/logs/1981_raw_6_being-with-you__smokey-robinson.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_7_keep-on-loving-you__reo-speedwagon.render.json` | `runs/deck_1981_spades/logs/1981_raw_7_keep-on-loving-you__reo-speedwagon.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_8_slow-hand__the-pointer-sisters.render.json` | `runs/deck_1981_spades/logs/1981_raw_8_slow-hand__the-pointer-sisters.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_9_just-the-two-of-us__grover-washington-jr.render.json` | `runs/deck_1981_spades/logs/1981_raw_9_just-the-two-of-us__grover-washington-jr.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_A_jessie-s-girl__rick-springfield.render.json` | `runs/deck_1981_spades/logs/1981_raw_A_jessie-s-girl__rick-springfield.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_J_ranks_11_20.render.json` | `runs/deck_1981_spades/logs/1981_raw_J_ranks_11_20.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_K_ranks_31_40.render.json` | `runs/deck_1981_spades/logs/1981_raw_K_ranks_31_40.render.json` | `json` | Structured project dataset or configuration. |
| `1981_raw_Q_ranks_21_30.render.json` | `runs/deck_1981_spades/logs/1981_raw_Q_ranks_21_30.render.json` | `json` | Structured project dataset or configuration. |
| `render_config.yaml` | `runs/deck_1981_spades/render_config.yaml` | `yaml` | Structured project dataset or configuration. |
| `package.json` | `tools/package.json` | `json` | Structured project dataset or configuration. |
| `pipeline.config.json` | `tools/pipeline.config.json` | `json` | Structured project dataset or configuration. |
| `tsconfig.json` | `tools/tsconfig.json` | `json` | Structured project dataset or configuration. |
| `tsconfig.app.json` | `tsconfig.app.json` | `json` | Structured project dataset or configuration. |
| `tsconfig.json` | `tsconfig.json` | `json` | Structured project dataset or configuration. |
| `tsconfig.node.json` | `tsconfig.node.json` | `json` | Structured project dataset or configuration. |
| `tsconfig.pipeline.json` | `tsconfig.pipeline.json` | `json` | Structured project dataset or configuration. |
| `year_end_top_40_1976.json` | `year_end_top_40_1976.json` | `json` | Year-end Top 40 song export by year. |
| `year_end_top_40_1977.json` | `year_end_top_40_1977.json` | `json` | Year-end Top 40 song export by year. |
| `year_end_top_40_1978.json` | `year_end_top_40_1978.json` | `json` | Year-end Top 40 song export by year. |
| `year_end_top_40_1979.json` | `year_end_top_40_1979.json` | `json` | Year-end Top 40 song export by year. |
| `year_end_top_40_1980.json` | `year_end_top_40_1980.json` | `json` | Year-end Top 40 song export by year. |
| `year_end_top_40_1981.json` | `year_end_top_40_1981.json` | `json` | Year-end Top 40 song export by year. |

## Databases

| File | Relative Path | Type | Purpose |
|---|---|---|---|
| `cultural_datasets.db` | `data/index/cultural_datasets.db` | `database` | SQLite or database artifact. |
| `billboard-200-albums-charts.db` | `raw-data/billboard-200-albums-charts.db` | `database` | Billboard 200 album chart history database. |
| `billboard-hot-100.db` | `raw-data/billboard-hot-100.db` | `database` | Primary Billboard Hot 100 SQLite dataset. |
| `billboard-hot-100.db` | `retroverse-1974/data/db/billboard-hot-100.db` | `database` | Primary Billboard Hot 100 SQLite dataset. |

## Scripts

| File | Relative Path | Type | Purpose |
|---|---|---|---|
| `dsm_webstack_repair.sh` | `dsm_webstack_repair.sh` | `shell` | Shell automation script. |
| `history_collect.py` | `history_collect.py` | `python` | Python automation script. |
| `extract_vdj_history.py` | `pipeline/history/extract_vdj_history.py` | `python` | Python automation script. |
| `song_premise_generator.py` | `pipeline/scripts/song_premise_generator.py` | `python` | Python automation script. |
| `rv_build_prompts.py` | `retroverse-1974/pipeline/scripts/rv_build_prompts.py` | `python` | Python automation script. |
| `rv_extract_spine.py` | `retroverse-1974/pipeline/scripts/rv_extract_spine.py` | `python` | Python automation script. |
| `rv_render_images.py` | `retroverse-1974/pipeline/scripts/rv_render_images.py` | `python` | Python automation script. |
| `rv_run_batch.py` | `retroverse-1974/pipeline/scripts/rv_run_batch.py` | `python` | Python automation script. |
| `rv_runtime.py` | `retroverse-1974/pipeline/scripts/rv_runtime.py` | `python` | Python automation script. |
| `rv_select_ambient.py` | `retroverse-1974/pipeline/scripts/rv_select_ambient.py` | `python` | Python automation script. |
| `rv_validate_outputs.py` | `retroverse-1974/pipeline/scripts/rv_validate_outputs.py` | `python` | Python automation script. |
| `generate_magazine.py` | `retroverse-magazine/generate_magazine.py` | `python` | Python automation script. |
| `audit_billboard200_db.py` | `retroverse-magazine/scripts/audit_billboard200_db.py` | `python` | Python automation script. |
| `audit_hot100_db.py` | `retroverse-magazine/scripts/audit_hot100_db.py` | `python` | Python automation script. |
| `build_full_issue.py` | `retroverse-magazine/scripts/build_full_issue.py` | `python` | Python automation script. |
| `build_issue.py` | `retroverse-magazine/scripts/build_issue.py` | `python` | Python automation script. |
| `db_common.py` | `retroverse-magazine/scripts/db_common.py` | `python` | Python automation script. |
| `editorial_supervisor.py` | `retroverse-magazine/scripts/editorial_supervisor.py` | `python` | Python automation script. |
| `find_art_asset.py` | `retroverse-magazine/scripts/find_art_asset.py` | `python` | Python automation script. |
| `generate_art_prompts.py` | `retroverse-magazine/scripts/generate_art_prompts.py` | `python` | Python automation script. |
| `generate_editorial.py` | `retroverse-magazine/scripts/generate_editorial.py` | `python` | Python automation script. |
| `generate_illustrations.py` | `retroverse-magazine/scripts/generate_illustrations.py` | `python` | Python automation script. |
| `generate_marginals.py` | `retroverse-magazine/scripts/generate_marginals.py` | `python` | Python automation script. |
| `generate_year_context.py` | `retroverse-magazine/scripts/generate_year_context.py` | `python` | Python automation script. |
| `index_artwork.py` | `retroverse-magazine/scripts/index_artwork.py` | `python` | Python automation script. |
| `print_daily_refresh_instructions.py` | `retroverse-magazine/scripts/print_daily_refresh_instructions.py` | `python` | Python automation script. |
| `update_data_inventory.py` | `retroverse-magazine/scripts/update_data_inventory.py` | `python` | Python automation script. |
| `build_retroverse_support_1958_2024.py` | `retroverse-output/build_retroverse_support_1958_2024.py` | `python` | Python automation script. |
| `export_billboard_json.py` | `retroverse_chart/scripts/export_billboard_json.py` | `python` | Python automation script. |
| `export_billboard_json.py` | `retroverse_v0/export_billboard_json.py` | `python` | Python automation script. |
| `archive_magazine_harvester.py` | `scripts/archive_magazine_harvester.py` | `python` | Python automation script. |
| `build_cultural_index.py` | `scripts/build_cultural_index.py` | `python` | Python automation script. |
| `build_multi_year_retroverse_decks.py` | `scripts/build_multi_year_retroverse_decks.py` | `python` | Python automation script. |
| `build_year_master.py` | `scripts/build_year_master.py` | `python` | Python automation script. |
| `compose_1974_deck.py` | `scripts/compose_1974_deck.py` | `python` | Python automation script. |
| `compute_billboard_stats.py` | `scripts/compute_billboard_stats.py` | `python` | Python automation script. |
| `dsm-web-stack-forensics.sh` | `scripts/dsm-web-stack-forensics.sh` | `shell` | Shell automation script. |
| `export-album-summaries.sh` | `scripts/export-album-summaries.sh` | `shell` | Shell automation script. |
| `export-hot100-summaries.sh` | `scripts/export-hot100-summaries.sh` | `shell` | Shell automation script. |
| `fix_1978_magazine.py` | `scripts/fix_1978_magazine.py` | `python` | Python automation script. |
| `generate_1974_deck.py` | `scripts/generate_1974_deck.py` | `python` | Python automation script. |
| `generate_at40_week30_rank01.py` | `scripts/generate_at40_week30_rank01.py` | `python` | Python automation script. |
| `generate_magazine_catalog.py` | `scripts/generate_magazine_catalog.py` | `python` | Python automation script. |
| `generate_retroverse_1974_week30_top5.py` | `scripts/generate_retroverse_1974_week30_top5.py` | `python` | Python automation script. |
| `generate_yearly_magazine_index.py` | `scripts/generate_yearly_magazine_index.py` | `python` | Python automation script. |
| `harvest_billboard.py` | `scripts/harvest_billboard.py` | `python` | Python automation script. |
| `harvest_magazines.py` | `scripts/harvest_magazines.py` | `python` | Python automation script. |
| `harvest_radio_logs.py` | `scripts/harvest_radio_logs.py` | `python` | Python automation script. |
| `harvest_tv_listings.py` | `scripts/harvest_tv_listings.py` | `python` | Python automation script. |
| `init_culture_dataset.py` | `scripts/init_culture_dataset.py` | `python` | Python automation script. |
| `merge_magazine_datasets.py` | `scripts/merge_magazine_datasets.py` | `python` | Python automation script. |
| `pipeline_common.py` | `scripts/pipeline_common.py` | `python` | Python automation script. |
| `rebuild_year_master.py` | `scripts/rebuild_year_master.py` | `python` | Python automation script. |
| `recover_issue_dates.py` | `scripts/recover_issue_dates.py` | `python` | Python automation script. |
| `recover_issue_dates_from_url.py` | `scripts/recover_issue_dates_from_url.py` | `python` | Python automation script. |
| `run_full_pipeline.py` | `scripts/run_full_pipeline.py` | `python` | Python automation script. |
| `rv_year_end_rank.py` | `scripts/rv_year_end_rank.py` | `python` | Python automation script. |
| `sync-index.sh` | `scripts/sync-index.sh` | `shell` | Shell automation script. |
| `analyze_playcounts.py` | `tools/analyze_playcounts.py` | `python` | Python automation script. |
| `faststart_mp4.sh` | `tools/faststart_mp4.sh` | `shell` | Shell automation script. |
| `install-folder-action.sh` | `tools/media-normalization/install-folder-action.sh` | `shell` | Shell automation script. |

## Generated Issues

| File | Relative Path | Type | Purpose |
|---|---|---|---|
| `charts.json` | `retroverse-magazine/issues/1978/data/charts.json` | `json` | Issue-specific source or generated page content. |
| `editorial.json` | `retroverse-magazine/issues/1978/data/editorial.json` | `json` | Issue-specific source or generated page content. |
| `issue.json` | `retroverse-magazine/issues/1978/data/issue.json` | `json` | Issue-specific source or generated page content. |
| `movies.json` | `retroverse-magazine/issues/1978/data/movies.json` | `json` | Issue-specific source or generated page content. |
| `tv.json` | `retroverse-magazine/issues/1978/data/tv.json` | `json` | Issue-specific source or generated page content. |
| `index.html` | `retroverse-magazine/issues/1978/index.html` | `html` | Issue-specific source or generated page content. |
| `page_01_cover.html` | `retroverse-magazine/issues/1978/layout/page_01_cover.html` | `html` | Issue-specific source or generated page content. |
| `page_02_contents.html` | `retroverse-magazine/issues/1978/layout/page_02_contents.html` | `html` | Issue-specific source or generated page content. |
| `page_03_editor.html` | `retroverse-magazine/issues/1978/layout/page_03_editor.html` | `html` | Issue-specific source or generated page content. |
| `page_04_feature_disco.html` | `retroverse-magazine/issues/1978/layout/page_04_feature_disco.html` | `html` | Issue-specific source or generated page content. |
| `page_05_feature_backlash.html` | `retroverse-magazine/issues/1978/layout/page_05_feature_backlash.html` | `html` | Issue-specific source or generated page content. |
| `page_06_collage_city.html` | `retroverse-magazine/issues/1978/layout/page_06_collage_city.html` | `html` | Issue-specific source or generated page content. |
| `page_07_parody_console.html` | `retroverse-magazine/issues/1978/layout/page_07_parody_console.html` | `html` | Issue-specific source or generated page content. |
| `page_08_data_billboard.html` | `retroverse-magazine/issues/1978/layout/page_08_data_billboard.html` | `html` | Issue-specific source or generated page content. |
| `page_09_data_albums.html` | `retroverse-magazine/issues/1978/layout/page_09_data_albums.html` | `html` | Issue-specific source or generated page content. |
| `page_10_department_culture.html` | `retroverse-magazine/issues/1978/layout/page_10_department_culture.html` | `html` | Issue-specific source or generated page content. |
| `page_11_parody_planner.html` | `retroverse-magazine/issues/1978/layout/page_11_parody_planner.html` | `html` | Issue-specific source or generated page content. |
| `page_12_data_timeline.html` | `retroverse-magazine/issues/1978/layout/page_12_data_timeline.html` | `html` | Issue-specific source or generated page content. |
| `page_13_feature_interview.html` | `retroverse-magazine/issues/1978/layout/page_13_feature_interview.html` | `html` | Issue-specific source or generated page content. |
| `page_14_parody_fake_ad.html` | `retroverse-magazine/issues/1978/layout/page_14_parody_fake_ad.html` | `html` | Issue-specific source or generated page content. |
| `page_15_comic_night.html` | `retroverse-magazine/issues/1978/layout/page_15_comic_night.html` | `html` | Issue-specific source or generated page content. |
| `page_16_feature_cinema.html` | `retroverse-magazine/issues/1978/layout/page_16_feature_cinema.html` | `html` | Issue-specific source or generated page content. |
| `page_17_collage_movies_toys.html` | `retroverse-magazine/issues/1978/layout/page_17_collage_movies_toys.html` | `html` | Issue-specific source or generated page content. |
| `page_18_parody_humor.html` | `retroverse-magazine/issues/1978/layout/page_18_parody_humor.html` | `html` | Issue-specific source or generated page content. |
| `page_19_data_music.html` | `retroverse-magazine/issues/1978/layout/page_19_data_music.html` | `html` | Issue-specific source or generated page content. |
| `page_20_feature_tv.html` | `retroverse-magazine/issues/1978/layout/page_20_feature_tv.html` | `html` | Issue-specific source or generated page content. |
| `page_21_department_sue.html` | `retroverse-magazine/issues/1978/layout/page_21_department_sue.html` | `html` | Issue-specific source or generated page content. |
| `page_22_parody_trend.html` | `retroverse-magazine/issues/1978/layout/page_22_parody_trend.html` | `html` | Issue-specific source or generated page content. |
| `page_23_parody_puzzle.html` | `retroverse-magazine/issues/1978/layout/page_23_parody_puzzle.html` | `html` | Issue-specific source or generated page content. |
| `page_24_back.html` | `retroverse-magazine/issues/1978/layout/page_24_back.html` | `html` | Issue-specific source or generated page content. |
| `page_01_cover.html` | `retroverse-magazine/issues/1978/page_01_cover.html` | `html` | Issue-specific source or generated page content. |
| `page_02_contents.html` | `retroverse-magazine/issues/1978/page_02_contents.html` | `html` | Issue-specific source or generated page content. |
| `page_03_editor.html` | `retroverse-magazine/issues/1978/page_03_editor.html` | `html` | Issue-specific source or generated page content. |
| `page_04_feature_disco.html` | `retroverse-magazine/issues/1978/page_04_feature_disco.html` | `html` | Issue-specific source or generated page content. |
| `page_05_feature_backlash.html` | `retroverse-magazine/issues/1978/page_05_feature_backlash.html` | `html` | Issue-specific source or generated page content. |
| `page_06_collage_city.html` | `retroverse-magazine/issues/1978/page_06_collage_city.html` | `html` | Issue-specific source or generated page content. |
| `page_07_parody_media.html` | `retroverse-magazine/issues/1978/page_07_parody_media.html` | `html` | Issue-specific source or generated page content. |
| `page_08_data_billboard.html` | `retroverse-magazine/issues/1978/page_08_data_billboard.html` | `html` | Issue-specific source or generated page content. |
| `page_09_data_albums.html` | `retroverse-magazine/issues/1978/page_09_data_albums.html` | `html` | Issue-specific source or generated page content. |
| `page_10_department_culture.html` | `retroverse-magazine/issues/1978/page_10_department_culture.html` | `html` | Issue-specific source or generated page content. |
| `page_11_parody_weekend.html` | `retroverse-magazine/issues/1978/page_11_parody_weekend.html` | `html` | Issue-specific source or generated page content. |
| `page_12_data_timeline.html` | `retroverse-magazine/issues/1978/page_12_data_timeline.html` | `html` | Issue-specific source or generated page content. |
| `page_13_feature_interview.html` | `retroverse-magazine/issues/1978/page_13_feature_interview.html` | `html` | Issue-specific source or generated page content. |
| `page_14_parody_fake_ad.html` | `retroverse-magazine/issues/1978/page_14_parody_fake_ad.html` | `html` | Issue-specific source or generated page content. |
| `page_15_comic_nightshift.html` | `retroverse-magazine/issues/1978/page_15_comic_nightshift.html` | `html` | Issue-specific source or generated page content. |
| `page_16_feature_cinema.html` | `retroverse-magazine/issues/1978/page_16_feature_cinema.html` | `html` | Issue-specific source or generated page content. |
| `page_17_collage_movies_toys.html` | `retroverse-magazine/issues/1978/page_17_collage_movies_toys.html` | `html` | Issue-specific source or generated page content. |
| `page_18_parody_humor.html` | `retroverse-magazine/issues/1978/page_18_parody_humor.html` | `html` | Issue-specific source or generated page content. |
| `page_19_data_music_pulse.html` | `retroverse-magazine/issues/1978/page_19_data_music_pulse.html` | `html` | Issue-specific source or generated page content. |
| `page_20_feature_television.html` | `retroverse-magazine/issues/1978/page_20_feature_television.html` | `html` | Issue-specific source or generated page content. |
| `page_21_department_letters.html` | `retroverse-magazine/issues/1978/page_21_department_letters.html` | `html` | Issue-specific source or generated page content. |
| `page_22_parody_trends.html` | `retroverse-magazine/issues/1978/page_22_parody_trends.html` | `html` | Issue-specific source or generated page content. |
| `page_23_parody_puzzle.html` | `retroverse-magazine/issues/1978/page_23_parody_puzzle.html` | `html` | Issue-specific source or generated page content. |
| `page_24_back.html` | `retroverse-magazine/issues/1978/page_24_back.html` | `html` | Issue-specific source or generated page content. |
| `index.html` | `retroverse-magazine/issues/1978/preview/index.html` | `html` | Issue-specific source or generated page content. |
| `page_01_cover.html` | `retroverse-magazine/issues/1978/preview/page_01_cover.html` | `html` | Issue-specific source or generated page content. |
| `page_02_contents.html` | `retroverse-magazine/issues/1978/preview/page_02_contents.html` | `html` | Issue-specific source or generated page content. |
| `page_03_editor.html` | `retroverse-magazine/issues/1978/preview/page_03_editor.html` | `html` | Issue-specific source or generated page content. |
| `page_04_feature_disco.html` | `retroverse-magazine/issues/1978/preview/page_04_feature_disco.html` | `html` | Issue-specific source or generated page content. |
| `page_05_feature_backlash.html` | `retroverse-magazine/issues/1978/preview/page_05_feature_backlash.html` | `html` | Issue-specific source or generated page content. |
| `page_06_collage_city.html` | `retroverse-magazine/issues/1978/preview/page_06_collage_city.html` | `html` | Issue-specific source or generated page content. |
| `page_07_parody_console.html` | `retroverse-magazine/issues/1978/preview/page_07_parody_console.html` | `html` | Issue-specific source or generated page content. |
| `page_08_data_billboard.html` | `retroverse-magazine/issues/1978/preview/page_08_data_billboard.html` | `html` | Issue-specific source or generated page content. |
| `page_09_data_albums.html` | `retroverse-magazine/issues/1978/preview/page_09_data_albums.html` | `html` | Issue-specific source or generated page content. |
| `page_10_department_culture.html` | `retroverse-magazine/issues/1978/preview/page_10_department_culture.html` | `html` | Issue-specific source or generated page content. |
| `page_11_parody_planner.html` | `retroverse-magazine/issues/1978/preview/page_11_parody_planner.html` | `html` | Issue-specific source or generated page content. |
| `page_12_data_timeline.html` | `retroverse-magazine/issues/1978/preview/page_12_data_timeline.html` | `html` | Issue-specific source or generated page content. |
| `page_13_feature_interview.html` | `retroverse-magazine/issues/1978/preview/page_13_feature_interview.html` | `html` | Issue-specific source or generated page content. |
| `page_14_parody_fake_ad.html` | `retroverse-magazine/issues/1978/preview/page_14_parody_fake_ad.html` | `html` | Issue-specific source or generated page content. |
| `page_15_comic_night.html` | `retroverse-magazine/issues/1978/preview/page_15_comic_night.html` | `html` | Issue-specific source or generated page content. |
| `page_16_feature_cinema.html` | `retroverse-magazine/issues/1978/preview/page_16_feature_cinema.html` | `html` | Issue-specific source or generated page content. |
| `page_17_collage_movies_toys.html` | `retroverse-magazine/issues/1978/preview/page_17_collage_movies_toys.html` | `html` | Issue-specific source or generated page content. |
| `page_18_parody_humor.html` | `retroverse-magazine/issues/1978/preview/page_18_parody_humor.html` | `html` | Issue-specific source or generated page content. |
| `page_19_data_music.html` | `retroverse-magazine/issues/1978/preview/page_19_data_music.html` | `html` | Issue-specific source or generated page content. |
| `page_20_feature_tv.html` | `retroverse-magazine/issues/1978/preview/page_20_feature_tv.html` | `html` | Issue-specific source or generated page content. |
| `page_21_department_sue.html` | `retroverse-magazine/issues/1978/preview/page_21_department_sue.html` | `html` | Issue-specific source or generated page content. |
| `page_22_parody_trend.html` | `retroverse-magazine/issues/1978/preview/page_22_parody_trend.html` | `html` | Issue-specific source or generated page content. |
| `page_23_parody_puzzle.html` | `retroverse-magazine/issues/1978/preview/page_23_parody_puzzle.html` | `html` | Issue-specific source or generated page content. |
| `page_24_back.html` | `retroverse-magazine/issues/1978/preview/page_24_back.html` | `html` | Issue-specific source or generated page content. |
| `retroverse_1978_pilot.md` | `retroverse-magazine/issues/1978/retroverse_1978_pilot.md` | `markdown` | Issue-specific source or generated page content. |
| `1978_context.json` | `retroverse-magazine/issues/context/1978_context.json` | `json` | Generated issue context artifact. |
| `example_context_1978.json` | `retroverse-magazine/issues/context/example_context_1978.json` | `json` | Generated issue context artifact. |

## Artwork Library

| File | Relative Path | Type | Purpose |
|---|---|---|---|
| `art_index.json` | `retroverse-magazine/art-library/art_index.json` | `json` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_10.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_10.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_11.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_11.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_12.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_12.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_13.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_13.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_14.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_14.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_2.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_2.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_3.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_3.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_4.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_4.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_5.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_5.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_6.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_6.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_7.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_7.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_8.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_8.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_cover_neon_city_nightlife_retro_1978_9.png` | `retroverse-magazine/art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978_9.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_10.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_10.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_11.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_11.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_12.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_12.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_13.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_13.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_14.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_14.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_15.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_15.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_16.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_16.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_17.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_17.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_18.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_18.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_19.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_19.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_2.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_2.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_20.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_20.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_21.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_21.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_22.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_22.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_23.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_23.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_24.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_24.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_25.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_25.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_26.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_26.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_27.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_27.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_28.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_28.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_3.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_3.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_4.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_4.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_5.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_5.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_6.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_6.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_7.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_7.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_8.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_8.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `fake_ad_gadget_advertisement_art_chrome_retro_1978_9.png` | `retroverse-magazine/art-library/fake_ads/fake_ad_gadget_advertisement_art_chrome_retro_1978_9.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_10.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_10.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_11.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_11.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_12.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_12.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_13.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_13.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_14.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_14.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_15.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_15.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_16.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_16.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_17.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_17.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_18.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_18.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_19.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_19.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_2.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_2.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_20.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_20.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_21.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_21.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_22.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_22.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_23.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_23.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_24.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_24.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_25.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_25.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_26.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_26.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_27.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_27.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_28.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_28.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_3.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_3.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_4.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_4.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_5.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_5.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_6.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_6.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_7.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_7.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_8.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_8.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `texture_cultural_bustling_night_street_retro_1978_9.png` | `retroverse-magazine/art-library/textures/texture_cultural_bustling_night_street_retro_1978_9.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `background_1970s_mad_printing_cover_1970s_1978.png` | `retroverse-magazine/art_library/backgrounds/background_1970s_mad_printing_cover_1970s_1978.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `scene_1970s_mad_printing_movie_1970s_1978.png` | `retroverse-magazine/art_library/scenes/scene_1970s_mad_printing_movie_1970s_1978.png` | `png` | Shared RetroVerse magazine artwork asset. |
| `collage_01.png` | `retroverse-magazine/issues/1978/art/collage/collage_01.png` | `png` | Issue-level artwork asset. |
| `collage_02.png` | `retroverse-magazine/issues/1978/art/collage/collage_02.png` | `png` | Issue-level artwork asset. |
| `collage_03.png` | `retroverse-magazine/issues/1978/art/collage/collage_03.png` | `png` | Issue-level artwork asset. |
| `collage_04.png` | `retroverse-magazine/issues/1978/art/collage/collage_04.png` | `png` | Issue-level artwork asset. |
| `collage_05.png` | `retroverse-magazine/issues/1978/art/collage/collage_05.png` | `png` | Issue-level artwork asset. |
| `collage_06.png` | `retroverse-magazine/issues/1978/art/collage/collage_06.png` | `png` | Issue-level artwork asset. |
| `collage_07.png` | `retroverse-magazine/issues/1978/art/collage/collage_07.png` | `png` | Issue-level artwork asset. |
| `collage_08.png` | `retroverse-magazine/issues/1978/art/collage/collage_08.png` | `png` | Issue-level artwork asset. |
| `collage_09.png` | `retroverse-magazine/issues/1978/art/collage/collage_09.png` | `png` | Issue-level artwork asset. |
| `comic_panel_01.png` | `retroverse-magazine/issues/1978/art/comic/comic_panel_01.png` | `png` | Issue-level artwork asset. |
| `comic_panel_02.png` | `retroverse-magazine/issues/1978/art/comic/comic_panel_02.png` | `png` | Issue-level artwork asset. |
| `comic_panel_03.png` | `retroverse-magazine/issues/1978/art/comic/comic_panel_03.png` | `png` | Issue-level artwork asset. |
| `comic_panel_04.png` | `retroverse-magazine/issues/1978/art/comic/comic_panel_04.png` | `png` | Issue-level artwork asset. |
| `comic_panel_05.png` | `retroverse-magazine/issues/1978/art/comic/comic_panel_05.png` | `png` | Issue-level artwork asset. |
| `comic_panel_06.png` | `retroverse-magazine/issues/1978/art/comic/comic_panel_06.png` | `png` | Issue-level artwork asset. |
| `back_page_1978.png` | `retroverse-magazine/issues/1978/art/cover/back_page_1978.png` | `png` | Issue-level artwork asset. |
| `cover_1978.png` | `retroverse-magazine/issues/1978/art/cover/cover_1978.png` | `png` | Issue-level artwork asset. |
| `department_portrait.png` | `retroverse-magazine/issues/1978/art/departments/department_portrait.png` | `png` | Issue-level artwork asset. |
| `fake_ad_kit.png` | `retroverse-magazine/issues/1978/art/fake_ads/fake_ad_kit.png` | `png` | Issue-level artwork asset. |
| `cinema_marquee.png` | `retroverse-magazine/issues/1978/art/feature/cinema_marquee.png` | `png` | Issue-level artwork asset. |
| `department_portrait.png` | `retroverse-magazine/issues/1978/art/feature/department_portrait.png` | `png` | Issue-level artwork asset. |
| `disco_floor.png` | `retroverse-magazine/issues/1978/art/feature/disco_floor.png` | `png` | Issue-level artwork asset. |
| `feature_placeholder.png` | `retroverse-magazine/issues/1978/art/feature/feature_placeholder.png` | `png` | Issue-level artwork asset. |
| `tv_livingroom.png` | `retroverse-magazine/issues/1978/art/feature/tv_livingroom.png` | `png` | Issue-level artwork asset. |
| `image_prompts.json` | `retroverse-magazine/issues/1978/art/image_prompts.json` | `json` | Issue-level artwork asset. |
| `fake_ad_kit.png` | `retroverse-magazine/issues/1978/art/parody/fake_ad_kit.png` | `png` | Issue-level artwork asset. |
| `parody_placeholder.png` | `retroverse-magazine/issues/1978/art/parody/parody_placeholder.png` | `png` | Issue-level artwork asset. |
| `trivia_grid.png` | `retroverse-magazine/issues/1978/art/parody/trivia_grid.png` | `png` | Issue-level artwork asset. |
| `weekend_console.png` | `retroverse-magazine/issues/1978/art/parody/weekend_console.png` | `png` | Issue-level artwork asset. |
| `collage_01.png` | `retroverse-magazine/issues/art/collage/collage_01.png` | `png` | Issue-level artwork asset. |
| `collage_02.png` | `retroverse-magazine/issues/art/collage/collage_02.png` | `png` | Issue-level artwork asset. |
| `collage_03.png` | `retroverse-magazine/issues/art/collage/collage_03.png` | `png` | Issue-level artwork asset. |
| `collage_04.png` | `retroverse-magazine/issues/art/collage/collage_04.png` | `png` | Issue-level artwork asset. |
| `collage_05.png` | `retroverse-magazine/issues/art/collage/collage_05.png` | `png` | Issue-level artwork asset. |
| `collage_06.png` | `retroverse-magazine/issues/art/collage/collage_06.png` | `png` | Issue-level artwork asset. |
| `collage_07.png` | `retroverse-magazine/issues/art/collage/collage_07.png` | `png` | Issue-level artwork asset. |
| `collage_08.png` | `retroverse-magazine/issues/art/collage/collage_08.png` | `png` | Issue-level artwork asset. |
| `collage_09.png` | `retroverse-magazine/issues/art/collage/collage_09.png` | `png` | Issue-level artwork asset. |
| `comic_panel_01.png` | `retroverse-magazine/issues/art/comic/comic_panel_01.png` | `png` | Issue-level artwork asset. |
| `comic_panel_02.png` | `retroverse-magazine/issues/art/comic/comic_panel_02.png` | `png` | Issue-level artwork asset. |
| `comic_panel_03.png` | `retroverse-magazine/issues/art/comic/comic_panel_03.png` | `png` | Issue-level artwork asset. |
| `comic_panel_04.png` | `retroverse-magazine/issues/art/comic/comic_panel_04.png` | `png` | Issue-level artwork asset. |
| `comic_panel_05.png` | `retroverse-magazine/issues/art/comic/comic_panel_05.png` | `png` | Issue-level artwork asset. |
| `comic_panel_06.png` | `retroverse-magazine/issues/art/comic/comic_panel_06.png` | `png` | Issue-level artwork asset. |
| `back_page_1978.png` | `retroverse-magazine/issues/art/cover/back_page_1978.png` | `png` | Issue-level artwork asset. |
| `cover_1978.png` | `retroverse-magazine/issues/art/cover/cover_1978.png` | `png` | Issue-level artwork asset. |
| `department_portrait.png` | `retroverse-magazine/issues/art/departments/department_portrait.png` | `png` | Issue-level artwork asset. |
| `cinema_marquee.png` | `retroverse-magazine/issues/art/feature/cinema_marquee.png` | `png` | Issue-level artwork asset. |
| `department_portrait.png` | `retroverse-magazine/issues/art/feature/department_portrait.png` | `png` | Issue-level artwork asset. |
| `disco_floor.png` | `retroverse-magazine/issues/art/feature/disco_floor.png` | `png` | Issue-level artwork asset. |
| `feature_placeholder.png` | `retroverse-magazine/issues/art/feature/feature_placeholder.png` | `png` | Issue-level artwork asset. |
| `tv_livingroom.png` | `retroverse-magazine/issues/art/feature/tv_livingroom.png` | `png` | Issue-level artwork asset. |
| `image_prompts.json` | `retroverse-magazine/issues/art/image_prompts.json` | `json` | Issue-level artwork asset. |
| `fake_ad_kit.png` | `retroverse-magazine/issues/art/parody/fake_ad_kit.png` | `png` | Issue-level artwork asset. |
| `parody_placeholder.png` | `retroverse-magazine/issues/art/parody/parody_placeholder.png` | `png` | Issue-level artwork asset. |
| `trivia_grid.png` | `retroverse-magazine/issues/art/parody/trivia_grid.png` | `png` | Issue-level artwork asset. |
| `weekend_console.png` | `retroverse-magazine/issues/art/parody/weekend_console.png` | `png` | Issue-level artwork asset. |

## Prompt Templates

| File | Relative Path | Type | Purpose |
|---|---|---|---|
| `image_prompts.json` | `retroverse-magazine/issues/1978/art/image_prompts.json` | `json` | Issue-level artwork asset. |
| `image_prompts.json` | `retroverse-magazine/issues/art/image_prompts.json` | `json` | Issue-level artwork asset. |
| `generate_issue_prompt.md` | `retroverse-magazine/prompts/generate_issue_prompt.md` | `markdown` | Prompt template used for editorial or art generation. |
| `generate_art_prompts.py` | `retroverse-magazine/scripts/generate_art_prompts.py` | `python` | Python automation script. |

## Observations

- Scan root: `/Users/bobhopp/Sites/retroverse`
- File counts: data=765, db=4, scripts=61, issues=82, art=130, prompts=4
- Excluded directories during scan: .cache, .git, .next, .venv, __pycache__, dist, dist-pipeline, node_modules
- Source map notes:
  - PyYAML unavailable; using built-in simple YAML parser.

