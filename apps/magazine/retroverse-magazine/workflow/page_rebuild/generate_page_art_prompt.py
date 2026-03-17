#!/usr/bin/env python3
"""Generate the illustrator-facing prompt for the page-aware artwork."""

from __future__ import annotations

from common import build_parser
from common import load_json
from common import output_path
from common import write_text


def zone_line(zone: dict[str, object]) -> str:
    x = zone["x"]
    y = zone["y"]
    width = zone["width"]
    height = zone["height"]
    return (
        f"- {zone['id']}: x={x}% y={y}% width={width}% height={height}% "
        f"({zone['purpose']})"
    )


def main() -> None:
    parser = build_parser("Generate the page-art prompt.")
    args = parser.parse_args()

    art_direction = load_json(output_path(args.year, args.page_slug, "art_direction.json"))

    safe_zone_lines = "\n".join(zone_line(zone) for zone in art_direction["text_safe_zones"])

    prompt = f"""RetroVerse page art brief

Target page: {args.year} / {args.page_slug}
Page slug: {args.page_slug}
Page number: {art_direction['page_number']}
Page title to be overlaid later: {art_direction['page_title']}
Story anchor to be overlaid later: {art_direction['story_subtitle']}

Assignment:
Create a page-aware full-page editorial background for a single portrait magazine page. This is not a random insert image. The illustration is the background layer for page {art_direction['page_number']} and must support the entire page design.

Scene:
{art_direction['scene_description']}

Composition:
- {art_direction['composition_type']}
- Put the strongest narrative action in the focal scene zone on the upper/right side.
- Keep the title and body side calmer, lighter, and lower-contrast so real layout text remains readable after overlay.
- Build the image as one integrated editorial page background with atmosphere, depth, and intentional negative space.

Protected text-safe zones:
{safe_zone_lines}

Hard constraints:
- DO NOT RENDER FINAL TEXT INTO THE ARTWORK.
- Do not render readable article body text.
- Do not render chart or table text.
- Do not render fake production typography, headline typography, byline typography, or page-number typography.
- Only environmental/signage text is allowed if it is natural, minimal, and clearly secondary to the scene.
- Do not place bright poster lettering, billboard copy, or high-detail faces inside the protected safe zones.

Style:
- RetroVerse editorial illustration style: late-1970s print energy, ink-and-watercolor feel, warm paper grain, restrained halftone texture, and cinematic red/gold/teal accents.
- The page should feel designed for a magazine feature page, not like a poster, splash art, or stock cinema scene.
- Use only subtle references to Grease, Superman, and Animal House; suggest them through mood, props, silhouettes, or secondary poster cases rather than readable final production text.

Easter egg:
- Optional and subtle only: {art_direction['optional_easter_egg_guidance']}
"""

    out_path = output_path(args.year, args.page_slug, "art_prompt.txt")
    write_text(out_path, prompt)
    print(out_path)


if __name__ == "__main__":
    main()
