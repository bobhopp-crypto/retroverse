# RetroVerse 1978 Press Check

Date: March 12, 2026

## Pipeline Status

Command run:

```bash
python3 scripts/magazine_pipeline.py --year 1978
```

Result: completed successfully with exit code 0.

Generated outputs found:

- `issues/1978/layout/index.html`
- `output/RetroVerse_1978.pdf`

## Page Count

- Layout index reports 14 designed HTML pages.
- Rendered PDF produces 35 physical pages.
- Conclusion: the PDF is not honoring the intended one-layout-page-per-print-page structure; significant vertical overflow/page splitting is occurring.

## Masthead Verification

Expected cover masthead:

```text
RetroVerse
Press ▶ Play for the Past
```

Expected interior header:

```text
RetroVerse • 1978
```

Observed result:

- HTML pages render a masthead block with `RetroVerse` plus a subtitle in the form `1978 | <page type>`.
- The required subtitle `Press ▶ Play for the Past` does not appear.
- The required interior header `RetroVerse • 1978` does not appear.
- PDF text extraction shows the visible masthead rendering as uppercase `RETROVERSE`, not the required canonical form.

Occurrence counts found during inspection:

- `RETROVERSE`: 28 occurrences in extracted PDF text
- `RetroVerse`: 13 occurrences in extracted PDF text
- `Retroverse`: 0 occurrences
- `Press ▶ Play for the Past`: 0 occurrences
- `RetroVerse • 1978`: 0 occurrences

Status: fail

## Image Rendering Verification

What is working:

- Generated HTML uses real `<img>` tags for the illustrated pages that exist.
- Cover art loads from `issues/1978/art/cover/cover_1978.png`.
- Feature art loads from `issues/1978/art/feature/*.png`.
- Department art loads from `issues/1978/art/departments/department_portrait.png`.
- Sampled PDF pages show images rendering as images, not as raw path text.

What is missing:

- No generated layout pages reference `issues/1978/art/collage/`.
- No generated layout pages reference `issues/1978/art/comic/`.
- No generated layout pages reference `issues/1978/art/fake_ads/` or `issues/1978/art/parody/`.
- Therefore collage, comic, and ad-style illustrated page types are not present in the generated issue even though source art files exist.

Pages without any `<img>` tag in layout HTML:

- `page_08_story_006.html`
- `page_12_story_010.html`
- `page_14_story_012.html`

Status: partial pass

## Page Structure Verification

Actual generated issue structure is a 14-page story package:

- cover
- cover-led opener continuation
- single-page profile
- single-page narrative
- two single-page infographics
- two-page spread
- two timeline spreads
- two screen feature spreads
- modular sidebar
- multi-card set

Required sections requested for the press check but not present as generated pages:

- masthead page
- editor letter
- charts overview
- top songs (10 pages)
- letters
- ads
- comic
- arcade
- puzzles
- chart_top23

Required sections with only partial/approximate coverage:

- movies: present via `Screen-Year Pulse: Grease`
- television: present via `Television in the Room: Laverne & Shirley`
- culture: loosely represented by `The Week-by-Week Yearline`, but not as a clearly labeled dedicated culture section

Status: fail

## Chart Page Verification

Expected: a RetroVerse Top 23 page with columns for rank, song title, artist, weeks, peak, and score, containing exactly 23 entries.

Observed result:

- No `chart_top23` page exists in `issues/1978/layout/`.
- No `Top 23` page appears in extracted PDF text.
- No table/header set matching `rank`, `song title`, `artist`, `weeks`, `peak`, and `score` appears as a dedicated chart page.
- Exactly 23 entries cannot be verified because the required page is absent.

Status: fail

## Easter Egg Rule Verification

File checked:

- `issues/1978/art/image_prompts.json`

Observed result:

- The prompts describe cover, feature, collage, comic, and parody art directions.
- No prompt includes an instruction to hide the word `RetroVerse` as a subtle Easter egg.

Status: fail

## PDF Output Verification

Observed in the generated PDF:

- Masthead renders incorrectly for press-check purposes. The visible masthead is `RETROVERSE`, not the required `RetroVerse` plus `Press ▶ Play for the Past`.
- Images do render on sampled illustrated pages.
- Page breaks are incorrect. The 14-page HTML issue expands into 35 PDF pages, with multiple designed pages spilling into extra print pages.
- Several spill pages contain only continuation text and large empty areas, which indicates print pagination/layout overflow rather than intentional extra pages.
- No obvious horizontal margin clipping was seen in sampled pages, but the vertical overflow makes the PDF unsuitable as a clean final issue.

Status: fail

## Layout Issues Found

- Canonical masthead text is not used.
- Interior header `RetroVerse • 1978` is missing.
- PDF masthead appears as `RETROVERSE`.
- 14 designed pages turn into 35 PDF pages.
- Required sections for a complete illustrated issue are missing.
- Collage, comic, ad/parody, arcade, puzzles, letters, and Top 23 chart pages are not generated.
- Existing collage/comic/parody art assets are not wired into layout pages.
- `image_prompts.json` does not include the required hidden-`RetroVerse` Easter egg instruction.

## Recommended Fixes

- Restore the canonical masthead strings for cover and interior pages.
- Generate the missing required sections, especially masthead, editor letter, charts overview, letters, ads, comic, arcade, puzzles, and `chart_top23`.
- Ensure the Top Songs package expands to the required 10 pages and add a dedicated RetroVerse Top 23 page with 23 entries.
- Wire collage/comic/parody/ad assets into actual layout pages instead of leaving those art sets unused.
- Adjust print CSS/layout constraints so each designed HTML page maps cleanly to one PDF page without spillover.
- Add the hidden `RetroVerse` Easter egg instruction to the applicable image prompts.
