# PROJECT_PIPELINE_REPORT

Generated: 2026-03-13

This report describes the current RetroVerse Magazine pipeline architecture as implemented in the repository. Script I/O notes are primary inferred reads and writes from code structure and path literals; helper modules may support additional caller-supplied paths beyond what is listed here.

## 1. PROJECT DIRECTORY TREE

Depth limited to 4 levels. `__pycache__`, `.pyc`, and `.DS_Store` files are omitted to keep the tree architectural rather than runtime-noise heavy. There is no single top-level `art/` directory; shared reusable art lives in `art-library/`, static web assets live in `assets/`, and issue art lives under `issues/{year}/art/`.

```text
retroverse-magazine/
├── archive/
│   ├── old_runs/
│   │   ├── issues_1978_preview/
│   │   │   ├── index.html
│   │   │   ├── page_01_cover.html
│   │   │   ├── page_02_contents.html
│   │   │   ├── page_03_editor.html
│   │   │   ├── page_04_feature_disco.html
│   │   │   ├── page_05_feature_backlash.html
│   │   │   ├── page_06_collage_city.html
│   │   │   ├── page_07_parody_console.html
│   │   │   ├── page_08_data_billboard.html
│   │   │   ├── page_09_data_albums.html
│   │   │   ├── page_10_department_culture.html
│   │   │   ├── page_11_parody_planner.html
│   │   │   ├── page_12_data_timeline.html
│   │   │   ├── page_13_feature_interview.html
│   │   │   ├── page_14_parody_fake_ad.html
│   │   │   ├── page_15_comic_night.html
│   │   │   ├── page_16_feature_cinema.html
│   │   │   ├── page_17_collage_movies_toys.html
│   │   │   ├── page_18_parody_humor.html
│   │   │   ├── page_19_data_music.html
│   │   │   ├── page_20_feature_tv.html
│   │   │   ├── page_21_department_sue.html
│   │   │   ├── page_22_parody_trend.html
│   │   │   ├── page_23_parody_puzzle.html
│   │   │   └── page_24_back.html
│   │   ├── prototype_pipelines/
│   │   │   ├── art_library/
│   │   │   ├── images/
│   │   │   ├── issues_1978_root_html/
│   │   │   └── generate_magazine.py
│   │   ├── deprecated_build_full_issue.py
│   │   └── deprecated_build_magazine.py
│   └── unused_assets/
│       ├── issues_art/
│       │   ├── collage/
│       │   ├── comic/
│       │   ├── cover/
│       │   ├── departments/
│       │   ├── fake_ads/
│       │   ├── feature/
│       │   ├── marginals/
│       │   ├── parody/
│       │   └── image_prompts.json
│       ├── issues_articles.DS_Store
│       └── issues_final.DS_Store
├── art-library/
│   ├── backgrounds/
│   │   ├── background_cover_neon_city_nightlife_retro_1978.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_10.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_11.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_12.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_13.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_14.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_2.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_3.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_4.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_5.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_6.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_7.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_8.png
│   │   ├── background_cover_neon_city_nightlife_retro_1978_9.png
│   │   └── background_retroverse_page_brief_target_1970s_1978.png
│   ├── characters/
│   ├── environments/
│   ├── fake_ads/
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_10.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_11.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_12.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_13.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_14.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_15.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_16.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_17.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_18.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_19.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_2.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_20.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_21.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_22.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_23.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_24.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_25.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_26.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_27.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_28.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_3.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_4.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_5.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_6.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_7.png
│   │   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_8.png
│   │   └── fake_ad_gadget_advertisement_art_chrome_retro_1978_9.png
│   ├── margin_gags/
│   ├── misc/
│   ├── props/
│   ├── scenes/
│   │   └── scene_retroverse_page_brief_target_1970s_1978.png
│   ├── textures/
│   │   ├── texture_cultural_bustling_night_street_retro_1978.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_10.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_11.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_12.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_13.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_14.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_15.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_16.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_17.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_18.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_19.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_2.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_20.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_21.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_22.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_23.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_24.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_25.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_26.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_27.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_28.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_3.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_4.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_5.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_6.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_7.png
│   │   ├── texture_cultural_bustling_night_street_retro_1978_8.png
│   │   └── texture_cultural_bustling_night_street_retro_1978_9.png
│   └── art_index.json
├── artifacts/
│   ├── logs/
│   │   ├── year_generation_log.json
│   │   └── year_generation_summary.md
│   └── output/
│       ├── 1978/
│       │   └── qa/
│       ├── RetroVerse_1978.html
│       └── RetroVerse_1978.pdf
├── assets/
│   ├── covers/
│   ├── css/
│   │   └── magazine.css
│   ├── illustrations/
│   └── layouts/
├── charter/
│   └── retroverse_editorial_charter.md
├── data/
│   └── DATA_SOURCES.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CANONICAL_PIPELINE.md
│   ├── SCREEN_CULTURE_DATA_AUDIT.md
│   └── SCREEN_CULTURE_WAREHOUSE_AUDIT.md
├── INSPECT_1978_IMAGES/
│   ├── 1978_magazine.jpg
│   ├── 1978_raw_02.png
│   ├── 1978_raw_03.png
│   ├── 1978_raw_04.png
│   ├── 1978_raw_05.png
│   ├── 1978_raw_06.png
│   ├── 1978_raw_07.png
│   ├── 1978_raw_08.png
│   ├── 1978_raw_09.png
│   ├── 1978_raw_10.png
│   ├── 1978_raw_A.png
│   ├── 1978_raw_J.png
│   ├── 1978_raw_K.png
│   ├── 1978_raw_Q.png
│   ├── 1978_raw_R1.png
│   ├── 1978_raw_R2.png
│   ├── 1978_raw_R3.png
│   ├── 1978_raw_R4.png
│   ├── back_page_1978.png
│   ├── background_1970s_mad_printing_cover_1970s_1978.png
│   ├── background_cover_neon_city_nightlife_retro_1978.png
│   ├── background_cover_neon_city_nightlife_retro_1978_10.png
│   ├── background_cover_neon_city_nightlife_retro_1978_11.png
│   ├── background_cover_neon_city_nightlife_retro_1978_12.png
│   ├── background_cover_neon_city_nightlife_retro_1978_13.png
│   ├── background_cover_neon_city_nightlife_retro_1978_14.png
│   ├── background_cover_neon_city_nightlife_retro_1978_2.png
│   ├── background_cover_neon_city_nightlife_retro_1978_3.png
│   ├── background_cover_neon_city_nightlife_retro_1978_4.png
│   ├── background_cover_neon_city_nightlife_retro_1978_5.png
│   ├── background_cover_neon_city_nightlife_retro_1978_6.png
│   ├── background_cover_neon_city_nightlife_retro_1978_7.png
│   ├── background_cover_neon_city_nightlife_retro_1978_8.png
│   ├── background_cover_neon_city_nightlife_retro_1978_9.png
│   ├── cinema_marquee.png
│   ├── collage_01.png
│   ├── collage_02.png
│   ├── collage_03.png
│   ├── collage_04.png
│   ├── collage_05.png
│   ├── collage_06.png
│   ├── collage_07.png
│   ├── collage_08.png
│   ├── collage_09.png
│   ├── comic_panel_01.png
│   ├── comic_panel_02.png
│   ├── comic_panel_03.png
│   ├── comic_panel_04.png
│   ├── comic_panel_05.png
│   ├── comic_panel_06.png
│   ├── cover_1978.png
│   ├── department_portrait.png
│   ├── disco_floor.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_10.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_11.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_12.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_13.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_14.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_15.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_16.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_17.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_18.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_19.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_2.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_20.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_21.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_22.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_23.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_24.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_25.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_26.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_27.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_28.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_3.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_4.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_5.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_6.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_7.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_8.png
│   ├── fake_ad_gadget_advertisement_art_chrome_retro_1978_9.png
│   ├── fake_ad_kit.png
│   ├── feature_placeholder.png
│   ├── parody_placeholder.png
│   ├── scene_1970s_mad_printing_movie_1970s_1978.png
│   ├── texture_cultural_bustling_night_street_retro_1978.png
│   ├── texture_cultural_bustling_night_street_retro_1978_10.png
│   ├── texture_cultural_bustling_night_street_retro_1978_11.png
│   ├── texture_cultural_bustling_night_street_retro_1978_12.png
│   ├── texture_cultural_bustling_night_street_retro_1978_13.png
│   ├── texture_cultural_bustling_night_street_retro_1978_14.png
│   ├── texture_cultural_bustling_night_street_retro_1978_15.png
│   ├── texture_cultural_bustling_night_street_retro_1978_16.png
│   ├── texture_cultural_bustling_night_street_retro_1978_17.png
│   ├── texture_cultural_bustling_night_street_retro_1978_18.png
│   ├── texture_cultural_bustling_night_street_retro_1978_19.png
│   ├── texture_cultural_bustling_night_street_retro_1978_2.png
│   ├── texture_cultural_bustling_night_street_retro_1978_20.png
│   ├── texture_cultural_bustling_night_street_retro_1978_21.png
│   ├── texture_cultural_bustling_night_street_retro_1978_22.png
│   ├── texture_cultural_bustling_night_street_retro_1978_23.png
│   ├── texture_cultural_bustling_night_street_retro_1978_24.png
│   ├── texture_cultural_bustling_night_street_retro_1978_25.png
│   ├── texture_cultural_bustling_night_street_retro_1978_26.png
│   ├── texture_cultural_bustling_night_street_retro_1978_27.png
│   ├── texture_cultural_bustling_night_street_retro_1978_28.png
│   ├── texture_cultural_bustling_night_street_retro_1978_3.png
│   ├── texture_cultural_bustling_night_street_retro_1978_4.png
│   ├── texture_cultural_bustling_night_street_retro_1978_5.png
│   ├── texture_cultural_bustling_night_street_retro_1978_6.png
│   ├── texture_cultural_bustling_night_street_retro_1978_7.png
│   ├── texture_cultural_bustling_night_street_retro_1978_8.png
│   ├── texture_cultural_bustling_night_street_retro_1978_9.png
│   ├── trivia_grid.png
│   ├── tv_livingroom.png
│   └── weekend_console.png
├── issues/
│   ├── 1978/
│   │   ├── art/
│   │   │   ├── collage/
│   │   │   ├── comic/
│   │   │   ├── cover/
│   │   │   ├── departments/
│   │   │   ├── fake_ads/
│   │   │   ├── feature/
│   │   │   ├── images/
│   │   │   ├── marginals/
│   │   │   ├── parody/
│   │   │   ├── prompts/
│   │   │   └── image_prompts.json
│   │   ├── art_direction/
│   │   │   ├── page_01_cover.json
│   │   │   ├── page_02_masthead.json
│   │   │   ├── page_03_editor_letter.json
│   │   │   ├── page_04_year_snapshot.json
│   │   │   ├── page_05_charts_overview.json
│   │   │   ├── page_06_top_song_1.json
│   │   │   ├── page_07_top_song_2.json
│   │   │   ├── page_08_top_song_3.json
│   │   │   ├── page_09_top_song_4.json
│   │   │   ├── page_10_top_song_5.json
│   │   │   ├── page_11_top_song_6.json
│   │   │   ├── page_12_top_song_7.json
│   │   │   ├── page_13_top_song_8.json
│   │   │   ├── page_14_top_song_9.json
│   │   │   ├── page_15_top_song_10.json
│   │   │   ├── page_16_movies.json
│   │   │   ├── page_17_television.json
│   │   │   ├── page_18_culture.json
│   │   │   ├── page_19_arcade.json
│   │   │   ├── page_20_retro_ad.json
│   │   │   ├── page_21_comic.json
│   │   │   ├── page_22_puzzle.json
│   │   │   ├── page_23_letters.json
│   │   │   ├── page_24_forgotten_hit.json
│   │   │   ├── page_25_one_hit_wonder.json
│   │   │   ├── page_26_album_spotlight.json
│   │   │   ├── page_27_year_timeline.json
│   │   │   ├── page_28_culture_collage.json
│   │   │   ├── page_29_retro_ads_page.json
│   │   │   ├── page_30_chart_top23.json
│   │   │   └── page_assignments.json
│   │   ├── articles/
│   │   │   ├── final/
│   │   │   ├── story_001.json
│   │   │   ├── story_001.md
│   │   │   ├── story_002.json
│   │   │   ├── story_002.md
│   │   │   ├── story_003.json
│   │   │   ├── story_003.md
│   │   │   ├── story_004.json
│   │   │   ├── story_004.md
│   │   │   ├── story_005.json
│   │   │   ├── story_005.md
│   │   │   ├── story_006.json
│   │   │   ├── story_006.md
│   │   │   ├── story_007.json
│   │   │   ├── story_007.md
│   │   │   ├── story_008.json
│   │   │   ├── story_008.md
│   │   │   ├── story_009.json
│   │   │   ├── story_009.md
│   │   │   ├── story_010.json
│   │   │   ├── story_010.md
│   │   │   ├── story_011.json
│   │   │   ├── story_011.md
│   │   │   ├── story_012.json
│   │   │   └── story_012.md
│   │   ├── charts/
│   │   ├── data/
│   │   │   ├── charts.json
│   │   │   ├── editorial.json
│   │   │   ├── issue.json
│   │   │   ├── movies.json
│   │   │   └── tv.json
│   │   ├── layout/
│   │   │   ├── art_direction/
│   │   │   ├── page_briefs/
│   │   │   ├── 1978_issue_map.json
│   │   │   ├── 1978_issue_map.md
│   │   │   ├── 1978_production_targets.json
│   │   │   ├── index.html
│   │   │   ├── page_01_cover.html
│   │   │   ├── page_02_masthead.html
│   │   │   ├── page_03_editor_letter.html
│   │   │   ├── page_04_year_snapshot.html
│   │   │   ├── page_05_charts_overview.html
│   │   │   ├── page_06_top_song_1.html
│   │   │   ├── page_07_top_song_2.html
│   │   │   ├── page_08_top_song_3.html
│   │   │   ├── page_09_top_song_4.html
│   │   │   ├── page_10_top_song_5.html
│   │   │   ├── page_11_top_song_6.html
│   │   │   ├── page_12_top_song_7.html
│   │   │   ├── page_13_top_song_8.html
│   │   │   ├── page_14_top_song_9.html
│   │   │   ├── page_15_top_song_10.html
│   │   │   ├── page_16_movies.html
│   │   │   ├── page_17_television.html
│   │   │   ├── page_18_culture.html
│   │   │   ├── page_19_arcade.html
│   │   │   ├── page_20_retro_ad.html
│   │   │   ├── page_21_comic.html
│   │   │   ├── page_22_puzzle.html
│   │   │   ├── page_23_letters.html
│   │   │   ├── page_24_forgotten_hit.html
│   │   │   ├── page_25_one_hit_wonder.html
│   │   │   ├── page_26_album_spotlight.html
│   │   │   ├── page_27_year_timeline.html
│   │   │   ├── page_28_culture_collage.html
│   │   │   ├── page_29_retro_ads_page.html
│   │   │   └── page_30_chart_top23.html
│   │   ├── pdf/
│   │   │   └──  .pdf
│   │   ├── songs/
│   │   │   ├── 01.md
│   │   │   ├── 02.md
│   │   │   ├── 03.md
│   │   │   ├── 04.md
│   │   │   ├── 05.md
│   │   │   ├── 06.md
│   │   │   ├── 07.md
│   │   │   ├── 08.md
│   │   │   ├── 09.md
│   │   │   └── 10.md
│   │   ├── ads.md
│   │   ├── arcade.md
│   │   ├── chart_top23.md
│   │   ├── charts_overview.md
│   │   ├── comic.md
│   │   ├── cover.md
│   │   ├── culture.md
│   │   ├── editor_letter.md
│   │   ├── letters.md
│   │   ├── masthead.md
│   │   ├── movies.md
│   │   ├── puzzle1.md
│   │   ├── puzzle2.md
│   │   ├── retroverse_1978_pilot.md
│   │   └── television.md
│   ├── 1979/
│   ├── 1980/
│   ├── context/
│   │   ├── 1958_context.json
│   │   ├── 1959_context.json
│   │   ├── 1960_context.json
│   │   ├── 1961_context.json
│   │   ├── 1962_context.json
│   │   ├── 1963_context.json
│   │   ├── 1964_context.json
│   │   ├── 1965_context.json
│   │   ├── 1966_context.json
│   │   ├── 1967_context.json
│   │   ├── 1968_context.json
│   │   ├── 1969_context.json
│   │   ├── 1970_context.json
│   │   ├── 1971_context.json
│   │   ├── 1972_context.json
│   │   ├── 1973_context.json
│   │   ├── 1974_context.json
│   │   ├── 1975_context.json
│   │   ├── 1976_context.json
│   │   ├── 1977_context.json
│   │   ├── 1978_context.json
│   │   ├── 1979_context.json
│   │   ├── 1980_context.json
│   │   ├── 1981_context.json
│   │   ├── 1982_context.json
│   │   ├── 1983_context.json
│   │   ├── 1984_context.json
│   │   ├── 1985_context.json
│   │   ├── 1986_context.json
│   │   ├── 1987_context.json
│   │   ├── 1988_context.json
│   │   ├── 1989_context.json
│   │   ├── 1990_context.json
│   │   ├── 1991_context.json
│   │   ├── 1992_context.json
│   │   ├── 1993_context.json
│   │   ├── 1994_context.json
│   │   ├── 1995_context.json
│   │   ├── 1996_context.json
│   │   ├── 1997_context.json
│   │   ├── 1998_context.json
│   │   ├── 1999_context.json
│   │   ├── 2000_context.json
│   │   ├── 2001_context.json
│   │   ├── 2002_context.json
│   │   ├── 2003_context.json
│   │   ├── 2004_context.json
│   │   ├── 2005_context.json
│   │   ├── 2006_context.json
│   │   ├── 2007_context.json
│   │   ├── 2008_context.json
│   │   ├── 2009_context.json
│   │   ├── 2010_context.json
│   │   ├── 2011_context.json
│   │   ├── 2012_context.json
│   │   ├── 2013_context.json
│   │   ├── 2014_context.json
│   │   ├── 2015_context.json
│   │   ├── 2016_context.json
│   │   ├── 2017_context.json
│   │   ├── 2018_context.json
│   │   ├── 2019_context.json
│   │   ├── 2020_context.json
│   │   ├── 2021_context.json
│   │   ├── 2022_context.json
│   │   ├── 2023_context.json
│   │   ├── 2024_context.json
│   │   ├── 2025_context.json
│   │   └── example_context_1978.json
│   └── plans/
│       ├── 1978_narrative_plan.json
│       └── 1978_narrative_plan.md
├── layout-library/
│   ├── css/
│   │   └── layout-library.css
│   ├── docs/
│   │   ├── page_rhythm_guide.md
│   │   └── retroverse_layout_library.md
│   ├── schemas/
│   │   └── layout_templates.json
│   └── templates/
│       ├── template_back_page.html
│       ├── template_contents.html
│       ├── template_cover.html
│       ├── template_data_page.html
│       ├── template_department_column.html
│       ├── template_feature_spread.html
│       ├── template_grid_collage.html
│       ├── template_narrative_comic.html
│       └── template_visual_parody.html
├── pipeline/
│   ├── __init__.py
│   ├── art_direction_stage.py
│   ├── common.py
│   ├── generate_issue_art_direction.py
│   ├── generate_issue_art_prompts.py
│   ├── generate_issue_page_briefs.py
│   ├── illustration_prompt_stage.py
│   ├── qa_art_direction.py
│   ├── qa_art_prompts.py
│   ├── qa_layout.py
│   ├── qa_page_briefs.py
│   ├── qa_press_check.py
│   └── run_issue_pipeline.py
├── prompts/
│   └── generate_issue_prompt.md
├── scripts/
│   ├── analyze_chart_dynamics.py
│   ├── audit_billboard200_db.py
│   ├── audit_hot100_db.py
│   ├── audit_screen_culture_data.py
│   ├── audit_screen_culture_warehouse.py
│   ├── build_issue.py
│   ├── build_movies_dataset.py
│   ├── build_screen_culture_warehouse.py
│   ├── build_television_dataset.py
│   ├── db_common.py
│   ├── editorial_supervisor.py
│   ├── enrich_omdb_metadata.py
│   ├── enrich_tmdb_metadata.py
│   ├── find_art_asset.py
│   ├── generate_all_year_contexts.py
│   ├── generate_art_prompts.py
│   ├── generate_editorial.py
│   ├── generate_final_articles.py
│   ├── generate_illustrations.py
│   ├── generate_marginals.py
│   ├── generate_year_context.py
│   ├── generate_year_narrative.py
│   ├── generate_year_range.py
│   ├── index_artwork.py
│   ├── ingest_imdb_datasets.py
│   ├── magazine_pipeline.py
│   ├── print_daily_refresh_instructions.py
│   ├── run_art_director.py
│   ├── run_staff_writers.py
│   ├── screen_culture_common.py
│   └── update_data_inventory.py
├── templates/
│   ├── sections/
│   │   ├── album_spotlight.html
│   │   ├── arcade.html
│   │   ├── chart_top23.html
│   │   ├── charts_overview.html
│   │   ├── comic.html
│   │   ├── cover.html
│   │   ├── culture.html
│   │   ├── culture_collage.html
│   │   ├── editor_letter.html
│   │   ├── forgotten_hit.html
│   │   ├── letters.html
│   │   ├── masthead.html
│   │   ├── movies.html
│   │   ├── one_hit_wonder.html
│   │   ├── puzzle.html
│   │   ├── retro_ad.html
│   │   ├── retro_ads_page.html
│   │   ├── television.html
│   │   ├── top_song.html
│   │   ├── year_snapshot.html
│   │   └── year_timeline.html
│   ├── issue_template.md
│   └── page_template.html
├── tools/
│   └── magazine_builder/
│       ├── build_issue.py
│       ├── render_browser_pdf.mjs
│       ├── style.css
│       └── template.html
├── workflow/
│   └── page_rebuild/
│       ├── output/
│       │   ├── 1978_movies_art_direction.json
│       │   ├── 1978_movies_art_direction_QA.md
│       │   ├── 1978_movies_art_prompt.txt
│       │   ├── 1978_movies_art_prompt_QA.md
│       │   ├── 1978_movies_layout_QA.md
│       │   ├── 1978_movies_mock_page.html
│       │   ├── 1978_movies_page_brief.json
│       │   └── 1978_movies_page_brief_QA.md
│       ├── build_mock_page.py
│       ├── common.py
│       ├── generate_art_direction.py
│       ├── generate_page_art_prompt.py
│       ├── generate_page_brief.py
│       ├── page_brief_schema.json
│       ├── qa_art_direction.py
│       ├── qa_art_prompt.py
│       ├── qa_layout.py
│       ├── qa_page_brief.py
│       ├── README.md
│       ├── rebuild_single_page.py
│       └── SINGLE_PAGE_REBUILD_REPORT.md
├── .env
├── .gitignore
├── DATA_INVENTORY.md
├── ISSUE_STRUCTURE_REPORT.md
├── MAGAZINE_PIPELINE_AUDIT.md
├── magazine_template.html
├── PIPELINE_REPAIR_IMPLEMENTATION.md
├── PIPELINE_REPAIR_REPORT.md
├── PRESS_CHECK_1978.md
├── PROJECT_AUDIT.md
├── PROJECT_STATE.md
└── requirements.txt
```

