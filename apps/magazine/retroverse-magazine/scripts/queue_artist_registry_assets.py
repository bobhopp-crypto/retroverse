#!/usr/bin/env python3
"""Queue RetroVerse Art Department prompts to ComfyUI in one batch."""

from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import requests

from art_department_common import (
    PROJECT_ROOT,
    append_log,
    ensure_art_department_directories,
    load_registry,
    prompt_slug,
    validate_registry,
)
from generate_illustrations import (
    ComfyUIRenderOptions,
    IllustrationBuildError,
    normalize_size,
)

LOG_NAME = "art_department_comfyui_batch.log"
DEFAULT_RENDER_SIZE = "1024x1024"
DEFAULT_CHECKPOINT = "flux1-schnell-fp8.safetensors"
DEFAULT_STEPS = 4
DEFAULT_SAMPLER = "euler"
DEFAULT_SCHEDULER = "simple"
DEFAULT_CFG = 1.0
DEFAULT_BATCH_SIZE = 1
DEFAULT_COMFYUI_BASE_URL = os.getenv("COMFYUI_BASE_URL", "http://127.0.0.1:8188").rstrip("/")
WORKFLOW_TEMPLATE_PATH = PROJECT_ROOT / "workflow" / "workflow_template.json"

_WORKFLOW_TEMPLATE_CACHE: dict[str, Any] | None = None


class RegistryValidationError(ValueError):
    """Raised when the artist registry is missing required structure."""

    def __init__(self, errors: list[str]):
        super().__init__("\n".join(errors))
        self.errors = errors


@dataclass(frozen=True)
class ArtistBatchJob:
    artist_id: str
    artist_name: str
    job_type: str
    output_prefix: str
    prompt_text: str
    index: int | None = None
    prompt_id: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class ArtistBatchSubmission:
    artist_filter: str | None
    portrait_size: str
    reference_size: str
    render_options: ComfyUIRenderOptions
    queued_jobs: list[ArtistBatchJob]
    failed_jobs: list[ArtistBatchJob]

    @property
    def queued_count(self) -> int:
        return len(self.queued_jobs)

    @property
    def failed_count(self) -> int:
        return len(self.failed_jobs)


@dataclass(frozen=True)
class BatchQueueClient:
    base_url: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Queue all RetroVerse artist portrait and style-sheet prompts to ComfyUI.")
    parser.add_argument("--artist", help="Queue prompts for only one artist id.")
    parser.add_argument(
        "--portrait-size",
        default=DEFAULT_RENDER_SIZE,
        help=f"Portrait render size passed to ComfyUI (default: {DEFAULT_RENDER_SIZE}).",
    )
    parser.add_argument(
        "--reference-size",
        default=DEFAULT_RENDER_SIZE,
        help=f"Reference-sheet render size passed to ComfyUI (default: {DEFAULT_RENDER_SIZE}).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_CHECKPOINT,
        help="Compatibility option; queue submission still uses the checkpoint baked into the canonical workflow.",
    )
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS, help=f"ComfyUI sampler steps (default: {DEFAULT_STEPS}).")
    parser.add_argument(
        "--sampler",
        default=DEFAULT_SAMPLER,
        help=f"ComfyUI sampler name (default: {DEFAULT_SAMPLER}).",
    )
    parser.add_argument(
        "--scheduler",
        default=DEFAULT_SCHEDULER,
        help=f"ComfyUI scheduler (default: {DEFAULT_SCHEDULER}).",
    )
    parser.add_argument(
        "--cfg",
        type=float,
        default=DEFAULT_CFG,
        help=f"Classifier-free guidance scale (default: {DEFAULT_CFG}).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Latent batch size override (default: {DEFAULT_BATCH_SIZE}).",
    )
    parser.add_argument("--denoise", type=float, default=1.0, help="ComfyUI denoise strength (default: 1.0).")
    parser.add_argument("--seed", default="random", help="Explicit seed or 'random' (default: random).")
    return parser.parse_args()


def parse_seed(seed_value: str) -> int | None:
    normalized = seed_value.strip().lower()
    if normalized in {"", "random"}:
        return None
    return int(seed_value)


