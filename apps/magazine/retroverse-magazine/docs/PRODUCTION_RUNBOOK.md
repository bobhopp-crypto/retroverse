# RetroVerse Magazine Production Runbook

**Read first:** `docs/DEFINITIVE_MAGAZINE_SYSTEM_AUDIT.md`

---

## Where to Start

1. **Project root:** `~/Sites/retroverse/apps/magazine/retroverse-magazine`
2. **Primary spec:** `PROJECT_STATE.md`
3. **Canonical pipeline:** `pipeline/run_issue_pipeline.py`

---

## Full Issue Build

```bash
cd ~/Sites/retroverse/apps/magazine/retroverse-magazine

# Full pipeline (context → narrative → articles → page briefs → art direction → prompts → illustrations → layout → QA → PDF)
python3 pipeline/run_issue_pipeline.py --year 1978

# Skip context regeneration (reuse existing)
python3 pipeline/run_issue_pipeline.py --year 1978 --skip-context

# Skip illustration generation (layout only)
python3 pipeline/run_issue_pipeline.py --year 1978 --skip-illustration

# Skip PDF (HTML only)
python3 pipeline/run_issue_pipeline.py --year 1978 --skip-pdf
```

**Outputs:** `issues/1978/layout/page_*.html`, `issues/1978/pdf/RetroVerse_1978.pdf`

---

## Layout-Only (No Regeneration)

```bash
python3 scripts/build_issue.py --year 1978
```

Rebuilds HTML from existing articles, markdown, and art. No context, narrative, or illustration generation.

---

## Single Image (OpenAI)

```bash
python3 scripts/generate_image.py "vintage disco dance floor 1978" --year 1978 --section editorial
```

**Output:** `issues/1978/art/editorial/{slug}.png`

Requires `OPENAI_API_KEY` in `.env`.

---

## Marginal Gags (OpenAI)

```bash
python3 scripts/generate_marginals.py --year 1978
```

**Output:** `issues/1978/art/marginals/marginal_01.png` … `marginal_20.png`

---

## Page-by-Page Workflow

For one page (currently hardcoded to 1978/movies):

```bash
cd workflow/page_rebuild
python3 rebuild_single_page.py
```

**Outputs:** `workflow/page_rebuild/output/1978_movies_*`

---

## Key Paths

| What | Path |
|------|------|
| Year context | `issues/context/{year}_context.json` |
| Final articles | `issues/{year}/articles/final/story_*.md` |
| Section markdown | `issues/{year}/*.md` |
| Page briefs | `issues/{year}/layout/page_briefs/page_*_*.json` |
| Art prompts | `issues/{year}/art/prompts/page_*.txt` |
| Page images | `issues/{year}/art/pages/page_*.png` |
| Layout HTML | `issues/{year}/layout/page_*.html` |
| PDF | `issues/{year}/pdf/RetroVerse_{year}.pdf` |

---

## Prerequisites

- Python 3.10+
- `pip install -r requirements.txt` (openai, python-dotenv, markdown, weasyprint)
- Node.js (for `render_browser_pdf.mjs`)
- ComfyUI (for `generate_illustrations.py`; optional if using OpenAI scripts only)
- `OPENAI_API_KEY` in `.env` (for `generate_image.py`, `generate_marginals.py`)

---

## Avoiding Drift

- Do not run `scripts/build_full_issue.py` or `scripts/build_magazine.py` (archived).
- Do not edit `archive/` contents.
- Use `pipeline/run_issue_pipeline.py` as the canonical entrypoint.
- For structural changes, consult `PROJECT_STATE.md` and `docs/DEFINITIVE_MAGAZINE_SYSTEM_AUDIT.md`.
