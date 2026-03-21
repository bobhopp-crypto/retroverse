#!/usr/bin/env python3
"""Generate RetroVerse issue illustrations with reusable art-library support."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - depends on local environment
    load_dotenv = None


def load_environment() -> None:
    if load_dotenv is None:
        print(
            "python-dotenv is not installed. Install app requirements with "
            "`pip install -r requirements.txt` or install `python-dotenv` so "
            "OPENAI_API_KEY can be loaded from .env.",
            file=sys.stderr,
        )
        return

    load_dotenv()

    script_path = Path(__file__).resolve()
    env_paths = [
        script_path.parents[1] / ".env",
        script_path.parents[4] / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)


load_environment()
PROJECT_ROOT = Path(__file__).resolve().parents[1]

OPENAI_PROMPT_PREFIX = (
    "Illustrated magazine artwork, 1970s editorial style, hand-drawn, painterly, no modern design, no typography. "
    "NO readable text in image. Leave space for layout. "
)

STYLE_SUFFIX = (
    "RetroVerse editorial illustration, late-1970s print texture, period-correct palette, scene-only artwork, "
    "hand-inked linework, atmospheric background illustration, no readable production typography"
)
DEFAULT_NEGATIVE_PROMPT = (
    "text, watermark, logo, signature, readable typography, article paragraphs, magazine headlines, "
    "page titles, pull quotes, sidebars, chart tables, magazine layout elements"
)
MAX_RETRIES = 3
LIBRARY_ART_TYPES = ["background", "scene", "environment"]
ISSUE_ART_TYPES = ["collage", "comic", "parody", "fake_ads", "marginal"]
LIBRARY_TYPE_TO_DIR = {
    "background": "backgrounds",
    "scene": "scenes",
    "environment": "environments",
}
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
    "art",
}


class IllustrationBuildError(Exception):
    """Raised when required input data is missing or invalid."""


@dataclass
class ImageJob:
    target: Path
    mirror_target: Path
    prompt: str
    note: str
    art_type: str
    job_type: str = "library_asset"
    page_number: int | None = None
    page_slug: str | None = None
    prompt_path: Path | None = None
    allow_reuse: bool = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate issue illustrations from image prompts.")
    parser.add_argument("--year", default="1978", help="Issue year to generate (default: 1978)")
    parser.add_argument("--page", type=int, help="Generate only one page number from image_prompts.json")
    parser.add_argument("--model", default="gpt-image-1", help="OpenAI image model (default: gpt-image-1)")
    parser.add_argument("--size", default="2048x2048", help="Image size (default: 2048x2048)")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate files even if they already exist")
    parser.add_argument("--force", action="store_true", help="Regenerate all images regardless of cache")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IllustrationBuildError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise IllustrationBuildError(f"Invalid JSON in {path}: {exc}") from exc


def sha256_digest(path: Path) -> str | None:
    if not path.exists():
        return None

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def is_placeholder_image(path: Path, placeholder_path: Path, placeholder_digest: str | None = None) -> bool:
    if not path.exists() or not placeholder_path.exists():
        return False

    if path.stat().st_size != placeholder_path.stat().st_size:
        return False

    expected = placeholder_digest or sha256_digest(placeholder_path)
    actual = sha256_digest(path)
    return expected is not None and actual == expected


def ensure_directories(root: Path, year_dir: Path) -> None:
    library_root = root / "art-library"
    for folder in ("backgrounds", "scenes", "environments"):
        (library_root / folder).mkdir(parents=True, exist_ok=True)

    art_dir = year_dir / "art"
    for folder in ("images", "pages", "collage", "comic", "parody", "fake_ads", "marginals", "feature", "cover", "departments"):
        (art_dir / folder).mkdir(parents=True, exist_ok=True)


def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[a-zA-Z0-9']+", text.lower())
    tokens: list[str] = []
    for token in raw:
        clean = token.strip("'")
        if not clean:
            continue
        if clean in STOPWORDS:
            continue
        if len(clean) < 3 and not clean.isdigit():
            continue
        tokens.append(clean)
    return tokens


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "asset"


def prompt_subject(prompt: str) -> str:
    tokens = [token for token in tokenize(prompt) if not token.isdigit()][:4]
    return "_".join(tokens) if tokens else "asset"


def build_library_filename(art_type: str, prompt: str, year: str) -> str:
    subject = slugify(prompt_subject(prompt))
    return f"{art_type}_{subject}_1970s_{year}.png"


def build_prompt(base_prompt: str, extra: str = "") -> str:
    guardrail = (
        "Do not render article paragraphs, magazine headlines, page titles, pull quotes, sidebars, chart or table text, "
        "or magazine layout elements into the artwork."
    )
    joined = " ".join(part.strip() for part in (STYLE_SUFFIX, base_prompt, extra, guardrail) if part and part.strip())
    return joined.strip()


def art_type_for_relpath(rel_path: str) -> str:
    if rel_path.startswith("issues/") and "/art/pages/" in rel_path:
        return "page"
    if rel_path.startswith("pages/"):
        return "page"
    if rel_path.startswith("cover/"):
        return "background"
    if rel_path.startswith("feature/") or rel_path.startswith("departments/"):
        return "scene"
    if rel_path.startswith("collage/"):
        return "collage"
    if rel_path.startswith("comic/"):
        return "comic"
    if rel_path.startswith("parody/"):
        return "parody"
    if rel_path.startswith("fake_ads/"):
        return "fake_ads"
    if rel_path.startswith("marginals/"):
        return "marginal"
    return "environment"


def reuse_allowed(art_type: str, overwrite: bool, allow_reuse: bool) -> bool:
    if not allow_reuse:
        return False
    if art_type in LIBRARY_ART_TYPES:
        return True
    if art_type in ISSUE_ART_TYPES:
        return not overwrite
    return not overwrite


def prompt_preview(prompt: str, limit: int = 120) -> str:
    compact = " ".join(prompt.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "..."


def load_prompt_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise IllustrationBuildError(f"Missing prompt file: {path}") from exc


def build_openai_prompt(base_prompt: str) -> str:
    """Prepend style guardrails to existing prompt. No readable text, leave space for layout."""
    return (OPENAI_PROMPT_PREFIX + base_prompt).strip()


def generate_with_openai(prompt: str, size: str = "1024x1024") -> bytes:
    """Generate image via OpenAI API. Returns PNG bytes. Raises on API error."""
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not str(api_key).strip():
        raise IllustrationBuildError(
            "OPENAI_API_KEY is not set. Set it in .env or environment before running."
        )

    client = OpenAI(api_key=api_key)
    full_prompt = build_openai_prompt(prompt)

    response = client.images.generate(
        model="dall-e-3",
        prompt=full_prompt,
        size=size,
        quality="hd",
        n=1,
        response_format="b64_json",
    )

    b64_data = response.data[0].b64_json
    if not b64_data:
        raise IllustrationBuildError("OpenAI returned no image data")

    return base64.b64decode(b64_data)


def mirror_job_output(job: ImageJob) -> None:
    if not job.target.exists():
        return
    if job.mirror_target == job.target:
        return
    job.mirror_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(job.target, job.mirror_target)


def should_skip_job(job: ImageJob, force: bool, placeholder_path: Path, placeholder_digest: str | None) -> bool:
    if force:
        return False
    if not job.mirror_target.exists():
        return False
    if job.job_type == "page_prompt" and is_placeholder_image(job.mirror_target, placeholder_path, placeholder_digest):
        return False
    return True


def restore_from_canonical_cache(job: ImageJob) -> None:
    if job.target == job.mirror_target:
        return
    job.target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(job.mirror_target, job.target)


def legacy_layout_images_for_page(year_dir: Path, page_number: int, page_slug: str) -> list[Path]:
    layout_html = year_dir / "layout" / f"page_{page_number:02d}_{page_slug}.html"
    if not layout_html.exists():
        return []
    html = layout_html.read_text(encoding="utf-8")
    paths: list[Path] = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
        if not src.startswith("../art/"):
            continue
        resolved = (layout_html.parent / src).resolve(strict=False)
        if resolved.exists():
            paths.append(resolved)
    return paths


def seed_page_job(root: Path, year_dir: Path, job: ImageJob) -> tuple[bool, str | None]:
    if job.job_type != "page_prompt" or job.page_number is None or not job.page_slug:
        return False, None

    legacy_images = legacy_layout_images_for_page(year_dir, job.page_number, job.page_slug)
    if legacy_images:
        source = legacy_images[0]
        job.target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve(strict=False) != job.target.resolve(strict=False):
            shutil.copy2(source, job.target)
        return True, str(source.relative_to(root))

    placeholder = root / "assets" / "placeholder.png"
    if placeholder.exists():
        job.target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(placeholder, job.target)
        return True, str(placeholder.relative_to(root))

    return False, None


def build_jobs(year_dir: Path, prompts: dict[str, Any], year: str, page_filter: int | None = None) -> list[ImageJob]:
    root = year_dir.parents[1]
    rows = prompts.get("prompts")
    if not isinstance(rows, list):
        raise IllustrationBuildError("image_prompts.json must include prompts[].")

    jobs: list[ImageJob] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        page_number = row.get("page_number")
        page_slug = row.get("page_slug")
        prompt_path_value = row.get("prompt_path")
        prompt_source = str(row.get("prompt_source") or "").strip().lower()
        if not isinstance(page_number, int) or not isinstance(page_slug, str) or not isinstance(prompt_path_value, str):
            continue
        if page_filter is not None and page_number != page_filter:
            continue
        if prompt_source == "comic_overview":
            continue

        prompt_path = root / prompt_path_value
        prompt_text = load_prompt_text(prompt_path)

        image_path_value = row.get("image_path")
        if isinstance(image_path_value, str) and image_path_value.strip():
            image_rel = image_path_value.strip()
            target = root / image_rel
        else:
            target = year_dir / "art" / "pages" / f"page_{page_number:02d}.png"

        jobs.append(
            ImageJob(
                target=target,
                mirror_target=target,
                prompt=prompt_text,
                note=f"page {page_number:02d} / {page_slug}",
                art_type="page",
                job_type="page_prompt",
                page_number=page_number,
                page_slug=page_slug,
                prompt_path=prompt_path,
                allow_reuse=False,
            )
        )

    comic_rows = prompts.get("comic_panel_prompts")
    if isinstance(comic_rows, list):
        issue_art_prefix = f"issues/{year}/art/"
        for row in comic_rows:
            if not isinstance(row, dict):
                continue
            page_number = row.get("page_number")
            page_slug = row.get("page_slug")
            prompt_path_value = row.get("prompt_path")
            asset_path_value = row.get("asset_path")
            panel_index = row.get("panel_index")
            if (
                not isinstance(page_number, int)
                or not isinstance(page_slug, str)
                or not isinstance(prompt_path_value, str)
                or not isinstance(asset_path_value, str)
            ):
                continue
            if page_filter is not None and page_number != page_filter:
                continue

            prompt_path = root / prompt_path_value
            prompt_text = load_prompt_text(prompt_path)
            asset_rel = asset_path_value.strip()
            target = root / asset_rel
            art_rel = asset_rel[len(issue_art_prefix) :] if asset_rel.startswith(issue_art_prefix) else asset_rel
            panel_note = (
                f"page {page_number:02d} / {page_slug} comic panel {panel_index:02d}"
                if isinstance(panel_index, int)
                else f"page {page_number:02d} / {page_slug} comic panel"
            )

            jobs.append(
                ImageJob(
                    target=target,
                    mirror_target=target,
                    prompt=prompt_text,
                    note=panel_note,
                    art_type=art_type_for_relpath(art_rel),
                    job_type="comic_panel",
                    page_number=page_number,
                    page_slug=page_slug,
                    prompt_path=prompt_path,
                    allow_reuse=False,
                )
            )

    unique_jobs: dict[Path, ImageJob] = {}
    for job in jobs:
        unique_jobs[job.target] = job
    return list(unique_jobs.values())


def find_reusable_asset(root: Path, prompt: str, art_type: str) -> Path | None:
    library_root = root / "art-library"
    if not library_root.exists():
        return None

    candidate_dirs: list[Path]
    if art_type in LIBRARY_TYPE_TO_DIR:
        candidate_dirs = [library_root / LIBRARY_TYPE_TO_DIR[art_type]]
    else:
        candidate_dirs = [
            library_root / "backgrounds",
            library_root / "scenes",
            library_root / "environments",
        ]

    prompt_tokens = set(tokenize(prompt))
    if not prompt_tokens:
        return None

    best_score = 0
    best_path: Path | None = None

    for directory in candidate_dirs:
        if not directory.exists():
            continue
        for file_path in directory.glob("*.png"):
            file_tokens = set(tokenize(file_path.stem.replace("_", " ")))
            score = len(prompt_tokens & file_tokens)
            if score > best_score:
                best_score = score
                best_path = file_path

    return best_path if best_score >= 2 else None


def store_library_asset(root: Path, image_bytes: bytes, prompt: str, art_type: str, year: str) -> Path | None:
    if art_type not in LIBRARY_TYPE_TO_DIR:
        return None

    library_dir = root / "art-library" / LIBRARY_TYPE_TO_DIR[art_type]
    library_dir.mkdir(parents=True, exist_ok=True)
    target = library_dir / build_library_filename(art_type, prompt, year)

    if target.exists():
        stem = target.stem
        suffix = target.suffix
        idx = 2
        while True:
            candidate = target.with_name(f"{stem}_{idx}{suffix}")
            if not candidate.exists():
                target = candidate
                break
            idx += 1

    target.write_bytes(image_bytes)
    return target


def main() -> int:
    args = parse_args()
    force = args.force or args.overwrite
    root = PROJECT_ROOT
    year = str(args.year)
    year_dir = root / "issues" / year
    art_dir = year_dir / "art"
    prompts_path = art_dir / "image_prompts.json"
    placeholder_path = root / "assets" / "placeholder.png"
    placeholder_digest = sha256_digest(placeholder_path)

    ensure_directories(root, year_dir)

    try:
        prompts = load_json(prompts_path)
        if not isinstance(prompts, dict):
            raise IllustrationBuildError("image_prompts.json root must be an object.")
        jobs = build_jobs(year_dir, prompts, year, page_filter=args.page)
        if args.page is not None and not jobs:
            raise IllustrationBuildError(f"No illustration jobs found for page {args.page}.")
    except IllustrationBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    generated = 0
    skipped = 0
    reused = 0
    failed: list[Path] = []

    for job in jobs:
        filename = job.target.name
        if should_skip_job(job, force, placeholder_path, placeholder_digest):
            restore_from_canonical_cache(job)
            skipped += 1
            print(f"[ISSUE GENERATE] Skipped existing page image: {filename}")
            continue

        seeded, seed_source = seed_page_job(root, year_dir, job) if not force else (False, None)
        if seeded:
            if is_placeholder_image(job.target, placeholder_path, placeholder_digest):
                print(f"[ISSUE GENERATE] Placeholder seed detected for {filename}; continuing to real generation")
            else:
                reused += 1
                print(f"[ISSUE GENERATE] Seeded page image: {filename} <- {seed_source}")
                continue

        job.target.parent.mkdir(parents=True, exist_ok=True)
        job.mirror_target.parent.mkdir(parents=True, exist_ok=True)

        if reuse_allowed(job.art_type, force, job.allow_reuse) and job.job_type == "library_asset":
            reusable = find_reusable_asset(root, job.prompt, job.art_type)
            if reusable:
                shutil.copy2(reusable, job.target)
                mirror_job_output(job)
                reused += 1
                print(f"[LIBRARY REUSE] {filename} <- {reusable.name}")
                continue

        print(f"Generating {filename} via OpenAI")
        try:
            image_bytes = generate_with_openai(job.prompt, size="1024x1024")
            job.target.write_bytes(image_bytes)
            mirror_job_output(job)
            generated += 1

            library_copy = store_library_asset(root, image_bytes, job.prompt, job.art_type, year)
            if library_copy is not None:
                print(f"[LIBRARY REUSE] Stored: {library_copy.name}")

            print(f"Saved: {job.target}")
        except Exception as exc:
            failed.append(job.target)
            print(f"ERROR: {filename} - {exc}", file=sys.stderr)
            print(f"Skipping {filename}, continuing batch", file=sys.stderr)

    print("Illustration generation complete.")
    print(f"Generated: {generated}")
    print(f"Reused:    {reused}")
    print(f"Skipped:   {skipped}")
    print(f"Failed:    {len(failed)}")
    if failed:
        print("[ISSUE GENERATE] Failed files:")
        for path in failed:
            print(f"[ISSUE GENERATE]   - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
