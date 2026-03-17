#!/usr/bin/env python3
"""QA gate for the illustration prompt."""

from __future__ import annotations

import sys

from common import build_parser
from common import load_text
from common import output_path
from common import qa_report_markdown
from common import write_text


def main() -> None:
    parser = build_parser("QA the illustration prompt.")
    args = parser.parse_args()

    prompt_path = output_path(args.year, args.page_slug, "art_prompt.txt")
    report_path = output_path(args.year, args.page_slug, "art_prompt_QA.md")
    prompt = load_text(prompt_path)
    lowered = prompt.lower()

    checks = [
        {
            "label": "Prompt is page-specific",
            "passed": f"target page: {args.year} / {args.page_slug}" in lowered and "page number: 16" in lowered and "grease" in lowered,
            "detail": "Prompt references target page, page number, and story anchor.",
        },
        {
            "label": "Prompt references exact page slug",
            "passed": f"page slug: {args.page_slug}" in lowered,
            "detail": f"Expected `page slug: {args.page_slug}`.",
        },
        {
            "label": "Safe zone instructions included",
            "passed": "protected text-safe zones" in lowered and "title_zone" in lowered and "body_zone" in lowered and "sidebar_zone" in lowered,
            "detail": "Prompt includes the protected safe-zone list.",
        },
        {
            "label": "Final production text is forbidden",
            "passed": "do not render final text into the artwork" in lowered
            and "do not render readable article body text" in lowered
            and "do not render chart or table text" in lowered
            and "do not render fake production typography" in lowered,
            "detail": "Prompt blocks article text, charts/tables, and fake typography.",
        },
        {
            "label": "RetroVerse Easter egg is optional/subtle",
            "passed": "optional and subtle only" in lowered and "retroverse" in lowered,
            "detail": "Prompt carries the optional Easter egg rule.",
        },
    ]

    notes = [
        "The illustration prompt must remain page-aware and keep the layout overlay order intact.",
        "Safe-zone coordinates are part of the prompt because the illustrator is designing for the entire page.",
    ]
    report = qa_report_markdown("1978 Movies Art Prompt QA", f"{args.year}/{args.page_slug}", checks, notes)
    write_text(report_path, report)

    if not all(check["passed"] for check in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
