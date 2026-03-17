#!/usr/bin/env python3
"""Generate RetroVerse Art Department self-portraits with local ComfyUI."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from art_department_common import (
    PROJECT_ROOT,
    append_log,
    ensure_art_department_directories,
    ensure_web_public_bridge,
    load_registry,
    save_registry,
    validate_registry,
    write_public_registry_cache,
)
from generate_illustrations import (
    ComfyUIRenderOptions,
    create_comfyui_client,
    normalize_size,
    queue_with_comfyui,
)

PORTRAIT_BRIEF = (
    "Editorial illustrator self-portrait, waist-up at a drawing desk, artist studio environment, sketchbooks, brushes or pens visible, "
    "personality reflected in the workspace, stylized illustration not photorealistic, vintage magazine illustration aesthetic, consistent framing."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RetroVerse Art Department self-portraits.")
    parser.add_argument("--artist", help="Generate only one artist id.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing portrait files.")
    parser.add_argument("--size", default="512x512", help="Final portrait size written to disk (default: 512x512).")
    parser.add_argument("--render-size", default="384x384", help="Internal ComfyUI render size (default: 384x384).")
    parser.add_argument("--model", default="flux1-schnell-fp8", help="Compatibility option; the workflow still uses the local FLUX checkpoint.")
    parser.add_argument("--steps", type=int, default=14, help="ComfyUI sampler steps (default: 14).")
    parser.add_argument("--sampler", default="dpmpp_2m", help="ComfyUI sampler name (default: dpmpp_2m).")
    parser.add_argument("--scheduler", default="karras", help="ComfyUI scheduler (default: karras).")
    parser.add_argument("--cfg", type=float, default=6.0, help="Classifier-free guidance scale (default: 6).")
    parser.add_argument("--batch-size", type=int, default=3, help="Latent batch size override (default: 3).")
    parser.add_argument("--denoise", type=float, default=1.0, help="ComfyUI denoise strength (default: 1.0).")
    parser.add_argument("--seed", default="random", help="Explicit seed or 'random' (default: random).")
    return parser.parse_args()


def portrait_target(artist_id: str) -> Path:
    return PROJECT_ROOT / "public" / "art-department" / "portraits" / f"{artist_id}.png"


def parse_seed(seed_value: str) -> int | None:
    normalized = seed_value.strip().lower()
    if normalized in {"", "random"}:
        return None
    return int(seed_value)


def portrait_prompt(artist: dict[str, object]) -> str:
    style_traits = artist.get("style_traits", [])
    trait_text = ""
    if isinstance(style_traits, list) and style_traits:
        trait_text = f" Hint at these style traits: {', '.join(str(trait) for trait in style_traits[:4])}."

    department = str(artist.get("department") or "").strip()
    department_note = ""
    if department.lower() == "type & lettering":
        department_note = " This should still be a literal waist-up portrait of the artist, not just a tool card or abstract specimen."

    base_prompt = str(artist.get("self_portrait_prompt") or "").strip()
    return f"{base_prompt} {PORTRAIT_BRIEF}{trait_text}{department_note}".strip()


def main() -> int:
    args = parse_args()
    ensure_art_department_directories()

    payload = load_registry()
    errors = validate_registry(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    artists = [artist for artist in payload.get("artists", []) if isinstance(artist, dict)]
    if args.artist:
        artists = [artist for artist in artists if artist.get("id") == args.artist]
        if not artists:
            print(f"ERROR: artist id not found: {args.artist}")
            return 1

    output_size = normalize_size(args.size)
    render_size = normalize_size(args.render_size)
    render_options = ComfyUIRenderOptions(
        steps=args.steps,
        cfg=args.cfg,
        sampler_name=args.sampler,
        scheduler=args.scheduler,
        batch_size=args.batch_size,
        denoise=args.denoise,
        seed=parse_seed(args.seed),
    )

    client = create_comfyui_client()
    queued = 0
    skipped = 0
    failed = 0

    append_log(
        "art_department_portraits.log",
        (
            "start batch "
            f"artist={args.artist or 'ALL'} "
            f"render_size={render_size} output_size={output_size} steps={args.steps} sampler={args.sampler} "
            f"scheduler={args.scheduler} cfg={args.cfg} batch_size={args.batch_size} denoise={args.denoise} seed={args.seed}"
        ),
    )

    for artist in artists:
        artist_id = str(artist["id"])
        artist_name = str(artist.get("display_name") or artist_id)
        target = portrait_target(artist_id)
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and not args.force:
            skipped += 1
            print(f"{artist_name}\nportrait skipped\n{target}")
            append_log("art_department_portraits.log", f"skip {artist_id} -> {target}")
            continue

        prompt = portrait_prompt(artist)
        output_prefix = f"art-department/portraits/{artist_id}"

        try:
            print(f"{artist_name}\nqueueing portrait")
            prompt_id = queue_with_comfyui(
                client,
                args.model,
                render_size,
                prompt,
                output_prefix,
                render_options=render_options,
            )
            queued += 1
            print(f"{artist_name}\nportrait queued\nprompt_id: {prompt_id}")
            append_log("art_department_portraits.log", f"Queued portrait job: {artist_name} (prompt_id: {prompt_id})")
        except Exception as exc:
            failed += 1
            append_log("art_department_portraits.log", f"failed {artist_id}: {exc}")
            print(f"{artist_name}\nportrait failed\n{exc}")

    save_registry(payload)
    write_public_registry_cache(payload)
    ensure_web_public_bridge()

    if failed:
        print(f"Failed to queue {failed} portrait jobs.")
    print(f"Queued {queued} portrait jobs to ComfyUI.")
    print("ComfyUI will then process the queue automatically.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
