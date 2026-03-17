#!/usr/bin/env python3
"""Generate a visual QA index for a RetroVerse issue."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ISSUES_ROOT = PROJECT_ROOT / "issues"
ARTIFACTS_ROOT = PROJECT_ROOT / "artifacts" / "output"
PAGE_CHECK_RE = re.compile(r"^- \[(PASS|FAIL)\] Page (\d{2}) / ([^:]+): (.+)$")
OVERALL_RE = re.compile(r"Overall:\s+\*\*(PASS|FAIL)\*\*")


@dataclass(frozen=True)
class Badge:
    label: str
    kind: str
    detail: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a visual QA index for an issue.")
    parser.add_argument("--year", type=int, required=True, help="Issue year")
    return parser.parse_args()


def load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def rel_to(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def rel_href(from_dir: Path, target: Path | None) -> str | None:
    if target is None:
        return None
    return os.path.relpath(target, from_dir).replace(os.sep, "/")


def find_layout_path(year_dir: Path, page_number: int, page_slug: str) -> Path | None:
    candidate = year_dir / "layout" / f"page_{page_number:02d}_{page_slug}.html"
    if candidate.exists():
        return candidate
    matches = sorted((year_dir / "layout").glob(f"page_{page_number:02d}_*.html"))
    return matches[0] if matches else None


def parse_qa_reports(year: int) -> tuple[dict[tuple[int, str], list[dict[str, str]]], list[dict[str, str]]]:
    qa_dir = ARTIFACTS_ROOT / str(year) / "qa"
    page_failures: dict[tuple[int, str], list[dict[str, str]]] = {}
    report_summaries: list[dict[str, str]] = []

    if not qa_dir.exists():
        return page_failures, report_summaries

    for path in sorted(qa_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        overall_match = OVERALL_RE.search(text)
        overall = overall_match.group(1) if overall_match else "UNKNOWN"
        report_summaries.append({"report": path.name, "overall": overall})

        for line in text.splitlines():
            match = PAGE_CHECK_RE.match(line.strip())
            if not match:
                continue
            status, number_text, slug, detail = match.groups()
            if status == "PASS":
                continue
            key = (int(number_text), slug.strip())
            page_failures.setdefault(key, []).append(
                {
                    "report": path.name,
                    "status": status,
                    "detail": detail.strip(),
                }
            )

    return page_failures, report_summaries


def load_pages(year: int) -> list[dict[str, Any]]:
    year_dir = ISSUES_ROOT / str(year)
    trace_payload = load_json(year_dir / "trace" / "trace_manifest.json")
    pages: list[dict[str, Any]] = []

    if isinstance(trace_payload, dict) and isinstance(trace_payload.get("pages"), list):
        for page in trace_payload["pages"]:
            if isinstance(page, dict):
                pages.append(dict(page))

    if pages:
        return sorted(pages, key=lambda item: int(item.get("page_number", 0)))

    manifest_payload = load_json(year_dir / "layout" / "page_briefs" / f"{year}_page_briefs_manifest.json")
    if isinstance(manifest_payload, dict) and isinstance(manifest_payload.get("pages"), list):
        for item in manifest_payload["pages"]:
            if not isinstance(item, dict):
                continue
            page_number = int(item.get("page_number", 0))
            page_slug = str(item.get("page_slug") or "").strip()
            pages.append(
                {
                    "page_number": page_number,
                    "page_slug": page_slug,
                    "generated_image_path": f"issues/{year}/art/pages/page_{page_number:02d}.png",
                    "layout_html_path": f"issues/{year}/layout/page_{page_number:02d}_{page_slug}.html",
                    "warnings": {},
                }
            )
    return sorted(pages, key=lambda item: int(item.get("page_number", 0)))


def build_badges(
    page: dict[str, Any],
    image_exists: bool,
    layout_exists: bool,
    qa_failures: dict[tuple[int, str], list[dict[str, str]]],
) -> list[Badge]:
    badges: list[Badge] = []
    warnings = page.get("warnings", {}) if isinstance(page.get("warnings"), dict) else {}
    page_number = int(page.get("page_number", 0))
    page_slug = str(page.get("page_slug") or "").strip()

    if not image_exists:
        badges.append(Badge("image missing", "danger"))
    if not layout_exists:
        badges.append(Badge("layout missing", "danger"))

    duplicate_images = warnings.get("duplicate_images", [])
    if isinstance(duplicate_images, list) and duplicate_images:
        badges.append(Badge(f"duplicate x{len(duplicate_images)}", "warn", "; ".join(str(item) for item in duplicate_images[:3])))

    if warnings.get("missing_image") is True:
        badges.append(Badge("trace missing image", "danger"))

    placeholder_hits = warnings.get("placeholder_or_fallback", [])
    if isinstance(placeholder_hits, list) and placeholder_hits:
        badges.append(Badge(f"fallback x{len(placeholder_hits)}", "warn", "; ".join(str(item) for item in placeholder_hits[:3])))

    prompt_mismatches = warnings.get("layout_prompt_mismatch", [])
    if isinstance(prompt_mismatches, list) and prompt_mismatches:
        badges.append(Badge(f"prompt mismatch x{len(prompt_mismatches)}", "warn", "; ".join(str(item) for item in prompt_mismatches[:2])))

    for failure in qa_failures.get((page_number, page_slug), []):
        report_name = failure["report"].removesuffix(".md")
        badges.append(Badge(f"{report_name} fail", "danger", failure["detail"]))

    return badges


def build_page_rows(year: int) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    year_dir = ISSUES_ROOT / str(year)
    qa_dir = year_dir / "qa"
    pages = load_pages(year)
    qa_failures, report_summaries = parse_qa_reports(year)
    rows: list[dict[str, Any]] = []

    for page in pages:
        page_number = int(page.get("page_number", 0))
        page_slug = str(page.get("page_slug") or "").strip() or f"page_{page_number:02d}"

        generated_image_path = page.get("generated_image_path")
        image_path = PROJECT_ROOT / str(generated_image_path) if isinstance(generated_image_path, str) else year_dir / "art" / "pages" / f"page_{page_number:02d}.png"
        layout_html_value = page.get("layout_html_path")
        layout_path = PROJECT_ROOT / str(layout_html_value) if isinstance(layout_html_value, str) else find_layout_path(year_dir, page_number, page_slug)
        if layout_path is not None and not layout_path.exists():
            layout_path = find_layout_path(year_dir, page_number, page_slug)

        image_exists = image_path.exists()
        layout_exists = layout_path is not None and layout_path.exists()
        badges = build_badges(page, image_exists, layout_exists, qa_failures)

        rows.append(
            {
                "page_number": page_number,
                "page_slug": page_slug,
                "image_path": rel_to(image_path, PROJECT_ROOT) if image_exists else None,
                "layout_path": rel_to(layout_path, PROJECT_ROOT) if layout_exists and layout_path is not None else None,
                "image_href": rel_href(qa_dir, image_path) if image_exists else None,
                "layout_href": rel_href(qa_dir, layout_path) if layout_exists and layout_path is not None else None,
                "badges": [{"label": badge.label, "kind": badge.kind, "detail": badge.detail} for badge in badges],
                "trace_warnings": page.get("warnings", {}),
            }
        )

    return rows, report_summaries


def render_html(year: int, rows: list[dict[str, Any]], report_summaries: list[dict[str, str]], generated_at: str) -> str:
    total = len(rows)
    missing_images = sum(1 for row in rows if row["image_path"] is None)
    missing_layouts = sum(1 for row in rows if row["layout_path"] is None)
    warning_pages = sum(1 for row in rows if row["badges"])
    summary_html = "".join(
        f"<span class=\"summary-pill {'ok' if item['overall'] == 'PASS' else 'warn'}\">{escape(item['report'])}: {escape(item['overall'])}</span>"
        for item in report_summaries
    )

    cards: list[str] = []
    for row in rows:
        badge_html = "".join(
            f"<span class=\"badge {escape(item['kind'])}\" title=\"{escape(item['detail'])}\">{escape(item['label'])}</span>"
            for item in row["badges"]
        )
        image_html = (
            f"<a class=\"thumb-link\" href=\"{escape(row['image_href'])}\"><img loading=\"lazy\" src=\"{escape(row['image_href'])}\" alt=\"Page {row['page_number']:02d} art preview\" /></a>"
            if row["image_href"]
            else "<div class=\"missing-thumb\">Missing image</div>"
        )
        layout_link = (
            f"<a href=\"{escape(row['layout_href'])}\">Open layout</a>"
            if row["layout_href"]
            else "<span class=\"missing-link\">Layout missing</span>"
        )
        image_link = (
            f"<a href=\"{escape(row['image_href'])}\">Open image</a>"
            if row["image_href"]
            else "<span class=\"missing-link\">Image missing</span>"
        )
        cards.append(
            "<article class=\"page-card\">"
            f"<div class=\"thumb\">{image_html}</div>"
            "<div class=\"meta\">"
            f"<div class=\"page-number\">Page {row['page_number']:02d}</div>"
            f"<div class=\"page-slug\">{escape(row['page_slug'])}</div>"
            f"<div class=\"badges\">{badge_html or '<span class=\"badge ok\">no warnings</span>'}</div>"
            f"<div class=\"links\">{layout_link} <span class=\"sep\">|</span> {image_link}</div>"
            "</div>"
            "</article>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>RetroVerse {year} Visual QA Index</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4efe6;
      --paper: #fffaf2;
      --ink: #1f1c17;
      --muted: #6a6257;
      --line: #d8cdbb;
      --ok: #245d3a;
      --warn: #9a5a00;
      --danger: #a02020;
      --accent: #2f4f7a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background: linear-gradient(180deg, #efe5d6 0%, var(--bg) 100%);
      color: var(--ink);
    }}
    main {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 2rem;
    }}
    .lede {{
      margin: 0 0 18px;
      color: var(--muted);
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 0 0 20px;
    }}
    .summary-card {{
      background: rgba(255, 250, 242, 0.96);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px 16px;
    }}
    .summary-card .label {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 4px;
    }}
    .summary-card .value {{
      font-size: 1.5rem;
      font-weight: bold;
    }}
    .report-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 0 0 24px;
    }}
    .summary-pill, .badge {{
      display: inline-block;
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 0.82rem;
      border: 1px solid currentColor;
      background: rgba(255,255,255,0.75);
    }}
    .summary-pill.ok, .badge.ok {{
      color: var(--ok);
    }}
    .summary-pill.warn, .badge.warn {{
      color: var(--warn);
    }}
    .badge.danger {{
      color: var(--danger);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }}
    .page-card {{
      background: rgba(255, 250, 242, 0.97);
      border: 1px solid var(--line);
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 10px 28px rgba(44, 33, 14, 0.08);
    }}
    .thumb {{
      background: #e6dccb;
      min-height: 340px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .thumb img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}
    .thumb-link {{
      display: block;
      width: 100%;
      height: 100%;
    }}
    .missing-thumb {{
      color: var(--danger);
      font-weight: bold;
      padding: 24px;
      text-align: center;
    }}
    .meta {{
      padding: 14px 16px 16px;
    }}
    .page-number {{
      font-size: 0.9rem;
      color: var(--muted);
      margin-bottom: 4px;
    }}
    .page-slug {{
      font-size: 1.15rem;
      font-weight: bold;
      margin-bottom: 10px;
      overflow-wrap: anywhere;
    }}
    .badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 10px;
      min-height: 30px;
    }}
    .links {{
      font-size: 0.95rem;
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .missing-link {{
      color: var(--danger);
    }}
    .sep {{
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    <h1>RetroVerse {year} Visual QA Index</h1>
    <p class="lede">Generated {escape(generated_at)}. Stable visual review surface built from issue art, layout HTML, trace warnings, and QA reports.</p>
    <section class="summary">
      <div class="summary-card"><span class="label">Pages</span><span class="value">{total}</span></div>
      <div class="summary-card"><span class="label">Warning Pages</span><span class="value">{warning_pages}</span></div>
      <div class="summary-card"><span class="label">Missing Images</span><span class="value">{missing_images}</span></div>
      <div class="summary-card"><span class="label">Missing Layouts</span><span class="value">{missing_layouts}</span></div>
    </section>
    <section class="report-strip">{summary_html or '<span class="summary-pill warn">No QA reports found</span>'}</section>
    <section class="grid">
      {''.join(cards)}
    </section>
  </main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    year = int(args.year)
    qa_dir = ISSUES_ROOT / str(year) / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)

    rows, report_summaries = build_page_rows(year)
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    payload = {
        "year": year,
        "generated_at": generated_at,
        "page_count": len(rows),
        "qa_reports": report_summaries,
        "pages": rows,
    }

    json_path = qa_dir / "page_visual_index.json"
    html_path = qa_dir / "page_visual_index.html"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    html_path.write_text(render_html(year, rows, report_summaries, generated_at), encoding="utf-8")

    print(f"Visual QA JSON: {json_path}")
    print(f"Visual QA HTML: {html_path}")
    print(f"Pages indexed: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
