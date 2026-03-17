# Placeholder Generation Fix Report

## Files Modified

- `scripts/generate_illustrations.py`

## Old Behavior

The illustration generator treated any existing page image file as completed artwork.

That created a bad loop:

1. page image missing
2. generator seeded `issues/<year>/art/pages/page_XX.png` from `assets/placeholder.png`
3. next existence check saw the file
4. generator skipped real illustration generation

Result:

- placeholder files blocked actual artwork generation

## New Behavior

Page images that match `assets/placeholder.png` are now treated as missing art.

Current behavior:

- if a real page image exists, the generator skips it unless `--force` or `--overwrite` is used
- if a page image exists but matches the placeholder image, the generator does **not** skip it
- if placeholder seeding happens during a run, the generator logs that the placeholder was detected and continues into real generation instead of counting the page as complete

## Placeholder Detection

Detection is implemented in `scripts/generate_illustrations.py` with two helpers:

- `sha256_digest(path)`
- `is_placeholder_image(path, placeholder_path, placeholder_digest=None)`

Method:

- compute SHA-256 for `assets/placeholder.png`
- compare candidate page image size and SHA-256 hash against the placeholder
- if they match exactly, the page image is treated as placeholder content

This keeps detection simple and reliable.

## Exact Test Commands Run

```bash
python3 -m py_compile scripts/generate_illustrations.py
rm -f issues/1978/art/pages/page_*.png
/bin/zsh -lc 'PYTHONUNBUFFERED=1 python3 scripts/generate_illustrations.py --year 1978'
python3 scripts/generate_illustrations.py --year 1978 --page 1
```

## Exact Test Results

### Compile Check

- `python3 -m py_compile scripts/generate_illustrations.py`
- result: passed

### Full 1978 Run After Clearing Page Images

Command:

```bash
/bin/zsh -lc 'PYTHONUNBUFFERED=1 python3 scripts/generate_illustrations.py --year 1978'
```

Observed output at the start of the run:

```text
[ISSUE GENERATE] Placeholder seed detected for page_01.png; continuing to real generation
Generating illustration for page 1 (cover)
[ISSUE GENERATE] Generating: page_01.png
```

Confirmed result:

- the generator did **not** treat the placeholder seed as completed artwork
- it proceeded into the real render path

### Existing Placeholder File Check

After the interrupted full run, `issues/1978/art/pages/page_01.png` still matched `assets/placeholder.png`.

Command:

```bash
python3 scripts/generate_illustrations.py --year 1978 --page 1
```

Observed output:

```text
[ISSUE GENERATE] Placeholder seed detected for page_01.png; continuing to real generation
Generating illustration for page 1 (cover)
[ISSUE GENERATE] Generating: page_01.png
```

Confirmed result:

- an existing placeholder page image no longer causes the generator to skip the page
- the page is treated as missing art and proceeds to generation

## External Dependency Status

Placeholder detection is fixed.

Real rendering could not be fully confirmed end-to-end during this test because the local ComfyUI render step did not complete within the observation window. The long-running render was manually interrupted after several minutes while waiting inside `generate_with_comfyui(...)`.

That means:

- placeholder handling fix: confirmed
- full image rendering completion: not confirmed in this test run because of external render timing/dependency
