# Canonical RetroVerse Magazine Pipeline

RetroVerse Magazine now uses a single canonical content flow:

1. Context
   - Build year context into `issues/context/{year}_context.json`

2. Planning
   - Generate issue planning and production targets
   - Canonical planning artifact: `issues/layout/{year}_production_targets.json`

3. Articles
   - Finalized editorial copy lives in `issues/final/{year}/`
   - These Markdown files are the canonical article source for issue builds

4. Art
   - Year-specific issue art lives in `issues/{year}/art/`
   - Reusable library art remains in `art-library/`

5. Layout
   - The canonical HTML issue builder is `scripts/build_issue.py`
   - It reads:
     - `issues/final/{year}/*.md`
     - `issues/layout/{year}_production_targets.json`
     - `issues/{year}/art/`
   - It writes:
     - `issues/{year}/layout/page_*.html`
     - `issues/{year}/layout/index.html`

6. Issue Build
   - The canonical PDF builder is `tools/magazine_builder/build_issue.py`
   - It reads the same finalized article and art sources as the HTML builder
   - It writes:
     - `output/RetroVerse_{year}.pdf`

## Canonical Inputs

The canonical magazine inputs are:

- `issues/final/{year}/`
- `issues/layout/{year}_production_targets.json`
- `issues/{year}/art/`

## Archived Prototype Systems

Legacy prototype systems have been moved under:

- `archive/prototype_pipelines/`

These archived assets are retained for reference only and are not part of the canonical build path.