## 2. SCRIPT INVENTORY

Scripts covered here are every root-level `scripts/*.py` and `pipeline/*.py` file currently present in the repository.

### `pipeline/__init__.py`

- Script name: `__init__.py`
- Purpose: Package marker for the canonical pipeline modules.
- CLI arguments: none
- Key functions: none
- Files it reads: None
- Files it writes: None

### `pipeline/art_direction_stage.py`

- Script name: `art_direction_stage.py`
- Purpose: Generate issue-wide art direction with explicit RetroVerse studio role assignments.
- CLI arguments: none
- Key functions: classify_role, composition_type_for_role, visual_hierarchy, build_assignment, build_art_direction, generate_art_direction, main
- Files it reads: issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json; issues/{year}/layout/page_briefs/page_*.json
- Files it writes: issues/{year}/art_direction/page_*.json; issues/{year}/art_direction/page_assignments.json

### `pipeline/common.py`

- Script name: `common.py`
- Purpose: Shared helpers for the canonical RetroVerse full-issue pipeline.
- CLI arguments: --year
- Key functions: parse_year_args, year_dir, articles_dir, final_articles_dir, charts_dir, layout_dir, art_dir, art_direction_dir, pdf_dir, page_briefs_dir, +32 more
- Files it reads: scripts/magazine_pipeline.py (imported helpers); PROJECT_STATE.md; issues/context/{year}_context.json; issues/{year}/layout/{year}_issue_map.json; issues/{year}/layout/{year}_production_targets.json
- Files it writes: Generic helper output only: caller-supplied JSON/text files via write_json() / write_text()

