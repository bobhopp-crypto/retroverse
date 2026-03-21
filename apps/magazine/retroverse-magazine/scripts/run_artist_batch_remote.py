#!/usr/bin/env python3
"""Run the full RetroVerse artist registry batch against a remote RunPod ComfyUI pod."""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import parse as urllib_parse

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from art_department_common import LOGS_ROOT, append_log, ensure_art_department_directories
import generate_illustrations as illustration_runtime
from generate_illustrations import (
    COMFYUI_WORKFLOW_PATH,
    ComfyUIClient,
    ComfyUIRenderOptions,
    IllustrationBuildError,
    load_workflow_template,
)
from queue_artist_registry_assets import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CFG,
    DEFAULT_CHECKPOINT,
    DEFAULT_RENDER_SIZE,
    DEFAULT_SAMPLER,
    DEFAULT_SCHEDULER,
    DEFAULT_STEPS,
    ArtistBatchJob,
    ArtistBatchSubmission,
    RegistryValidationError,
    parse_seed,
    submit_artist_registry_batch,
)

LOG_NAME = "artist_batch_remote.log"
RUNPOD_GRAPHQL_URL = "https://api.runpod.io/graphql"
DEFAULT_POLL_INTERVAL = 5.0
DEFAULT_IDLE_TIMEOUT = 2700.0
DEFAULT_REQUEST_TIMEOUT = 30
DEFAULT_REQUEST_RETRIES = 4
DEFAULT_RETRY_DELAY_SECONDS = 3.0
LOCAL_HOSTS = {"127.0.0.1", "localhost", "0.0.0.0"}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass(frozen=True)
class PromptFailure:
    job: ArtistBatchJob
    error: str


@dataclass(frozen=True)
class BatchMonitorResult:
    completed_jobs: list[ArtistBatchJob]
    failed_jobs: list[PromptFailure]
    duration_seconds: float

    @property
    def completed_count(self) -> int:
        return len(self.completed_jobs)

    @property
    def failed_count(self) -> int:
        return len(self.failed_jobs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Queue and monitor the full RetroVerse artist registry batch on remote ComfyUI.")
    parser.add_argument("--artist", help="Run only one artist id from retroverse_artists.json.")
    parser.add_argument("--portrait-size", default=DEFAULT_RENDER_SIZE, help=f"Portrait render size (default: {DEFAULT_RENDER_SIZE}).")
    parser.add_argument("--reference-size", default=DEFAULT_RENDER_SIZE, help=f"Reference render size (default: {DEFAULT_RENDER_SIZE}).")
    parser.add_argument("--model", default=DEFAULT_CHECKPOINT, help=f"Checkpoint compatibility flag (default: {DEFAULT_CHECKPOINT}).")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS, help=f"ComfyUI sampler steps (default: {DEFAULT_STEPS}).")
    parser.add_argument("--sampler", default=DEFAULT_SAMPLER, help=f"ComfyUI sampler name (default: {DEFAULT_SAMPLER}).")
    parser.add_argument("--scheduler", default=DEFAULT_SCHEDULER, help=f"ComfyUI scheduler (default: {DEFAULT_SCHEDULER}).")
    parser.add_argument("--cfg", type=float, default=DEFAULT_CFG, help=f"Classifier-free guidance scale (default: {DEFAULT_CFG}).")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help=f"Latent batch size override (default: {DEFAULT_BATCH_SIZE}).")
    parser.add_argument("--denoise", type=float, default=1.0, help="ComfyUI denoise strength (default: 1.0).")
    parser.add_argument("--seed", default="random", help="Explicit seed or 'random' (default: random).")
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL, help=f"Seconds between queue polls (default: {DEFAULT_POLL_INTERVAL}).")
    parser.add_argument("--idle-timeout", type=float, default=DEFAULT_IDLE_TIMEOUT, help=f"Abort if no batch progress is seen for this many seconds (default: {DEFAULT_IDLE_TIMEOUT}).")
    parser.add_argument("--request-timeout", type=int, default=DEFAULT_REQUEST_TIMEOUT, help=f"HTTP timeout per ComfyUI/RunPod request in seconds (default: {DEFAULT_REQUEST_TIMEOUT}).")
    parser.add_argument("--request-retries", type=int, default=DEFAULT_REQUEST_RETRIES, help=f"Retry count for GET status polling (default: {DEFAULT_REQUEST_RETRIES}).")
    parser.add_argument("--skip-shutdown", action="store_true", help="Do not call the RunPod stop API after batch completion.")
    return parser.parse_args()


