#!/usr/bin/env python3
"""Build and run artist image jobs against a remote ComfyUI endpoint."""

from __future__ import annotations

import copy
import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import parse as urllib_parse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

REPO_ROOT = Path(__file__).resolve().parents[2]
DERIVED_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_MAGAZINE_ROOT = REPO_ROOT / "apps" / "magazine" / "retroverse-magazine"
CANONICAL_SCRIPTS_ROOT = CANONICAL_MAGAZINE_ROOT / "scripts"

if str(CANONICAL_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(CANONICAL_SCRIPTS_ROOT))

import art_department_common
import generate_artist_portraits
import generate_illustrations

DEFAULT_COMFYUI_BASE_URL = "https://7xqscdf49l0bs2-8188.proxy.runpod.net"
DEFAULT_ISSUE_YEAR = "1978"
DEFAULT_RENDER_SIZE = "1024x1024"
DEFAULT_REQUEST_TIMEOUT = 120
DEFAULT_RENDER_TIMEOUT_SECONDS = 1800
DEFAULT_POLL_INTERVAL_SECONDS = 2.0
JOBS_PATH = DERIVED_ROOT / "image_jobs.json"
OUTPUT_ROOT = DERIVED_ROOT / "issues" / DEFAULT_ISSUE_YEAR / "art" / "generated"
WORKFLOW_PATH = CANONICAL_MAGAZINE_ROOT / "comfy" / "artist_render_workflow.json"


@dataclass(frozen=True)
class ImageJob:
    artist_name: str
    artist_id: str
    job_type: str
    prompt: str

    @property
    def output_path(self) -> Path:
        return OUTPUT_ROOT / self.artist_id / f"{self.job_type}.png"

    @property
    def output_prefix(self) -> str:
        return f"retroverse-magazine/{DEFAULT_ISSUE_YEAR}/{self.artist_id}/{self.job_type}"


@dataclass(frozen=True)
class RunStats:
    artists: int
    expected_images: int
    rendered: int
    skipped_existing: int
    saved_images: int
    failures: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and run RetroVerse artist image jobs against RunPod ComfyUI.")
    parser.add_argument("--build-only", action="store_true", help="Write image_jobs.json and exit without rendering.")
    return parser.parse_args()


def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


SESSION = create_session()


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if method.upper() == "GET":
        response = SESSION.get(url, timeout=DEFAULT_REQUEST_TIMEOUT)
    elif method.upper() == "POST":
        response = SESSION.post(url, json=payload, timeout=DEFAULT_REQUEST_TIMEOUT)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    response.raise_for_status()
    return response.json()


