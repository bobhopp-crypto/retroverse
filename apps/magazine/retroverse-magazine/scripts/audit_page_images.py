#!/usr/bin/env python3
"""Audit page-image usage across a RetroVerse issue layout."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
ISSUES_DIR = PROJECT_ROOT / "issues"
IMG_SRC_RE = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit page-image usage for a RetroVerse issue.")
    parser.add_argument("--year", type=int, required=True, help="Issue year to audit")
    return parser.parse_args()


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def load_page_images(year: int) -> dict[Path, dict[str, Any]]:
    pages_dir = ISSUES_DIR / str(year) / "art" / "pages"
    if not pages_dir.exists():
        raise FileNotFoundError(f"Missing page image directory: {pages_dir}")

    images: dict[Path, dict[str, Any]] = {}
    for path in sorted(pages_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        images[path.resolve()] = {
            "image_file": path.name,
            "image_path": rel(path),
            "page_files": [],
            "raw_reference_count": 0,
            "page_reference_counts": {},
        }
    return images


def scan_layout_usage(year: int, images: dict[Path, dict[str, Any]]) -> None:
    layout_dir = ISSUES_DIR / str(year) / "layout"
    if not layout_dir.exists():
        raise FileNotFoundError(f"Missing layout directory: {layout_dir}")

    for html_path in sorted(layout_dir.glob("page_*.html")):
        html = html_path.read_text(encoding="utf-8")
        local_counts: dict[Path, int] = {}

        for raw_src in IMG_SRC_RE.findall(html):
            clean_src = raw_src.split("?", 1)[0].split("#", 1)[0]
            resolved = (html_path.parent / clean_src).resolve(strict=False)
            if resolved not in images:
                continue
            local_counts[resolved] = local_counts.get(resolved, 0) + 1

        for image_path, count in local_counts.items():
            row = images[image_path]
            row["page_files"].append(html_path.name)
            row["raw_reference_count"] += count
            row["page_reference_counts"][html_path.name] = count


def build_payload(year: int, images: dict[Path, dict[str, Any]]) -> dict[str, Any]:
    rows = []
    duplicates = []
    total_page_references = 0
    total_raw_references = 0

    for row in sorted(images.values(), key=lambda item: item["image_file"]):
        page_files = sorted(row["page_files"])
        page_reference_counts = row["page_reference_counts"]
        total_page_references += len(page_files)
        total_raw_references += int(row["raw_reference_count"])

        payload_row = {
            "image_file": row["image_file"],
            "image_path": row["image_path"],
            "page_files": page_files,
            "page_count": len(page_files),
            "raw_reference_count": int(row["raw_reference_count"]),
            "page_reference_counts": {name: page_reference_counts[name] for name in sorted(page_reference_counts)},
        }
        rows.append(payload_row)

        if len(page_files) > 1:
            duplicates.append(payload_row)

    return {
        "year": year,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "image_directory": rel(ISSUES_DIR / str(year) / "art" / "pages"),
        "layout_directory": rel(ISSUES_DIR / str(year) / "layout"),
        "total_image_files": len(rows),
        "total_page_references": total_page_references,
        "total_raw_img_references": total_raw_references,
        "images": rows,
        "duplicate_image_warnings": duplicates,
    }


def render_report(payload: dict[str, Any]) -> str:
    year = int(payload["year"])
    lines = [
        f"# Image Uniqueness Report {year}",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        f"TOTAL IMAGE FILES: {payload['total_image_files']}",
        f"TOTAL PAGE REFERENCES: {payload['total_page_references']}",
        "",
        "## IMAGE USAGE",
        "",
    ]

    for row in payload["images"]:
        lines.append(f"`{row['image_file']}`")
        lines.append("used by:")
        if row["page_files"]:
            for page_file in row["page_files"]:
                count = row["page_reference_counts"].get(page_file, 0)
                if count > 1:
                    lines.append(f"- `{page_file}` ({count} img tags)")
                else:
                    lines.append(f"- `{page_file}`")
        else:
            lines.append("- none")
        lines.append("")

    lines.extend(["## DUPLICATE IMAGE WARNINGS", ""])
    if payload["duplicate_image_warnings"]:
        for row in payload["duplicate_image_warnings"]:
            lines.append(f"`{row['image_file']}` is used by more than one page:")
            for page_file in row["page_files"]:
                lines.append(f"- `{page_file}`")
            lines.append("")
    else:
        lines.append("No images are referenced by more than one page.")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    year = int(args.year)

    images = load_page_images(year)
    scan_layout_usage(year, images)
    payload = build_payload(year, images)

    qa_dir = ISSUES_DIR / str(year) / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = qa_dir / "image_usage.json"
    report_path = DOCS_DIR / f"image_uniqueness_report_{year}.md"

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")

    print(f"Image usage JSON: {json_path}")
    print(f"Image uniqueness report: {report_path}")
    print(f"Total image files: {payload['total_image_files']}")
    print(f"Total page references: {payload['total_page_references']}")
    print(f"Duplicate image warnings: {len(payload['duplicate_image_warnings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
