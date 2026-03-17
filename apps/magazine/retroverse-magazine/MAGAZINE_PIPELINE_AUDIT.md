# Magazine Pipeline Audit

Project root: `/Users/bobhopp/Sites/retroverse/retroverse-magazine`

Specification audited: `PROJECT_STATE.md`

Audit scope: full repository structure, pipeline scripts, stage coverage, directory compliance, artwork heuristics, and unused-file candidates.

Audit mode: read-only analysis. No project files were modified by the audit itself.

## 1. Repository Overview

Overall verdict: **NOT CURRENTLY CONFORMANT** with `PROJECT_STATE.md`.

Summary counts:

- Directories scanned: 78
- Files scanned: 538
- Scripts discovered: 46 (`45` Python, `1` Node `.mjs`)
- Image files discovered: 145 (`144` PNG, `1` JPG)
- Generated outputs discovered: 94
- Structured config/metadata files discovered: 113

Generated output concentration:

- `issues/1978/layout`: 31 files
- `issues/1978/preview`: 25 files
- `issues/final/1978`: 24 files
- `workflow/page_rebuild/output`: 8 files
- `issues/layout`: 3 files
- `output/`: 2 files

Top-level directories present:

- `archive/`
- `art-library/`
- `assets/`
- `charter/`
- `data/`
- `docs/`
- `issues/`
- `layout-library/`
- `logs/`
- `output/`
- `prompts/`
- `scripts/`
- `templates/`
- `tools/`
- `workflow/`

Highest-signal findings:

- The repository contains **multiple competing pipelines** rather than one canonical 8-stage issue pipeline.
- **All 68** `issues/context/*_context.json` files currently fail the spec's cultural-data requirement.
- Several required canonical directories are missing, including `issues/{year}/articles`, `issues/{year}/charts`, `issues/{year}/pdf`, `artifacts/logs`, `artifacts/output`, `archive/old_runs`, and `archive/unused_assets`.
- The illustration pipeline conflicts with the spec: current art-generation scripts still use **MAD-style prompts**, create ad/parody assets, and generate mostly **sub-2000px** images.
- Full-issue press-check QA is not implemented as a reusable blocking stage.
- A newer controlled page workflow exists under `workflow/page_rebuild/`, but it only covers **one page**, not the full issue.

Specification ambiguity note:

- PROJECT_STATE.md is internally inconsistent about staff names. The top-level ## Editorial Staff block lists BJ Lovestreet, A.J. Hunter, Nicole Thomas, Professor Wheeler, Emily Bennet and Charles Cursor, Nick Nitro, and Daisy Delgado, while later voice-profile and page-design sections still refer to Bob Jones, Martin Hale, Linda Park, and Eve Binet. This audit treated the top-level ## Editorial Staff block as canonical when checking writer/name compliance.

## 2. Directory Tree

Category counts used in the tree below:

- `[script]` = executable pipeline/support script
- `[image]` = image asset
- `[output]` = generated HTML/PDF/JSON/Markdown/TXT output in an output-like directory
- `[config]` = JSON/YAML/env/gitignore/schema/config-style file

