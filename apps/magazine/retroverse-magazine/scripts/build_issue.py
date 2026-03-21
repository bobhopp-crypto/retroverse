#!/usr/bin/env python3
"""Build the canonical RetroVerse HTML issue from finalized article sources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from magazine_pipeline import (
    build_issue_pages,
    expand_layout_pages,
    expected_issue_page_count,
    normalize_page_numbers,
    render_combined_print_html,
    render_layout_index,
    render_layout_page,
    run_preflight_check,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the canonical RetroVerse HTML issue.")
    parser.add_argument("--year", type=int, required=True, help="Issue year to build.")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip preflight validation.")
    return parser.parse_args()


def clean_layout_output(layout_dir: Path) -> None:
    for path in layout_dir.glob("page_*.html"):
        path.unlink(missing_ok=True)
    (layout_dir / "index.html").unlink(missing_ok=True)


def main() -> int:
    args = parse_args()
    year = int(args.year)

    if not args.skip_preflight:
        status = run_preflight_check(year)
        status["year"] = year
        layout_dir = PROJECT_ROOT / "issues" / str(year) / "layout"
        layout_dir.mkdir(parents=True, exist_ok=True)
        (layout_dir / "preflight_status.json").write_text(
            json.dumps(status, indent=2), encoding="utf-8"
        )
        print("Preflight:")
        print(f"  Movies: {status['movies']}")
        print(f"  TV: {status['tv']}")
        print(f"  Layout: {status['layout']}")
        if status.get("env") == "FAIL":
            print(f"  Env: FAIL")
        if any(v == "FAIL" for v in status.values()):
            print("Preflight failed. Fix errors above or use --skip-preflight to bypass.")
            return 1

    canonical_pages = build_issue_pages(year)
    expected_pages = expected_issue_page_count(year)
    if len(canonical_pages) != expected_pages:
        raise SystemExit(
            f"Page count mismatch for {year}: generated {len(canonical_pages)} pages, expected {expected_pages}"
        )
    pages = normalize_page_numbers(expand_layout_pages(year, canonical_pages))
    print(f"Page numbering normalized: 1–{len(pages)}")

    movie_pages = [p for p in pages if p.story_id in ("movies", "movies_spread_2", "projection_booth", "movies_charts")]
    if movie_pages:
        print("Movies Section:")
        if any(p.story_id == "movies" for p in pages):
            print("  - Spread added")
        if any(p.story_id == "projection_booth" for p in pages):
            print("  - Projection Booth page added")
        if any(p.story_id == "movies_charts" for p in pages):
            print("  - Charts page added")

    layout_dir = PROJECT_ROOT / "issues" / str(year) / "layout"
    layout_dir.mkdir(parents=True, exist_ok=True)
    clean_layout_output(layout_dir)

    for page in pages:
        html = render_layout_page(page, pages, year)
        (layout_dir / page.filename).write_text(html, encoding="utf-8")

    index_html, song_range = render_layout_index(pages, year)
    (layout_dir / "index.html").write_text(index_html, encoding="utf-8")

    combined_html = render_combined_print_html(pages, year)
    (layout_dir / "combined_for_print.html").write_text(combined_html, encoding="utf-8")

    if song_range:
        print(f"Grouped Top Songs pages: {song_range}")
    print(f"Index rebuilt from {len(pages)} pages")
    print(f"Built canonical HTML issue for {year}")
    print(f"Pages: {len(canonical_pages)} canonical / {len(pages)} rendered")
    print(f"Layout index: {layout_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
