#!/usr/bin/env python3
"""Build a forensic page-by-page trace for a RetroVerse issue."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PLACEHOLDER_TERMS = (
    "placeholder",
    "reserve slot",
    "reserved canonical feature slot",
    "current editorial build",
    "replace this reserve slot",
    "production note",
    "fallback",
)

class ImageParser(HTMLParser):
    """Collect image sources from layout HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        attr_map = dict(attrs)
        src = attr_map.get("src")
        if src:
            self.sources.append(src)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a page-by-page forensic issue trace.")
    parser.add_argument("--year", type=int, default=1978, help="Issue year to trace.")
    return parser.parse_args()


def project_rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def rel_link(from_dir: Path, rel_path: str | None) -> str | None:
    if not rel_path:
        return None
    return os.path.relpath(PROJECT_ROOT / rel_path, from_dir).replace(os.sep, "/")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        output.append(item)
    return output


def normalize_rel_path(value: str | Path) -> str:
    return Path(str(value)).as_posix()


def resolve_rel(base_path: Path, relative_ref: str) -> str:
    resolved = (base_path.parent / relative_ref).resolve(strict=False)
    try:
        return project_rel(resolved)
    except ValueError:
        return normalize_rel_path(relative_ref)


def strip_markdown(text: str) -> str:
    cleaned = text.replace("\r", "")
    cleaned = re.sub(r"`([^`]*)`", r"\1", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^[>*-]\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"_([^_]+)_", r"\1", cleaned)
    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_markdown_title_and_excerpt(text: str) -> tuple[str | None, str | None]:
    if not text.strip():
        return None, None
    lines = [line.strip() for line in text.splitlines()]
    title = next((line.lstrip("# ").strip() for line in lines if line.startswith("#")), None)
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    excerpt = None
    for block in blocks:
        stripped = strip_markdown(block)
        if not stripped:
            continue
        if title and stripped == title:
            continue
        if stripped.lower().startswith("by "):
            continue
        excerpt = stripped
        break
    return title, excerpt


def excerpt_text(text: str | None, limit: int = 260) -> str:
    if not text:
        return ""
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "..."


def find_existing_thumbnail(year: int, page_number: int, page_slug: str) -> str | None:
    candidates = [
        PROJECT_ROOT / f"issues/{year}/trace/thumbnails/page_{page_number:02d}_{page_slug}.png",
        PROJECT_ROOT / f"issues/{year}/layout/thumbnails/page_{page_number:02d}_{page_slug}.png",
        PROJECT_ROOT / f"issues/{year}/layout/page_{page_number:02d}_{page_slug}.png",
        PROJECT_ROOT / f"issues/{year}/layout/page_{page_number:02d}_{page_slug}.jpg",
    ]
    for candidate in candidates:
        if candidate.exists():
            return project_rel(candidate)
    return None


def heuristic_source_candidates(year: int, page_slug: str) -> list[str]:
    year_dir = PROJECT_ROOT / f"issues/{year}"
    candidates: list[str] = []

    top_song_match = re.fullmatch(r"top_song_(\d+)", page_slug)
    if top_song_match:
        rank = int(top_song_match.group(1))
        candidates.append(project_rel(year_dir / "songs" / f"{rank:02d}.md"))

    explicit_map = {
        "cover": f"issues/{year}/cover.md",
        "masthead": f"issues/{year}/masthead.md",
        "editor_letter": f"issues/{year}/editor_letter.md",
        "year_snapshot": f"issues/{year}/data/editorial.json",
        "charts_overview": f"issues/{year}/charts_overview.md",
        "movies": f"issues/{year}/movies.md",
        "television": f"issues/{year}/television.md",
        "culture": f"issues/{year}/culture.md",
        "arcade": f"issues/{year}/arcade.md",
        "retro_ad": f"issues/{year}/ads.md",
        "comic": f"issues/{year}/comic.md",
        "puzzle": f"issues/{year}/puzzle1.md",
        "letters": f"issues/{year}/letters.md",
        "chart_top23": f"issues/{year}/chart_top23.md",
        "culture_collage": f"issues/{year}/culture.md",
        "retro_ads_page": f"issues/{year}/ads.md",
    }
    explicit = explicit_map.get(page_slug)
    if explicit:
        candidates.append(explicit)
    candidates.append(f"issues/{year}/{page_slug}.md")
    return unique_preserve_order(candidates)


