# RetroVerse Art Department Build Report

Date: March 15, 2026
Project root: `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine`
Web app root: `/Users/bobhopp/Sites/retroverse/apps/web`

## Completion Summary

Completed in this build:

- audited the current art-department state and documented the existing app, data, workflow, scripts, and asset expectations
- created a canonical staff registry at `data/retroverse_artists.json`
- added a public registry cache and frontend bridge at `public/art-department/registry.json`
- added Art Department and Art Director routes to the existing web app
- added artist directory, artist profile, and first-pass artist recommendation pages
- added three Type & Lettering specialists with placeholder type sample assets
- added portrait and reference-work operating scripts that use the existing ComfyUI integration
- validated end-to-end portrait generation with one successful local ComfyUI render

Not fully completed in this pass:

- bulk portrait generation for all 12 illustration artists
- bulk reference-work generation for all 24 first-pass reference images

## Files Created

- `docs/art_department_build_audit.md`
- `data/retroverse_artists.json`
- `public/art-department/registry.json`
- `public/art-department/type-samples/vera-kern-sample.svg`
- `public/art-department/type-samples/mitch-capstan-sample.svg`
- `public/art-department/type-samples/sonia-rubylith-sample.svg`
- `scripts/art_department_common.py`
- `scripts/build_art_department_cache.py`
- `scripts/generate_artist_portraits.py`
- `scripts/generate_artist_reference_works.py`
- `apps/web/src/components/ArtDepartmentMedia.tsx`
- `apps/web/src/lib/artDepartmentClient.ts`
- `apps/web/src/pages/magazine/ArtDepartment.css`
- `apps/web/src/pages/magazine/ArtDepartmentPage.tsx`
- `apps/web/src/pages/magazine/ArtDepartmentArtistPage.tsx`
- `apps/web/src/pages/magazine/ArtDirectorPage.tsx`

## Files Modified

- `scripts/generate_illustrations.py`
- `apps/web/src/App.tsx`
- `apps/web/src/pages/magazine/MagazineArchivePage.tsx`

## App Pages Completed

- `/art-department`
- `/art-department/:artistId`
- `/art-director`

## Asset Generation Results

Portraits generated:

- `1 / 12`
- successful verification render: `public/art-department/portraits/darla-quill.png`

Reference works generated:

- `0 / 24`

Current generated asset counts on disk:

- illustration staff portraits present: `1`
- artist reference images present: `0`
- type sample placeholders present: `3`

## Failures And Skips

Historical failures logged during setup and troubleshooting:

- two portrait attempts failed when localhost access to `http://127.0.0.1:8188` was sandbox-blocked
- two portrait attempts were interrupted at the ComfyUI `KSampler` stage during renderer/process troubleshooting

Successful verification:

- one Darla Quill portrait completed successfully through the current ComfyUI workflow

Skipped items:

- `0` existing portrait files skipped during the successful verification run
- `0` existing reference files skipped because no reference batch has been run yet

Remaining ungenerated assets after this pass:

- `11` illustration staff portraits
- `24` first-pass reference works

## Performance Notes

Observed local ComfyUI behavior on this machine:

- workflow: `workflow/retroverse_comfyui_page_workflow.json`
- model: `flux1-schnell-fp8.safetensors`
- test size: `512x512`
- one successful portrait render took about `508.92` seconds according to `comfyui.stderr.log`

That runtime is acceptable for a long-running batch but too slow to complete all remaining portrait and reference renders inside the current interactive build window.

## Verification

- `python3 scripts/build_art_department_cache.py`
- `npm run build`
- `python3 scripts/generate_artist_portraits.py --artist darla-quill --force --size 512x512`