### `pipeline/generate_issue_art_direction.py`

- Script name: `generate_issue_art_direction.py`
- Purpose: Backward-compatible wrapper that delegates to the canonical art direction stage.
- CLI arguments: none
- Key functions: none
- Files it reads: Delegates to pipeline/art_direction_stage.py
- Files it writes: Delegates to pipeline/art_direction_stage.py

### `pipeline/generate_issue_art_prompts.py`

- Script name: `generate_issue_art_prompts.py`
- Purpose: Backward-compatible wrapper that delegates to the canonical illustration prompt stage.
- CLI arguments: none
- Key functions: none
- Files it reads: Delegates to pipeline/illustration_prompt_stage.py
- Files it writes: Delegates to pipeline/illustration_prompt_stage.py

### `pipeline/generate_issue_page_briefs.py`

- Script name: `generate_issue_page_briefs.py`
- Purpose: Generate structured page briefs for every page in a RetroVerse issue.
- CLI arguments: none
- Key functions: build_text_blocks, build_brief, main
- Files it reads: Issue markdown sources under issues/{year}/*.md; issues/context/{year}_context.json; issues/{year}/layout/{year}_issue_map.json; issues/{year}/layout/{year}_production_targets.json; scripts/magazine_pipeline.py page records
- Files it writes: issues/{year}/layout/page_briefs/page_*.json; issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json

### `pipeline/illustration_prompt_stage.py`

- Script name: `illustration_prompt_stage.py`
- Purpose: Generate issue-wide illustration prompts from page briefs and art-direction assignments.
- CLI arguments: none
- Key functions: zone_line, assignment_map, build_prompt, generate_prompts, main
- Files it reads: issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json; issues/{year}/layout/page_briefs/page_*.json; issues/{year}/art_direction/page_assignments.json; issues/{year}/art_direction/page_*.json
- Files it writes: issues/{year}/art/prompts/page_*.txt; issues/{year}/art/image_prompts.json

### `pipeline/qa_art_direction.py`

- Script name: `qa_art_direction.py`
- Purpose: QA gate for issue-wide page art direction.
- CLI arguments: none
- Key functions: main
- Files it reads: issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json; issues/{year}/layout/page_briefs/page_*.json; issues/{year}/art_direction/page_assignments.json; issues/{year}/art_direction/page_*.json
- Files it writes: artifacts/output/{year}/qa/{year}_art_direction_QA.md

### `pipeline/qa_art_prompts.py`

- Script name: `qa_art_prompts.py`
- Purpose: QA gate for issue-wide illustration prompts.
- CLI arguments: none
- Key functions: main
- Files it reads: issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json; issues/{year}/art_direction/page_assignments.json; issues/{year}/art/prompts/page_*.txt
- Files it writes: artifacts/output/{year}/qa/{year}_art_prompt_QA.md

### `pipeline/qa_layout.py`

- Script name: `qa_layout.py`
- Purpose: QA gate for the canonical full-issue layout build.
- CLI arguments: none
- Key functions: body_budget, main
- Files it reads: issues/{year}/layout/page_*.html; issues/{year}/layout/index.html
- Files it writes: artifacts/output/{year}/qa/{year}_layout_QA.md

### `pipeline/qa_page_briefs.py`

- Script name: `qa_page_briefs.py`
- Purpose: QA gate for issue-wide page briefs.
- CLI arguments: none
- Key functions: main
- Files it reads: issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json; issues/{year}/layout/page_briefs/page_*.json
- Files it writes: artifacts/output/{year}/qa/{year}_page_briefs_QA.md

### `pipeline/qa_press_check.py`

- Script name: `qa_press_check.py`
- Purpose: Run a pre-PDF press-check QA pass over the canonical layout output.
- CLI arguments: none
- Key functions: list_page_files, extract_image_sources, main
- Files it reads: issues/{year}/layout/page_*.html; issues/{year}/layout/page_02_masthead.html; issues/{year}/layout/page_{last}_chart_top23.html; Referenced issues/{year}/art/** image files
- Files it writes: artifacts/output/{year}/qa/{year}_press_check_QA.md

### `pipeline/run_issue_pipeline.py`

- Script name: `run_issue_pipeline.py`
- Purpose: Run the canonical RetroVerse issue pipeline in order with blocking QA gates.
- CLI arguments: --year, --overwrite-art, --skip-illustration, --skip-pdf
- Key functions: parse_args, run_step, main
- Files it reads: Pipeline CLI args; pipeline/common.py; tools/magazine_builder/render_browser_pdf.mjs
- Files it writes: Delegates all stage outputs; optionally writes issues/{year}/pdf/RetroVerse_{year}.pdf

### `scripts/analyze_chart_dynamics.py`

- Script name: `analyze_chart_dynamics.py`
- Purpose: Analyze weekly chart movement patterns and append dynamics to year context.
- CLI arguments: --year
- Key functions: parse_args, as_int, date_sort_key, normalize_name, pick_source_path, choose_column, load_hot100_rows, load_album_rows, build_timelines, consecutive_max, +8 more
- Files it reads: data/DATA_SOURCES.yaml; Canonical Hot 100 SQLite DB; Canonical Billboard 200 SQLite DB; issues/context/{year}_context.json
- Files it writes: issues/context/{year}_context.json (appends chart_dynamics and album_dynamics)

### `scripts/audit_billboard200_db.py`

- Script name: `audit_billboard200_db.py`
- Purpose: Audit Billboard 200 coverage and schema from canonical source map.
- CLI arguments: none
- Key functions: print_schema, pick_source_path, find_album_table, count_rows_by_year, main
- Files it reads: data/DATA_SOURCES.yaml; Canonical Billboard 200 SQLite DB
- Files it writes: stdout only

### `scripts/audit_hot100_db.py`

- Script name: `audit_hot100_db.py`
- Purpose: Audit Billboard Hot 100 coverage and schema from canonical source map.
- CLI arguments: none
- Key functions: print_schema, find_hot100_table, count_rows_by_year, has_event_entry_model, count_rows_by_year_event_model, diagnose_coverage, main
- Files it reads: data/DATA_SOURCES.yaml; Canonical Hot 100 SQLite DB
- Files it writes: stdout only

### `scripts/audit_screen_culture_data.py`

- Script name: `audit_screen_culture_data.py`
- Purpose: Audit movies, television, and cultural event dataset coverage.
- CLI arguments: --year
- Key functions: parse_args, empty_counts, parse_year, infer_year_from_path, add_count, merge_counts_max, detect_dataset_hints, resolve_entry_paths, discover_sources, count_list_items, +12 more
- Files it reads: data/DATA_SOURCES.yaml; Discovered JSON/CSV/DB screen-culture sources
- Files it writes: docs/SCREEN_CULTURE_DATA_AUDIT.md; stdout audit summary

### `scripts/audit_screen_culture_warehouse.py`

- Script name: `audit_screen_culture_warehouse.py`
- Purpose: Audit coverage and quality for the screen/culture warehouse.
- CLI arguments: none
- Key functions: parse_args, load_records, movie_has_box_office, movie_has_critic, movie_has_ratings, movie_has_popularity, tv_has_network, tv_has_popularity, tv_has_critic, group_by_year, +6 more
- Files it reads: Warehouse movies_master.json; Warehouse television_master.json
- Files it writes: docs/SCREEN_CULTURE_WAREHOUSE_AUDIT.md

### `scripts/build_issue.py`

- Script name: `build_issue.py`
- Purpose: Build the canonical RetroVerse HTML issue from finalized article sources.
- CLI arguments: --year
- Key functions: parse_args, clean_layout_output, main
- Files it reads: issues/{year}/articles/final/*.md; issues/{year}/*.md; issues/{year}/data/*.json; templates/sections/*.html; scripts/magazine_pipeline.py
- Files it writes: issues/{year}/layout/page_*.html; issues/{year}/layout/index.html

### `scripts/build_movies_dataset.py`

- Script name: `build_movies_dataset.py`
- Purpose: Build the RetroVerse movies master dataset with provenance and trust labels.
- CLI arguments: --stdout
- Key functions: parse_args, split_list_value, normalize_movie_row, rows_from_json, rows_from_csv, rows_from_sqlite, find_existing_key, apply_movie_fields, ingest_year_master, ingest_issue_movies, +3 more
- Files it reads: retroverse_year_master_1958_2024.json; issues/*/data/movies.json; Local screen-culture enrichment JSON/CSV/DB files
- Files it writes: Warehouse movies_master.json (or stdout with --stdout)