def score_source_candidate(rel_path: str, year: int) -> tuple[int, int, str]:
    path = rel_path
    if path.endswith(".md") and f"issues/{year}/articles/final/" in path:
        return (0, 2, path)
    if path.endswith(".md") and f"issues/{year}/articles/" in path:
        return (1, 0, path)
    if path.endswith(".md") and f"issues/{year}/songs/" in path:
        return (1, 1, path)
    if path.endswith(".md") and path.startswith(f"issues/{year}/"):
        return (2, 0, path)
    if path.endswith(".json") and f"issues/{year}/articles/final/" in path:
        return (3, 0, path)
    if path.endswith(".json") and path.startswith(f"issues/{year}/"):
        return (4, 0, path)
    return (9, 0, path)


def detect_article_paths(
    year: int,
    page_slug: str,
    source_files: list[str],
) -> tuple[str | None, str | None]:
    final_candidates = [
        rel_path
        for rel_path in source_files
        if rel_path.startswith(f"issues/{year}/articles/final/") and rel_path.endswith(".md")
    ]
    if final_candidates:
        final_path = final_candidates[0]
        raw_path = final_path.replace(f"issues/{year}/articles/final/", f"issues/{year}/articles/")
        if (PROJECT_ROOT / raw_path).exists():
            return raw_path, final_path
        return final_path, final_path

    raw_candidates = [
        rel_path
        for rel_path in source_files
        if rel_path.startswith(f"issues/{year}/articles/") and "/final/" not in rel_path and rel_path.endswith(".md")
    ]
    if raw_candidates:
        raw_path = raw_candidates[0]
        final_path = raw_path.replace(f"issues/{year}/articles/", f"issues/{year}/articles/final/")
        if (PROJECT_ROOT / final_path).exists():
            return raw_path, final_path
        return raw_path, None

    heuristic_candidates = heuristic_source_candidates(year, page_slug)
    for rel_path in heuristic_candidates:
        if (PROJECT_ROOT / rel_path).exists():
            return rel_path, None

    usable_sources = [
        rel_path
        for rel_path in source_files
        if not is_generic_source(rel_path, year)
    ]
    if usable_sources:
        usable_sources.sort(key=lambda item: score_source_candidate(item, year))
        rel_path = usable_sources[0]
        return rel_path, None

    return None, None


def extract_article_preview(
    article_source_path: str | None,
    final_article_path: str | None,
    fallback_title: str,
    fallback_excerpt: str,
) -> tuple[str, str]:
    preferred_paths = [final_article_path, article_source_path]
    for rel_path in preferred_paths:
        if not rel_path:
            continue
        abs_path = PROJECT_ROOT / rel_path
        if not abs_path.exists():
            continue
        if abs_path.suffix.lower() == ".md":
            title, excerpt = extract_markdown_title_and_excerpt(read_text(abs_path))
            if title or excerpt:
                return title or fallback_title, excerpt_text(excerpt or fallback_excerpt)
        if abs_path.suffix.lower() == ".json":
            try:
                payload = read_json(abs_path)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                title = payload.get("title") or payload.get("page_title") or fallback_title
                excerpt_source = (
                    payload.get("story_summary")
                    or payload.get("subtitle")
                    or payload.get("summary")
                    or fallback_excerpt
                )
                return str(title), excerpt_text(str(excerpt_source))
    return fallback_title, excerpt_text(fallback_excerpt)


def format_json_block(rel_path: str | None) -> str:
    if not rel_path:
        return "Unavailable."
    abs_path = PROJECT_ROOT / rel_path
    if not abs_path.exists():
        return f"Missing file: {rel_path}"
    try:
        payload = read_json(abs_path)
    except json.JSONDecodeError:
        return read_text(abs_path)
    return json.dumps(payload, indent=2, ensure_ascii=True)


def detect_layout_images(layout_html_rel: str | None) -> tuple[list[str], str]:
    if not layout_html_rel:
        return [], ""
    html_path = PROJECT_ROOT / layout_html_rel
    html_text = read_text(html_path)
    parser = ImageParser()
    parser.feed(html_text)
    resolved = [resolve_rel(html_path, src) for src in parser.sources]
    return unique_preserve_order(resolved), html_text


