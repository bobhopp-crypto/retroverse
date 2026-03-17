#!/usr/bin/env python3
"""Build the canonical RetroVerse HTML issue from finalized article sources."""

from __future__ import annotations

import argparse
from pathlib import Path

from magazine_pipeline import build_issue_pages, expected_issue_page_count, render_layout_index, render_layout_page


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the canonical RetroVerse HTML issue.")
    parser.add_argument("--year", type=int, required=True, help="Issue year to build.")
    return parser.parse_args()


def clean_layout_output(layout_dir: Path) -> None:
    for path in layout_dir.glob("page_*.html"):
        path.unlink(missing_ok=True)
    (layout_dir / "index.html").unlink(missing_ok=True)


def main() -> int:
    args = parse_args()
    year = int(args.year)

    pages = build_issue_pages(year)
    expected_pages = expected_issue_page_count(year)
    if len(pages) != expected_pages:
        raise SystemExit(
            f"Page count mismatch for {year}: generated {len(pages)} pages, expected {expected_pages}"
        )

    layout_dir = PROJECT_ROOT / "issues" / str(year) / "layout"
    layout_dir.mkdir(parents=True, exist_ok=True)
    clean_layout_output(layout_dir)

    for page in pages:
        html = render_layout_page(page, pages, year)
        (layout_dir / page.filename).write_text(html, encoding="utf-8")

    index_html = render_layout_index(pages, year)
    (layout_dir / "index.html").write_text(index_html, encoding="utf-8")

    print(f"Built canonical HTML issue for {year}")
    print(f"Pages: {len(pages)}")
    print(f"Layout index: {layout_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
