# PIPELINE REPAIR IMPLEMENTATION

## Files moved

- `issues/articles/1978/*` -> `issues/1978/articles/`
- `issues/final/1978/*` -> `issues/1978/articles/final/`
- `issues/layout/1978_issue_map.json` -> `issues/1978/layout/1978_issue_map.json`
- `issues/layout/1978_issue_map.md` -> `issues/1978/layout/1978_issue_map.md`
- `issues/layout/1978_production_targets.json` -> `issues/1978/layout/1978_production_targets.json`
- `logs/` -> `artifacts/logs/`
- `output/` -> `artifacts/output/`
- `issues/1978/preview/` -> `archive/old_runs/issues_1978_preview/`
- `archive/prototype_pipelines/` -> `archive/old_runs/prototype_pipelines/`
- `issues/art/` -> `archive/unused_assets/issues_art/`
- `scripts/build_full_issue.py` -> `archive/old_runs/deprecated_build_full_issue.py`
- `scripts/build_magazine.py` -> `archive/old_runs/deprecated_build_magazine.py`
- `issues/articles/.DS_Store` -> `archive/unused_assets/issues_articles.DS_Store`
- `issues/final/.DS_Store` -> `archive/unused_assets/issues_final.DS_Store`

## Scripts modified

- `scripts/generate_year_context.py`
- `scripts/run_staff_writers.py`
- `scripts/generate_final_articles.py`
- `scripts/run_art_director.py`
- `scripts/magazine_pipeline.py`
- `scripts/generate_illustrations.py`
- `scripts/generate_marginals.py`
- `tools/magazine_builder/build_issue.py`
- `workflow/page_rebuild/common.py`
- `workflow/page_rebuild/generate_page_brief.py`

## New pipeline structure

### Canonical entrypoint

- `pipeline/run_issue_pipeline.py`

### Shared pipeline helpers

- `pipeline/__init__.py`
- `pipeline/common.py`

### New issue-wide generation stages

- `pipeline/generate_issue_page_briefs.py`
- `pipeline/generate_issue_art_direction.py`
- `pipeline/generate_issue_art_prompts.py`

### New issue-wide QA gates

- `pipeline/qa_page_briefs.py`
- `pipeline/qa_art_direction.py`
- `pipeline/qa_art_prompts.py`
- `pipeline/qa_layout.py`
- `pipeline/qa_press_check.py`

### Canonical stage order now enforced

1. Context generation
2. Narrative planning
3. Staff writer article drafts
4. Final article production
5. Page brief generation
6. QA: page briefs
7. Issue art direction
8. Page art direction synthesis
9. QA: art direction
10. Illustration prompt generation
11. QA: art prompts
12. Illustration generation
13. Layout composition
14. QA: layout
15. Press check QA
16. PDF build

## Directories created

- `pipeline/`
- `issues/1978/articles/`
- `issues/1978/articles/final/`
- `issues/1978/charts/`
- `issues/1978/pdf/`
- `issues/1978/layout/page_briefs/`
- `issues/1978/layout/art_direction/`
- `issues/1978/art/prompts/`
- `artifacts/logs/`
- `artifacts/output/`
- `artifacts/output/1978/`
- `artifacts/output/1978/qa/`
- `archive/old_runs/`
- `archive/unused_assets/`

## Illustration rule enforcement

- Removed `"MAD magazine style"` prompting from `scripts/generate_illustrations.py` and `scripts/generate_marginals.py`
- Raised default illustration generation size to at least `2048px` width
- Added explicit no-text / no-layout prompt guardrails to generated artwork prompts
- Switched issue illustration generation to consume canonical `issues/{year}/art/image_prompts.json` asset prompts from the new full-issue prompt stage

## Canonical output paths

- Final articles now write to `issues/{year}/articles/final/`
- Issue map and production targets now write to `issues/{year}/layout/`
- Browser PDF now writes to `issues/{year}/pdf/RetroVerse_{year}.pdf`

## Verification run

### Full issue generation and QA

- `python3 pipeline/run_issue_pipeline.py --year 1978 --skip-pdf`
- Result: passed through context, narrative, drafts, final articles, page briefs, art direction, art prompts, illustration generation, layout QA, and press check QA

### Browser PDF output

- `node tools/magazine_builder/render_browser_pdf.mjs --layout-dir issues/1978/layout --output issues/1978/pdf/RetroVerse_1978.pdf`
- Result: built `issues/1978/pdf/RetroVerse_1978.pdf`

### Generated QA outputs

- `artifacts/output/1978/qa/1978_page_briefs_QA.md`
- `artifacts/output/1978/qa/1978_art_direction_QA.md`
- `artifacts/output/1978/qa/1978_art_prompt_QA.md`
- `artifacts/output/1978/qa/1978_layout_QA.md`
- `artifacts/output/1978/qa/1978_press_check_QA.md`
