#!/usr/bin/env python3
"""QA gate for the mock page layout."""

from __future__ import annotations

import sys

from common import BODY_LAYOUT_METRICS
from common import SIDEBAR_LAYOUT_METRICS
from common import build_parser
from common import estimate_text_capacity
from common import load_json
from common import load_text
from common import output_path
from common import qa_report_markdown
from common import zone_lookup
from common import write_text


def main() -> None:
    parser = build_parser("QA the mock page layout.")
    args = parser.parse_args()

    brief = load_json(output_path(args.year, args.page_slug, "page_brief.json"))
    html = load_text(output_path(args.year, args.page_slug, "mock_page.html"))
    report_path = output_path(args.year, args.page_slug, "layout_QA.md")

    zones = zone_lookup(brief["text_safe_zones"])
    title = brief["title"]
    subtitle = brief["subtitle"]
    byline = brief["writer"]["byline"]
    body_text = " ".join(block["content"] for block in brief["text_blocks"] if block["role"] == "body")
    sidebar_text = " ".join(
        f"{block['title']} " + " ".join(f"{item['label']} {item['value']}" for item in block["items"])
        for block in brief["sidebar_blocks"]
    )

    body_capacity = estimate_text_capacity(zones["body_zone"], metrics=BODY_LAYOUT_METRICS)
    sidebar_capacity = estimate_text_capacity(zones["sidebar_zone"], metrics=SIDEBAR_LAYOUT_METRICS)

    checks = [
        {
            "label": "Title is visible",
            "passed": f"<h1 class=\"page-title\">{title}</h1>" in html and subtitle in html and byline in html,
            "detail": f"Expected title={title!r}, subtitle={subtitle!r}, byline={byline!r}.",
        },
        {
            "label": "Body text is readable",
            "passed": "data-zone=\"body_zone\"" in html and len(body_text) <= int(body_capacity * 0.97),
            "detail": f"body_chars={len(body_text)} body_capacity={body_capacity}",
        },
        {
            "label": "Sidebar exists",
            "passed": "<aside class=\"overlay sidebar-zone\" data-zone=\"sidebar_zone\">" in html and "Verified Facts" in html,
            "detail": "Sidebar/stat box container found.",
        },
        {
            "label": "Layout matches intended page structure",
            "passed": all(token in html for token in ["data-zone=\"title_zone\"", "data-zone=\"body_zone\"", "data-zone=\"sidebar_zone\"", "data-zone=\"footer_zone\""]),
            "detail": "All overlay zones are present in the mock HTML.",
        },
        {
            "label": "No overflow is detected",
            "passed": len(sidebar_text) <= int(sidebar_capacity * 0.97),
            "detail": f"sidebar_chars={len(sidebar_text)} sidebar_capacity={sidebar_capacity}",
        },
        {
            "label": "Page reads as a complete editorial page",
            "passed": "Artwork Placeholder" in html and "Page 16" in html and "Screen Feature" in html,
            "detail": "Mock page includes art slot, header framing, and page number.",
        },
    ]

    notes = [
        "Overflow is estimated from safe-zone geometry and the fixed mock-page typography metrics.",
        "The mock page intentionally keeps the illustration as a placeholder layer so real text is overlaid after art approval.",
    ]
    report = qa_report_markdown("1978 Movies Layout QA", f"{args.year}/{args.page_slug}", checks, notes)
    write_text(report_path, report)

    if not all(check["passed"] for check in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
