# Illustration Path Resolution Audit

## Scope

Audited these illustration-pipeline scripts:

- `scripts/generate_illustrations.py`
- `scripts/generate_issue_art_prompts.py`
- `pipeline/generate_issue_art_prompts.py`
- `pipeline/illustration_prompt_stage.py`

Related path helpers inspected:

- `pipeline/common.py`
- `scripts/load_visual_concepts.py`

## Summary

The live illustration pipeline is already reading from the migrated magazine app root:

- `apps/magazine/retroverse-magazine/issues`

No active code in the audited illustration scripts points to:

- `retroverse-magazine/issues`
- `retroverse/issues`

The path conflicts are historical rather than live:

- duplicate wrapper entrypoints exist for art prompt generation
- archived duplicate asset trees still exist under `archive/`
- old documentation still mentions pre-migration layouts

## Expected Canonical Root

All illustration and issue-art data should resolve from:

- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine`

Canonical issue root:

- `/Users/bobhopp/Sites/retroverse/apps/magazine/retroverse-magazine/issues`

Canonical per-year illustration paths:

- `issues/{year}/layout/page_briefs/{year}_page_briefs_manifest.json`
- `issues/{year}/layout/page_briefs/page_XX_<slug>.json`
- `issues/{year}/art_direction/page_visual_concepts_{year}.json`
- `issues/{year}/art/prompts/page_XX.txt`
- `issues/{year}/art/image_prompts.json`
- `issues/{year}/art/pages/page_XX.png`

## Actual Project Layout

Confirmed live directories:

- `apps/magazine/retroverse-magazine/issues`
- `apps/magazine/retroverse-magazine/issues/1978/art`
- `apps/magazine/retroverse-magazine/issues/1978/art/prompts`
- `apps/magazine/retroverse-magazine/issues/1978/art/pages`
- `apps/magazine/retroverse-magazine/issues/1978/art_direction`
- `apps/magazine/retroverse-magazine/issues/1978/layout/page_briefs`

Confirmed missing parallel roots:

- `/Users/bobhopp/Sites/retroverse/retroverse-magazine/issues` -> missing
- `/Users/bobhopp/Sites/retroverse/retroverse/issues` -> missing

## Script-by-Script Path Resolution

### `pipeline/illustration_prompt_stage.py`

Role:

- canonical prompt generator

Root resolution:

- `PROJECT_ROOT = Path(__file__).resolve().parents[1]`
- resolves to `apps/magazine/retroverse-magazine`

Inputs:

- page brief manifest from `pipeline.common.manifest_path(year)`
- per-page brief JSON from `PROJECT_ROOT / page["brief_path"]`
- visual concept JSON from `scripts/load_visual_concepts.py`

Outputs:

- prompt text files via `pipeline.common.art_prompt_path(year, page_number, page_slug)`
- prompt manifest via `issues/{year}/art/image_prompts.json`

Actual 1978 sample:

- brief manifest: `issues/1978/layout/page_briefs/1978_page_briefs_manifest.json`
- first brief record path: `issues/1978/layout/page_briefs/page_01_cover.json`
- prompt output: `issues/1978/art/prompts/page_01.txt`
- image output reference: `issues/1978/art/pages/page_01.png`

Status:

- correct

### `scripts/generate_issue_art_prompts.py`

Role:

- wrapper entrypoint

Behavior:

- imports and runs `pipeline.illustration_prompt_stage.main`

Filesystem behavior:

- no separate path logic

Status:

- correct but duplicative

### `pipeline/generate_issue_art_prompts.py`

Role:

- backward-compatible wrapper entrypoint

Behavior:

- imports and runs `pipeline.illustration_prompt_stage.main`

Filesystem behavior:

- no separate path logic

Status:

- correct but duplicative

### `scripts/generate_illustrations.py`

Role:

- reads prompt manifest and renders page images

Root resolution:

- `root = Path(__file__).resolve().parents[1]`
- resolves to `apps/magazine/retroverse-magazine`

Primary inputs:

- `prompts_path = root / "issues" / year / "art" / "image_prompts.json"`
- prompt text files loaded from `root / prompt_path_value`
- legacy layout image seed lookup from `year_dir / "layout" / f"page_{page_number:02d}_{page_slug}.html"`

Outputs:

- page images under `issues/{year}/art/pages`
- optional reusable assets under `art-library/...`

Actual 1978 sample:

- prompt manifest: `issues/1978/art/image_prompts.json`
- first prompt file in manifest: `issues/1978/art/prompts/page_01.txt`
- first page image target in manifest: `issues/1978/art/pages/page_01.png`

Status:

- correct today
- path logic is duplicated here rather than shared through one helper module

## Duplicate Or Conflicting Directory Structures

### Live issue roots

- `apps/magazine/retroverse-magazine/issues` -> active canonical root
- `retroverse-magazine/issues` -> does not exist
- `retroverse/issues` -> does not exist

Conclusion:

- there is only one live issue root in the current migrated repository

### Archived duplicate asset trees

- `apps/magazine/retroverse-magazine/archive/unused_assets/issues_art`
- `apps/magazine/retroverse-magazine/archive/old_runs/issues_1978_preview`

Conclusion:

- these are duplicates of older issue-art or preview structures
- they are not referenced by the audited live illustration scripts
- they are still a source of confusion when auditing the repository manually

### Duplicate script entrypoints

- `apps/magazine/retroverse-magazine/scripts/generate_issue_art_prompts.py`
- `apps/magazine/retroverse-magazine/pipeline/generate_issue_art_prompts.py`

Conclusion:

- both wrappers call the same canonical implementation
- they do not create path divergence today
- they do create entrypoint ambiguity

## Wrong Or Outdated Paths

No wrong issue-root paths were found in the audited live illustration scripts.

Outdated or confusing structures are:

- `archive/unused_assets/issues_art`
- `archive/old_runs/issues_1978_preview`
- older markdown documents that still discuss pre-migration paths

The only live script in this audit area that remains vulnerable to future drift is:

- `scripts/generate_illustrations.py`

Reason:

- it reconstructs key paths locally using `Path(__file__).resolve().parents[1]`, `year_dir.parents[1]`, and relative strings from `image_prompts.json`
- these resolve correctly today, but they are not centralized through the same helper layer used by the prompt stage

## Proposed Fix

Standardize all illustration-path resolution to one root:

- `apps/magazine/retroverse-magazine`

Concrete fix:

1. Keep `pipeline/illustration_prompt_stage.py` as the canonical prompt generator.
2. Keep `apps/magazine/retroverse-magazine/issues` as the only canonical issue root.
3. Move all illustration path construction behind shared helpers in one module.
4. Update `scripts/generate_illustrations.py` to use shared helpers for:
   - issue year root
   - `image_prompts.json`
   - `art/prompts`
   - `art/pages`
   - `art_direction/page_visual_concepts_{year}.json`
5. Treat both `generate_issue_art_prompts.py` wrappers as compatibility shims only, or retire one later.
6. Leave `archive/unused_assets/issues_art` and `archive/old_runs/...` out of active path resolution permanently.

## Recommended Minimal Standardization

Without changing editorial logic:

- add or reuse one shared helper module for issue-path construction
- remove ad hoc `root / "issues" / year / ...` assembly from `scripts/generate_illustrations.py`
- validate that any relative paths stored in `issues/{year}/art/image_prompts.json` stay under the canonical `issues/{year}/art/...` tree

## Conclusion

The migrated illustration pipeline is already reading and writing from the correct live issue root.

The real cleanup target is not a broken active path reference. It is:

- duplicate wrapper entrypoints
- archived duplicate asset trees
- duplicated path-construction logic in `scripts/generate_illustrations.py`

No editorial pipeline logic needs to change to standardize this.