def log_message(message: str) -> None:
    print(message)
    append_log(LOG_NAME, message)


def require_remote_base_url(raw_value: str | None) -> str:
    base_url = (raw_value or "").strip().rstrip("/")
    if not base_url:
        raise ValueError("COMFYUI_BASE_URL is required and must point to the RunPod proxy URL.")

    parsed = urllib_parse.urlparse(base_url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host.endswith(".proxy.runpod.net"):
        raise ValueError("COMFYUI_BASE_URL must use the RunPod proxy format: https://<POD_ID>-8188.proxy.runpod.net")
    if host in LOCAL_HOSTS:
        raise ValueError("COMFYUI_BASE_URL must not point to localhost or another local bind address.")
    return base_url


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
    print(f"[DEBUG] Requesting: {url}")
    try:
        if method.upper() == "GET":
            response = SESSION.get(
                url,
                timeout=(10, 60),
                verify=False,
            )
        elif method.upper() == "POST":
            response = SESSION.post(
                url,
                json=payload,
                timeout=(10, 60),
                verify=False,
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print(f"[ERROR] Request failed: {e}")
        if e.response is not None:
            print(f"[ERROR] Status: {e.response.status_code}")
            print(f"[ERROR] Response snippet: {e.response.text[:2000]}")
        raise
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        raise


def check_comfyui(base_url: str) -> bool:
    session = create_session()
    base_url = base_url.rstrip("/")
    url = f"{base_url}/system_stats"

    print(f"[DEBUG] Checking ComfyUI at: {url}")
    try:
        response = session.get(
            url,
            timeout=(10, 60),
            verify=False,
        )

        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Response snippet: {response.text[:200]}")

        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        raise


def patch_comfyui_requests() -> None:
    def patched_comfyui_request_json(
        method: str,
        url: str,
        payload: dict[str, Any] | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        del timeout
        try:
            return request_json(method, url, payload=payload)
        except Exception as e:
            raise IllustrationBuildError(
                f"Unable to reach ComfyUI server at {url}. Verify the configured COMFYUI_BASE_URL is reachable and responding."
            ) from e

    illustration_runtime.comfyui_request_json = patched_comfyui_request_json


def workflow_checkpoint_name(workflow_template: dict[str, Any]) -> str | None:
    for node in workflow_template.values():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        if node.get("class_type") in {"CheckpointLoaderSimple", "CheckpointLoader"}:
            ckpt_name = inputs.get("ckpt_name")
            if isinstance(ckpt_name, str) and ckpt_name.strip():
                return ckpt_name.strip()
    return None


def find_workflow_node_ids(workflow_template: dict[str, Any], class_type: str) -> list[str]:
    node_ids: list[str] = []
    for node_id, node in workflow_template.items():
        if isinstance(node, dict) and node.get("class_type") == class_type:
            node_ids.append(str(node_id))
    return node_ids


def checkpoint_loader_node_id(workflow_template: dict[str, Any]) -> str | None:
    for class_type in ("CheckpointLoaderSimple", "CheckpointLoader"):
        node_ids = find_workflow_node_ids(workflow_template, class_type)
        if node_ids:
            return node_ids[0]
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


def validate_workflow_template_structure(workflow_template: dict[str, Any]) -> None:
    if not isinstance(workflow_template, dict) or not workflow_template:
        raise IllustrationBuildError("Workflow JSON is empty.")
    if not find_workflow_node_ids(workflow_template, "CLIPTextEncode"):
        raise IllustrationBuildError("Workflow JSON must include at least one CLIPTextEncode node.")
    if not find_workflow_node_ids(workflow_template, "KSampler"):
        raise IllustrationBuildError("Workflow JSON must include a KSampler node.")
    if checkpoint_loader_node_id(workflow_template) is None:
        raise IllustrationBuildError("Workflow JSON must include a model loader node.")


def prepare_remote_workflow_template(base_url: str, workflow_template: dict[str, Any]) -> dict[str, Any]:
    validate_workflow_template_structure(workflow_template)

    loader_id = checkpoint_loader_node_id(workflow_template)
    if loader_id is None:
        raise IllustrationBuildError("Workflow JSON must include a model loader node.")

    loader_node = workflow_template.get(loader_id)
    if not isinstance(loader_node, dict):
        raise IllustrationBuildError("Workflow model loader node must be a JSON object.")

    loader_inputs = loader_node.get("inputs")
    if not isinstance(loader_inputs, dict):
        raise IllustrationBuildError("Workflow model loader inputs must be a JSON object.")

    requested_checkpoint = str(loader_inputs.get("ckpt_name") or "").strip()
    available_checkpoints = available_remote_checkpoints(base_url)
    if available_checkpoints and requested_checkpoint not in available_checkpoints:
        fallback_checkpoint = available_checkpoints[0]
        log_message(
            "[ART BATCH REMOTE] remote checkpoint override "
            f"requested={requested_checkpoint or 'unset'} "
            f"using={fallback_checkpoint}"
        )
        loader_inputs["ckpt_name"] = fallback_checkpoint

    return workflow_template


def request_comfyui_json_with_retry(
    client: ComfyUIClient,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: int = DEFAULT_REQUEST_TIMEOUT,
    retries: int = DEFAULT_REQUEST_RETRIES,
    retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
) -> dict[str, Any]:
    attempts = 1 if method.upper() != "GET" else max(1, retries)
    url = f"{client.base_url}{path}"
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            del timeout
            return request_json(method.upper(), url, payload=payload)
        except IllustrationBuildError as exc:
            last_error = exc
            if attempt >= attempts:
                raise
            log_message(f"[ART BATCH REMOTE] retry {attempt}/{attempts} for {path}: {exc}")
            time.sleep(retry_delay_seconds * attempt)
        except Exception as e:
            last_error = e
            if attempt >= attempts:
                raise IllustrationBuildError(f"Unable to reach ComfyUI server at {url}. Verify the configured COMFYUI_BASE_URL is reachable and responding.") from e
            log_message(f"[ART BATCH REMOTE] retry {attempt}/{attempts} for {path}: {e}")
            time.sleep(retry_delay_seconds * attempt)

    assert last_error is not None
    raise last_error


def extract_prompt_ids(queue_entries: Any) -> set[str]:
    prompt_ids: set[str] = set()
    if not isinstance(queue_entries, list):
        return prompt_ids

    for entry in queue_entries:
        prompt_id = prompt_id_from_queue_entry(entry)
        if prompt_id:
            prompt_ids.add(prompt_id)
    return prompt_ids


def prompt_id_from_queue_entry(entry: Any) -> str | None:
    if isinstance(entry, dict):
        candidate = entry.get("prompt_id")
        if isinstance(candidate, str) and candidate:
            return candidate
        return None

    if isinstance(entry, list):
        if len(entry) > 1 and isinstance(entry[1], str) and entry[1]:
            return entry[1]
        for item in entry:
            if isinstance(item, str) and item:
                return item
    return None


def prompt_history_status(history_entry: dict[str, Any]) -> tuple[str, str | None]:
    status = history_entry.get("status")
    if isinstance(status, dict) and status.get("status_str") == "error":
        return "failed", json.dumps(status, sort_keys=True, ensure_ascii=True)
    if "outputs" in history_entry:
        return "completed", None
    return "pending", None


def monitor_batch(
    client: ComfyUIClient,
    submission: ArtistBatchSubmission,
    *,
    poll_interval: float,
    idle_timeout: float,
    request_timeout: int,
    request_retries: int,
) -> BatchMonitorResult:
    started_at = time.monotonic()
    last_activity = started_at
    last_progress_line = ""
    running_seen: set[str] = set()
    remaining_jobs = {job.prompt_id: job for job in submission.queued_jobs if job.prompt_id}
    completed_jobs: list[ArtistBatchJob] = []
    failed_jobs: list[PromptFailure] = []

    while remaining_jobs:
        queue_payload = request_comfyui_json_with_retry(
            client,
            "/queue",
            timeout=request_timeout,
            retries=request_retries,
        )
        running_ids = extract_prompt_ids(queue_payload.get("queue_running"))
        pending_ids = extract_prompt_ids(queue_payload.get("queue_pending"))
        active_ids = running_ids | pending_ids

        for prompt_id in sorted((running_ids & set(remaining_jobs.keys())) - running_seen):
            running_seen.add(prompt_id)
            job = remaining_jobs[prompt_id]
            log_message(f"[ART BATCH REMOTE] running {job.output_prefix} (prompt_id: {prompt_id})")
            last_activity = time.monotonic()

        resolved_any = False
        # A job is considered complete only after it leaves /queue and its history entry contains outputs or an error.
        for prompt_id in list(remaining_jobs.keys()):
            if prompt_id in active_ids:
                continue

            history_payload = request_comfyui_json_with_retry(
                client,
                f"/history/{urllib_parse.quote(prompt_id, safe='')}",
                timeout=request_timeout,
                retries=request_retries,
            )
            history_entry = history_payload.get(prompt_id)
            if not isinstance(history_entry, dict):
                continue

            status, error_text = prompt_history_status(history_entry)
            job = remaining_jobs[prompt_id]
            if status == "completed":
                completed_jobs.append(job)
                del remaining_jobs[prompt_id]
                resolved_any = True
                last_activity = time.monotonic()
                log_message(f"[ART BATCH REMOTE] completed {job.output_prefix} (prompt_id: {prompt_id})")
            elif status == "failed":
                failed_jobs.append(PromptFailure(job=job, error=error_text or "unknown ComfyUI error"))
                del remaining_jobs[prompt_id]
                resolved_any = True
                last_activity = time.monotonic()
                log_message(f"[ART BATCH REMOTE] failed {job.output_prefix} (prompt_id: {prompt_id}) {error_text}")

        progress_line = (
            "[ART BATCH REMOTE] progress "
            f"completed={len(completed_jobs)} failed={len(failed_jobs)} "
            f"running={len(running_ids)} pending={len(pending_ids)} remaining={len(remaining_jobs)}"
        )
        if progress_line != last_progress_line:
            log_message(progress_line)
            last_progress_line = progress_line

        if not remaining_jobs:
            break

        if not resolved_any and time.monotonic() - last_activity > idle_timeout:
            unresolved = ", ".join(sorted(remaining_jobs.keys())[:5])
            raise TimeoutError(f"Timed out waiting for ComfyUI batch completion. Remaining prompt_ids: {unresolved}")

        time.sleep(poll_interval)

    return BatchMonitorResult(
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        duration_seconds=time.monotonic() - started_at,
    )


def stop_runpod_pod(api_key: str, pod_id: str, *, timeout: int = DEFAULT_REQUEST_TIMEOUT) -> str:
    query = f"mutation {{ podStop(input: {{podId: {json.dumps(pod_id)}}}) {{ id desiredStatus }} }}"
    endpoint = f"{RUNPOD_GRAPHQL_URL}?api_key={urllib_parse.quote(api_key, safe='')}"
    try:
        print(f"[DEBUG] Requesting: {endpoint}")
        response = SESSION.post(
            endpoint,
            json={"query": query},
            timeout=(10, max(timeout, 60)),
            verify=False,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        raise RuntimeError(f"RunPod shutdown request failed: {e}") from e

    errors = payload.get("errors")
    if isinstance(errors, list) and errors:
        raise RuntimeError(f"RunPod shutdown request returned errors: {errors}")

    result = payload.get("data", {}).get("podStop")
    if not isinstance(result, dict):
        raise RuntimeError(f"RunPod shutdown response was missing podStop: {payload}")

    desired_status = result.get("desiredStatus")
    if not isinstance(desired_status, str) or not desired_status:
        raise RuntimeError(f"RunPod shutdown response was missing desiredStatus: {payload}")
    return desired_status


def completion_message(*, skip_shutdown: bool) -> str:
    if skip_shutdown:
        append_log(LOG_NAME, "shutdown skipped by flag; manual stop required")
        return "batch complete, stop pod manually"

    api_key = (os.getenv("RUNPOD_API_KEY") or "").strip()
    pod_id = (os.getenv("RUNPOD_POD_ID") or "").strip()
    if not api_key or not pod_id:
        append_log(LOG_NAME, "shutdown skipped; RUNPOD_API_KEY or RUNPOD_POD_ID missing")
        return "batch complete, stop pod manually"

    try:
        desired_status = stop_runpod_pod(api_key, pod_id)
    except Exception as exc:
        append_log(LOG_NAME, f"shutdown request failed for pod {pod_id}: {exc}")
        return "batch complete, stop pod manually"

    append_log(LOG_NAME, f"shutdown requested for pod {pod_id} desired_status={desired_status}")
    return f"batch complete, pod shutdown requested ({desired_status})"


def main() -> int:
    args = parse_args()
    ensure_art_department_directories()
    log_path = LOGS_ROOT / LOG_NAME

    try:
        base_url = require_remote_base_url(os.getenv("COMFYUI_BASE_URL"))
        patch_comfyui_requests()
        check_comfyui(base_url)
        workflow_template = prepare_remote_workflow_template(base_url, load_workflow_template(COMFYUI_WORKFLOW_PATH))
    except (IllustrationBuildError, ValueError) as exc:
        log_message(f"[ART BATCH REMOTE] configuration error: {exc}")
        return 1
    except Exception as e:
        log_message(f"[ART BATCH REMOTE] configuration error: {e}")
        return 1

    checkpoint_name = workflow_checkpoint_name(workflow_template) or "unknown"
    client = ComfyUIClient(base_url=base_url, workflow_template=workflow_template)

    try:
        system_stats = request_comfyui_json_with_retry(
            client,
            "/system_stats",
            timeout=args.request_timeout,
            retries=args.request_retries,
        )
    except IllustrationBuildError as exc:
        log_message(f"[ART BATCH REMOTE] ComfyUI health check failed: {exc}")
        return 1

    log_message(
        (
            "[ART BATCH REMOTE] start "
            f"base_url={base_url} "
            f"workflow={COMFYUI_WORKFLOW_PATH} "
            f"checkpoint={checkpoint_name} "
            f"log={log_path}"
        )
    )
    comfyui_version = system_stats.get("comfyui_version") if isinstance(system_stats, dict) else None
    if isinstance(comfyui_version, str) and comfyui_version:
        log_message(f"[ART BATCH REMOTE] ComfyUI reachable version={comfyui_version}")

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
            client=client,
            log_name=LOG_NAME,
        )
    except RegistryValidationError as exc:
        for error in exc.errors:
            log_message(f"[ART BATCH REMOTE] registry error: {error}")
        return 1
    except Exception as exc:
        log_message(f"[ART BATCH REMOTE] submission failed: {exc}")
        return 1

    if submission.failed_count:
        for job in submission.failed_jobs:
            log_message(
                f"[ART BATCH REMOTE] submission failure artist={job.artist_id} "
                f"job={job.output_prefix} error={job.error or 'unknown'}"
            )

    if submission.queued_count == 0:
        log_message("[ART BATCH REMOTE] no prompts were queued")
        return 1

    first_prompt_id = submission.queued_jobs[0].prompt_id or "unknown"
    log_message(
        "[ART BATCH REMOTE] queue submitted "
        f"queued={submission.queued_count} "
        f"submission_failed={submission.failed_count} "
        f"first_prompt_id={first_prompt_id} "
        "expected_output=art-department/<artist-id>/..."
    )

    try:
        monitor_result = monitor_batch(
            client,
            submission,
            poll_interval=args.poll_interval,
            idle_timeout=args.idle_timeout,
            request_timeout=args.request_timeout,
            request_retries=args.request_retries,
        )
    except Exception as exc:
        log_message(f"[ART BATCH REMOTE] monitoring failed: {exc}")
        return 1

    for failure in monitor_result.failed_jobs:
        log_message(
            f"[ART BATCH REMOTE] render failure artist={failure.job.artist_id} "
            f"job={failure.job.output_prefix} error={failure.error}"
        )

    log_message(
        "[ART BATCH REMOTE] summary "
        f"queued={submission.queued_count} "
        f"submission_failed={submission.failed_count} "
        f"completed={monitor_result.completed_count} "
        f"render_failed={monitor_result.failed_count} "
        f"duration_seconds={monitor_result.duration_seconds:.1f}"
    )

    final_message = completion_message(skip_shutdown=args.skip_shutdown)
    log_message(final_message)
    return 0 if submission.failed_count == 0 and monitor_result.failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