```text
.
├── .env [config]
├── .gitignore [config]
├── archive/
│   └── prototype_pipelines/
│       ├── art_library/
│       │   ├── backgrounds/
│       │   │   └── background_1970s_mad_printing_cover_1970s_1978.png [image]
│       │   ├── environments/
│       │   └── scenes/
│       │       └── scene_1970s_mad_printing_movie_1970s_1978.png [image]
│       ├── generate_magazine.py [script]
│       ├── images/
│       │   ├── 1978_magazine.jpg [image]
│       │   ├── 1978_raw_02.png [image]
│       │   ├── 1978_raw_03.png [image]
│       │   ├── 1978_raw_04.png [image]
│       │   ├── 1978_raw_05.png [image]
│       │   ├── 1978_raw_06.png [image]
│       │   ├── 1978_raw_07.png [image]
│       │   ├── 1978_raw_08.png [image]
│       │   ├── 1978_raw_09.png [image]
│       │   ├── 1978_raw_10.png [image]
│       │   ├── 1978_raw_A.png [image]
│       │   ├── 1978_raw_J.png [image]
│       │   ├── 1978_raw_K.png [image]
│       │   ├── 1978_raw_Q.png [image]
│       │   ├── 1978_raw_R1.png [image]
│       │   ├── 1978_raw_R2.png [image]
│       │   ├── 1978_raw_R3.png [image]
│       │   └── 1978_raw_R4.png [image]
│       └── issues_1978_root_html/
├── art-library/
│   ├── art_index.json [config]
│   ├── backgrounds/
│   │   ├── background_cover_neon_city_nightlife_retro_1978.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_10.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_11.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_12.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_13.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_14.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_2.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_3.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_4.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_5.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_6.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_7.png [image]
│   │   ├── background_cover_neon_city_nightlife_retro_1978_8.png [image]
│   │   └── background_cover_neon_city_nightlife_retro_1978_9.png [image]
│   ├── characters/
│   ├── environments/
│   ├── fake_ads/
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_10.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_11.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_12.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_13.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_14.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_15.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_16.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_17.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_18.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_19.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_2.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_20.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_21.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_22.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_23.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_24.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_25.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_26.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_27.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_28.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_3.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_4.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_5.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_6.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_7.png [image]
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_8.png [image]
│   │   └── fake_ad_gadget_advertisement_art_chrome_retro_1978_9.png [image]
│   ├── margin_gags/
│   ├── misc/
│   ├── props/
│   ├── scenes/
│   └── textures/
│       ├── texture_cultural_bustling_night_street_retro_1978.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_10.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_11.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_12.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_13.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_14.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_15.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_16.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_17.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_18.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_19.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_2.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_20.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_21.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_22.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_23.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_24.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_25.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_26.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_27.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_28.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_3.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_4.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_5.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_6.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_7.png [image]
│       ├── texture_cultural_bustling_night_street_retro_1978_8.png [image]
│       └── texture_cultural_bustling_night_street_retro_1978_9.png [image]
├── assets/
│   ├── covers/
│   ├── css/
│   ├── illustrations/
│   └── layouts/
├── charter/
├── data/
│   └── DATA_SOURCES.yaml [config]
├── docs/
├── issues/
│   ├── 1978/
│   │   ├── art/
│   │   │   ├── collage/
│   │   │   │   ├── collage_01.png [image]
│   │   │   │   ├── collage_02.png [image]
│   │   │   │   ├── collage_03.png [image]
│   │   │   │   ├── collage_04.png [image]
│   │   │   │   ├── collage_05.png [image]
│   │   │   │   ├── collage_06.png [image]
│   │   │   │   ├── collage_07.png [image]
│   │   │   │   ├── collage_08.png [image]
│   │   │   │   └── collage_09.png [image]
│   │   │   ├── comic/
│   │   │   │   ├── comic_panel_01.png [image]
│   │   │   │   ├── comic_panel_02.png [image]
│   │   │   │   ├── comic_panel_03.png [image]
│   │   │   │   ├── comic_panel_04.png [image]
│   │   │   │   ├── comic_panel_05.png [image]
│   │   │   │   └── comic_panel_06.png [image]
│   │   │   ├── cover/
│   │   │   │   ├── back_page_1978.png [image]
│   │   │   │   └── cover_1978.png [image]
│   │   │   ├── departments/
│   │   │   │   └── department_portrait.png [image]
│   │   │   ├── fake_ads/
│   │   │   │   └── fake_ad_kit.png [image]
│   │   │   ├── feature/
│   │   │   │   ├── cinema_marquee.png [image]
│   │   │   │   ├── department_portrait.png [image]
│   │   │   │   ├── disco_floor.png [image]
│   │   │   │   ├── feature_placeholder.png [image]
│   │   │   │   └── tv_livingroom.png [image]
│   │   │   ├── image_prompts.json [config]
│   │   │   ├── marginals/
│   │   │   └── parody/
│   │   │       ├── fake_ad_kit.png [image]
│   │   │       ├── parody_placeholder.png [image]
│   │   │       ├── trivia_grid.png [image]
│   │   │       └── weekend_console.png [image]
│   │   ├── data/
│   │   │   ├── charts.json [config]
│   │   │   ├── editorial.json [config]
│   │   │   ├── issue.json [config]
│   │   │   ├── movies.json [config]
│   │   │   └── tv.json [config]
│   │   ├── layout/
│   │   │   ├── index.html [output]
│   │   │   ├── page_01_cover.html [output]
│   │   │   ├── page_02_masthead.html [output]
│   │   │   ├── page_03_editor_letter.html [output]
│   │   │   ├── page_04_year_snapshot.html [output]
│   │   │   ├── page_05_charts_overview.html [output]
│   │   │   ├── page_06_top_song_1.html [output]
│   │   │   ├── page_07_top_song_2.html [output]
│   │   │   ├── page_08_top_song_3.html [output]
│   │   │   ├── page_09_top_song_4.html [output]
│   │   │   ├── page_10_top_song_5.html [output]
│   │   │   ├── page_11_top_song_6.html [output]
│   │   │   ├── page_12_top_song_7.html [output]
│   │   │   ├── page_13_top_song_8.html [output]
│   │   │   ├── page_14_top_song_9.html [output]
│   │   │   ├── page_15_top_song_10.html [output]
│   │   │   ├── page_16_movies.html [output]
│   │   │   ├── page_17_television.html [output]
│   │   │   ├── page_18_culture.html [output]
│   │   │   ├── page_19_arcade.html [output]
│   │   │   ├── page_20_retro_ad.html [output]
│   │   │   ├── page_21_comic.html [output]
│   │   │   ├── page_22_puzzle.html [output]
│   │   │   ├── page_23_letters.html [output]
│   │   │   ├── page_24_forgotten_hit.html [output]
│   │   │   ├── page_25_one_hit_wonder.html [output]
│   │   │   ├── page_26_album_spotlight.html [output]
│   │   │   ├── page_27_year_timeline.html [output]
│   │   │   ├── page_28_culture_collage.html [output]
│   │   │   ├── page_29_retro_ads_page.html [output]
│   │   │   └── page_30_chart_top23.html [output]
│   │   ├── preview/
│   │   │   ├── index.html [output]
│   │   │   ├── page_01_cover.html [output]
│   │   │   ├── page_02_contents.html [output]
│   │   │   ├── page_03_editor.html [output]
│   │   │   ├── page_04_feature_disco.html [output]
│   │   │   ├── page_05_feature_backlash.html [output]
│   │   │   ├── page_06_collage_city.html [output]
│   │   │   ├── page_07_parody_console.html [output]
│   │   │   ├── page_08_data_billboard.html [output]
│   │   │   ├── page_09_data_albums.html [output]
│   │   │   ├── page_10_department_culture.html [output]
│   │   │   ├── page_11_parody_planner.html [output]
│   │   │   ├── page_12_data_timeline.html [output]
│   │   │   ├── page_13_feature_interview.html [output]
│   │   │   ├── page_14_parody_fake_ad.html [output]
│   │   │   ├── page_15_comic_night.html [output]
│   │   │   ├── page_16_feature_cinema.html [output]
│   │   │   ├── page_17_collage_movies_toys.html [output]
│   │   │   ├── page_18_parody_humor.html [output]
│   │   │   ├── page_19_data_music.html [output]
│   │   │   ├── page_20_feature_tv.html [output]
│   │   │   ├── page_21_department_sue.html [output]
│   │   │   ├── page_22_parody_trend.html [output]
│   │   │   ├── page_23_parody_puzzle.html [output]
│   │   │   └── page_24_back.html [output]
│   │   └── songs/
│   ├── 1979/
│   ├── 1980/
│   ├── art/
│   │   ├── collage/
│   │   │   ├── collage_01.png [image]
│   │   │   ├── collage_02.png [image]
│   │   │   ├── collage_03.png [image]
│   │   │   ├── collage_04.png [image]
│   │   │   ├── collage_05.png [image]
│   │   │   ├── collage_06.png [image]
│   │   │   ├── collage_07.png [image]
│   │   │   ├── collage_08.png [image]
│   │   │   └── collage_09.png [image]
│   │   ├── comic/
│   │   │   ├── comic_panel_01.png [image]
│   │   │   ├── comic_panel_02.png [image]
│   │   │   ├── comic_panel_03.png [image]
│   │   │   ├── comic_panel_04.png [image]
│   │   │   ├── comic_panel_05.png [image]
│   │   │   └── comic_panel_06.png [image]
│   │   ├── cover/
│   │   │   ├── back_page_1978.png [image]
│   │   │   └── cover_1978.png [image]
│   │   ├── departments/
│   │   │   └── department_portrait.png [image]
│   │   ├── fake_ads/
│   │   ├── feature/
│   │   │   ├── cinema_marquee.png [image]
│   │   │   ├── department_portrait.png [image]
│   │   │   ├── disco_floor.png [image]
│   │   │   ├── feature_placeholder.png [image]
│   │   │   └── tv_livingroom.png [image]
│   │   ├── image_prompts.json [config]
│   │   ├── marginals/
│   │   └── parody/
│   │       ├── fake_ad_kit.png [image]
│   │       ├── parody_placeholder.png [image]
│   │       ├── trivia_grid.png [image]
│   │       └── weekend_console.png [image]
│   ├── articles/
│   │   └── 1978/
│   │       ├── story_001.json [config]
│   │       ├── story_002.json [config]
│   │       ├── story_003.json [config]
│   │       ├── story_004.json [config]
│   │       ├── story_005.json [config]
│   │       ├── story_006.json [config]
│   │       ├── story_007.json [config]
│   │       ├── story_008.json [config]
│   │       ├── story_009.json [config]
│   │       ├── story_010.json [config]
│   │       ├── story_011.json [config]
│   │       └── story_012.json [config]
│   ├── context/
│   │   ├── 1958_context.json [config]
│   │   ├── 1959_context.json [config]
│   │   ├── 1960_context.json [config]
│   │   ├── 1961_context.json [config]
│   │   ├── 1962_context.json [config]
│   │   ├── 1963_context.json [config]
│   │   ├── 1964_context.json [config]
│   │   ├── 1965_context.json [config]
│   │   ├── 1966_context.json [config]
│   │   ├── 1967_context.json [config]
│   │   ├── 1968_context.json [config]
│   │   ├── 1969_context.json [config]
│   │   ├── 1970_context.json [config]
│   │   ├── 1971_context.json [config]
│   │   ├── 1972_context.json [config]
│   │   ├── 1973_context.json [config]
│   │   ├── 1974_context.json [config]
│   │   ├── 1975_context.json [config]
│   │   ├── 1976_context.json [config]
│   │   ├── 1977_context.json [config]
│   │   ├── 1978_context.json [config]
│   │   ├── 1979_context.json [config]
│   │   ├── 1980_context.json [config]
│   │   ├── 1981_context.json [config]
│   │   ├── 1982_context.json [config]
│   │   ├── 1983_context.json [config]
│   │   ├── 1984_context.json [config]
│   │   ├── 1985_context.json [config]
│   │   ├── 1986_context.json [config]
│   │   ├── 1987_context.json [config]
│   │   ├── 1988_context.json [config]
│   │   ├── 1989_context.json [config]
│   │   ├── 1990_context.json [config]
│   │   ├── 1991_context.json [config]
│   │   ├── 1992_context.json [config]
│   │   ├── 1993_context.json [config]
│   │   ├── 1994_context.json [config]
│   │   ├── 1995_context.json [config]
│   │   ├── 1996_context.json [config]
│   │   ├── 1997_context.json [config]
│   │   ├── 1998_context.json [config]
│   │   ├── 1999_context.json [config]
│   │   ├── 2000_context.json [config]
│   │   ├── 2001_context.json [config]
│   │   ├── 2002_context.json [config]
│   │   ├── 2003_context.json [config]
│   │   ├── 2004_context.json [config]
│   │   ├── 2005_context.json [config]
│   │   ├── 2006_context.json [config]
│   │   ├── 2007_context.json [config]
│   │   ├── 2008_context.json [config]
│   │   ├── 2009_context.json [config]
│   │   ├── 2010_context.json [config]
│   │   ├── 2011_context.json [config]
│   │   ├── 2012_context.json [config]
│   │   ├── 2013_context.json [config]
│   │   ├── 2014_context.json [config]
│   │   ├── 2015_context.json [config]
│   │   ├── 2016_context.json [config]
│   │   ├── 2017_context.json [config]
│   │   ├── 2018_context.json [config]
│   │   ├── 2019_context.json [config]
│   │   ├── 2020_context.json [config]
│   │   ├── 2021_context.json [config]
│   │   ├── 2022_context.json [config]
│   │   ├── 2023_context.json [config]
│   │   ├── 2024_context.json [config]
│   │   ├── 2025_context.json [config]
│   │   └── example_context_1978.json [config]
│   ├── final/
│   │   ├── .DS_Store [output]
│   │   └── 1978/
│   │       ├── story_001.json [output ,config]
│   │       ├── story_001.md [output]
│   │       ├── story_002.json [output ,config]
│   │       ├── story_002.md [output]
│   │       ├── story_003.json [output ,config]
│   │       ├── story_003.md [output]
│   │       ├── story_004.json [output ,config]
│   │       ├── story_004.md [output]
│   │       ├── story_005.json [output ,config]
│   │       ├── story_005.md [output]
│   │       ├── story_006.json [output ,config]
│   │       ├── story_006.md [output]
│   │       ├── story_007.json [output ,config]
│   │       ├── story_007.md [output]
│   │       ├── story_008.json [output ,config]
│   │       ├── story_008.md [output]
│   │       ├── story_009.json [output ,config]
│   │       ├── story_009.md [output]
│   │       ├── story_010.json [output ,config]
│   │       ├── story_010.md [output]
│   │       ├── story_011.json [output ,config]
│   │       ├── story_011.md [output]
│   │       ├── story_012.json [output ,config]
│   │       └── story_012.md [output]
│   ├── layout/
│   │   ├── 1978_issue_map.json [output ,config]
│   │   ├── 1978_issue_map.md [output]
│   │   └── 1978_production_targets.json [output ,config]
│   └── plans/
│       └── 1978_narrative_plan.json [config]
├── layout-library/
│   ├── css/
│   ├── docs/
│   ├── schemas/
│   │   └── layout_templates.json [config]
│   └── templates/
├── logs/
│   └── year_generation_log.json [config]
├── output/
│   ├── RetroVerse_1978.html [output]
│   └── RetroVerse_1978.pdf [output]
├── prompts/
├── requirements.txt [config]
├── scripts/
│   ├── __pycache__/
│   ├── analyze_chart_dynamics.py [script]
│   ├── audit_billboard200_db.py [script]
│   ├── audit_hot100_db.py [script]
│   ├── audit_screen_culture_data.py [script]
│   ├── audit_screen_culture_warehouse.py [script]
│   ├── build_full_issue.py [script]
│   ├── build_issue.py [script]
│   ├── build_magazine.py [script]
│   ├── build_movies_dataset.py [script]
│   ├── build_screen_culture_warehouse.py [script]
│   ├── build_television_dataset.py [script]
│   ├── db_common.py [script]
│   ├── editorial_supervisor.py [script]
│   ├── enrich_omdb_metadata.py [script]
│   ├── enrich_tmdb_metadata.py [script]
│   ├── find_art_asset.py [script]
│   ├── generate_all_year_contexts.py [script]
│   ├── generate_art_prompts.py [script]
│   ├── generate_editorial.py [script]
│   ├── generate_final_articles.py [script]
│   ├── generate_illustrations.py [script]
│   ├── generate_marginals.py [script]
│   ├── generate_year_context.py [script]
│   ├── generate_year_narrative.py [script]
│   ├── generate_year_range.py [script]
│   ├── index_artwork.py [script]
│   ├── ingest_imdb_datasets.py [script]
│   ├── magazine_pipeline.py [script]
│   ├── print_daily_refresh_instructions.py [script]
│   ├── run_art_director.py [script]
│   ├── run_staff_writers.py [script]
│   ├── screen_culture_common.py [script]
│   └── update_data_inventory.py [script]
├── templates/
│   └── sections/
├── tools/
│   └── magazine_builder/
│       ├── __pycache__/
│       ├── build_issue.py [script]
│       └── render_browser_pdf.mjs [script]
└── workflow/
    └── page_rebuild/
        ├── __pycache__/
        ├── build_mock_page.py [script]
        ├── common.py [script]
        ├── generate_art_direction.py [script]
        ├── generate_page_art_prompt.py [script]
        ├── generate_page_brief.py [script]
        ├── output/
        │   ├── 1978_movies_art_direction.json [output ,config]
        │   ├── 1978_movies_art_direction_QA.md [output]
        │   ├── 1978_movies_art_prompt.txt [output]
        │   ├── 1978_movies_art_prompt_QA.md [output]
        │   ├── 1978_movies_layout_QA.md [output]
        │   ├── 1978_movies_mock_page.html [output]
        │   ├── 1978_movies_page_brief.json [output ,config]
        │   └── 1978_movies_page_brief_QA.md [output]
        ├── page_brief_schema.json [config]
        ├── qa_art_direction.py [script]
        ├── qa_art_prompt.py [script]
        ├── qa_layout.py [script]
        ├── qa_page_brief.py [script]
        └── rebuild_single_page.py [script]
```

