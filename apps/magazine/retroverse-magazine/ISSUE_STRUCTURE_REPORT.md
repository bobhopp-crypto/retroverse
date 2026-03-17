# RetroVerse Issue Structure Report

## Summary

Canonical issue structure is integrated into the build pipeline.

Verified build outputs:

- `issues/1978/layout/index.html`
- `output/RetroVerse_1978.pdf`

The 1978 issue now builds as a fixed 30-page sequence and ends on `chart_top23`.

## Confirmed Page Order

1. `cover`
2. `masthead`
3. `editor_letter`
4. `year_snapshot`
5. `charts_overview`
6. `top_song_1`
7. `top_song_2`
8. `top_song_3`
9. `top_song_4`
10. `top_song_5`
11. `top_song_6`
12. `top_song_7`
13. `top_song_8`
14. `top_song_9`
15. `top_song_10`
16. `movies`
17. `television`
18. `culture`
19. `arcade`
20. `retro_ad`
21. `comic`
22. `puzzle`
23. `letters`
24. `forgotten_hit`
25. `one_hit_wonder`
26. `album_spotlight`
27. `year_timeline`
28. `culture_collage`
29. `retro_ads_page`
30. `chart_top23`

## Final Page Count

- HTML issue pages: `30`
- PDF pages: `30` according to the browser PDF build step output

## Missing Templates

None.

Required section templates now exist under `templates/sections/` for:

- `cover`
- `masthead`
- `editor_letter`
- `year_snapshot`
- `charts_overview`
- `top_song`
- `movies`
- `television`
- `culture`
- `arcade`
- `retro_ad`
- `comic`
- `puzzle`
- `letters`
- `forgotten_hit`
- `one_hit_wonder`
- `album_spotlight`
- `year_timeline`
- `culture_collage`
- `retro_ads_page`
- `chart_top23`

## Pipeline Integration Status

- `PROJECT_STATE.md` already contains the canonical `RetroVerse Issue Structure` section.
- `scripts/magazine_pipeline.py` now defines `ISSUE_STRUCTURE = [...]` as the source of truth.
- Page generation now follows that explicit order instead of assembling pages from the older story-target scan path.
- Existing issue markdown is reused where available.
- Missing content slots are generated as placeholder pages at build time instead of requiring new issue content files.
- `one_hit_wonder` currently renders as a generated placeholder page because no year-specific source copy exists for that section.
- `chart_top23` is page 30 and the generated HTML page contains `23` chart rows.

## Verification Notes

- `issues/1978/layout/index.html` lists all 30 pages in canonical order.
- `issues/1978/layout/page_01_cover.html` renders the cover masthead as `RetroVerse` with the tagline `Press ▶ Play for the Past`.
- Interior pages such as `issues/1978/layout/page_02_masthead.html` render the header as `RetroVerse • 1978`.
- Sampled generated pages including `cover`, `top_song_1`, `comic`, `culture_collage`, and `chart_top23` render artwork through `<img>` tags.
