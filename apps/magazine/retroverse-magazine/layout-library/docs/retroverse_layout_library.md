# RetroVerse Layout Library

## RetroVerse Page Philosophy
RetroVerse pages are designed as magazine architecture, not web articles. Every page should feel printed, paced, and intentionally composed for a 9x12 frame. The reader should sense editorial curation in each spread through headline scale, illustration cadence, sidebars, and artifact callouts.

The visual voice is a hybrid:
- Late-1970s cultural magazine seriousness
- MAD-style rhythm shifts and visual surprise
- Comic-book energy in framing and sequencing
- Hand-drawn editorial illustration sensibility

A good RetroVerse page balances three forces:
1. Readability: text blocks remain legible and paced.
2. Personality: each section has a distinct voice.
3. Graphic momentum: no two consecutive pages feel mechanically identical.

## Why Page Templates Matter
Templates prevent the issue generator from collapsing into one generic article layout. A template library allows the system to:
- Match page structure to editorial intent.
- Keep production predictable while preserving visual variation.
- Reuse known block patterns for faster generation and QA.
- Preserve brand identity across years without repeating one rigid frame.

Templates also make automation practical. The builder can map content blocks into predefined layout zones rather than inventing page composition from scratch each run.

## How the Issue Generator Should Choose Templates
Template choice should be rule-driven, not random. Recommended decision process:
1. Identify page purpose from the issue plan (cover, feature, department, chart, parody, etc.).
2. Evaluate visual density target for current page sequence.
3. Pick template that best fits content priority (image-led, text-led, data-led, panel-led).
4. Check required blocks are available in page JSON.
5. Apply alternation rule so adjacent pages do not share near-identical density and structure.

Selection hints:
- Use image-led templates after dense text pages.
- Use data page templates where chart interpretation is central.
- Use comic/parody templates to reset pacing mid-issue.
- Reserve high-impact templates for opener, mid-issue pivot, and finish.

## How Illustrations, Artifacts, Sidebars, and Text Blocks Interact
RetroVerse pages should layer content types rather than stack only paragraphs.

Interaction model:
- **Illustrations** anchor emotion and period texture.
- **Artifacts** (ticket stubs, ad snippets, ephemera) provide cultural evidence.
- **Sidebars** deliver context, quick facts, or alternate voice.
- **Body text** carries narrative argument and reporting.

Composition rules:
- Every page must have one dominant block (headline, hero image, chart, or panel row).
- Secondary blocks should support the dominant block, not compete with it.
- Sidebars should add utility, not repeat body text.
- Artifact tiles should be concise and image-adjacent whenever possible.
- Captions must do interpretive work, not only describe what is visible.

## Staying Varied While Remaining Consistent
Consistency comes from systems. Variety comes from controlled rotation.

Consistent elements:
- Masthead treatment
- Page number and footer nav placement
- Typography families and rule lines
- Cream-paper canvas and print-like borders

Varied elements:
- Column count
- Image scale
- Block ordering
- Sidebar treatment
- Presence of collage, comic panels, data tables, or parody frames

Do not repeat the same layout archetype more than twice in a short run unless the editorial purpose explicitly demands it.

## RetroVerse Page Archetypes

### 1. Cover Page
- **Purpose:** Establish issue identity, tone, and cultural hook at a glance.
- **Visual structure:** Dominant hero art, large masthead, selective cover lines, minimal clutter.
- **Text-to-image ratio:** 20/80.
- **Ideal use case:** Issue open with strongest visual statement and year signal.

### 2. Contents Page
- **Purpose:** Navigation and editorial framing of issue structure.
- **Visual structure:** Department list column plus collage/imagery panel; contributor box.
- **Text-to-image ratio:** 45/55.
- **Ideal use case:** Immediately after cover to orient reader and set rhythm.

### 3. Feature Spread
- **Purpose:** Deliver lead story with depth and visual drama.
- **Visual structure:** Hero image, multicolumn body copy, pull quote, supporting sidebar/inset.
- **Text-to-image ratio:** 60/40.
- **Ideal use case:** Signature reporting or central cultural argument.

### 4. Department Column
- **Purpose:** Recurring voice page for columnist-driven perspective.
- **Visual structure:** Portrait/spot illustration, byline priority, two text columns, compact sidebar.
- **Text-to-image ratio:** 70/30.
- **Ideal use case:** Advice, culture notes, recurring critic/columnist sections.

### 5. Illustration Grid / Collage
- **Purpose:** Fast visual scan of artifacts, moments, and references.
- **Visual structure:** 6 to 9 modular tiles mixing images, captions, and fact snippets.
- **Text-to-image ratio:** 35/65.
- **Ideal use case:** Scene-setting pages, trend snapshots, montage transitions.

### 6. Data / Charts Page
- **Purpose:** Quantify momentum and compare signals in one glance.
- **Visual structure:** Intro paragraph, chart/table block, notes sidebar, tight captioning.
- **Text-to-image ratio:** 55/45.
- **Ideal use case:** Music chart movement, release tallies, trend comparisons.

### 7. Visual Parody Page
- **Purpose:** Inject satire and tonal reset while staying period-authentic.
- **Visual structure:** One dominant faux ad/parody image with supporting caption block.
- **Text-to-image ratio:** 25/75.
- **Ideal use case:** Mid-issue energy shift or cultural critique through humor.

### 8. Narrative Comic Page
- **Purpose:** Tell cultural commentary through panel progression.
- **Visual structure:** Panel rows, dialogue/caption blocks, strong gutters and framing.
- **Text-to-image ratio:** 40/60.
- **Ideal use case:** Story beats that benefit from sequential pacing and character voice.

### 9. Back Page
- **Purpose:** Deliver memorable exit beat (poster, puzzle, gag, or final thought).
- **Visual structure:** Strong single visual with minimal supporting text.
- **Text-to-image ratio:** 15/85.
- **Ideal use case:** Issue close with collectible feel and strong final impression.

## How the Issue Builder Should Use This Library
1. Read issue plan.
2. Choose page templates.
3. Populate blocks from issue JSON.
4. Render HTML pages.
5. Export preview.

Implementation note: the builder should validate required blocks per template before rendering and fall back to the nearest compatible template when content is incomplete.
