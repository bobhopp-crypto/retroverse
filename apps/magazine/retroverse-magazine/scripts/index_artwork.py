#!/usr/bin/env python3
"""Index RetroVerse artwork and maintain reusable art-library metadata."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any


LIBRARY_CATEGORIES = (
    "characters",
    "backgrounds",
    "props",
    "textures",
    "fake_ads",
    "margin_gags",
    "misc",
)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
STOPWORDS = {
    "the",
    "and",
    "with",
    "from",
    "for",
    "into",
    "that",
    "this",
    "style",
    "illustration",
    "magazine",
    "retro",
    "cartoon",
    "hand",
    "inked",
    "lines",
    "colors",
    "satirical",
    "caricature",
    "panel",
    "image",
    "asset",
    "issue",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def ensure_art_library(root: Path) -> Path:
    library_dir = root / "art-library"
    library_dir.mkdir(parents=True, exist_ok=True)
    for category in LIBRARY_CATEGORIES:
        (library_dir / category).mkdir(parents=True, exist_ok=True)
    index_path = library_dir / "art_index.json"
    if not index_path.exists():
        index_path.write_text('{\n  "assets": []\n}\n', encoding="utf-8")
    return index_path


def load_art_index(root: Path) -> dict[str, Any]:
    index_path = ensure_art_library(root)
    payload = load_json(index_path, {"assets": []})
    if not isinstance(payload, dict):
        payload = {"assets": []}
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        payload["assets"] = []
    return payload


def save_art_index(root: Path, payload: dict[str, Any]) -> None:
    index_path = ensure_art_library(root)
    index_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "asset"


def tokenize_prompt(prompt: str) -> list[str]:
    raw = re.findall(r"[a-zA-Z0-9']+", prompt.lower())
    tokens: list[str] = []
    for token in raw:
        plain = token.strip("'")
        if not plain:
            continue
        if plain in STOPWORDS:
            continue
        if len(plain) < 3 and not plain.isdigit():
            continue
        tokens.append(plain)
    return tokens


def tags_from_prompt(prompt: str, limit: int = 8) -> list[str]:
    tags: list[str] = []
    for token in tokenize_prompt(prompt):
        if token not in tags:
            tags.append(token)
        if len(tags) >= limit:
            break
    return tags


def parse_year_from_text(value: str) -> str:
    match = re.search(r"(19\d{2}|20\d{2})", value)
    return match.group(1) if match else ""


def folder_to_category(folder: str) -> str:
    mapping = {
        "feature": "backgrounds",
        "cover": "backgrounds",
        "collage": "props",
        "comic": "margin_gags",
        "departments": "characters",
        "parody": "fake_ads",
        "characters": "characters",
        "backgrounds": "backgrounds",
        "props": "props",
        "textures": "textures",
        "fake_ads": "fake_ads",
        "margin_gags": "margin_gags",
        "misc": "misc",
    }
    return mapping.get(folder, "misc")


def infer_category(prompt: str, fallback: str = "misc") -> str:
    text = prompt.lower()
    if any(word in text for word in ("portrait", "columnist", "character", "host", "caricature")):
        return "characters"
    if "comic panel" in text or any(word in text for word in ("comic", "margin gag", "gag strip")):
        return "margin_gags"
    if any(word in text for word in ("ad ", "advert", "faux", "parody")):
        return "fake_ads"
    if any(word in text for word in ("texture", "paper grain", "ink wash")):
        return "textures"
    if any(
        word in text
        for word in (
            "background",
            "interior",
            "street",
            "city",
            "club",
            "theater",
            "marquee",
            "living room",
            "night",
        )
    ):
        return "backgrounds"
    if any(
        word in text
        for word in (
            "token",
            "ticket",
            "record",
            "radio",
            "poster",
            "package",
            "wrist stamp",
            "prop",
            "artifact",
        )
    ):
        return "props"
    return fallback if fallback in LIBRARY_CATEGORIES else "misc"


def singular_category(category: str) -> str:
    mapping = {
        "characters": "character",
        "backgrounds": "background",
        "props": "prop",
        "textures": "texture",
        "fake_ads": "fake_ad",
        "margin_gags": "margin_gag",
        "misc": "misc",
    }
    return mapping.get(category, "asset")


def style_from_prompt(prompt: str) -> str:
    text = prompt.lower()
    if "1970" in text:
        return "1970s"
    if "mad" in text:
        return "madstyle"
    if "comic" in text:
        return "comic"
    return "retro"


def build_library_filename(category: str, prompt: str, year: str) -> str:
    prompt_tags = tags_from_prompt(prompt, limit=12)
    subject_parts = [tag for tag in prompt_tags if not tag.isdigit() and tag not in {"1970s", "retro"}][:4]
    subject = "_".join(subject_parts) if subject_parts else "asset"
    style = style_from_prompt(prompt)
    year_value = year if year and year.isdigit() else parse_year_from_text(prompt) or "0000"
    return f"{singular_category(category)}_{slugify(subject)}_{slugify(style)}_{year_value}.png"


def canonical_relative(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def issue_prompt_for_asset(rel_art_path: str, prompts: dict[str, Any], year: str) -> str:
    if rel_art_path.startswith("cover/cover_"):
        return str(prompts.get("cover", ""))
    if rel_art_path.startswith("cover/back_page_"):
        return str(prompts.get("cover", ""))
    if rel_art_path.endswith("department_portrait.png"):
        return str(prompts.get("department_portrait", prompts.get("feature_hero", "")))
    if rel_art_path.endswith("cinema_marquee.png"):
        return str(prompts.get("feature_cinema", prompts.get("feature_hero", "")))
    if rel_art_path.endswith("tv_livingroom.png"):
        return str(prompts.get("feature_hero", "")) + f" {year} television living room scene"
    if rel_art_path.endswith("weekend_console.png"):
        return str(prompts.get("parody_console", ""))
    if rel_art_path.startswith("parody/"):
        return str(prompts.get("parody_console", ""))
    if rel_art_path.startswith("feature/"):
        return str(prompts.get("feature_hero", prompts.get("cover", "")))
    return str(prompts.get("feature_hero", prompts.get("cover", "")))


def build_issue_prompt_map(issue_dir: Path) -> dict[Path, str]:
    year = issue_dir.name
    art_dir = issue_dir / "art"
    prompts = load_json(art_dir / "image_prompts.json", {})
    if not isinstance(prompts, dict):
        prompts = {}

    prompt_map: dict[Path, str] = {}

    issue_payload = load_json(issue_dir / "data" / "issue.json", {})
    pages = issue_payload.get("pages", []) if isinstance(issue_payload, dict) else []
    if isinstance(pages, list):
        for page in pages:
            if not isinstance(page, dict):
                continue
            art_filename = page.get("art_filename")
            if isinstance(art_filename, str) and art_filename.strip():
                full_path = (art_dir / art_filename).resolve()
                prompt_map[full_path] = issue_prompt_for_asset(art_filename, prompts, year)

    collage_prompts = prompts.get("collage_tiles", prompts.get("collage_items", []))
    if not isinstance(collage_prompts, list):
        collage_prompts = []
    for idx in range(9):
        prompt = str(collage_prompts[idx]) if idx < len(collage_prompts) else f"{year} collage artifact"
        prompt_map[(art_dir / "collage" / f"collage_{idx + 1:02d}.png").resolve()] = prompt

    comic_prompts = prompts.get("comic_panels", [])
    if not isinstance(comic_prompts, list):
        comic_prompts = []
    panel_count = max(6, len(comic_prompts))
    for idx in range(panel_count):
        prompt = str(comic_prompts[idx]) if idx < len(comic_prompts) else f"{year} comic panel"
        prompt_map[(art_dir / "comic" / f"comic_panel_{idx + 1:02d}.png").resolve()] = prompt

    dept_prompt = str(prompts.get("department_portrait", prompts.get("feature_hero", "")))
    prompt_map[(art_dir / "departments" / "department_portrait.png").resolve()] = dept_prompt
    return prompt_map


def register_asset(
    root: Path,
    index_payload: dict[str, Any],
    asset_path: Path,
    prompt: str,
    year_created: str,
    source_issue: str,
    category_hint: str | None = None,
) -> bool:
    if not asset_path.exists() or asset_path.suffix.lower() not in IMAGE_SUFFIXES:
        return False

    assets = index_payload.setdefault("assets", [])
    if not isinstance(assets, list):
        index_payload["assets"] = []
        assets = index_payload["assets"]

    rel_file = canonical_relative(root, asset_path)
    existing = {entry.get("file") for entry in assets if isinstance(entry, dict)}
    if rel_file in existing:
        return False

    prompt_text = str(prompt or "").strip()
    fallback = folder_to_category(asset_path.parent.name)
    category = infer_category(prompt_text, category_hint or fallback)
    tags = tags_from_prompt(prompt_text)
    if not tags:
        tags = tags_from_prompt(asset_path.stem.replace("_", " "))

    entry = {
        "file": rel_file,
        "category": category,
        "prompt": prompt_text,
        "year_created": str(year_created or ""),
        "source_issue": str(source_issue or ""),
        "tags": tags,
    }
    assets.append(entry)
    return True


def jaccard_similarity(tokens_a: set[str], tokens_b: set[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return len(tokens_a & tokens_b) / len(union)


def build_library_destination(root: Path, category: str, prompt: str, year_created: str) -> Path:
    base_name = build_library_filename(category, prompt, year_created)
    dest = root / "art-library" / category / base_name
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    idx = 2
    while True:
        candidate = dest.with_name(f"{stem}_{idx}{suffix}")
        if not candidate.exists():
            return candidate
        idx += 1


def promote_reusable_assets(root: Path, index_payload: dict[str, Any]) -> int:
    assets = [entry for entry in index_payload.get("assets", []) if isinstance(entry, dict)]
    issue_assets = [
        entry
        for entry in assets
        if str(entry.get("file", "")).startswith("issues/")
        and str(entry.get("source_issue", "")) not in {"", "library"}
        and str(entry.get("prompt", "")).strip()
    ]

    by_prompt: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in issue_assets:
        signature = " ".join(tokenize_prompt(str(entry.get("prompt", ""))))
        if signature:
            by_prompt[signature].append(entry)

    candidates: set[str] = set()

    # Exact/same prompt clusters across issues (or repeated within one issue).
    for signature, entries in by_prompt.items():
        issues = {str(entry.get("source_issue", "")) for entry in entries}
        if signature and (len(issues) >= 2 or len(entries) >= 2):
            for entry in entries:
                candidates.add(str(entry.get("file", "")))

    # Similar prompt clusters (token similarity).
    for idx, left in enumerate(issue_assets):
        left_tokens = set(tokenize_prompt(str(left.get("prompt", ""))))
        for right in issue_assets[idx + 1 :]:
            if str(left.get("source_issue")) == str(right.get("source_issue")):
                continue
            right_tokens = set(tokenize_prompt(str(right.get("prompt", ""))))
            if jaccard_similarity(left_tokens, right_tokens) >= 0.7:
                candidates.add(str(left.get("file", "")))
                candidates.add(str(right.get("file", "")))

    if not candidates:
        return 0

    promoted = 0
    for entry in issue_assets:
        rel = str(entry.get("file", ""))
        if rel not in candidates:
            continue

        src = root / rel
        if not src.exists():
            continue

        prompt = str(entry.get("prompt", ""))
        category = str(entry.get("category", "misc"))
        if category not in LIBRARY_CATEGORIES:
            category = infer_category(prompt, "props")

        year_created = str(entry.get("year_created", "")) or parse_year_from_text(rel)
        dest = build_library_destination(root, category, prompt, year_created)
        shutil.copy2(src, dest)

        added = register_asset(
            root=root,
            index_payload=index_payload,
            asset_path=dest,
            prompt=prompt,
            year_created=year_created,
            source_issue=str(entry.get("source_issue", "")),
            category_hint=category,
        )
        if added:
            promoted += 1

    return promoted


def find_best_library_match(index_payload: dict[str, Any], prompt: str) -> dict[str, Any] | None:
    query_tags = set(tags_from_prompt(prompt, limit=12))
    if not query_tags:
        return None

    best_score = 0.0
    best_entry: dict[str, Any] | None = None
    for entry in index_payload.get("assets", []):
        if not isinstance(entry, dict):
            continue
        file_ref = str(entry.get("file", ""))
        if not file_ref.startswith("art-library/"):
            continue

        entry_tags = set(str(tag).lower() for tag in entry.get("tags", []) if isinstance(tag, str))
        prompt_tokens = set(tokenize_prompt(str(entry.get("prompt", ""))))

        score = 3 * len(query_tags & entry_tags) + len(query_tags & prompt_tokens)
        if score > best_score:
            best_score = score
            best_entry = entry

    return best_entry if best_score >= 3 else None


def scan_and_index(root: Path, year_filter: str | None = None, promote: bool = True) -> dict[str, int]:
    index_payload = load_art_index(root)
    before = len(index_payload.get("assets", []))
    added = 0

    issues_root = root / "issues"
    if issues_root.exists():
        for issue_dir in sorted(issues_root.iterdir()):
            if not issue_dir.is_dir() or not issue_dir.name.isdigit():
                continue
            if year_filter and issue_dir.name != str(year_filter):
                continue

            art_dir = issue_dir / "art"
            if not art_dir.exists():
                continue

            prompt_map = build_issue_prompt_map(issue_dir)
            for file_path in sorted(art_dir.rglob("*")):
                if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_SUFFIXES:
                    continue
                prompt = prompt_map.get(file_path.resolve(), "")
                if register_asset(
                    root=root,
                    index_payload=index_payload,
                    asset_path=file_path,
                    prompt=prompt,
                    year_created=issue_dir.name,
                    source_issue=issue_dir.name,
                    category_hint=folder_to_category(file_path.parent.name),
                ):
                    added += 1

    library_root = root / "art-library"
    for category in LIBRARY_CATEGORIES:
        category_dir = library_root / category
        if not category_dir.exists():
            continue
        for file_path in sorted(category_dir.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            derived_prompt = file_path.stem.replace("_", " ")
            derived_year = parse_year_from_text(file_path.name)
            if register_asset(
                root=root,
                index_payload=index_payload,
                asset_path=file_path,
                prompt=derived_prompt,
                year_created=derived_year,
                source_issue="library",
                category_hint=category,
            ):
                added += 1

    promoted = promote_reusable_assets(root, index_payload) if promote else 0
    save_art_index(root, index_payload)
    after = len(index_payload.get("assets", []))
    return {"added": added, "promoted": promoted, "total": after, "delta": after - before}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index RetroVerse artwork into art-library metadata.")
    parser.add_argument("--year", default=None, help="Optional year to scope issue scanning (example: 1978).")
    parser.add_argument("--no-promote", action="store_true", help="Skip reusable-art promotion.")
    parser.add_argument("--asset", default=None, help="Optional single asset file to register.")
    parser.add_argument("--prompt", default="", help="Prompt text used for --asset registration.")
    parser.add_argument("--category", default=None, help="Optional category hint for --asset.")
    parser.add_argument("--source-issue", default="", help="Optional source issue label for --asset.")
    parser.add_argument("--year-created", default="", help="Optional year label for --asset.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = project_root()
    ensure_art_library(root)

    if args.asset:
        asset_path = Path(args.asset)
        if not asset_path.is_absolute():
            asset_path = root / asset_path

        index_payload = load_art_index(root)
        source_issue = args.source_issue or parse_year_from_text(asset_path.as_posix()) or "manual"
        year_created = args.year_created or parse_year_from_text(asset_path.name) or parse_year_from_text(source_issue)
        added = register_asset(
            root=root,
            index_payload=index_payload,
            asset_path=asset_path,
            prompt=args.prompt,
            year_created=year_created,
            source_issue=source_issue,
            category_hint=args.category,
        )
        save_art_index(root, index_payload)
        print("Artwork indexed." if added else "Artwork already indexed or missing.")
        return 0

    stats = scan_and_index(root=root, year_filter=args.year, promote=not args.no_promote)
    print(f"Index complete. Added: {stats['added']} | Promoted: {stats['promoted']} | Total: {stats['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