def normalize_source_files(raw_source_files: list[Any]) -> list[str]:
    normalized: list[str] = []
    for value in raw_source_files:
        if not isinstance(value, str):
            continue
        normalized.append(normalize_rel_path(value))
    return unique_preserve_order(normalized)


def is_generic_source(rel_path: str, year: int) -> bool:
    if rel_path == "PROJECT_STATE.md":
        return True
    if rel_path.startswith(f"issues/context/{year}_"):
        return True
    if rel_path.endswith(f"/{year}_production_targets.json"):
        return True
    if rel_path.endswith(f"/{year}_issue_map.json"):
        return True
    return False


def build_trace(year: int) -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    year_dir = PROJECT_ROOT / f"issues/{year}"
    layout_dir = year_dir / "layout"
    trace_dir = year_dir / "trace"
    brief_manifest_path = layout_dir / "page_briefs" / f"{year}_page_briefs_manifest.json"
    prompt_manifest_path = year_dir / "art" / "image_prompts.json"

    if not brief_manifest_path.exists():
        raise FileNotFoundError(f"Missing page brief manifest: {brief_manifest_path}")

    brief_manifest = read_json(brief_manifest_path)
    prompt_manifest = read_json(prompt_manifest_path) if prompt_manifest_path.exists() else {}

    pages_by_key: dict[tuple[int, str], dict[str, Any]] = {}

    for page in brief_manifest.get("pages", []):
        page_number = int(page["page_number"])
        page_slug = str(page["page_slug"])
        key = (page_number, page_slug)
        pages_by_key[key] = {
            "page_number": page_number,
            "page_slug": page_slug,
            "brief_path": normalize_rel_path(page.get("brief_path") or ""),
        }

    for html_path in sorted(layout_dir.glob("page_*.html")):
        match = re.fullmatch(r"page_(\d+)_(.+)\.html", html_path.name)
        if not match:
            continue
        page_number = int(match.group(1))
        page_slug = match.group(2)
        key = (page_number, page_slug)
        pages_by_key.setdefault(key, {"page_number": page_number, "page_slug": page_slug})
        pages_by_key[key]["layout_html_path"] = project_rel(html_path)

    prompts_by_key: dict[tuple[int, str], str] = {}
    asset_prompts_by_key: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for entry in prompt_manifest.get("prompts", []):
        if not isinstance(entry, dict):
            continue
        try:
            key = (int(entry["page_number"]), str(entry["page_slug"]))
        except (KeyError, TypeError, ValueError):
            continue
        prompt_path = entry.get("prompt_path")
        if isinstance(prompt_path, str):
            prompts_by_key[key] = normalize_rel_path(prompt_path)
    for entry in prompt_manifest.get("asset_prompts", []):
        if not isinstance(entry, dict):
            continue
        try:
            key = (int(entry["page_number"]), str(entry["page_slug"]))
        except (KeyError, TypeError, ValueError):
            continue
        asset_prompts_by_key[key].append(entry)

    page_rows: list[dict[str, Any]] = []
    shared_image_index: dict[str, list[int]] = defaultdict(list)

    for page_number, page_slug in sorted(pages_by_key):
        key = (page_number, page_slug)
        page_row = pages_by_key[key]
        brief_rel = page_row.get("brief_path") or f"issues/{year}/layout/page_briefs/page_{page_number:02d}_{page_slug}.json"
        art_rel = f"issues/{year}/art_direction/page_{page_number:02d}_{page_slug}.json"
        layout_rel = page_row.get("layout_html_path") or f"issues/{year}/layout/page_{page_number:02d}_{page_slug}.html"
        prompt_rel = prompts_by_key.get(key) or f"issues/{year}/art/prompts/page_{page_number:02d}_{page_slug}.txt"

        brief_json = read_json(PROJECT_ROOT / brief_rel) if (PROJECT_ROOT / brief_rel).exists() else {}
        brief_title = str(brief_json.get("title") or page_slug.replace("_", " ").title())
        brief_summary = str(brief_json.get("story_summary") or "")
        source_files = normalize_source_files(brief_json.get("source_files", []))

        article_source_path, final_article_path = detect_article_paths(year, page_slug, source_files)
        article_title, article_excerpt = extract_article_preview(
            article_source_path,
            final_article_path,
            brief_title,
            brief_summary,
        )

        layout_image_paths, layout_html = detect_layout_images(layout_rel if (PROJECT_ROOT / layout_rel).exists() else None)
        prompt_asset_paths = []
        for item in asset_prompts_by_key.get(key, []):
            asset_path = item.get("asset_path")
            if isinstance(asset_path, str):
                prompt_asset_paths.append(normalize_rel_path(f"issues/{year}/art/{asset_path}"))
        prompt_asset_paths = unique_preserve_order(prompt_asset_paths)

        generated_image_paths = layout_image_paths or prompt_asset_paths
        for image_path in generated_image_paths:
            shared_image_index[image_path].append(page_number)

        final_page_thumbnail_path = find_existing_thumbnail(year, page_number, page_slug)

        placeholder_reasons: list[str] = []
        if any(any(term in image_path.lower() for term in ("placeholder", "fallback")) for image_path in generated_image_paths):
            placeholder_reasons.append("Image path contains placeholder/fallback naming.")
        lowered_layout = layout_html.lower()
        if lowered_layout and any(term in lowered_layout for term in PLACEHOLDER_TERMS):
            placeholder_reasons.append("Final page copy includes placeholder or reserve language.")

        prompt_text = read_text(PROJECT_ROOT / prompt_rel)
        if not prompt_text and asset_prompts_by_key.get(key):
            prompt_text = str(asset_prompts_by_key[key][0].get("prompt") or "")

        page_rows.append(
            {
                "page_number": page_number,
                "page_slug": page_slug,
                "article_title": article_title,
                "article_excerpt": article_excerpt,
                "article_source_path": article_source_path,
                "final_article_path": final_article_path,
                "page_brief_path": brief_rel,
                "art_direction_path": art_rel,
                "illustration_prompt_path": prompt_rel,
                "generated_image_path": generated_image_paths[0] if generated_image_paths else None,
                "generated_image_paths": generated_image_paths,
                "layout_image_paths": layout_image_paths,
                "prompt_asset_paths": prompt_asset_paths,
                "layout_html_path": layout_rel,
                "final_page_thumbnail_path": final_page_thumbnail_path,
                "page_brief_text": format_json_block(brief_rel),
                "art_direction_text": format_json_block(art_rel),
                "illustration_prompt_text": prompt_text or "Unavailable.",
                "warnings": {
                    "duplicate_images": [],
                    "missing_image": not bool(generated_image_paths),
                    "placeholder_or_fallback": placeholder_reasons,
                    "layout_prompt_mismatch": [],
                },
            }
        )

    for row in page_rows:
        layout_set = set(row["layout_image_paths"])
        prompt_set = set(row["prompt_asset_paths"])
        duplicate_warnings = []
        for image_path in row["generated_image_paths"]:
            other_pages = sorted(page for page in shared_image_index.get(image_path, []) if page != row["page_number"])
            if other_pages:
                duplicate_warnings.append(
                    {
                        "image_path": image_path,
                        "other_pages": other_pages,
                    }
                )
        row["warnings"]["duplicate_images"] = duplicate_warnings

        if layout_set and prompt_set and layout_set != prompt_set:
            only_layout = sorted(layout_set - prompt_set)
            only_prompt = sorted(prompt_set - layout_set)
            mismatch_bits = []
            if only_layout:
                mismatch_bits.append(f"layout-only: {', '.join(only_layout)}")
            if only_prompt:
                mismatch_bits.append(f"prompt-only: {', '.join(only_prompt)}")
            row["warnings"]["layout_prompt_mismatch"] = mismatch_bits

    trace_dir.mkdir(parents=True, exist_ok=True)

    duplicate_summary: dict[str, list[int]] = {
        path: pages
        for path, pages in sorted(shared_image_index.items())
        if len(set(pages)) > 1
    }
    return page_rows, duplicate_summary


