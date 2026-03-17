#!/usr/bin/env python3
"""Generate art-direction handoff from the approved page brief."""

from __future__ import annotations

from common import build_parser
from common import load_json
from common import output_path
from common import write_json


def main() -> None:
    parser = build_parser("Generate the art-direction handoff.")
    args = parser.parse_args()

    brief = load_json(output_path(args.year, args.page_slug, "page_brief.json"))

    art_direction = {
        "year": args.year,
        "page_slug": args.page_slug,
        "page_number": brief["layout_requirements"]["page_number"],
        "page_title": brief["title"],
        "story_subtitle": brief["subtitle"],
        "page_purpose": brief["page_purpose"],
        "page_intent_readback": brief["art_direction"]["page_readback"],
        "composition_type": "full-page editorial background with right-heavy focal scene and protected overlay zones",
        "page_orientation": brief["layout_requirements"]["orientation"],
        "page_aware_design": True,
        "art_zone_dimensions": [
            {
                "id": "full_page_background",
                "label": "Full Page Background",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
                "unit": "percent",
                "purpose": "Artwork layer that lives behind all final layout text.",
            },
            {
                "id": "focal_scene_zone",
                "label": "Focal Scene",
                "x": 60,
                "y": 9,
                "width": 31,
                "height": 34,
                "unit": "percent",
                "purpose": "Primary theater/marquee/crowd action zone.",
            },
            {
                "id": "supporting_texture_zone",
                "label": "Supporting Texture",
                "x": 63,
                "y": 46,
                "width": 28,
                "height": 34,
                "unit": "percent",
                "purpose": "Secondary poster, ticket, sidewalk, and atmosphere detail without crowding the sidebar safe zone.",
            },
        ],
        "text_safe_zones": brief["text_safe_zones"],
        "mood": "crowded, cinematic, rain-slick, editorial, anticipatory",
        "color_palette": [
            {
                "name": "Marquee Red",
                "hex": "#b64635",
                "usage": "Hero glow and warm headline-adjacent energy.",
            },
            {
                "name": "Projector Gold",
                "hex": "#d2a34d",
                "usage": "Marquee bulbs, ticket booth warmth, reflected light.",
            },
            {
                "name": "CRT Teal",
                "hex": "#2f7e86",
                "usage": "Cool balancing accents and street-night contrast.",
            },
            {
                "name": "Newsprint Cream",
                "hex": "#efe2c6",
                "usage": "Quiet negative-space base behind overlay text.",
            },
            {
                "name": "Ink Brown",
                "hex": "#41342b",
                "usage": "Line work, shadow structure, and print texture.",
            },
        ],
        "scene_description": (
            "Design a full-page 1978 movie feature scene outside a theater at dusk or night. Grease is the emotional anchor, "
            "but the page should feel like a broader screen-year mood piece, not a single-poster tribute. Use a marquee, ticket "
            "window, queueing moviegoers, wet pavement reflections, and supporting poster-case or reel details to suggest the pull "
            "of Grease, Superman, and Animal House. Keep the upper-left and lower-left fields quieter so the real title and body "
            "copy can sit over the illustration cleanly. Use the right side for the highest contrast and the strongest narrative action."
        ),
        "visual_hierarchy": [
            "The marquee and crowd line dominate the upper-right focal scene.",
            "Ticket booth, poster cases, and reflected sidewalk light support the moviegoing story without taking over safe zones.",
            "Left-side paper tone and simpler texture stay calm for title and body overlays.",
            "Lower-right background texture supports the sidebar box but does not compete with its final text.",
        ],
        "optional_easter_egg_guidance": brief["easter_egg_rule"],
        "environmental_text_policy": (
            "Only minimal environmental/signage text is allowed if it feels natural to the scene and remains tiny, sparse, "
            "and clearly secondary. Suggested examples: a small 'Tickets' sign or tiny showtime numerals."
        ),
        "forbidden_rendering": brief["must_not_render_in_art"],
        "text_rendering_instruction": "DO NOT RENDER FINAL TEXT INTO THE ARTWORK",
    }

    out_path = output_path(args.year, args.page_slug, "art_direction.json")
    write_json(out_path, art_direction)
    print(out_path)


if __name__ == "__main__":
    main()
