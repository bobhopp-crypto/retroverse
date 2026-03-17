# RetroVerse Art Department Build Audit

Date: March 15, 2026
Project root: `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine`
Web app root: `/Users/bobhopp/Sites/retroverse/apps/web`

## Summary

The current RetroVerse codebase has an active magazine illustration pipeline and an active web app, but it does not yet have a dedicated Art Department feature wired end to end.

The key pieces already present are:

- an active Vite/React web app in `apps/web`
- a working local ComfyUI instance at `http://127.0.0.1:8188`
- an existing ComfyUI workflow template in `workflow/retroverse_comfyui_page_workflow.json`
- reusable illustration generation code in `scripts/generate_illustrations.py`
- existing issue-level sample art in `issues/{year}/art/*`
- existing illustration logs in `logs/illustration_runs.log`

The key missing pieces are:

- no dedicated art department route or page in the web app
- no canonical artist registry for art-department staff
- no dedicated artist portrait/reference generation scripts
- no current portrait/reference asset structure under `public/art-department/`
- no current app data source for artist profiles

## 1. RetroVerse Art Department App Status

Status: not yet implemented as a dedicated feature.

Current web app findings:

- The active frontend is the Vite app rooted at `apps/web` via `/Users/bobhopp/Sites/retroverse/vite.config.ts`.
- Current routes in `/Users/bobhopp/Sites/retroverse/apps/web/src/App.tsx` include `/magazine`, `/magazine/:year`, `/artist/:name`, and other site tools.
- There is no existing `/art-department` or `/art-director` route.
- There is no existing art-department-specific page, profile page, card grid, or artist recommendation page in `apps/web/src`.

Current magazine UI findings:

- `/Users/bobhopp/Sites/retroverse/apps/web/src/pages/magazine/MagazineArchivePage.tsx` is an issue index.
- `/Users/bobhopp/Sites/retroverse/apps/web/src/pages/magazine/MagazineReaderPage.tsx` is a spread reader for magazine issues.
- `/Users/bobhopp/Sites/retroverse/apps/web/src/data/magazineIssues.ts` is static issue content and currently points at `/images/...` assets.

Conclusion:

- The correct integration target is the existing `apps/web` frontend.
- The Art Department feature needs to be added as an additive extension rather than a rewrite.

## 2. Artist Data Files Status

Status: no dedicated artist registry found.

Search results:

- No existing `retroverse_artists.json` file is present in the magazine project.
- No dedicated art-department artist registry with fields like `display_name`, `public_credit`, `style_traits`, `self_portrait_prompt`, or `reference_scene_prompts` was found in the RetroVerse repo.
- The nearest related concept is the illustration-studio role system documented in `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/PROJECT_STATE.md`.

Current related source:

- `PROJECT_STATE.md` defines five canonical illustration roles:
  - `COVER_ARTIST`
  - `EDITORIAL_SCENE_ARTIST`
  - `INFOGRAPHIC_ARTIST`
  - `COMIC_ARTIST`
  - `SPOT_ARTIST`

Conclusion:

- There is no existing canonical artist registry in usable profile form.
- A new canonical registry is required at `data/retroverse_artists.json`.

## 3. Current Portraits or Sample Works

Status: existing issue art exists, but not artist-profile assets.

Existing sample art folders:

- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues/1978/art/cover`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues/1978/art/feature`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues/1978/art/departments`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues/1978/art/comic`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues/1978/art/collage`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues/1978/art/fake_ads`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues/1978/art/parody`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues/1978/art/images`

Representative file checks:

- `issues/1978/art/departments/department_portrait.png` is a real `1024 x 1024` PNG.
- `issues/1978/art/feature/cinema_marquee.png` is a real `1024 x 1024` PNG.
- `issues/1978/art/pages/page_01.png` is a `1 x 1` PNG and behaves like a placeholder artifact, not a usable editorial image.

Assessment:

- The repo already contains usable issue-level sample works that show the current editorial art direction.
- There are no artist self-portraits stored in a dedicated artist/profile structure.
- There are no artist reference galleries stored by artist id.

## 4. ComfyUI Workflow Templates

Status: present and reusable.

