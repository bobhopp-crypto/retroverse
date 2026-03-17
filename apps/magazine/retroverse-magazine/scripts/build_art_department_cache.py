#!/usr/bin/env python3
"""Build the public Art Department registry cache and frontend asset bridge."""

from __future__ import annotations

from art_department_common import (
    CANONICAL_REGISTRY_PATH,
    WEB_PUBLIC_ART_DEPARTMENT_PATH,
    append_log,
    ensure_art_department_directories,
    ensure_web_public_bridge,
    load_registry,
    validate_registry,
    write_public_registry_cache,
)


def main() -> int:
    ensure_art_department_directories()
    payload = load_registry()
    errors = validate_registry(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        append_log("art_department_cache.log", f"cache build failed for {CANONICAL_REGISTRY_PATH}: {len(errors)} validation errors")
        return 1

    write_public_registry_cache(payload)
    bridge_status = ensure_web_public_bridge()

    print(f"Built public art-department registry cache from {CANONICAL_REGISTRY_PATH}")
    print(f"Frontend bridge status: {bridge_status} ({WEB_PUBLIC_ART_DEPARTMENT_PATH})")
    append_log("art_department_cache.log", f"cache built successfully; bridge_status={bridge_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