def warning_badges(row: dict[str, Any]) -> str:
    badges: list[str] = []
    if row["warnings"]["duplicate_images"]:
        badges.append('<span class="badge badge-warn">Duplicate image reuse</span>')
    if row["warnings"]["missing_image"]:
        badges.append('<span class="badge badge-danger">Missing image</span>')
    if row["warnings"]["placeholder_or_fallback"]:
        badges.append('<span class="badge badge-danger">Placeholder/fallback signal</span>')
    if row["warnings"]["layout_prompt_mismatch"]:
        badges.append('<span class="badge badge-warn">Layout/prompt drift</span>')
    if not badges:
        badges.append('<span class="badge badge-ok">No image warning</span>')
    return "".join(badges)


def render_image_panel(trace_dir: Path, image_paths: list[str], duplicate_warnings: list[dict[str, Any]]) -> str:
    if not image_paths:
        return '<p class="empty">No generated image detected for this page.</p>'

    warning_lookup = {item["image_path"]: item["other_pages"] for item in duplicate_warnings}
    parts: list[str] = []
    for rel_path in image_paths:
        link = rel_link(trace_dir, rel_path) or "#"
        duplicate_note = ""
        if rel_path in warning_lookup:
            duplicate_note = (
                f'<p class="warning-line">Shared with pages: '
                f'{", ".join(str(page) for page in warning_lookup[rel_path])}</p>'
            )
        parts.append(
            f"""
            <figure class="image-card">
              <a href="{escape(link)}"><img src="{escape(link)}" alt="{escape(rel_path)}" loading="lazy" /></a>
              <figcaption>{escape(rel_path)}</figcaption>
              {duplicate_note}
            </figure>
            """
        )
    return "\n".join(parts)