### `scripts/build_screen_culture_warehouse.py`

- Script name: `build_screen_culture_warehouse.py`
- Purpose: Build unified screen/culture warehouse outputs for RetroVerse.
- CLI arguments: --no-sqlite
- Key functions: parse_args, union_years, build_inventory, write_sqlite, build_screen_culture_warehouse, main
- Files it reads: Warehouse movies_master.json; Warehouse television_master.json
- Files it writes: Warehouse movies_by_year.json; Warehouse television_by_year.json; Warehouse screen_culture_inventory.json; Warehouse screen_culture.db

### `scripts/build_television_dataset.py`

- Script name: `build_television_dataset.py`
- Purpose: Build the RetroVerse television master dataset with provenance and trust labels.
- CLI arguments: --stdout
- Key functions: parse_args, split_list_value, normalize_tv_row, rows_from_json, rows_from_csv, rows_from_sqlite, find_existing_key, apply_television_fields, ingest_year_master, ingest_issue_television, +5 more
- Files it reads: retroverse_year_master_1958_2024.json; issues/*/data/tv.json; tv_listings.csv; Local screen-culture enrichment JSON/CSV/DB files
- Files it writes: Warehouse television_master.json (or stdout with --stdout)

### `scripts/db_common.py`

- Script name: `db_common.py`
- Purpose: Shared SQLite and YAML helpers for RetroVerse data scripts.
- CLI arguments: none
- Key functions: parse_scalar, parse_simple_yaml, load_data_sources, resolve_path, project_relative, connect_read_only, list_tables, table_columns, sql_year_expression
- Files it reads: data/DATA_SOURCES.yaml; SQLite databases resolved from the data source map
- Files it writes: None

### `scripts/editorial_supervisor.py`

- Script name: `editorial_supervisor.py`
- Purpose: Coordinate data preparation and integrity checks for a RetroVerse issue.
- CLI arguments: --year
- Key functions: parse_args, run_script, ensure_project_state, ensure_data_sources, ensure_data_inventory, context_needs_refresh, ensure_year_context, ensure_screen_culture_coverage, ensure_chart_dynamics, ensure_year_narrative_plan, +8 more
- Files it reads: PROJECT_STATE.md; data/DATA_SOURCES.yaml; DATA_INVENTORY.md; issues/context/{year}_context.json; issues/plans/{year}_narrative_plan.json; issues/{year}/articles/*.json; issues/{year}/layout/{year}_issue_map.json; issues/{year}/layout/{year}_production_targets.json
- Files it writes: Runs subordinate scripts that write context, plans, articles, art direction, and final articles; may also trigger DATA_INVENTORY.md generation

### `scripts/enrich_omdb_metadata.py`

- Script name: `enrich_omdb_metadata.py`
- Purpose: Enrich screen/culture warehouse records with OMDb critic/acclaim metadata.
- CLI arguments: --sleep, --max-movies, --max-television
- Key functions: parse_args, parse_year, parse_int, parse_box_office, derive_field_trust, set_if_empty, has_existing_critic_scores, omdb_request, extract_critic_fields, load_payload, +5 more
- Files it reads: .env (OMDB_API_KEY); Warehouse movies_master.json; Warehouse television_master.json; Warehouse screen_culture.db
- Files it writes: Updated warehouse movies_master.json; Updated warehouse television_master.json; Updated warehouse movies_by_year.json; Updated warehouse television_by_year.json; Updated warehouse screen_culture_inventory.json; Updated warehouse screen_culture.db

### `scripts/enrich_tmdb_metadata.py`

- Script name: `enrich_tmdb_metadata.py`
- Purpose: Enrich screen/culture warehouse records with TMDb metadata.
- CLI arguments: --sleep, --max-movies, --max-television
- Key functions: parse_args, parse_year, title_similarity, derive_field_trust, set_if_empty, list_if_empty, pick_movie_candidate, pick_tv_candidate, load_payload, get_top_cast, +6 more
- Files it reads: .env (TMDB_API_KEY); Warehouse movies_master.json; Warehouse television_master.json; Warehouse screen_culture.db
- Files it writes: Updated warehouse movies_master.json; Updated warehouse television_master.json; Updated warehouse movies_by_year.json; Updated warehouse television_by_year.json; Updated warehouse screen_culture_inventory.json; Updated warehouse screen_culture.db

### `scripts/find_art_asset.py`

- Script name: `find_art_asset.py`
- Purpose: Find reusable art assets by tags/prompt text.
- CLI arguments: query, --limit
- Key functions: project_root, tokenize, load_index, score_asset, search_art_assets, find_art_asset, parse_args, main
- Files it reads: art-library/art_index.json
- Files it writes: stdout only

### `scripts/generate_all_year_contexts.py`

- Script name: `generate_all_year_contexts.py`
- Purpose: Legacy helper that iterates chart years and calls generate_year_context.py for each discovered year.
- CLI arguments: none
- Key functions: none
- Files it reads: ../../retroverse-data/databases/source_billboard_hot_100.db
- Files it writes: issues/context/{year}_context.json via subprocess calls to generate_year_context.py

### `scripts/generate_art_prompts.py`

- Script name: `generate_art_prompts.py`
- Purpose: Generate RetroVerse art prompt payloads from editorial data.
- CLI arguments: --year
- Key functions: load_json, add_easter_egg_rule, build_feature_prompt, build_collage_prompts, build_comic_prompts, build_prompt_payload, parse_args, main
- Files it reads: issues/{year}/data/editorial.json
- Files it writes: issues/{year}/art/image_prompts.json

### `scripts/generate_editorial.py`

- Script name: `generate_editorial.py`
- Purpose: Generate editorial payloads for a RetroVerse issue year.
- CLI arguments: --year
- Key functions: load_json, top_titles, generate_feature_story, generate_collage, generate_comic, build_editorial_payload, parse_args, main
- Files it reads: issues/{year}/data/charts.json; issues/{year}/data/movies.json; issues/{year}/data/tv.json
- Files it writes: issues/{year}/data/editorial.json

### `scripts/generate_final_articles.py`

- Script name: `generate_final_articles.py`
- Purpose: Generate final magazine prose from structured article drafts and production targets.
- CLI arguments: --year
- Key functions: parse_args, read_json, unique_list, role_to_beat, parse_project_state, lookup_path, parse_story_assignments, parse_article_drafts, parse_production_targets, parse_count_estimate, +18 more
- Files it reads: PROJECT_STATE.md; issues/context/{year}_context.json; issues/plans/{year}_narrative_plan.json; issues/{year}/articles/*.json; issues/{year}/layout/{year}_production_targets.json
- Files it writes: issues/{year}/articles/final/*.json; issues/{year}/articles/final/*.md

### `scripts/generate_illustrations.py`

- Script name: `generate_illustrations.py`
- Purpose: Generate RetroVerse issue illustrations with reusable art-library support.
- CLI arguments: --year, --page, --model, --size, --overwrite, --force
- Key functions: parse_args, load_json, ensure_directories, tokenize, slugify, prompt_subject, build_library_filename, build_prompt, normalize_size, art_type_for_relpath, +15 more
- Files it reads: .env (OPENAI_API_KEY); issues/{year}/art/image_prompts.json; issues/{year}/art/prompts/page_*.txt (via prompt_path); Optional issues/{year}/data/issue.json fallback; art-library/**/*.png reusable library assets
- Files it writes: issues/{year}/art/<category>/*.png; issues/{year}/art/images/*.png; art-library/backgrounds/*.png; art-library/scenes/*.png; art-library/environments/*.png

### `scripts/generate_marginals.py`

- Script name: `generate_marginals.py`
- Purpose: Generate RetroVerse marginal gag illustrations.
- CLI arguments: --year, --model, --overwrite
- Key functions: parse_args, create_client, build_prompt, generate_png_bytes, main
- Files it reads: .env (OPENAI_API_KEY); Year argument and built-in marginal prompt templates
- Files it writes: issues/{year}/art/marginals/*.png

### `scripts/generate_year_context.py`

- Script name: `generate_year_context.py`
- Purpose: Generate a canonical RetroVerse year context payload.
- CLI arguments: year, --year
- Key functions: calculate_score, read_json, load_optional_json, load_movies, load_television, load_cultural_events, build_top_artists, build_chart_dynamics, build_album_context, build_artist_power_index, +4 more
- Files it reads: source_billboard_hot_100.db; cultural_events_{year}.json; albums_{year}_sample.csv; issues/{year}/data/movies.json; issues/{year}/data/tv.json; Existing issues/context/{year}_context.json
- Files it writes: issues/context/{year}_context.json

### `scripts/generate_year_narrative.py`

- Script name: `generate_year_narrative.py`
- Purpose: Build a data-grounded editorial narrative plan from year context.
- CLI arguments: --year
- Key functions: parse_args, as_int, as_float, read_context, first_row, song_label, album_label, safe_list, gather_signals, derive_year_identity, +15 more
- Files it reads: issues/context/{year}_context.json
- Files it writes: issues/plans/{year}_narrative_plan.json; issues/plans/{year}_narrative_plan.md

### `scripts/generate_year_range.py`

- Script name: `generate_year_range.py`
- Purpose: Generate RetroVerse issues across a year range with failure-tolerant orchestration.
- CLI arguments: --start-year, --end-year
- Key functions: parse_args, read_json, load_year_warehouse_map, check_required_inputs, check_optional_coverage, parse_articles_generated, parse_supervisor_warnings, run_supervisor_for_year, now_timestamp, summary_notes, +4 more
- Files it reads: Warehouse movies_by_year.json; Warehouse television_by_year.json; issues/context/{year}_context.json; issues/plans/{year}_narrative_plan.json
- Files it writes: artifacts/logs/year_generation_log.json; artifacts/logs/year_generation_summary.md

### `scripts/index_artwork.py`

- Script name: `index_artwork.py`
- Purpose: Index RetroVerse artwork and maintain reusable art-library metadata.
- CLI arguments: --year, --no-promote, --asset, --prompt, --category, --source-issue, --year-created
- Key functions: project_root, load_json, ensure_art_library, load_art_index, save_art_index, slugify, tokenize_prompt, tags_from_prompt, parse_year_from_text, folder_to_category, +15 more
- Files it reads: art-library/art_index.json; issues/{year}/art/image_prompts.json; issues/{year}/data/issue.json; issues/{year}/art/**/*.png
- Files it writes: art-library/art_index.json; Promoted reusable assets under art-library/