## 3. Pipeline Script Inventory

### Core / Issue-Facing Scripts

| Script | Stage / Role | Purpose (best inference from code) |
| --- | --- | --- |
| `scripts/update_data_inventory.py` | Data inventory refresh | Rebuilds DATA_INVENTORY.md from the project filesystem. |
| `scripts/generate_year_context.py` | Year Context Generation | Legacy context generator that writes issues/context/{year}_context.json from Hot 100 data only. |
| `scripts/analyze_chart_dynamics.py` | Year Context Generation | Appends chart_dynamics and album_dynamics to the year context. |
| `scripts/generate_all_year_contexts.py` | Year Context Generation | Batch wrapper that runs generate_year_context.py across all years. |
| `scripts/generate_year_narrative.py` | Editorial Assignment | Builds issues/plans/{year}_narrative_plan.json and story assignments from context. |
| `scripts/run_staff_writers.py` | Editorial Assignment / Article Writing | Parses PROJECT_STATE.md, assigns staff writers, and writes issues/articles/{year}/story_*.json/md. |
| `scripts/generate_final_articles.py` | Article Writing | Converts structured drafts into final prose packages in issues/final/{year}. |
| `scripts/run_art_director.py` | Art Direction | Creates issues/layout/{year}_issue_map.* and issues/layout/{year}_production_targets.json. |
| `scripts/generate_editorial.py` | Legacy pre-art editorial generator | Builds issues/{year}/data/editorial.json for the older prompt/illustration pipeline. |
| `scripts/generate_art_prompts.py` | Illustration Generation | Builds issues/{year}/art/image_prompts.json from editorial.json. |
| `scripts/generate_illustrations.py` | Illustration Generation | Calls the OpenAI image API to create issue art and art-library assets. |
| `scripts/generate_marginals.py` | Illustration Generation | Generates marginal gag illustrations with the OpenAI image API. |
| `scripts/build_issue.py` | Layout Composition | Renders canonical HTML pages into issues/{year}/layout from finalized article sources. |
| `scripts/magazine_pipeline.py` | Layout Composition / shared render engine | Provides ISSUE_STRUCTURE, page-building logic, HTML rendering, and PDF document assembly helpers. |
| `scripts/build_magazine.py` | PDF Build | Runs the HTML builder and PDF builder together. |
| `tools/magazine_builder/build_issue.py` | PDF Build | Builds the PDF from issues/{year}/layout using Playwright or WeasyPrint. |
| `tools/magazine_builder/render_browser_pdf.mjs` | PDF Build | Screenshots each layout page and prints a PDF shell with Playwright. |
| `scripts/editorial_supervisor.py` | Partial orchestrator | Runs inventory/context/narrative/writer/art-director/final-prose checks, but stops before illustration, full press check, layout, and PDF stages. |
| `scripts/build_full_issue.py` | Legacy / bypass orchestrator | Runs generate_editorial -> generate_art_prompts -> generate_illustrations -> generate_marginals -> build_issue, skipping several canonical stages. |
| `workflow/page_rebuild/rebuild_single_page.py` | Single-page controlled workflow | Runs story-first page brief -> QA -> art direction -> QA -> prompt -> QA -> mock layout -> QA for one page only. |
| `archive/prototype_pipelines/generate_magazine.py` | Archived prototype | Generates a printable satirical RetroVerse HTML issue from the older prototype pipeline. |

