# RetroVerse Art Department Next Steps

Date: March 15, 2026

## Recommended Next Steps

1. Run the full portrait batch overnight for the remaining `11` illustration artists using the existing portrait script and the local ComfyUI service.
2. Run the first-pass reference batch for `24` images total using the first two prompts per illustration artist.
3. After the first two reference scenes are complete, generate the remaining three reference prompts per illustration artist to reach five reference scenes each.
4. Attach real magazine pages and issue references to `published_examples[]` for each artist so profile pages can display actual production history.
5. Expand the illustration roster from `12` starter artists to `24` while keeping the same canonical schema.
6. Add lightweight metadata filters to `/art-department` for department, era, and tone once the image inventory is populated.
7. Add export support for a PDF or print-ready staff handbook sourced from the canonical registry.
8. If batch speed remains a problem, benchmark a non-`--lowvram` ComfyUI launch profile before the next large generation pass.

## Operational Notes

- Current local FLUX throughput is slow enough that full image generation should be treated as a batch task, not an interactive quick command.
- The canonical source of truth remains `data/retroverse_artists.json`.
- The frontend should continue consuming `public/art-department/registry.json`, rebuilt from the canonical registry.

