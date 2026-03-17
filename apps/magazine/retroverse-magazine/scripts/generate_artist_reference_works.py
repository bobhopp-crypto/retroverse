#!/usr/bin/env python3
"""Generate RetroVerse Art Department reference works with local ComfyUI."""

from __future__ import annotations

import argparse
from pathlib import Path

from art_department_common import (
    PROJECT_ROOT,
    append_log,
    ensure_art_department_directories,
    ensure_web_public_bridge,
    illustration_artists,
    load_registry,
    prompt_slug,
    save_registry,
    validate_registry,
    write_public_registry_cache,
)
from generate_illustrations import create_comfyui_client, generate_with_comfyui, normalize_size


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RetroVerse Art Department reference works.")
    parser.add_argument("--artist", help="Generate only one artist id.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing reference files.")
    parser.add_argument("--size", default="768x768", help="Requested render size (default: 768x768).")
    parser.add_argument("--model", default="gpt-image-1", help="Compatibility option; ignored by the current ComfyUI workflow.")
    return parser.parse_args()


def reference_target(artist_id: str, slug: str) -> Path:
    return PROJECT_ROOT / "public" / "art-department" / "reference" / artist_id / f"{slug}.png"


def main() -> int:
    args = parse_args()
    ensure_art_department_directories()

    payload = load_registry()
    errors = validate_registry(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    artists = illustration_artists(payload)
    if args.artist:
        artists = [artist for artist in artists if artist.get("id") == args.artist]
        if not artists:
            print(f"ERROR: artist id not found or not reference-work-enabled: {args.artist}")
            return 1

    client = create_comfyui_client()
    generated = 0
    skipped = 0
    failed = 0

    for artist in artists:
        artist_id = str(artist["id"])
        prompts = artist.get("reference_scene_prompts", [])
        if not isinstance(prompts, list):
            append_log("art_department_reference_works.log", f"failed {artist_id}: reference_scene_prompts is not a list")
            failed += 1
            continue

        attached_paths: list[str] = []
        for prompt in prompts[:2]:
            prompt_text = str(prompt).strip()
            slug = prompt_slug(prompt_text)
            rel_path = f"/art-department/reference/{artist_id}/{slug}.png"
            target = reference_target(artist_id, slug)
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists() and not args.force:
                attached_paths.append(rel_path)
                skipped += 1
                print(f"[ART REF] Skipped existing reference: {artist_id}/{slug}")
                append_log("art_department_reference_works.log", f"skip {artist_id}/{slug} -> {target}")
                continue

            try:
                print(f"[ART REF] Generating: {artist_id}/{slug}")
                output_prefix = f"art-department/reference/{artist_id}/{slug}"
                image_bytes = generate_with_comfyui(client, args.model, normalize_size(args.size), prompt_text, output_prefix)
                target.write_bytes(image_bytes)
                attached_paths.append(rel_path)
                generated += 1
                append_log("art_department_reference_works.log", f"generated {artist_id}/{slug} -> {target}")
            except Exception as exc:
                failed += 1
                append_log("art_department_reference_works.log", f"failed {artist_id}/{slug}: {exc}")
                print(f"[ART REF] Failed: {artist_id}/{slug} ({exc})")

        existing = artist.get("reference_images", [])
        if not isinstance(existing, list):
            existing = []
        remainder = [path for path in existing if path not in attached_paths]
        artist["reference_images"] = attached_paths + remainder

    save_registry(payload)
    write_public_registry_cache(payload)
    ensure_web_public_bridge()

    print("Reference-work generation complete.")
    print(f"Generated: {generated}")
    print(f"Skipped:   {skipped}")
    print(f"Failed:    {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