### Upstream Data / Art Support Scripts

- `scripts/build_movies_dataset.py`: Builds the movie master dataset used by screen-year planning.
- `scripts/build_television_dataset.py`: Builds the television master dataset used by screen-year planning.
- `scripts/build_screen_culture_warehouse.py`: Builds unified warehouse outputs for movies/television.
- `scripts/enrich_omdb_metadata.py`: Adds OMDb-derived metadata to warehouse records.
- `scripts/enrich_tmdb_metadata.py`: Adds TMDb-derived metadata to warehouse records.
- `scripts/ingest_imdb_datasets.py`: Ingests IMDb bulk data for warehouse enrichment.
- `scripts/audit_screen_culture_data.py`: Audits movies/television/cultural-event coverage.
- `scripts/audit_screen_culture_warehouse.py`: Audits warehouse quality and coverage.
- `scripts/index_artwork.py`: Indexes reusable artwork into art-library metadata.
- `scripts/find_art_asset.py`: Searches the art library by tags/prompt text.
- `scripts/generate_year_range.py`: Runs editorial_supervisor.py across a year range and writes logs/ summaries.


## 4. Pipeline Stage Coverage

### Canonical Stage Comparison

| Canonical Stage | Status | Evidence | Audit Finding |
| --- | --- | --- | --- |
| 1. Year Context Generation | **Exists, but non-conformant** | `scripts/generate_year_context.py, scripts/analyze_chart_dynamics.py, scripts/generate_all_year_contexts.py, scripts/editorial_supervisor.py` | All 68 issues/context/*_context.json files currently fail the PROJECT_STATE requirement for cultural data; the legacy generator only writes chart-centric keys. |
| 2. Editorial Assignment | **Exists, but inconsistent** | `scripts/generate_year_narrative.py, scripts/run_staff_writers.py, scripts/editorial_supervisor.py` | Story assignment and writer-draft generation exist, but generated writers include Kevin Casey and Lola Vance, who are not listed in the current top-level ## Editorial Staff block. |
| 3. Article Writing | **Exists** | `scripts/run_staff_writers.py, scripts/generate_final_articles.py` | Drafts and final prose packages exist. A phrase scan did not find the canonical banned future-knowledge phrases in issues/articles or issues/final. |
| 4. Art Direction | **Exists, but only partly enforced** | `scripts/run_art_director.py; workflow/page_rebuild/generate_art_direction.py` | Full-issue art-direction outputs exist, but the main illustration pipeline does not enforce the newer scene-only/no-final-text page rules. The page_rebuild workflow does. |
| 5. Illustration Generation | **Exists, but non-conformant** | `scripts/generate_art_prompts.py, scripts/generate_illustrations.py, scripts/generate_marginals.py` | The live illustration scripts still use a MAD-style prompt suffix, generate fake-ad/parody assets, and default to 1024px/512px outputs, which conflicts with the current specification. |
| 6. Layout Composition | **Exists** | `scripts/build_issue.py, scripts/magazine_pipeline.py, workflow/page_rebuild/build_mock_page.py` | The canonical 1978 HTML issue builds to 30 pages in the expected order and ends on chart_top23, but some pages still contain placeholders and mixed-era staff identities. |
| 7. Press Check QA | **Missing for full issues** | `No dedicated full-issue QA script; only PRESS_CHECK_1978.md and workflow/page_rebuild/qa_*.py` | There is no reusable full-issue press-check automation that blocks publication before PDF build. |
| 8. PDF Build | **Exists, but output path is non-canonical** | `scripts/build_magazine.py, tools/magazine_builder/build_issue.py, tools/magazine_builder/render_browser_pdf.mjs` | PDF generation exists, but the output is written to output/RetroVerse_1978.pdf instead of issues/{year}/pdf/. |


### Scripts That Currently Bypass the Canonical Pipeline

- `scripts/build_full_issue.py`: Bypasses explicit year-context validation, editorial assignment, writer draft generation, art direction, press-check QA, and PDF build.
- `scripts/build_magazine.py`: Jumps straight from finalized article sources to HTML/PDF build and assumes upstream stages already happened.
- `scripts/build_issue.py`: Can be run directly to compose layout pages without any prior stage validation.
- `scripts/generate_illustrations.py`: Can generate issue art directly from prompt payloads without page-aware art direction or layout QA.
- `archive/prototype_pipelines/generate_magazine.py`: Archived prototype generator that ignores the canonical issue structure and current directory rules.
- `workflow/page_rebuild/rebuild_single_page.py`: Compliant for one page only, but not a full-issue implementation of the 8-stage pipeline.


### Stage-by-Stage Interpretation

- **Stage 1 fails in practice** even though context-generation scripts exist, because the generated context files do not contain the cultural layers required by `PROJECT_STATE.md`.
- **Stages 2–4 exist** in the `editorial_supervisor.py` branch, but they are not the only active path through the repo.
- **Stage 5 exists** but is currently driven by older prompt/style assumptions that conflict with the updated illustration rules.
- **Stage 6 exists** and the canonical 1978 issue layout is structurally close to spec, but it still includes placeholder content and mixed staff identities.
- **Stage 7 is the clearest missing full-issue capability.** The only reusable QA automation is the new one-page `workflow/page_rebuild/qa_*.py` suite.
- **Stage 8 exists** but outputs to a non-canonical directory.

## 5. Directory Structure Compliance

### Required Paths From `PROJECT_STATE.md`

| Required Path | Status | Notes |
| --- | --- | --- |
| `issues/context` | **Present** | Canonical year-context directory exists. |
| `issues/1978/articles` | **Missing** | Article drafts are currently written to issues/articles/1978 instead. |
| `issues/1978/art` | **Present** | Year-scoped art directory exists. |
| `issues/1978/layout` | **Present** | Year-scoped canonical HTML layout directory exists. |
| `issues/1978/charts` | **Missing** | No year-scoped chart directory exists; chart output is embedded in markdown/layout files. |
| `issues/1978/pdf` | **Missing** | PDF output is currently written to output/RetroVerse_1978.pdf. |
| `artifacts/logs` | **Missing** | The repo has logs/ instead of artifacts/logs/. |
| `artifacts/output` | **Missing** | No artifacts/ directory exists in the repository. |
| `archive/old_runs` | **Missing** | Archive only contains prototype_pipelines/. |
| `archive/unused_assets` | **Missing** | No canonical destination exists yet for move-only cleanup. |


### Non-Canonical or Mislocated Paths In Active Use

- `issues/articles/1978/`
- `issues/final/1978/`
- `issues/layout/`
- `issues/art/`
- `issues/1978/preview/`
- `output/`
- `logs/`
- `workflow/page_rebuild/output/`
- `archive/prototype_pipelines/`
- `.DS_Store and workflow/page_rebuild/.DS_Store`


### Layout Validation Snapshot Against the Spec

Passes:

- issues/1978/layout contains 30 page_*.html files, which is within the 28–32 page target.
- issues/1978/layout/index.html orders the issue correctly and ends on page_30_chart_top23.html.
- Interior pages use the header format "RetroVerse • 1978".
- The cover page prints the masthead as "RetroVerse" with the tagline "Press ▶ Play for the Past".

Concerns:

- Page 02 masthead content lists the older staff roster (Bob Jones, Martin Hale, Linda Park, Eve Binet) rather than the current top-level PROJECT_STATE Editorial Staff block.
- Several canonical layout pages still contain placeholder text (for example page_19_arcade.html and page_20_retro_ad.html).


Additional hard directory-compliance findings:

- `issues/articles/1978/` is the active article-draft location, but the spec requires `issues/{year}/articles/`.
- `issues/final/1978/` is the active final-article location, but the spec does not currently define this directory.
- `logs/` exists, but the spec requires `artifacts/logs/`.
- No `artifacts/` directory exists, even though the spec requires `artifacts/logs/` and `artifacts/output/`.
- `issues/1979/` and `issues/1980/` exist only as empty placeholder directories.

## 6. Artwork Violations

Method used:

- Dimensions were read with Pillow.
- OCR heuristics were run on suspicious images (cover/back-page/fake-ad/parody/raw composite names and portrait-like assets) using Tesseract.
- OCR on textured/noisy art can produce false positives, so the list below is split into **high-confidence** and **heuristic** risk.

### Resolution Rule Failures

- Images below the required `2000px` width: **144 / 145**
- Images at or above `2000px` width: **1 / 145**
- The only image meeting the width threshold is `archive/prototype_pipelines/images/1978_magazine.jpg` at `3900x5700`, and it is an archived prototype full-page composite rather than a clean scene illustration.

### High-Confidence Potential Violations

These assets appear to conflict with the Illustration Production Rules because they are page-like, ad-like, or OCR-detectable text/layout composites.

Prototype full-page/text-heavy composites:

- `archive/prototype_pipelines/images/1978_magazine.jpg`
- `archive/prototype_pipelines/images/1978_raw_02.png`
- `archive/prototype_pipelines/images/1978_raw_03.png`
- `archive/prototype_pipelines/images/1978_raw_04.png`
- `archive/prototype_pipelines/images/1978_raw_05.png`
- `archive/prototype_pipelines/images/1978_raw_06.png`
- `archive/prototype_pipelines/images/1978_raw_07.png`
- `archive/prototype_pipelines/images/1978_raw_08.png`
- `archive/prototype_pipelines/images/1978_raw_09.png`
- `archive/prototype_pipelines/images/1978_raw_10.png`
- `archive/prototype_pipelines/images/1978_raw_A.png`
- `archive/prototype_pipelines/images/1978_raw_J.png`
- `archive/prototype_pipelines/images/1978_raw_K.png`
- `archive/prototype_pipelines/images/1978_raw_Q.png`
- `archive/prototype_pipelines/images/1978_raw_R1.png`
- `archive/prototype_pipelines/images/1978_raw_R2.png`
- `archive/prototype_pipelines/images/1978_raw_R3.png`
- `archive/prototype_pipelines/images/1978_raw_R4.png`

Issue-scoped assets with likely layout/ad/text risk:

- `issues/1978/art/cover/cover_1978.png`
- `issues/1978/art/cover/back_page_1978.png`
- `issues/1978/art/fake_ads/fake_ad_kit.png`
- `issues/1978/art/feature/cinema_marquee.png`
- `issues/1978/art/parody/fake_ad_kit.png`
- `issues/1978/art/parody/parody_placeholder.png`
- `issues/1978/art/parody/trivia_grid.png`
- `issues/1978/art/parody/weekend_console.png`

Root-level duplicate art tree with the same risk pattern:

- `issues/art/cover/cover_1978.png`
- `issues/art/cover/back_page_1978.png`
- `issues/art/feature/cinema_marquee.png`
- `issues/art/parody/fake_ad_kit.png`
- `issues/art/parody/parody_placeholder.png`
- `issues/art/parody/trivia_grid.png`
- `issues/art/parody/weekend_console.png`


### Heuristic / Medium-Confidence Notes

- `art-library/backgrounds/background_cover_neon_city_nightlife_retro_1978*.png` was repeatedly flagged by OCR-like noise and cover-risk heuristics. These may simply be noisy cover plates, but they are still sub-2000px and should not be treated as validated production illustrations.
- `issues/1978/art/feature/cinema_marquee.png` and `issues/art/feature/cinema_marquee.png` produced OCR hits, suggesting more than minimal environmental lettering may be baked into the asset.
- `scripts/generate_illustrations.py` still appends the prompt suffix `"1970s MAD magazine style cartoon illustration..."`, which directly conflicts with the current `PROJECT_STATE.md` rule to avoid MAD imitation style.
- `scripts/generate_marginals.py` explicitly asks for `"1970s MAD magazine marginal gag cartoon"` and generates `512x512` PNGs, violating both style and resolution expectations.

### What Currently Passes Best

- Many `issues/1978/art/collage/*.png`, `issues/1978/art/comic/*.png`, and `issues/1978/art/feature/*.png` files look like scene/asset tiles rather than page layouts by filename alone, but they still fail the current resolution threshold.

## 7. Unused Files

Best-effort heuristic only: these are **candidates** for move-based cleanup because they are experimental, duplicated, or not referenced by the current scripts.

| Candidate | Count / Scope | Why It Looks Unused or Legacy | Recommended Destination |
| --- | --- | --- | --- |
| `issues/1978/preview/*.html` | 25 preview HTML files | Not referenced by current scripts; appears to be an older parallel preview pipeline. | `archive/old_runs/` |
| `issues/art/**` | 28 root-level art files | Duplicate non-year-scoped art tree; year-scoped copies already exist under issues/1978/art/. | `archive/unused_assets/` |
| `output/RetroVerse_1978.html and output/RetroVerse_1978.pdf` | 2 standalone build artifacts | Generated outside the canonical per-year structure. | `archive/old_runs/ after a canonical issues/{year}/pdf/ destination exists` |
| `workflow/page_rebuild/output/*` | 8 single-page rebuild artifacts | Experimental one-page workflow outputs; not consumed by the full-issue builder. | `Keep while active; otherwise archive/old_runs/` |
| `archive/prototype_pipelines/issues_1978_root_html and archive/prototype_pipelines/images` | prototype HTML and composite images | Already archived prototype material; not part of the canonical pipeline. | `archive/old_runs/ (or leave under archive after archive/old_runs is created)` |
| `.DS_Store files` | 2 Finder metadata files | Stray OS metadata files not part of the project. | `archive/unused_assets/ or remove manually` |


Files that should **not** be moved without a larger pipeline decision:

- `issues/articles/1978/` and `issues/final/1978/`: non-canonical, but actively consumed by the current canonical HTML builder and editorial supervisor flow.
- `issues/layout/1978_issue_map.json`, `issues/layout/1978_issue_map.md`, and `issues/layout/1978_production_targets.json`: intermediate build products, but currently used by the art-direction and page-rebuild flows.
- `issues/plans/1978_narrative_plan.json` and `issues/plans/1978_narrative_plan.md`: active planning inputs.
- `workflow/page_rebuild/` source files: new controlled workflow code, not disposable output.

## 8. Recommended Cleanup Plan

1. **Choose one canonical full-issue orchestrator.** Extend either `scripts/editorial_supervisor.py` or a new top-level wrapper so it runs all 8 required stages in order and stops on failure.
2. **Repair Year Context Generation first.** Replace or rewrite `scripts/generate_year_context.py` so `issues/context/{year}_context.json` includes chart data **and** cultural data (movies, television, cultural events, provenance) before any article stage runs.
3. **Create the missing canonical directories.** At minimum: `issues/{year}/articles/`, `issues/{year}/charts/`, `issues/{year}/pdf/`, `artifacts/logs/`, `artifacts/output/`, `archive/old_runs/`, and `archive/unused_assets/`.
4. **Resolve the article/final output locations.** Either migrate `issues/articles/1978/` and `issues/final/1978/` into the new canonical per-year structure, or update the spec to match reality. Right now the repo and spec disagree.
5. **Archive the parallel preview/output trees.** Move `issues/1978/preview/`, standalone `output/RetroVerse_1978.*`, and the duplicate `issues/art/` tree into the archive structure once the canonical replacements exist.
6. **Fix the illustration stack to match the new rules.** Remove MAD-style prompt suffixes, stop generating ad/layout-like page art as illustration assets, enforce no-final-text rules, and generate production-resolution assets (>= 2000px width).
7. **Add a real full-issue Press Check stage.** This should validate missing images, blank pages, page numbering, final page identity, chart-source integrity, and PDF generation before release.
8. **Add move-only cleanup automation.** Implement a script that moves unused or deprecated assets into `archive/unused_assets/` or `archive/old_runs/` instead of deleting them.
9. **Unify editorial staff definitions.** `PROJECT_STATE.md`, generated layouts, and final story writers currently use mixed staff rosters. Pick one canonical roster and update the pipeline to enforce it.
10. **Promote `workflow/page_rebuild/` concepts into the full issue pipeline.** The new page-level QA gates are closer to the updated spec than the current full-issue illustration/layout flow.

## Conformance Summary

- **Conformant / partially conformant areas:** canonical 1978 layout page count/order/final page, presence of rendering and PDF tooling, existence of planning/writer/art-director/final-prose scripts, absence of banned future-knowledge phrases in current article outputs.
- **Non-conformant areas:** context completeness, full-issue stage orchestration, full-issue press-check QA, directory structure, illustration production rules, illustration resolution, output placement, and cleanup/archive structure.
- **Bottom line:** the repository contains enough pieces to support the intended RetroVerse workflow, but the current implementation is still a mix of legacy, prototype, and newer controlled paths rather than a single canonical pipeline that satisfies `PROJECT_STATE.md` end to end.