def request_bytes(url: str) -> bytes:
    response = SESSION.get(url, timeout=DEFAULT_REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.content


def normalize_text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    seen: set[str] = set()
    for raw in value:
        text = str(raw).strip()
        if not text:
            continue
        key = " ".join(text.lower().split())
        if key in seen:
            continue
        seen.add(key)
        items.append(text)
    return items


def first_item(values: list[str], fallback: str) -> str:
    return values[0] if values else fallback


def item_at(values: list[str], index: int, fallback: str) -> str:
    if not values:
        return fallback
    return values[index] if index < len(values) else values[-1]


def project_phrase(project_type: str) -> str:
    normalized = project_type.strip().lower()
    mapping = {
        "cover art": "cover-package",
        "magazine feature": "feature-opener",
        "poster": "poster",
        "infographic": "infographic-spread",
        "card illustration": "card-system",
    }
    return mapping.get(normalized, normalized or "magazine-package")


def with_article(phrase: str) -> str:
    article = "an" if phrase[:1].lower() in {"a", "e", "i", "o", "u"} else "a"
    return f"{article} {phrase}"


def supplemental_reference_candidates(artist: dict[str, Any]) -> list[str]:
    project_types = normalize_text_list(artist.get("project_type_fit"))
    best_use = normalize_text_list(artist.get("best_use"))
    style_traits = normalize_text_list(artist.get("style_traits"))
    tone_fit = normalize_text_list(artist.get("tone_fit"))
    signature_notes = str(artist.get("signature_notes") or "").strip().rstrip(".")

    trait_a = first_item(style_traits, "period-correct display forms")
    trait_b = item_at(style_traits, 1, trait_a)
    trait_c = item_at(style_traits, 2, trait_b)
    tone_a = first_item(tone_fit, "editorial")
    tone_b = item_at(tone_fit, 1, tone_a)
    project_a = project_phrase(first_item(project_types, "Magazine Feature"))
    project_b = project_phrase(item_at(project_types, 1, "Magazine Feature"))
    best_use_a = first_item(best_use, "editorial lettering")
    best_use_b = item_at(best_use, 1, best_use_a)
    signature_clause = signature_notes[:1].lower() + signature_notes[1:] if signature_notes else "with disciplined 1978 editorial pacing"

    return [
        (
            f"A {tone_a} lettering sample for {best_use_a}, designed as {with_article(project_a)} study using "
            f"{trait_a}, {trait_b}, and {trait_c}, {signature_clause}, no readable words."
        ),
        (
            f"A period-correct title-treatment concept for {with_article(project_b)}, balancing {tone_b} energy with "
            f"{trait_b}, {trait_a}, and clear magazine hierarchy, built for {best_use_b}, no actual text."
        ),
        (
            f"A promotional nameplate study for {best_use_a}, shaped by {trait_c}, {trait_a}, and "
            f"{tone_a} editorial drama, no readable lettering."
        ),
    ]


def build_reference_prompts(artist: dict[str, Any]) -> list[str]:
    prompts = normalize_text_list(artist.get("reference_scene_prompts"))
    existing_keys = {" ".join(prompt.lower().split()) for prompt in prompts}

    if len(prompts) < 5:
        for candidate in supplemental_reference_candidates(artist):
            key = " ".join(candidate.lower().split())
            if key in existing_keys:
                continue
            prompts.append(candidate)
            existing_keys.add(key)
            if len(prompts) == 5:
                break

    if len(prompts) != 5:
        artist_id = str(artist.get("id") or "unknown")
        raise RuntimeError(f"Expected exactly 5 reference prompts for {artist_id}, found {len(prompts)}")
    return prompts


def build_jobs() -> list[ImageJob]:
    payload = art_department_common.load_registry()
    errors = art_department_common.validate_registry(payload)
    if errors:
        raise RuntimeError("\n".join(errors))

    jobs: list[ImageJob] = []
    seen_pairs: set[tuple[str, str]] = set()
    artists = [artist for artist in payload.get("artists", []) if isinstance(artist, dict)]

    for artist in artists:
        artist_id = str(artist["id"])
        artist_name = str(artist["display_name"])

        portrait = generate_artist_portraits.portrait_prompt(artist)
        pair = (artist_name, "self_portrait")
        if pair in seen_pairs:
            raise RuntimeError(f"Duplicate job detected for {artist_name} self_portrait")
        seen_pairs.add(pair)
        jobs.append(
            ImageJob(
                artist_name=artist_name,
                artist_id=artist_id,
                job_type="self_portrait",
                prompt=portrait,
            )
        )

        for index, prompt in enumerate(build_reference_prompts(artist), start=1):
            job_type = f"reference_{index}"
            pair = (artist_name, job_type)
            if pair in seen_pairs:
                raise RuntimeError(f"Duplicate job detected for {artist_name} {job_type}")
            seen_pairs.add(pair)
            jobs.append(
                ImageJob(
                    artist_name=artist_name,
                    artist_id=artist_id,
                    job_type=job_type,
                    prompt=prompt,
                )
            )

    return jobs


def write_jobs_manifest(jobs: list[ImageJob]) -> None:
    payload = [
        {
            "artist": job.artist_name,
            "type": job.job_type,
            "prompt": job.prompt,
        }
        for job in jobs
    ]
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def load_jobs_manifest(artists_by_name: dict[str, str]) -> list[ImageJob]:
    payload = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise RuntimeError(f"{JOBS_PATH} must contain a JSON array.")

    jobs: list[ImageJob] = []
    seen_pairs: set[tuple[str, str]] = set()

    for entry in payload:
        if not isinstance(entry, dict):
            raise RuntimeError("image_jobs.json contains a non-object entry.")
        artist_name = str(entry.get("artist") or "").strip()
        job_type = str(entry.get("type") or "").strip()
        prompt = str(entry.get("prompt") or "").strip()
        if not artist_name or not job_type or not prompt:
            raise RuntimeError("image_jobs.json contains an entry with missing artist, type, or prompt.")
        if "__PROMPT__" in prompt:
            raise RuntimeError(f"Unexpanded placeholder detected for {artist_name} {job_type}")
        if artist_name not in artists_by_name:
            raise RuntimeError(f"Artist not found in registry: {artist_name}")
        pair = (artist_name, job_type)
        if pair in seen_pairs:
            raise RuntimeError(f"Duplicate manifest entry for {artist_name} {job_type}")
        seen_pairs.add(pair)
        jobs.append(
            ImageJob(
                artist_name=artist_name,
                artist_id=artists_by_name[artist_name],
                job_type=job_type,
                prompt=prompt,
            )
        )

    return jobs


def checkpoint_loader_node(workflow_template: dict[str, Any]) -> dict[str, Any] | None:
    for node in workflow_template.values():
        if isinstance(node, dict) and node.get("class_type") in {"CheckpointLoaderSimple", "CheckpointLoader"}:
            return node
    return None


def available_remote_checkpoints(base_url: str) -> list[str]:
    payload = request_json("GET", f"{base_url.rstrip('/')}/object_info/CheckpointLoaderSimple")
    loader = payload.get("CheckpointLoaderSimple")
    if not isinstance(loader, dict):
        return []

    required = loader.get("input", {}).get("required", {})
    ckpt_name_config = required.get("ckpt_name")
    if (
        isinstance(ckpt_name_config, list)
        and ckpt_name_config
        and isinstance(ckpt_name_config[0], list)
    ):
        return [str(value) for value in ckpt_name_config[0] if isinstance(value, str) and value.strip()]
    return []


def prepare_workflow(base_url: str) -> dict[str, Any]:
    workflow_template = generate_illustrations.load_workflow_template(WORKFLOW_PATH)
    loader = checkpoint_loader_node(workflow_template)
    if loader is None:
        raise RuntimeError(f"Workflow is missing CheckpointLoaderSimple: {WORKFLOW_PATH}")

    available = available_remote_checkpoints(base_url)
    inputs = loader.setdefault("inputs", {})
    if not isinstance(inputs, dict):
        raise RuntimeError("Workflow checkpoint loader inputs must be a JSON object.")

    requested = str(inputs.get("ckpt_name") or "").strip()
    if available and requested not in available:
        inputs["ckpt_name"] = available[0]
    return workflow_template


def create_client(base_url: str) -> generate_illustrations.ComfyUIClient:
    workflow_template = prepare_workflow(base_url)
    return generate_illustrations.ComfyUIClient(base_url=base_url.rstrip("/"), workflow_template=workflow_template)


def ensure_png_bytes(image_bytes: bytes) -> None:
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("ComfyUI returned non-PNG bytes.")


def render_job(
    client: generate_illustrations.ComfyUIClient,
    job: ImageJob,
    render_options: generate_illustrations.ComfyUIRenderOptions,
) -> bytes:
    workflow = generate_illustrations.build_comfyui_prompt(
        copy.deepcopy(client.workflow_template),
        job.prompt,
        DEFAULT_RENDER_SIZE,
        job.output_prefix,
        render_options=render_options,
    )
    generate_illustrations.validate_comfyui_queue_workflow(workflow, job.prompt)

    queue_response = request_json(
        "POST",
        f"{client.base_url}/prompt",
        payload={"prompt": workflow},
    )
    prompt_id = queue_response.get("prompt_id")
    if not isinstance(prompt_id, str) or not prompt_id:
        raise RuntimeError(f"ComfyUI queue response did not include prompt_id: {queue_response!r}")

    started_at = time.monotonic()
    while True:
        if time.monotonic() - started_at > DEFAULT_RENDER_TIMEOUT_SECONDS:
            raise TimeoutError(f"Render exceeded {DEFAULT_RENDER_TIMEOUT_SECONDS} seconds for {job.artist_name} {job.job_type}")

        history = request_json("GET", f"{client.base_url}/history/{urllib_parse.quote(prompt_id, safe='')}")
        run_payload = history.get(prompt_id)
        if isinstance(run_payload, dict):
            status = run_payload.get("status")
            if isinstance(status, dict) and status.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI generation failed: {json.dumps(status, ensure_ascii=True, sort_keys=True)}")
            if "outputs" in run_payload:
                image_ref = generate_illustrations.extract_comfyui_image_ref(run_payload)
                query = urllib_parse.urlencode(image_ref)
                image_bytes = request_bytes(f"{client.base_url}/view?{query}")
                ensure_png_bytes(image_bytes)
                return image_bytes

        time.sleep(DEFAULT_POLL_INTERVAL_SECONDS)


def save_image(path: Path, image_bytes: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_bytes(image_bytes)
    tmp_path.replace(path)


def run_queue(jobs: list[ImageJob], base_url: str) -> RunStats:
    client = create_client(base_url)
    render_options = generate_illustrations.ComfyUIRenderOptions(
        steps=4,
        cfg=1.0,
        sampler_name="euler",
        scheduler="simple",
        batch_size=1,
        denoise=1.0,
        seed=None,
    )

    rendered = 0
    skipped_existing = 0

    for job in jobs:
        target = job.output_path
        print(f"START {job.artist_name} {job.job_type}")

        if target.exists() and target.stat().st_size > 0:
            skipped_existing += 1
            print(f"COMPLETE {job.artist_name} {job.job_type} (existing)")
            continue

        image_bytes: bytes | None = None
        last_error: Exception | None = None
        for attempt in range(1, 3):
            try:
                image_bytes = render_job(client, job, render_options)
                break
            except Exception as exc:
                last_error = exc
                if attempt == 1:
                    time.sleep(3)
                    continue
        if image_bytes is None:
            print(f"FAIL {job.artist_name} {job.job_type}: {last_error}")
            continue

        save_image(target, image_bytes)
        rendered += 1
        print(f"COMPLETE {job.artist_name} {job.job_type}")

    saved_images = sum(1 for job in jobs if job.output_path.exists() and job.output_path.stat().st_size > 0)
    artist_count = len({job.artist_id for job in jobs})
    return RunStats(
        artists=artist_count,
        expected_images=len(jobs),
        rendered=rendered,
        skipped_existing=skipped_existing,
        saved_images=saved_images,
        failures=len(jobs) - saved_images,
    )


def main() -> int:
    args = parse_args()
    try:
        jobs_from_registry = build_jobs()
        write_jobs_manifest(jobs_from_registry)

        artists_by_name = {job.artist_name: job.artist_id for job in jobs_from_registry if job.job_type == "self_portrait"}
        jobs = load_jobs_manifest(artists_by_name)
        expected_images = len(artists_by_name) * 6
        if len(jobs) != expected_images:
            raise RuntimeError(f"Expected {expected_images} jobs, found {len(jobs)}")

        if args.build_only:
            print(f"Artists: {len(artists_by_name)}")
            print(f"Images generated: 0")
            print(f"Failures: 0")
            return 0

        base_url = (os.getenv("COMFYUI_BASE_URL") or DEFAULT_COMFYUI_BASE_URL).strip().rstrip("/")
        print(f"Using COMFYUI_BASE_URL={base_url}")
        stats = run_queue(jobs, base_url)

        print(f"Artists: {stats.artists}")
        print(f"Images generated: {stats.saved_images}")
        print(f"Failures: {stats.failures}")

        return 0 if stats.saved_images == stats.expected_images and stats.failures == 0 else 1
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
