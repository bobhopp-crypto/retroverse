#!/usr/bin/env python3
"""Generate a single image via OpenAI Images API."""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ENV_PATH = Path(__file__).resolve().parents[4] / ".env"
if REPO_ENV_PATH.exists():
    load_dotenv(dotenv_path=REPO_ENV_PATH, override=False)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_FILENAME_CHARS = 50
EDITORIAL_STYLE_PREFIX = (
    "hand-drawn 1970s editorial illustration, colored pencil and watercolor, "
    "visible strokes, textured paper, vintage print style, slightly imperfect "
    "linework, stylized figures, warm analog color palette,"
)
EDITORIAL_STYLE_SUFFIX = (
    "people in motion, expressive poses, clear environment, magazine-friendly "
    "composition, no text"
)
COMIC_STYLE_PREFIX = (
    "simple hand-drawn 1970s humor-magazine cartoon, loose black ink lines, "
    "flat muted color fills, minimal background detail, exaggerated expressions, "
    "simple shapes, readable comic-book staging, 1970s print-cartoon feel,"
)
COMIC_STYLE_SUFFIX = (
    "one clear visual joke, sparse background, people posed clearly, no cinematic lighting, "
    "no painterly rendering, no photorealism, no poster composition, no dramatic realism, "
    "no glossy finish, no text"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an image via OpenAI Images API.")
    parser.add_argument("prompt", nargs="?", help="Image generation prompt")
    parser.add_argument("--prompt-file", help="Path to a text file containing the prompt")
    parser.add_argument("--year", default="1978", help="Issue year (default: 1978)")
    parser.add_argument("--section", default="editorial", help="Art section subfolder (default: editorial)")
    parser.add_argument("--output-name", help="Optional output filename to overwrite inside the section folder")
    return parser.parse_args()


def slug_from_prompt(prompt: str) -> str:
    """Derive a safe filename from the prompt, max ~50 chars."""
    slug = re.sub(r"[^a-z0-9\s-]", "", prompt.lower())
    slug = re.sub(r"[\s-]+", "_", slug).strip("_")
    slug = slug[:MAX_FILENAME_CHARS] if slug else "image"
    return slug or "image"


def create_client() -> OpenAI:
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not found. Check .env file.", file=sys.stderr)
        raise ValueError("OPENAI_API_KEY not found")
    return OpenAI(api_key=OPENAI_API_KEY, timeout=120)


def load_prompt_text(path_value: str) -> str:
    path = Path(path_value)
    return path.read_text(encoding="utf-8").strip()


def resolve_source_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return load_prompt_text(args.prompt_file)
    if args.prompt:
        return args.prompt.strip()
    raise ValueError("prompt or --prompt-file is required")


def build_editorial_prompt(prompt: str, section: str) -> str:
    prompt_body = prompt.strip()
    if section.strip().lower() == "comic":
        return f"{COMIC_STYLE_PREFIX} {prompt_body}, {COMIC_STYLE_SUFFIX}"
    return f"{EDITORIAL_STYLE_PREFIX} {prompt_body}, {EDITORIAL_STYLE_SUFFIX}"


def generate_image(client: OpenAI, prompt: str) -> bytes:
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1536",
    )
    if not getattr(result, "data", None):
        raise ValueError("OpenAI returned no image data")
    b64_json = getattr(result.data[0], "b64_json", None)
    if not b64_json:
        raise ValueError("OpenAI image response missing b64_json")
    return base64.b64decode(b64_json)


def main() -> int:
    args = parse_args()
    output_dir = PROJECT_ROOT / "issues" / str(args.year) / "art" / str(args.section)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        source_prompt = resolve_source_prompt(args)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    styled_prompt = build_editorial_prompt(source_prompt, str(args.section))
    stem = slug_from_prompt(source_prompt)
    filename = Path(args.output_name).name if args.output_name else f"{stem}.png"
    target = output_dir / filename

    try:
        client = create_client()
    except ValueError:
        return 1

    try:
        png_bytes = generate_image(client, styled_prompt)
        target.write_bytes(png_bytes)
        print(str(target))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
