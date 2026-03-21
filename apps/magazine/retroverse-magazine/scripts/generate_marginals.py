#!/usr/bin/env python3
"""Generate RetroVerse marginal gag illustrations."""

from __future__ import annotations

import argparse
import base64
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ENV_PATH = Path(__file__).resolve().parents[4] / ".env"
if REPO_ENV_PATH.exists():
    load_dotenv(dotenv_path=REPO_ENV_PATH, override=False)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_RETRIES = 3
WATCHDOG_SECONDS = 90


class MarginalError(Exception):
    """Raised when marginal generation inputs are invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate marginal gag illustrations for an issue.")
    parser.add_argument("--year", default="1978", help="Issue year to generate (default: 1978)")
    parser.add_argument("--model", default="gpt-image-1", help="OpenAI image model (default: gpt-image-1)")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate marginals even if cached.")
    return parser.parse_args()


def create_client() -> OpenAI:
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not found. Check .env file.", file=sys.stderr)
        raise MarginalError("OPENAI_API_KEY not found")
    return OpenAI(api_key=OPENAI_API_KEY, timeout=60)


def build_prompt(index: int) -> str:
    return (
        "RetroVerse marginal gag illustration, late-1970s ink cartoon, simple background, absurd visual joke, "
        "no readable text, no page layout elements, no headline typography. "
        f"Variation {index}: quirky visual situation with exaggerated expressions and clean linework."
    )


def generate_png_bytes(client: OpenAI, model: str, prompt: str) -> bytes:
    start = time.monotonic()
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        elapsed = time.monotonic() - start
        remaining = WATCHDOG_SECONDS - elapsed
        if remaining <= 0:
            raise TimeoutError(f"Marginal watchdog exceeded {WATCHDOG_SECONDS} seconds")

        timeout = min(60, max(1, int(remaining)))
        try:
            result = client.with_options(timeout=timeout).images.generate(
                model=model,
                prompt=prompt,
                size="2048x2048",
            )
            if not getattr(result, "data", None):
                raise MarginalError("OpenAI returned no image data")

            b64_json = getattr(result.data[0], "b64_json", None)
            if not b64_json:
                raise MarginalError("OpenAI image response missing b64_json")
            return base64.b64decode(b64_json)
        except Exception as exc:
            last_error = exc
            if attempt == MAX_RETRIES - 1:
                raise
            print(f"[MARGINAL GENERATE] Retrying ({attempt + 1}/{MAX_RETRIES})")

    if last_error is not None:
        raise last_error
    raise MarginalError("Unknown marginal generation error")


def main() -> int:
    args = parse_args()
    output_dir = PROJECT_ROOT / "issues" / str(args.year) / "art" / "marginals"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        client = create_client()
    except MarginalError:
        return 1

    generated = 0
    skipped = 0
    failed = 0

    for index in range(1, 21):
        filename = f"marginal_{index:02d}.png"
        target = output_dir / filename

        if target.exists() and not args.overwrite:
            skipped += 1
            print(f"[MARGINAL GENERATE] Skipped (cached): {filename}")
            continue

        print(f"[MARGINAL GENERATE] Generating: {filename}")
        try:
            png_bytes = generate_png_bytes(client, args.model, build_prompt(index))
            target.write_bytes(png_bytes)
            generated += 1
            print(f"[MARGINAL GENERATE] Generated: {filename}")
        except Exception as exc:
            failed += 1
            print(f"[MARGINAL GENERATE] Failed: {filename} ({exc})")

    print("Marginal generation complete.")
    print(f"Generated: {generated}")
    print(f"Skipped:   {skipped}")
    print(f"Failed:    {failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
