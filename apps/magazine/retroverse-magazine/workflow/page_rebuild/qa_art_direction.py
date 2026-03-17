#!/usr/bin/env python3
"""QA gate for art-direction handoff."""

from __future__ import annotations

import sys

from common import build_parser
from common import load_json
from common import normalize_for_check
from common import output_path
from common import qa_report_markdown
from common import write_text


def main() -> None:
    parser = build_parser("QA the art-direction handoff.")
    args = parser.parse_args()

    brief = load_json(output_path(args.year, args.page_slug, "page_brief.json"))
    art_direction = load_json(output_path(args.year, args.page_slug, "art_direction.json"))
    report_path = output_path(args.year, args.page_slug, "art_direction_QA.md")

    safe_zones = art_direction.get("text_safe_zones", [])
    full_page_zone = next((zone for zone in art_direction.get("art_zone_dimensions", []) if zone.get("id") == "full_page_background"), None)
    normalized_scene = normalize_for_check(art_direction.get("scene_description", ""))
    required_keywords = {
        normalize_for_check("1978"),
        normalize_for_check("Grease"),
        normalize_for_check("movie"),
        normalize_for_check("theater"),
    }
    flattened_scene_tokens = set(normalized_scene.split())
    forbidden = {normalize_for_check(item) for item in art_direction.get("forbidden_rendering", [])}

    zones_reasonable = True
    for zone in safe_zones:
        zone_values = [zone.get("x", -1), zone.get("y", -1), zone.get("width", 0), zone.get("height", 0)]
        if any(value < 0 for value in zone_values[:2]) or any(value <= 0 for value in zone_values[2:]):
            zones_reasonable = False
            break
        if zone["x"] + zone["width"] > 100 or zone["y"] + zone["height"] > 100:
            zones_reasonable = False
            break

    checks = [
        {
            "label": "Art direction matches page purpose",
            "passed": art_direction.get("page_purpose") == brief.get("page_purpose")
            and all(keyword in flattened_scene_tokens for keyword in required_keywords),
            "detail": art_direction.get("scene_description", ""),
        },
        {
            "label": "Safe zones exist and are reasonable",
            "passed": len(safe_zones) >= 3 and zones_reasonable,
            "detail": f"{len(safe_zones)} safe zones found.",
        },
        {
            "label": "Composition is page-aware",
            "passed": art_direction.get("page_aware_design") is True
            and "full-page" in art_direction.get("composition_type", ""),
            "detail": art_direction.get("composition_type", ""),
        },
        {
            "label": "Artwork is designed for the whole page",
            "passed": bool(full_page_zone) and full_page_zone.get("width") == 100 and full_page_zone.get("height") == 100,
            "detail": f"full_page_background={full_page_zone!r}",
        },
        {
            "label": "Forbidden text rendering is blocked",
            "passed": normalize_for_check("article body text") in forbidden
            and normalize_for_check("charts/tables") in forbidden
            and normalize_for_check("exact production typography") in forbidden
            and art_direction.get("text_rendering_instruction") == "DO NOT RENDER FINAL TEXT INTO THE ARTWORK",
            "detail": art_direction.get("text_rendering_instruction", ""),
        },
    ]

    notes = [
        "This QA gate makes sure the illustrator receives a page-level composition brief rather than a floating insert prompt.",
        "Safe-zone geometry must remain inside the page bounds.",
        "The art-direction file must carry the explicit no-text-rendering instruction verbatim.",
    ]
    report = qa_report_markdown("1978 Movies Art Direction QA", f"{args.year}/{args.page_slug}", checks, notes)
    write_text(report_path, report)

    if not all(check["passed"] for check in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
