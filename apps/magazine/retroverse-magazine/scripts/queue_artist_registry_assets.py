#!/usr/bin/env python3
"""Queue RetroVerse Art Department prompts to ComfyUI in one batch."""

from __future__ import annotations

import argparse

from art_department_common import (
    append_log,
    ensure_art_department_directories,
    load_registry,
    prompt_slug,
    validate_registry,
)
from generate_illustrations import (
    ComfyUIRenderOptions,
    create_comfyui_client,
    normalize_size,
    queue_with_comfyui,
)

LOG_NAME = "art_department_comfyui_batch.log"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Queue all RetroVerse artist portrait and style-sheet prompts to ComfyUI.")
    parser.add_argument("--artist", help="Queue prompts for only one artist id.")
    parser.add_argument("--portrait-size", default="384x384", help="Portrait render size passed to ComfyUI (default: 384x384).")
    parser.add_argument("--reference-size", default="768x768", help="Reference-sheet render size passed to ComfyUI (default: 768x768).")
    parser.add_argument("--model", default="flux1-schnell-fp8", help="Compatibility option; the workflow still uses the local FLUX checkpoint.")
    parser.add_argument("--steps", type=int, default=14, help="ComfyUI sampler steps (default: 14).")
    parser.add_argument("--sampler", default="dpmpp_2m", help="ComfyUI sampler name (default: dpmpp_2m).")
    parser.add_argument("--scheduler", default="karras", help="ComfyUI scheduler (default: karras).")
    parser.add_argument("--cfg", type=float, default=6.0, help="Classifier-free guidance scale (default: 6).")
    parser.add_argument("--batch-size", type=int, default=3, help="Latent batch size override (default: 3).")
    parser.add_argument("--denoise", type=float, default=1.0, help="ComfyUI denoise strength (default: 1.0).")
    parser.add_argument("--seed", default="random", help="Explicit seed or 'random' (default: random).")
    return parser.parse_args()


def parse_seed(seed_value: str) -> int | None:
    normalized = seed_value.strip().lower()
    if normalized in {"", "random"}:
        return None
    return int(seed_value)


def queue_job(
    client,
    *,
    model: str,
    size: str,
    prompt: str,
    output_prefix: str,
    render_options: ComfyUIRenderOptions,
) -> str:
    return queue_with_comfyui(
        client,
        model,
        size,
        prompt,
        output_prefix,
        render_options=render_options,
    )


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

    portrait_size = normalize_size(args.portrait_size)
    reference_size = normalize_size(args.reference_size)
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
    failed = 0

    append_log(
        LOG_NAME,
        (
            "start batch "
            f"artist={args.artist or 'ALL'} "
            f"portrait_size={portrait_size} reference_size={reference_size} "
            f"steps={args.steps} sampler={args.sampler} scheduler={args.scheduler} "
            f"cfg={args.cfg} batch_size={args.batch_size} denoise={args.denoise} seed={args.seed}"
        ),
    )

    for artist in artists:
        artist_id = str(artist["id"])
        artist_name = str(artist.get("display_name") or artist_id)

        portrait_prompt = str(artist.get("self_portrait_prompt") or "").strip()
        if portrait_prompt:
            output_prefix = f"art-department/{artist_id}/00-self-portrait"
            try:
                prompt_id = queue_job(
                    client,
                    model=args.model,
                    size=portrait_size,
                    prompt=portrait_prompt,
                    output_prefix=output_prefix,
                    render_options=render_options,
                )
                queued += 1
                print(f"[ART BATCH] Queued portrait: {artist_name} -> /{output_prefix} (prompt_id: {prompt_id})")
                append_log(LOG_NAME, f"queued {artist_id}/00-self-portrait (prompt_id: {prompt_id})")
            except Exception as exc:
                failed += 1
                print(f"[ART BATCH] Failed portrait: {artist_name} ({exc})")
                append_log(LOG_NAME, f"failed {artist_id}/00-self-portrait: {exc}")

        reference_prompts = artist.get("reference_scene_prompts", [])
        if not isinstance(reference_prompts, list):
            failed += 1
            print(f"[ART BATCH] Failed references: {artist_name} (reference_scene_prompts is not a list)")
            append_log(LOG_NAME, f"failed {artist_id}: reference_scene_prompts is not a list")
            continue

        for index, prompt in enumerate(reference_prompts, start=1):
            prompt_text = str(prompt).strip()
            if not prompt_text:
                continue

            slug = prompt_slug(prompt_text)
            output_prefix = f"art-department/{artist_id}/{index:02d}-{slug}"
            try:
                prompt_id = queue_job(
                    client,
                    model=args.model,
                    size=reference_size,
                    prompt=prompt_text,
                    output_prefix=output_prefix,
                    render_options=render_options,
                )
                queued += 1
                print(f"[ART BATCH] Queued reference: {artist_name} -> /{output_prefix} (prompt_id: {prompt_id})")
                append_log(LOG_NAME, f"queued {artist_id}/{index:02d}-{slug} (prompt_id: {prompt_id})")
            except Exception as exc:
                failed += 1
                print(f"[ART BATCH] Failed reference: {artist_name} [{index}] ({exc})")
                append_log(LOG_NAME, f"failed {artist_id}/{index:02d}-{slug}: {exc}")

    if failed:
        print(f"Failed to queue {failed} artist prompt jobs.")
    print(f"Queued {queued} artist prompt jobs to ComfyUI.")
    print("ComfyUI will process the queue automatically.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
