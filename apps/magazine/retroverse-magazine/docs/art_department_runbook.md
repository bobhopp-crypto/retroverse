# RetroVerse Art Department Runbook

Date: March 15, 2026

## Working Paths

- repo root: `/Users/bobhopp/Sites/retroverse`
- magazine project root: `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine`
- web app root: `/Users/bobhopp/Sites/retroverse/apps/web`
- local ComfyUI: `http://127.0.0.1:8188`

## Commands

Launch the RetroVerse web app:

```bash
cd /Users/bobhopp/Sites/retroverse && npm run dev
```

Rebuild the public art-department cache and frontend bridge:

```bash
cd /Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine && python3 scripts/build_art_department_cache.py
```

Regenerate all illustration-staff portraits, overwriting existing files:

```bash
cd /Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine && PYTHONUNBUFFERED=1 python3 scripts/generate_artist_portraits.py --force --size 512x512
```

Regenerate all first-pass reference works, overwriting existing files:

```bash
cd /Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine && PYTHONUNBUFFERED=1 python3 scripts/generate_artist_reference_works.py --force --size 512x512
```

Regenerate one portrait for a single artist:

```bash
cd /Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine && PYTHONUNBUFFERED=1 python3 scripts/generate_artist_portraits.py --artist darla-quill --force --size 512x512
```

Regenerate two first-pass reference works for a single artist:

```bash
cd /Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine && PYTHONUNBUFFERED=1 python3 scripts/generate_artist_reference_works.py --artist darla-quill --force --size 512x512
```

## Logs

- portrait runs: `logs/art_department_portraits.log`
- reference runs: `logs/art_department_reference_works.log`
- cache builds: `logs/art_department_cache.log`
- existing issue illustration history: `logs/illustration_runs.log`
- ComfyUI service stderr: `/Users/bobhopp/AI/logs/comfyui.stderr.log`

## Current Runtime Guidance

- The existing FLUX workflow is functional, but one successful `512x512` portrait render took about `8.5` minutes on this machine.
- For the remaining portrait and reference batches, prefer an unattended or overnight run.
- The generation scripts skip existing files unless `--force` is supplied.
- Rebuild the cache after any direct registry edits if the frontend data needs to be refreshed immediately.
