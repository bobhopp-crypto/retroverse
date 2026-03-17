# 1978 Movies Art Prompt QA

Target: `1978/movies`

Overall: **PASS**

## Checks

- [PASS] Prompt is page-specific: Prompt references target page, page number, and story anchor.
- [PASS] Prompt references exact page slug: Expected `page slug: movies`.
- [PASS] Safe zone instructions included: Prompt includes the protected safe-zone list.
- [PASS] Final production text is forbidden: Prompt blocks article text, charts/tables, and fake typography.
- [PASS] RetroVerse Easter egg is optional/subtle: Prompt carries the optional Easter egg rule.

## Notes

- The illustration prompt must remain page-aware and keep the layout overlay order intact.
- Safe-zone coordinates are part of the prompt because the illustrator is designing for the entire page.
