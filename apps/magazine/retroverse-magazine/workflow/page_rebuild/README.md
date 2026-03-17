# Single-Page Rebuild Workflow

This directory holds a controlled rebuild pipeline for one RetroVerse page at a time.

Scope for the first pass:

- Year: `1978`
- Page slug: `movies`
- Target page label: `1978 Movies of the Year`

Workflow goals:

- Writing is treated as the source of truth before any art direction work begins.
- Art direction reads the whole page brief, not a detached illustration prompt.
- Illustration is commissioned as page-aware background art for one page only.
- Final production text is never generated inside the artwork.
- Layout overlays the approved title, body copy, sidebar, and page number after art.
- Each handoff has a QA gate that can stop the pipeline.

Main scripts:

- `generate_page_brief.py`
- `qa_page_brief.py`
- `generate_art_direction.py`
- `qa_art_direction.py`
- `generate_page_art_prompt.py`
- `qa_art_prompt.py`
- `build_mock_page.py`
- `qa_layout.py`
- `rebuild_single_page.py`

Outputs are written to `workflow/page_rebuild/output/`.

Canonical issue outputs under `issues/1978/` are read as source material only and are not modified by this workflow.
