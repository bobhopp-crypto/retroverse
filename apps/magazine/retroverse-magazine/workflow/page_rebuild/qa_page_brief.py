#!/usr/bin/env python3
"""QA gate for the generated page brief."""

from __future__ import annotations

import sys

from common import build_parser
from common import load_json
from common import normalize_for_check
from common import output_path
from common import qa_report_markdown
from common import write_text


def main() -> None:
    parser = build_parser("QA the single-page brief.")
    args = parser.parse_args()

    brief_path = output_path(args.year, args.page_slug, "page_brief.json")
    report_path = output_path(args.year, args.page_slug, "page_brief_QA.md")
    brief = load_json(brief_path)

    zone_ids = {zone["id"] for zone in brief.get("text_safe_zones", [])}
    roles = [block.get("role", "") for block in brief.get("text_blocks", [])]
    forbidden = {normalize_for_check(item) for item in brief.get("must_not_render_in_art", [])}
    required_forbidden = {
        normalize_for_check("article body text"),
        normalize_for_check("charts/tables"),
        normalize_for_check("exact production typography"),
    }

    checks = [
        {
            "label": "Title exists",
            "passed": bool(str(brief.get("title", "")).strip()),
            "detail": f"title={brief.get('title', '')!r}",
        },
        {
            "label": "Story summary exists",
            "passed": bool(str(brief.get("story_summary", "")).strip()),
            "detail": "Story summary is populated." if brief.get("story_summary") else "Story summary is missing.",
        },
        {
            "label": "Verified facts present",
            "passed": len(brief.get("verified_facts", [])) >= 4,
            "detail": f"{len(brief.get('verified_facts', []))} verified facts found.",
        },
        {
            "label": "Text-safe zones defined",
            "passed": {"title_zone", "body_zone", "sidebar_zone"}.issubset(zone_ids),
            "detail": f"Zones found: {', '.join(sorted(zone_ids))}",
        },
        {
            "label": "Art direction defined",
            "passed": bool(brief.get("art_direction")) and bool(brief["art_direction"].get("concept")),
            "detail": brief.get("art_direction", {}).get("concept", "Missing art direction concept."),
        },
        {
            "label": "Forbidden art text list is complete",
            "passed": required_forbidden.issubset(forbidden),
            "detail": ", ".join(brief.get("must_not_render_in_art", [])),
        },
        {
            "label": "Written page text exists before art",
            "passed": {"title", "subtitle", "byline", "body"}.issubset(set(roles)),
            "detail": f"Text roles found: {', '.join(roles)}",
        },
        {
            "label": "Brief is handoff-complete",
            "passed": bool(brief.get("page_purpose")) and bool(brief.get("sidebar_blocks")) and bool(brief.get("layout_requirements")),
            "detail": (
                f"page_purpose={bool(brief.get('page_purpose'))}, "
                f"sidebar_blocks={len(brief.get('sidebar_blocks', []))}, "
                f"layout_requirements={bool(brief.get('layout_requirements'))}"
            ),
        },
    ]

    notes = [
        "This QA gate blocks art direction if the story-first handoff is incomplete.",
        "Required text-safe zones are title, body, and sidebar.",
        "Forbidden art text must explicitly cover article body text, charts/tables, and exact production typography.",
    ]

    report = qa_report_markdown("1978 Movies Page Brief QA", f"{args.year}/{args.page_slug}", checks, notes)
    write_text(report_path, report)

    if not all(check["passed"] for check in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