### `scripts/ingest_imdb_datasets.py`

- Script name: `ingest_imdb_datasets.py`
- Purpose: Download, parse, and apply IMDb bulk dataset enrichment to screen/culture warehouse.
- CLI arguments: --force-download, --force-decompress
- Key functions: parse_args, ensure_directories, download_file, decompress_file, as_int, as_float, parse_genres, medium_from_imdb_type, load_master, build_record_indexes, +12 more
- Files it reads: IMDb TSV downloads under /Users/bobhopp/Sites/retroverse/raw-data/imdb; Warehouse movies_master.json; Warehouse television_master.json
- Files it writes: Reference imdb_enrichment.json; Updated warehouse movies_master.json; Updated warehouse television_master.json; Updated warehouse movies_by_year.json; Updated warehouse television_by_year.json; Updated warehouse screen_culture_inventory.json; Updated warehouse screen_culture.db

### `scripts/magazine_pipeline.py`

- Script name: `magazine_pipeline.py`
- Purpose: Shared helpers and CLI entrypoint for the canonical RetroVerse magazine build pipeline.
- CLI arguments: --year, --overwrite-art
- Key functions: issue_year_dir, final_year_dir, issue_markdown_path, load_json, load_json_if_exists, load_text_if_exists, slugify, template_key_for_section, template_path_for_section, assert_canonical_templates_exist, +40 more
- Files it reads: issues/{year}/*.md; issues/{year}/articles/final/*.md; issues/{year}/data/editorial.json; issues/{year}/chart_top23.md; issues/{year}/art/**/*.png; templates/sections/*.html
- Files it writes: Rendered HTML/PDF strings to callers; when used via CLI it writes issues/{year}/layout/*.html and final PDF-related output through caller scripts

### `scripts/print_daily_refresh_instructions.py`

- Script name: `print_daily_refresh_instructions.py`
- Purpose: Print suggested macOS instructions for daily data inventory refresh.
- CLI arguments: none
- Key functions: main
- Files it reads: scripts/update_data_inventory.py path
- Files it writes: stdout only

### `scripts/run_art_director.py`

- Script name: `run_art_director.py`
- Purpose: Build RetroVerse art direction outputs from context, plans, and writer drafts.
- CLI arguments: --year
- Key functions: parse_args, read_json, unique_list, parse_project_state, infer_story_medium, story_role_from_signals, target_map, needs_illustration, choose_dependency, supporting_assets, +21 more
- Files it reads: PROJECT_STATE.md; issues/context/{year}_context.json; issues/plans/{year}_narrative_plan.json; issues/{year}/articles/*.json
- Files it writes: issues/{year}/layout/{year}_issue_map.json; issues/{year}/layout/{year}_issue_map.md; issues/{year}/layout/{year}_production_targets.json

### `scripts/run_staff_writers.py`

- Script name: `run_staff_writers.py`
- Purpose: Assign staff writers and generate structured story drafts from the narrative plan.
- CLI arguments: --year
- Key functions: parse_args, read_json, normalize_role_to_beat, build_writer_voice, build_writer_data_focus, parse_project_state, get_source_basis, lookup_path, summarize_value, infer_story_medium, +8 more
- Files it reads: PROJECT_STATE.md; Warehouse movies_by_year.json; Warehouse television_by_year.json; Warehouse screen_culture_inventory.json; issues/plans/{year}_narrative_plan.json; issues/context/{year}_context.json
- Files it writes: issues/{year}/articles/*.json; issues/{year}/articles/*.md

### `scripts/screen_culture_common.py`

- Script name: `screen_culture_common.py`
- Purpose: Shared helpers for screen/culture warehouse build and audits.
- CLI arguments: none
- Key functions: now_utc_iso, ensure_screen_culture_dirs, read_json, write_json, parse_year, as_int, as_float, normalize_title, tokens, canonical_key, +26 more
- Files it reads: data/DATA_SOURCES.yaml; issues/*/data/movies.json; issues/*/data/tv.json; Warehouse JSON/CSV/DB paths resolved from the data source map
- Files it writes: Generic helper output only: caller-supplied JSON/SQLite targets

### `scripts/update_data_inventory.py`

- Script name: `update_data_inventory.py`
- Purpose: Rebuild DATA_INVENTORY.md from the RetroVerse project filesystem.
- CLI arguments: --write, --stdout
- Key functions: parse_args, parse_scalar, parse_simple_yaml, load_data_sources, is_glob_pattern, resolve_path, expand_path, relative_to_scan_root, iter_project_files, detect_file_type, +10 more
- Files it reads: Project filesystem scan; data/DATA_SOURCES.yaml
- Files it writes: DATA_INVENTORY.md when --write is used; stdout when --stdout is used

## 3. ILLUSTRATION PIPELINE FLOW

The current canonical illustration flow is split across prompt production, prompt-to-job mapping, image generation, and mirrored file output.

1. Prompt manifest generation
The canonical prompt stage is `pipeline/illustration_prompt_stage.py`. It reads the page brief manifest, page brief JSON files, page-level art direction JSON, and `issues/{year}/art_direction/page_assignments.json`. It writes one prompt text file per page under `issues/{year}/art/prompts/` and a consolidated manifest at `issues/{year}/art/image_prompts.json`.

2. Prompt manifest structure
`issues/1978/art/image_prompts.json` currently has two lists:
- `prompts`: one row per page with `page_number`, `page_slug`, `prompt_path`, and `illustrator_role`
- `asset_prompts`: one row per concrete image asset with `asset_path`, `page_number`, `page_slug`, `illustrator_role`, `note`, and embedded prompt text

3. Prompt loading inside `scripts/generate_illustrations.py`
The generator loads `issues/{year}/art/image_prompts.json`, builds a prompt-path index from the `prompts` list, and then resolves each `asset_prompts` entry back to its source `.txt` prompt file. For prompt-driven page jobs, the generator reads the full text from `prompt_path` and stores that text on the image job. This is the current fix that prevents the generator from collapsing different pages into one generic default prompt.

4. Job creation
Each resolved asset becomes an `ImageJob` with:
- a typed issue-art target such as `issues/1978/art/feature/disco_floor.png`
- a canonical mirrored output such as `issues/1978/art/images/disco_floor.png`
- the full prompt text
- page metadata (`page_number`, `page_slug`)
- `job_type="page_prompt"` for prompt-driven issue assets

5. OpenAI image generation
For prompt-driven jobs, the script logs the page number and a 120-character prompt preview, bypasses library reuse, normalizes the requested size to an OpenAI-supported size, then calls `client.images.generate(model=..., prompt=..., size=...)`. The returned base64 image payload is decoded and written to disk.

6. Image caching and reuse
The canonical cache check is now the mirrored file under `issues/{year}/art/images/`. If that mirror exists and `--force` is not set, the script restores the typed asset from `art/images/` and skips regeneration. Reuse from `art-library/` is limited to `job_type="library_asset"`; prompt-driven page jobs set `allow_reuse=False` and always regenerate when forced or missing from the canonical image mirror.

7. File output
Generated or reused outputs are written twice:
- typed issue-art path: `issues/{year}/art/<category>/<filename>.png`
- canonical flattened mirror: `issues/{year}/art/images/<filename>.png`

When a new image is generated (not just reused), the script also stores a library copy under `art-library/backgrounds/`, `art-library/scenes/`, or `art-library/environments/` when the asset type matches a reusable library category.

## 4. PROMPT MAPPING

Source file summarized: `issues/1978/art/image_prompts.json`

| page_number | page_slug | prompt_path | output filename |
| --- | --- | --- | --- |
| 1 | `cover` | `issues/1978/art/prompts/page_01_cover.txt` | cover_1978.png |
| 2 | `masthead` | `issues/1978/art/prompts/page_02_masthead.txt` | none (no direct asset_prompt entry) |
| 3 | `editor_letter` | `issues/1978/art/prompts/page_03_editor_letter.txt` | department_portrait.png |
| 4 | `year_snapshot` | `issues/1978/art/prompts/page_04_year_snapshot.txt` | disco_floor.png |
| 5 | `charts_overview` | `issues/1978/art/prompts/page_05_charts_overview.txt` | none (no direct asset_prompt entry) |
| 6 | `top_song_1` | `issues/1978/art/prompts/page_06_top_song_1.txt` | none (no direct asset_prompt entry) |
| 7 | `top_song_2` | `issues/1978/art/prompts/page_07_top_song_2.txt` | none (no direct asset_prompt entry) |
| 8 | `top_song_3` | `issues/1978/art/prompts/page_08_top_song_3.txt` | none (no direct asset_prompt entry) |
| 9 | `top_song_4` | `issues/1978/art/prompts/page_09_top_song_4.txt` | none (no direct asset_prompt entry) |
| 10 | `top_song_5` | `issues/1978/art/prompts/page_10_top_song_5.txt` | none (no direct asset_prompt entry) |
| 11 | `top_song_6` | `issues/1978/art/prompts/page_11_top_song_6.txt` | none (no direct asset_prompt entry) |
| 12 | `top_song_7` | `issues/1978/art/prompts/page_12_top_song_7.txt` | none (no direct asset_prompt entry) |
| 13 | `top_song_8` | `issues/1978/art/prompts/page_13_top_song_8.txt` | none (no direct asset_prompt entry) |
| 14 | `top_song_9` | `issues/1978/art/prompts/page_14_top_song_9.txt` | none (no direct asset_prompt entry) |
| 15 | `top_song_10` | `issues/1978/art/prompts/page_15_top_song_10.txt` | none (no direct asset_prompt entry) |
| 16 | `movies` | `issues/1978/art/prompts/page_16_movies.txt` | cinema_marquee.png |
| 17 | `television` | `issues/1978/art/prompts/page_17_television.txt` | tv_livingroom.png |
| 18 | `culture` | `issues/1978/art/prompts/page_18_culture.txt` | none (no direct asset_prompt entry) |
| 19 | `arcade` | `issues/1978/art/prompts/page_19_arcade.txt` | weekend_console.png |
| 20 | `retro_ad` | `issues/1978/art/prompts/page_20_retro_ad.txt` | fake_ad_kit.png |
| 21 | `comic` | `issues/1978/art/prompts/page_21_comic.txt` | comic_panel_01.png, comic_panel_02.png, comic_panel_03.png, comic_panel_04.png, comic_panel_05.png, comic_panel_06.png |
| 22 | `puzzle` | `issues/1978/art/prompts/page_22_puzzle.txt` | trivia_grid.png |
| 23 | `letters` | `issues/1978/art/prompts/page_23_letters.txt` | none (no direct asset_prompt entry) |
| 24 | `forgotten_hit` | `issues/1978/art/prompts/page_24_forgotten_hit.txt` | none (no direct asset_prompt entry) |
| 25 | `one_hit_wonder` | `issues/1978/art/prompts/page_25_one_hit_wonder.txt` | none (no direct asset_prompt entry) |
| 26 | `album_spotlight` | `issues/1978/art/prompts/page_26_album_spotlight.txt` | none (no direct asset_prompt entry) |
| 27 | `year_timeline` | `issues/1978/art/prompts/page_27_year_timeline.txt` | none (no direct asset_prompt entry) |
| 28 | `culture_collage` | `issues/1978/art/prompts/page_28_culture_collage.txt` | collage_01.png, collage_02.png, collage_03.png, collage_04.png, collage_05.png, collage_06.png, collage_07.png, collage_08.png, collage_09.png |
| 29 | `retro_ads_page` | `issues/1978/art/prompts/page_29_retro_ads_page.txt` | none (no direct asset_prompt entry) |
| 30 | `chart_top23` | `issues/1978/art/prompts/page_30_chart_top23.txt` | none (no direct asset_prompt entry) |

Notes:
- The `prompts` list has 30 rows: one per editorial page.
- The `asset_prompts` list has 23 rows: only pages with concrete image assets are actionable by `generate_illustrations.py`.
- Pages such as `top_song_5` have a prompt file but no direct image asset row, so `--page 10` currently returns “No illustration jobs found”.

## 5. CACHE LOGIC

Current cache behavior in `scripts/generate_illustrations.py`:

- `skip`: The script skips only when the canonical mirror file already exists in `issues/{year}/art/images/` and neither `--force` nor `--overwrite` is set. In that case it restores the typed asset from the canonical mirror and prints `Restored from images cache:`.
- `reuse`: Reuse from `art-library/` happens only for `job_type="library_asset"` jobs. Prompt-driven page jobs from `image_prompts.json` are marked `job_type="page_prompt"` with `allow_reuse=False`, so they do not reuse library cache.
- `overwrite`: `--overwrite` is treated as a force-style bypass for cache checks. It disables the skip path and permits regeneration even if the canonical image mirror exists.
- `force regenerate`: `--force` does the same bypass explicitly and is the preferred flag for rebuilding prompt-driven page art. In current code `force = args.force or args.overwrite`.
- `store after generate`: When a fresh image is created, the script writes the typed asset, mirrors it into `issues/{year}/art/images/`, and optionally stores a reusable library copy for background/scene/environment asset classes.

## 6. POSSIBLE FAILURE POINTS

- Prompt/file drift: `image_prompts.json` stores both a `prompts` list and embedded prompt text inside `asset_prompts`. If the embedded prompt text and the source `.txt` file ever diverge, the generator must keep preferring `prompt_path` to avoid stale prompts.
- Missing asset mappings: many page prompt files do not map to a direct asset row. Single-page generation for those pages correctly returns no jobs, but this can surprise callers who assume every page prompt produces an image.
- Basename collisions in `art/images/`: the canonical mirror flattens paths to bare filenames. Two different asset paths with the same filename would collide in `issues/{year}/art/images/`.
- Library pollution: newly generated prompt-driven page art is still stored back into `art-library/` for some asset classes. If prompts are too generic, the library may accumulate semantically overlapping assets.
- API size mismatch: the generator normalizes unsupported sizes such as `2048x2048` to supported OpenAI sizes. If downstream layout assumptions depend on exact dimensions, the normalized aspect ratio can matter.
- External model latency/timeouts: forced regeneration depends on the OpenAI image API. A single slow request can stall the batch, which is exactly what was observed during full-force cover regeneration attempts.
- JSON mapping bugs: if `page_number` types change from integers to strings in `image_prompts.json`, the prompt index and `--page` filtering will silently stop matching unless the loader is updated.
- Legacy fallback path: if `asset_prompts` is absent entirely, the script falls back to `issues/{year}/data/issue.json` and generates generic issue targets. This is useful for older flows but is a separate behavior path from the canonical prompt-file system.

## 7. SAMPLE EXECUTION TRACE

Command simulated from the current implementation and verified against an actual run:

```bash
python3 scripts/generate_illustrations.py --year 1978 --page 4 --force
```

Step-by-step path:

1. `parse_args()` reads `--year 1978`, `--page 4`, and `--force`.
2. `main()` sets `force = True` and resolves:
- prompt manifest: `issues/1978/art/image_prompts.json`
- typed issue-art root: `issues/1978/art/`
- canonical mirror root: `issues/1978/art/images/`
3. `build_jobs(year_dir, prompts, "1978", page_filter=4)` filters `asset_prompts` to rows with `page_number == 4`.
4. `resolve_prompt_for_asset()` uses the `prompts` list to find `issues/1978/art/prompts/page_04_year_snapshot.txt` and loads the full prompt text from that file.
5. The resulting `ImageJob` contains:
- `page_number = 4`
- `page_slug = year_snapshot`
- `target = issues/1978/art/feature/disco_floor.png`
- `mirror_target = issues/1978/art/images/disco_floor.png`
- `job_type = "page_prompt"`
- `allow_reuse = False`
6. `should_skip_job(job, force=True)` returns `False`, so the generator does not skip even if the image already exists.
7. The script logs:

```text
Generating illustration for page 4 (year_snapshot)
Prompt preview: RetroVerse page art brief Target page: 1978 / year_snapshot ...
```

8. Because the job is `page_prompt`, library reuse is bypassed and `generate_with_openai()` is called with the full prompt text.
9. Returned bytes are written to `issues/1978/art/feature/disco_floor.png`.
10. `mirror_job_output()` copies that file to `issues/1978/art/images/disco_floor.png`.
11. `store_library_asset()` also stores a library copy under `art-library/scenes/` because the asset type is `scene`.
12. The actual run completed with:

```text
[ISSUE GENERATE] Generated: disco_floor.png
Illustration generation complete.
Generated: 1
Reused:    0
Skipped:   0
Failed:    0
```

That trace demonstrates the intended current behavior: prompt-file lookup, single-page filtering, forced regeneration, typed output write, and canonical mirror write under `issues/1978/art/images/`.
