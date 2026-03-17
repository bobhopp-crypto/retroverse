#!/usr/bin/env python3.12

from __future__ import annotations

import base64
import importlib
import os
import subprocess
import sys
from io import BytesIO
from pathlib import Path


def ensure_package(import_name: str, pip_name: str) -> None:
    try:
        importlib.import_module(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])


def main() -> None:
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"Python 3.12 required, found {sys.version.split()[0]}")

    ensure_package("openai", "openai")
    ensure_package("dotenv", "python-dotenv")
    ensure_package("PIL", "pillow")

    from dotenv import load_dotenv
    from openai import OpenAI
    from PIL import Image

    repo_root = Path(__file__).resolve().parents[1]
    env_path = repo_root / "public" / "1974" / ".env"
    if not env_path.exists():
        env_path = repo_root / ".env"

    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(f"OPENAI_API_KEY not found in {env_path}")

    output_path = repo_root / "artifacts" / "at40" / "week30_rank01.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prompt = (
        "American Top 40 countdown card, 1974 radio chart style, bold vintage typography, "
        "large ranking number #1 at the top, artist name George McCrae, song title Rock Your Baby, "
        "classic Casey Kasem era design, warm paper texture background, red white and blue accent stripes, "
        "subtle 1970s broadcast graphics, clean centered layout, high detail, collectible trading card style"
    )

    client = OpenAI(api_key=api_key)

    fallback_resize = False
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="800x1200",
        )
    except Exception as exc:
        message = str(exc).lower()
        if "size" not in message:
            raise
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1536",
        )
        fallback_resize = True

    b64_json = None
    if getattr(response, "data", None):
        first = response.data[0]
        b64_json = getattr(first, "b64_json", None)

    if not b64_json and hasattr(response, "model_dump"):
        payload = response.model_dump()
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list) and data and isinstance(data[0], dict):
                b64_json = data[0].get("b64_json")

    if not b64_json:
        raise RuntimeError("No base64 image data returned by OpenAI Images API")

    image_bytes = base64.b64decode(b64_json)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    if fallback_resize or image.size != (800, 1200):
        image = image.resize((800, 1200), Image.Resampling.LANCZOS)
    image.save(output_path, format="PNG")

    print(f"Success: saved image to {output_path}")


if __name__ == "__main__":
    main()