def render_final_page_panel(trace_dir: Path, row: dict[str, Any]) -> str:
    layout_link = rel_link(trace_dir, row["layout_html_path"]) or "#"
    thumb_link = rel_link(trace_dir, row["final_page_thumbnail_path"]) if row["final_page_thumbnail_path"] else None
    if thumb_link:
        preview = (
            f'<a href="{escape(layout_link)}"><img class="page-thumb" src="{escape(thumb_link)}" '
            f'alt="Page {row["page_number"]:02d} thumbnail" loading="lazy" /></a>'
        )
    else:
        preview = (
            f'<iframe class="page-frame" src="{escape(layout_link)}" '
            f'title="Page {row["page_number"]:02d} preview" loading="lazy"></iframe>'
        )
    thumb_text = row["final_page_thumbnail_path"] or "No static page thumbnail detected."
    return (
        f"{preview}"
        f'<p class="path-line"><a href="{escape(layout_link)}">{escape(row["layout_html_path"])}</a></p>'
        f'<p class="meta-line">{escape(thumb_text)}</p>'
    )


def render_warnings(row: dict[str, Any]) -> str:
    lines: list[str] = []
    for item in row["warnings"]["duplicate_images"]:
        pages = ", ".join(str(page) for page in item["other_pages"])
        lines.append(f"Duplicate image {item['image_path']} also appears on pages {pages}.")
    if row["warnings"]["missing_image"]:
        lines.append("No generated image path was detected in layout HTML or prompt assets.")
    for reason in row["warnings"]["placeholder_or_fallback"]:
        lines.append(reason)
    for reason in row["warnings"]["layout_prompt_mismatch"]:
        lines.append(f"Layout/prompt mismatch: {reason}")
    if not lines:
        lines.append("No automated warning on this page.")
    return "".join(f"<li>{escape(line)}</li>" for line in lines)