def load_workflow_template() -> dict[str, Any]:
    global _WORKFLOW_TEMPLATE_CACHE

    if _WORKFLOW_TEMPLATE_CACHE is not None:
        return deepcopy(_WORKFLOW_TEMPLATE_CACHE)

    try:
        payload = json.loads(WORKFLOW_TEMPLATE_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IllustrationBuildError(f"Missing ComfyUI workflow template: {WORKFLOW_TEMPLATE_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise IllustrationBuildError(f"Invalid ComfyUI workflow JSON in {WORKFLOW_TEMPLATE_PATH}: {exc}") from exc

    if not isinstance(payload, dict):
        raise IllustrationBuildError(f"ComfyUI workflow template must be a JSON object: {WORKFLOW_TEMPLATE_PATH}")
    if not isinstance(payload.get("nodes"), list) or not isinstance(payload.get("links"), list):
        raise IllustrationBuildError(
            f"ComfyUI workflow template must contain LiteGraph nodes[] and links[]: {WORKFLOW_TEMPLATE_PATH}"
        )

    _WORKFLOW_TEMPLATE_CACHE = payload
    return deepcopy(payload)


def workflow_dimensions(size: str) -> tuple[int, int]:
    normalized = normalize_size(size)
    if normalized == "auto":
        return 1024, 1024
    width_text, height_text = normalized.split("x", maxsplit=1)
    return int(width_text), int(height_text)


def workflow_nodes_by_id(workflow_template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = workflow_template.get("nodes")
    if not isinstance(nodes, list):
        raise IllustrationBuildError("Workflow template nodes[] must be a list.")

    indexed: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if node_id is None:
            continue
        indexed[str(node_id)] = node
    return indexed


def workflow_links_by_id(workflow_template: dict[str, Any]) -> dict[int, tuple[str, int]]:
    links = workflow_template.get("links")
    if not isinstance(links, list):
        raise IllustrationBuildError("Workflow template links[] must be a list.")

    indexed: dict[int, tuple[str, int]] = {}
    for link in links:
        if not isinstance(link, list) or len(link) < 6:
            continue
        link_id = link[0]
        origin_node_id = link[1]
        origin_slot = link[2]
        if not isinstance(link_id, int):
            continue
        indexed[link_id] = (str(origin_node_id), int(origin_slot))
    return indexed


def find_first_node_of_type(workflow_template: dict[str, Any], node_type: str) -> dict[str, Any]:
    for node in workflow_nodes_by_id(workflow_template).values():
        if node.get("type") == node_type:
            return node
    raise IllustrationBuildError(f"Workflow template is missing required node type {node_type}: {WORKFLOW_TEMPLATE_PATH}")


def node_input_descriptor(node: dict[str, Any], input_name: str) -> dict[str, Any]:
    for item in node.get("inputs", []):
        if isinstance(item, dict) and item.get("name") == input_name:
            return item
    raise IllustrationBuildError(
        f"Workflow template node {node.get('id')} ({node.get('type')}) is missing input {input_name}: {WORKFLOW_TEMPLATE_PATH}"
    )


def linked_source_node_id(
    workflow_template: dict[str, Any],
    node: dict[str, Any],
    input_name: str,
) -> str:
    descriptor = node_input_descriptor(node, input_name)
    link_id = descriptor.get("link")
    if not isinstance(link_id, int):
        raise IllustrationBuildError(
            f"Workflow template node {node.get('id')} ({node.get('type')}) is missing a link for {input_name}: {WORKFLOW_TEMPLATE_PATH}"
        )

    link = workflow_links_by_id(workflow_template).get(link_id)
    if link is None:
        raise IllustrationBuildError(f"Workflow template link {link_id} was not found in {WORKFLOW_TEMPLATE_PATH}")
    return link[0]


def widget_inputs_for_node(node: dict[str, Any]) -> dict[str, Any]:
    node_type = str(node.get("type") or "")
    values = node.get("widgets_values")
    if not isinstance(values, list):
        values = []

    if node_type == "KSampler":
        result: dict[str, Any] = {}
        if len(values) > 0:
            result["seed"] = values[0]
        if len(values) > 2:
            result["steps"] = values[2]
        if len(values) > 3:
            result["cfg"] = values[3]
        if len(values) > 4:
            result["sampler_name"] = values[4]
        if len(values) > 5:
            result["scheduler"] = values[5]
        if len(values) > 6:
            result["denoise"] = values[6]
        return result

    widget_index = 0
    result: dict[str, Any] = {}
    for item in node.get("inputs", []):
        if not isinstance(item, dict):
            continue
        if item.get("link") is not None:
            continue
        if "widget" not in item:
            continue
        if widget_index >= len(values):
            break
        name = item.get("name")
        if isinstance(name, str) and name:
            result[name] = values[widget_index]
        widget_index += 1
    return result


def build_prompt_workflow(
    workflow_template: dict[str, Any],
    *,
    model: str,
    size: str,
    prompt: str,
    output_prefix: str,
    render_options: ComfyUIRenderOptions,
) -> dict[str, Any]:
    nodes_by_id = workflow_nodes_by_id(workflow_template)
    links_by_id = workflow_links_by_id(workflow_template)

    if not nodes_by_id:
        raise IllustrationBuildError(f"Workflow template contains no nodes: {WORKFLOW_TEMPLATE_PATH}")

    prompt_workflow: dict[str, Any] = {}
    for node_id, node in nodes_by_id.items():
        class_type = node.get("type")
        if not isinstance(class_type, str) or not class_type:
            raise IllustrationBuildError(f"Workflow node {node_id} is missing type in {WORKFLOW_TEMPLATE_PATH}")

        inputs: dict[str, Any] = {}
        for item in node.get("inputs", []):
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            link_id = item.get("link")
            if not isinstance(name, str) or not name:
                continue
            if isinstance(link_id, int):
                link = links_by_id.get(link_id)
                if link is None:
                    raise IllustrationBuildError(f"Workflow template link {link_id} was not found in {WORKFLOW_TEMPLATE_PATH}")
                inputs[name] = [link[0], link[1]]

        inputs.update(widget_inputs_for_node(node))
        prompt_workflow[node_id] = {
            "inputs": inputs,
            "class_type": class_type,
        }

    sampler_node = find_first_node_of_type(workflow_template, "KSampler")
    model_loader_node = find_first_node_of_type(workflow_template, "CheckpointLoaderSimple")
    save_node = find_first_node_of_type(workflow_template, "SaveImage")
    positive_node_id = linked_source_node_id(workflow_template, sampler_node, "positive")
    latent_node_id = linked_source_node_id(workflow_template, sampler_node, "latent_image")

    positive_node = prompt_workflow.get(positive_node_id)
    if not isinstance(positive_node, dict) or positive_node.get("class_type") != "CLIPTextEncode":
        raise IllustrationBuildError(
            f"Workflow template positive prompt path must resolve to CLIPTextEncode in {WORKFLOW_TEMPLATE_PATH}"
        )

    positive_inputs = positive_node.setdefault("inputs", {})
    if not isinstance(positive_inputs, dict):
        raise IllustrationBuildError("Positive CLIPTextEncode inputs must be a JSON object.")
    positive_inputs["text"] = prompt

    width, height = workflow_dimensions(size)
    latent_prompt_node = prompt_workflow.get(latent_node_id)
    if isinstance(latent_prompt_node, dict):
        latent_inputs = latent_prompt_node.setdefault("inputs", {})
        if isinstance(latent_inputs, dict):
            latent_inputs["width"] = width
            latent_inputs["height"] = height
            if render_options.batch_size is not None:
                latent_inputs["batch_size"] = render_options.batch_size

    sampler_inputs = prompt_workflow[str(sampler_node["id"])]["inputs"]
    if render_options.steps is not None:
        sampler_inputs["steps"] = render_options.steps
    if render_options.cfg is not None:
        sampler_inputs["cfg"] = render_options.cfg
    if render_options.sampler_name is not None:
        sampler_inputs["sampler_name"] = render_options.sampler_name
    if render_options.scheduler is not None:
        sampler_inputs["scheduler"] = render_options.scheduler
    if render_options.denoise is not None:
        sampler_inputs["denoise"] = render_options.denoise
    sampler_inputs["seed"] = (
        render_options.seed
        if render_options.seed is not None
        else int.from_bytes(os.urandom(8), "big") % (2**31)
    )

    model_loader_inputs = prompt_workflow[str(model_loader_node["id"])]["inputs"]
    if model.strip():
        model_loader_inputs["ckpt_name"] = model.strip()

    save_inputs = prompt_workflow[str(save_node["id"])]["inputs"]
    save_inputs["filename_prefix"] = output_prefix

    return prompt_workflow


def queue_workflow(base_url: str, workflow: dict[str, Any]) -> str:
    url = base_url.rstrip("/") + "/prompt"
    print("POST URL:", url)
    response = requests.post(
        url,
        json={"prompt": workflow},
        headers={"Content-Type": "application/json"},
        timeout=120,
        verify=True,
    )
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text[:500])
    response.raise_for_status()

    queue_response = response.json()
    prompt_id = queue_response.get("prompt_id")
    if not isinstance(prompt_id, str) or not prompt_id:
        raise IllustrationBuildError(f"ComfyUI queue response did not include prompt_id: {queue_response!r}")
    return prompt_id


def load_batch_artists(artist_id: str | None = None) -> list[dict[str, Any]]:
    payload = load_registry()
    errors = validate_registry(payload)
    if errors:
        raise RegistryValidationError(errors)

    artists = [artist for artist in payload.get("artists", []) if isinstance(artist, dict)]
    if artist_id:
        artists = [artist for artist in artists if artist.get("id") == artist_id]
        if not artists:
            raise ValueError(f"artist id not found: {artist_id}")
    return artists


def queue_job(
    client,
    *,
    model: str,
    size: str,
    prompt: str,
    output_prefix: str,
    render_options: ComfyUIRenderOptions,
) -> str:
    workflow_template = load_workflow_template()
    workflow = build_prompt_workflow(
        workflow_template,
        model=model,
        size=size,
        prompt=prompt,
        output_prefix=output_prefix,
        render_options=render_options,
    )
    base_url = str(getattr(client, "base_url", DEFAULT_COMFYUI_BASE_URL) or DEFAULT_COMFYUI_BASE_URL).rstrip("/")
    return queue_workflow(base_url, workflow)


def submit_artist_registry_batch(
    *,
    artist: str | None = None,
    portrait_size: str = DEFAULT_RENDER_SIZE,
    reference_size: str = DEFAULT_RENDER_SIZE,
    model: str = DEFAULT_CHECKPOINT,
    render_options: ComfyUIRenderOptions | None = None,
    client=None,
    log_name: str = LOG_NAME,
) -> ArtistBatchSubmission:
    ensure_art_department_directories()
    artists = load_batch_artists(artist)
    normalized_portrait_size = normalize_size(portrait_size)
    normalized_reference_size = normalize_size(reference_size)
    render_options = render_options or ComfyUIRenderOptions()
    client = client or BatchQueueClient(base_url=DEFAULT_COMFYUI_BASE_URL)

    append_log(
        log_name,
        (
            "start batch "
            f"artist={artist or 'ALL'} "
            f"portrait_size={normalized_portrait_size} reference_size={normalized_reference_size} "
            f"steps={render_options.steps} sampler={render_options.sampler_name} scheduler={render_options.scheduler} "
            f"cfg={render_options.cfg} batch_size={render_options.batch_size} denoise={render_options.denoise} "
            f"seed={render_options.seed if render_options.seed is not None else 'random'} "
            f"base_url={getattr(client, 'base_url', 'unknown')}"
        ),
    )

    queued_jobs: list[ArtistBatchJob] = []
    failed_jobs: list[ArtistBatchJob] = []

    for artist_record in artists:
        artist_id = str(artist_record["id"])
        artist_name = str(artist_record.get("display_name") or artist_id)

        portrait_prompt = str(artist_record.get("self_portrait_prompt") or "").strip()
        if portrait_prompt:
            output_prefix = f"art-department/{artist_id}/00-self-portrait"
            try:
                prompt_id = queue_job(
                    client,
                    model=model,
                    size=normalized_portrait_size,
                    prompt=portrait_prompt,
                    output_prefix=output_prefix,
                    render_options=render_options,
                )
                job = ArtistBatchJob(
                    artist_id=artist_id,
                    artist_name=artist_name,
                    job_type="portrait",
                    output_prefix=output_prefix,
                    prompt_text=portrait_prompt,
                    prompt_id=prompt_id,
                )
                queued_jobs.append(job)
                print(f"[ART BATCH] Queued portrait: {artist_name} -> /{output_prefix} (prompt_id: {prompt_id})")
                append_log(log_name, f"queued {artist_id}/00-self-portrait (prompt_id: {prompt_id})")
            except Exception as exc:
                job = ArtistBatchJob(
                    artist_id=artist_id,
                    artist_name=artist_name,
                    job_type="portrait",
                    output_prefix=output_prefix,
                    prompt_text=portrait_prompt,
                    error=str(exc),
                )
                failed_jobs.append(job)
                print(f"[ART BATCH] Failed portrait: {artist_name} ({exc})")
                append_log(log_name, f"failed {artist_id}/00-self-portrait: {exc}")

        reference_prompts = artist_record.get("reference_scene_prompts", [])
        if not isinstance(reference_prompts, list):
            job = ArtistBatchJob(
                artist_id=artist_id,
                artist_name=artist_name,
                job_type="reference",
                output_prefix=f"art-department/{artist_id}",
                prompt_text="",
                error="reference_scene_prompts is not a list",
            )
            failed_jobs.append(job)
            print(f"[ART BATCH] Failed references: {artist_name} (reference_scene_prompts is not a list)")
            append_log(log_name, f"failed {artist_id}: reference_scene_prompts is not a list")
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
                    model=model,
                    size=normalized_reference_size,
                    prompt=prompt_text,
                    output_prefix=output_prefix,
                    render_options=render_options,
                )
                job = ArtistBatchJob(
                    artist_id=artist_id,
                    artist_name=artist_name,
                    job_type="reference",
                    output_prefix=output_prefix,
                    prompt_text=prompt_text,
                    index=index,
                    prompt_id=prompt_id,
                )
                queued_jobs.append(job)
                print(f"[ART BATCH] Queued reference: {artist_name} -> /{output_prefix} (prompt_id: {prompt_id})")
                append_log(log_name, f"queued {artist_id}/{index:02d}-{slug} (prompt_id: {prompt_id})")
            except Exception as exc:
                job = ArtistBatchJob(
                    artist_id=artist_id,
                    artist_name=artist_name,
                    job_type="reference",
                    output_prefix=output_prefix,
                    prompt_text=prompt_text,
                    index=index,
                    error=str(exc),
                )
                failed_jobs.append(job)
                print(f"[ART BATCH] Failed reference: {artist_name} [{index}] ({exc})")
                append_log(log_name, f"failed {artist_id}/{index:02d}-{slug}: {exc}")

    return ArtistBatchSubmission(
        artist_filter=artist,
        portrait_size=normalized_portrait_size,
        reference_size=normalized_reference_size,
        render_options=render_options,
        queued_jobs=queued_jobs,
        failed_jobs=failed_jobs,
    )


def main() -> int:
    args = parse_args()
    render_options = ComfyUIRenderOptions(
        steps=args.steps,
        cfg=args.cfg,
        sampler_name=args.sampler,
        scheduler=args.scheduler,
        batch_size=args.batch_size,
        denoise=args.denoise,
        seed=parse_seed(args.seed),
    )
    try:
        submission = submit_artist_registry_batch(
            artist=args.artist,
            portrait_size=args.portrait_size,
            reference_size=args.reference_size,
            model=args.model,
            render_options=render_options,
            log_name=LOG_NAME,
        )
    except RegistryValidationError as exc:
        for error in exc.errors:
            print(f"ERROR: {error}")
        return 1
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    if submission.failed_count:
        print(f"Failed to queue {submission.failed_count} artist prompt jobs.")
    print(f"Queued {submission.queued_count} artist prompt jobs to ComfyUI.")
    print("ComfyUI will process the queue automatically.")
    return 0 if submission.failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
