#!/usr/bin/env python3.12

from __future__ import annotations

import base64
import os
import sqlite3
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


def load_api_key(repo_root: Path) -> str:
    env_paths = [
        repo_root / ".env",
        repo_root / "public" / "1974" / ".env",
    ]
    found = False
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            found = True
            break
    if not found:
        raise RuntimeError("No .env file found.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing in .env.")
    return api_key


def get_week30_top5(db_path: Path) -> tuple[str, list[tuple[int, str, str]]]:
    with sqlite3.connect(db_path) as conn:
        chart_dates = [
            row[0]
            for row in conn.execute(
                """
                SELECT DISTINCT issue_date
                FROM event
                WHERE substr(issue_date, 1, 4) = '1974'
                ORDER BY issue_date ASC
                """
            ).fetchall()
        ]

        if len(chart_dates) < 30:
            raise RuntimeError(f"Expected at least 30 chart dates for 1974, found {len(chart_dates)}.")

        chart_date = chart_dates[29]

        top5 = conn.execute(
            """
            SELECT ee.rank, w.title_display, p.name_display
            FROM event e
            JOIN event_entry ee ON ee.event_id = e.event_id
            JOIN work w ON w.work_id = ee.work_id
            LEFT JOIN person p ON p.person_id = w.primary_person_id
            WHERE e.issue_date = ?
              AND ee.rank <= 5
            ORDER BY ee.rank ASC
            """,
            (chart_date,),
        ).fetchall()

    if len(top5) < 5:
        raise RuntimeError(f"Expected 5 songs for {chart_date}, found {len(top5)}.")

    return chart_date, [(int(rank), str(title), str(artist)) for rank, title, artist in top5]


def render_image_bytes(
    client: OpenAI,
    *,
    prompt: str,
    size: str = "1024x1536",
) -> bytes:
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
    )

    if getattr(response, "data", None):
        entry = response.data[0]
        b64_json = getattr(entry, "b64_json", None)
        if b64_json:
            return base64.b64decode(b64_json)
        url = getattr(entry, "url", None)
        if url:
            with urlopen(url) as http_response:
                return http_response.read()

    if hasattr(response, "model_dump"):
        payload = response.model_dump()
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list) and data and isinstance(data[0], dict):
                b64_json = data[0].get("b64_json")
                if b64_json:
                    return base64.b64decode(b64_json)
                url = data[0].get("url")
                if url:
                    with urlopen(url) as http_response:
                        return http_response.read()

    raise RuntimeError("OpenAI Images response did not contain image data.")


def build_prompt(rank: int, chart_date: str, title: str, artist: str) -> str:
    return (
        "Retroverse brand illustrated poster card, 1974 Billboard Hot 100 music feature aesthetic. "
        "Portrait 800x1200, rich layered typography, warm textured paper background, cinematic composition, "
        "high-detail collectible print look with period-accurate 1970s styling. "
        f"Include ranking text exactly: \"#{rank} Billboard Hot 100 - {chart_date}\". "
        f"Include song title text: \"{title}\". "
        f"Include artist name text: \"{artist}\". "
        "No reference to American Top 40. No Casey Kasem. No modern minimal design."
    )


def resize_to_800x1200(image_bytes: bytes) -> bytes:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    resized = image.resize((800, 1200), Image.Resampling.LANCZOS)
    out_buffer = BytesIO()
    resized.save(out_buffer, format="PNG")
    return out_buffer.getvalue()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    db_path = repo_root / "raw-data" / "billboard-hot-100.db"
    out_dir = repo_root / "artifacts" / "at40"
    out_dir.mkdir(parents=True, exist_ok=True)

    api_key = load_api_key(repo_root)
    chart_date, top5 = get_week30_top5(db_path)

    print(f"Selected chart date: {chart_date}")

    client = OpenAI(api_key=api_key)

    for rank, title, artist in top5:
        prompt = build_prompt(rank, chart_date, title, artist)
        image_bytes = render_image_bytes(client, prompt=prompt, size="1024x1536")
        image_bytes = resize_to_800x1200(image_bytes)
        output_path = out_dir / f"1974_week30_rank{rank:02d}.png"
        output_path.write_bytes(image_bytes)
        print(f"Success: {output_path}")


if __name__ == "__main__":
    main()