def build_html(year: int, rows: list[dict[str, Any]], duplicate_summary: dict[str, list[int]]) -> str:
    trace_dir = PROJECT_ROOT / f"issues/{year}/trace"
    duplicate_count = sum(len(row["warnings"]["duplicate_images"]) for row in rows)
    missing_count = sum(1 for row in rows if row["warnings"]["missing_image"])
    placeholder_count = sum(1 for row in rows if row["warnings"]["placeholder_or_fallback"])

    repeated_images_html = "".join(
        f"<li><code>{escape(path)}</code> -> pages {escape(', '.join(str(page) for page in pages))}</li>"
        for path, pages in duplicate_summary.items()
    ) or "<li>No duplicate generated image paths detected.</li>"

    page_sections: list[str] = []
    for row in rows:
        article_source_link = rel_link(trace_dir, row["article_source_path"]) if row["article_source_path"] else None
        final_article_link = rel_link(trace_dir, row["final_article_path"]) if row["final_article_path"] else None
        page_sections.append(
            f"""
            <section class="page-trace" id="page-{row['page_number']:02d}">
              <header class="page-header">
                <div>
                  <p class="eyebrow">Page {row['page_number']:02d}</p>
                  <h2>{escape(row['page_slug'])}</h2>
                </div>
                <div class="badge-row">{warning_badges(row)}</div>
              </header>
              <div class="trace-grid">
                <section class="panel">
                  <h3>A. Article</h3>
                  <p class="article-title">{escape(row['article_title'])}</p>
                  <p>{escape(row['article_excerpt'] or 'No article excerpt available.')}</p>
                  <p class="path-line">
                    Source:
                    {f'<a href="{escape(article_source_link)}">{escape(row["article_source_path"])}</a>' if article_source_link else escape(row["article_source_path"] or "Unavailable.")}
                  </p>
                  <p class="path-line">
                    Final:
                    {f'<a href="{escape(final_article_link)}">{escape(row["final_article_path"])}</a>' if final_article_link else escape(row["final_article_path"] or "Unavailable.")}
                  </p>
                </section>
                <section class="panel">
                  <h3>B. Page Brief</h3>
                  <pre>{escape(row['page_brief_text'])}</pre>
                </section>
                <section class="panel">
                  <h3>C. Art Direction</h3>
                  <pre>{escape(row['art_direction_text'])}</pre>
                </section>
                <section class="panel">
                  <h3>D. Illustration Prompt</h3>
                  <pre>{escape(row['illustration_prompt_text'])}</pre>
                </section>
                <section class="panel">
                  <h3>E. Generated Image</h3>
                  <div class="image-grid">{render_image_panel(trace_dir, row['generated_image_paths'], row['warnings']['duplicate_images'])}</div>
                </section>
                <section class="panel">
                  <h3>F. Final Page</h3>
                  {render_final_page_panel(trace_dir, row)}
                </section>
                <section class="panel">
                  <h3>G. Notes</h3>
                  <ul class="warning-list">{render_warnings(row)}</ul>
                  <textarea placeholder="Manual review notes"></textarea>
                </section>
              </div>
            </section>
            """
        )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>RetroVerse {year} Issue Trace</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f3ede2;
      --paper: #fffaf2;
      --ink: #1e1b18;
      --muted: #6a6055;
      --line: #d3c5ac;
      --accent: #a23b23;
      --warn: #9a6a00;
      --ok: #0c6a45;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(162,59,35,0.12), transparent 24rem),
        linear-gradient(180deg, #efe3cb 0%, var(--bg) 100%);
    }}
    a {{ color: var(--accent); }}
    .shell {{
      width: min(96vw, 1800px);
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}
    .hero {{
      background: rgba(255, 250, 242, 0.92);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 1.5rem;
      box-shadow: 0 18px 60px rgba(30, 27, 24, 0.08);
    }}
    .hero h1 {{
      margin: 0 0 0.4rem;
      font-size: clamp(2rem, 3vw, 3.4rem);
      line-height: 1.05;
    }}
    .hero p {{
      margin: 0.35rem 0;
      color: var(--muted);
      max-width: 72rem;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.8rem;
      margin-top: 1.25rem;
    }}
    .summary-card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.9rem 1rem;
    }}
    .summary-card strong {{
      display: block;
      font-size: 1.4rem;
      margin-top: 0.2rem;
    }}
    .repeated-images {{
      margin-top: 1.4rem;
      padding: 1rem 1.2rem;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255,255,255,0.64);
    }}
    .repeated-images ul {{
      margin: 0.5rem 0 0;
      padding-left: 1.2rem;
    }}
    .page-trace {{
      margin-top: 1.4rem;
      background: rgba(255, 250, 242, 0.95);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 1rem;
      box-shadow: 0 14px 40px rgba(30, 27, 24, 0.06);
    }}
    .page-header {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: flex-start;
      margin-bottom: 1rem;
    }}
    .page-header h2 {{
      margin: 0.15rem 0 0;
      font-size: 1.6rem;
    }}
    .eyebrow {{
      margin: 0;
      text-transform: uppercase;
      font-size: 0.76rem;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .badge-row {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 0.28rem 0.7rem;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      border: 1px solid currentColor;
      background: rgba(255,255,255,0.72);
    }}
    .badge-ok {{ color: var(--ok); }}
    .badge-warn {{ color: var(--warn); }}
    .badge-danger {{ color: var(--accent); }}
    .trace-grid {{
      display: grid;
      grid-template-columns: repeat(7, minmax(300px, 1fr));
      gap: 0.9rem;
      overflow-x: auto;
      padding-bottom: 0.25rem;
    }}
    .panel {{
      min-height: 300px;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.9rem;
    }}
    .panel h3 {{
      margin: 0 0 0.75rem;
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
    }}
    .article-title {{
      margin: 0 0 0.5rem;
      font-size: 1.15rem;
      font-weight: 700;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.76rem;
      line-height: 1.45;
      color: #2d2924;
    }}
    .path-line, .meta-line {{
      margin: 0.5rem 0 0;
      font-size: 0.82rem;
      color: var(--muted);
      word-break: break-word;
    }}
    .image-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 0.75rem;
    }}
    .image-card {{
      margin: 0;
      border: 1px solid var(--line);
      border-radius: 12px;
      overflow: hidden;
      background: #f8f2e8;
    }}
    .image-card img {{
      display: block;
      width: 100%;
      height: 150px;
      object-fit: cover;
      background: #e8dcc9;
    }}
    .image-card figcaption {{
      padding: 0.55rem 0.6rem 0.15rem;
      font-size: 0.74rem;
      color: var(--muted);
      word-break: break-word;
    }}
    .warning-line {{
      margin: 0;
      padding: 0 0.6rem 0.55rem;
      color: var(--accent);
      font-size: 0.72rem;
    }}
    .page-frame {{
      width: 100%;
      height: 360px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fff;
    }}
    .page-thumb {{
      display: block;
      width: 100%;
      max-height: 360px;
      object-fit: contain;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fff;
    }}
    .warning-list {{
      margin: 0 0 0.8rem;
      padding-left: 1.1rem;
    }}
    .warning-list li {{
      margin-bottom: 0.45rem;
      font-size: 0.88rem;
    }}
    textarea {{
      width: 100%;
      min-height: 180px;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.8rem;
      resize: vertical;
      font: inherit;
      background: #fffdf8;
    }}
    .empty {{
      color: var(--muted);
      font-style: italic;
    }}
    @media (max-width: 900px) {{
      .page-header {{
        flex-direction: column;
      }}
      .badge-row {{
        justify-content: flex-start;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h1>RetroVerse {year} Forensic Issue Trace</h1>
      <p>Static inspection surface for page-by-page drift review. This trace compares article sources, page briefs, art direction, prompts, rendered images, and final layout outputs without changing issue generation behavior.</p>
      <p>Generated at {escape(generated_at)}. Manifest: <a href="trace_manifest.json">trace_manifest.json</a></p>
      <div class="summary-grid">
        <article class="summary-card"><span>Pages traced</span><strong>{len(rows)}</strong></article>
        <article class="summary-card"><span>Duplicate image warnings</span><strong>{duplicate_count}</strong></article>
        <article class="summary-card"><span>Missing image warnings</span><strong>{missing_count}</strong></article>
        <article class="summary-card"><span>Placeholder/fallback signals</span><strong>{placeholder_count}</strong></article>
      </div>
      <section class="repeated-images">
        <h2>Shared Generated Images</h2>
        <ul>{repeated_images_html}</ul>
      </section>
    </section>
    {''.join(page_sections)}
  </main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    year = args.year
    rows, duplicate_summary = build_trace(year)

    trace_dir = PROJECT_ROOT / f"issues/{year}/trace"
    trace_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = trace_dir / "trace_manifest.json"
    html_path = trace_dir / "index.html"

    manifest_pages = []
    for row in rows:
        manifest_pages.append(
            {
                key: value
                for key, value in row.items()
                if key
                not in {
                    "page_brief_text",
                    "art_direction_text",
                    "illustration_prompt_text",
                }
            }
        )

    manifest = {
        "year": year,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "page_count": len(rows),
        "duplicate_image_paths": duplicate_summary,
        "pages": manifest_pages,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    html_path.write_text(build_html(year, rows, duplicate_summary), encoding="utf-8")

    duplicate_count = sum(len(row["warnings"]["duplicate_images"]) for row in rows)
    missing_count = sum(1 for row in rows if row["warnings"]["missing_image"])

    print(f"Trace HTML: {project_rel(html_path)}")
    print(f"Trace manifest: {project_rel(manifest_path)}")
    print(f"Pages traced: {len(rows)}")
    print(f"Duplicate image warnings: {duplicate_count}")
    print(f"Missing image warnings: {missing_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