Available template:

- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/workflow/retroverse_comfyui_page_workflow.json`

Template characteristics:

- Loads `flux1-schnell-fp8.safetensors`
- Uses `CLIPTextEncode`
- Uses `EmptySD3LatentImage`
- Uses `KSampler`
- Uses `SaveImage`
- Default latent size is `1024 x 1024`

Operational status:

- On March 15, 2026, local ComfyUI responded successfully at `http://127.0.0.1:8188/system_stats`.
- The running local process is a long-lived `main.py --listen 127.0.0.1 --port 8188` instance.

Conclusion:

- The existing workflow template is sufficient for first-pass portrait and reference generation.
- No additional ComfyUI workflow template is strictly required for the first pass.

## 5. Illustration Generation Scripts

Status: reusable existing pipeline code is present.

Relevant scripts:

- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/generate_illustrations.py`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/generate_art_prompts.py`
- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/scripts/run_illustration_variations.py`

What already exists in `generate_illustrations.py`:

- `.env` loading
- ComfyUI base URL handling
- workflow template loading
- prompt injection into the workflow JSON
- prompt queue submission to ComfyUI
- history polling
- image download from ComfyUI
- retry/timeout-aware generation behavior
- issue-art directory creation
- logging through stdout

Current operational history:

- `logs/illustration_runs.log` shows repeated historical failures when ComfyUI was unavailable.
- The same log also shows some later successful generation entries for `department_portrait.png`.

Conclusion:

- Portrait/reference generation should reuse helper logic from `generate_illustrations.py`.
- Dedicated scripts for artist portraits and artist reference works are appropriate and low risk.

## 6. Where Generated Art Is Currently Saved

Status: current system saves issue art, not artist-profile art.

Current issue-level destinations include:

- `issues/{year}/art/cover/*.png`
- `issues/{year}/art/feature/*.png`
- `issues/{year}/art/departments/*.png`
- `issues/{year}/art/comic/*.png`
- `issues/{year}/art/collage/*.png`
- `issues/{year}/art/fake_ads/*.png`
- `issues/{year}/art/parody/*.png`
- `issues/{year}/art/pages/*.png`
- `art-library/backgrounds/*.png`
- `art-library/scenes/*.png`
- `art-library/environments/*.png`

Important note:

- These locations are tied to the editorial issue pipeline and should not be repurposed for artist-profile assets.

Conclusion:

- New artist assets should be isolated under a new `public/art-department/` structure.

## 7. Where the Web App Expects Images to Live

Status: current frontend expects public web assets under `apps/web/public`.

Evidence:

- Vite root is set to `apps/web` in `/Users/bobhopp/Sites/retroverse/vite.config.ts`.
- Existing magazine issue content points to `/images/...`, which resolves from `/Users/bobhopp/Sites/retroverse/apps/web/public/images`.
- Existing public directories include:
  - `/Users/bobhopp/Sites/retroverse/apps/web/public/data`
  - `/Users/bobhopp/Sites/retroverse/apps/web/public/images`
  - `/Users/bobhopp/Sites/retroverse/apps/web/public/magazine`

Implication for Art Department:

- Any browser-served art-department image path like `/art-department/portraits/<id>.png` must ultimately resolve from the web app public tree.
- To keep the magazine project as the canonical asset owner, the cleanest implementation is:
  - canonical source directory in the magazine project: `public/art-department/`
  - exposed in the web app public tree via a stable bridge, ideally a symlink or generated cache/sync step

## Recommended Build Direction

1. Create canonical artist data in `data/retroverse_artists.json`.
2. Create canonical artist asset directories under `public/art-department/` in the magazine project.
3. Bridge those public assets into `apps/web/public/art-department`.
4. Add a cache/export step so the web app consumes canonical artist data safely.
5. Add new app routes for:
   - `/art-department`
   - `/art-department/:artistId`
   - `/art-director`

## Audit Outcome

The repo already contains the right building blocks for a first complete Art Department pass:

- existing frontend
- existing ComfyUI renderer
- existing workflow template
- existing generation client code
- existing editorial art examples

The missing work is primarily product wiring, canonical artist data, artist-specific generation scripts, and public asset structure.
