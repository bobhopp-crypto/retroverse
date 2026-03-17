#!/usr/bin/env python3
"""Generate RetroVerse issue illustrations with reusable art-library support."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - depends on local environment
    load_dotenv = None


def load_environment() -> None:
    if load_dotenv is None:
        print(
            "python-dotenv is not installed. Install app requirements with "
            "`pip install -r requirements.txt` or install `python-dotenv` so "
            "optional ComfyUI settings can be loaded from .env.",
            file=sys.stderr,
        )
        return

    load_dotenv()

    script_path = Path(__file__).resolve()
    env_paths = [
        script_path.parents[1] / ".env",
        script_path.parents[4] / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)


load_environment()
PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMFYUI_BASE_URL = os.getenv("COMFYUI_BASE_URL", "http://127.0.0.1:8188").rstrip("/")
COMFYUI_WORKFLOW_PATH = Path(
    os.getenv(
        "RETROVERSE_COMFYUI_WORKFLOW",
        str(PROJECT_ROOT / "workflow" / "retroverse_comfyui_page_workflow.json"),
    )
)

STYLE_SUFFIX = (
    "RetroVerse editorial illustration, late-1970s print texture, period-correct palette, scene-only artwork, "
    "hand-inked linework, atmospheric background illustration, no readable production typography"
)
DEFAULT_NEGATIVE_PROMPT = (
    "text, watermark, logo, signature, readable typography, article paragraphs, magazine headlines, "
    "page titles, pull quotes, sidebars, chart tables, magazine layout elements"
)
MAX_RETRIES = 3
RENDER_TIMEOUT_SECONDS = 1800
LIBRARY_ART_TYPES = ["background", "scene", "environment"]
ISSUE_ART_TYPES = ["collage", "comic", "parody", "fake_ads", "marginal"]
LIBRARY_TYPE_TO_DIR = {
    "background": "backgrounds",
    "scene": "scenes",
    "environment": "environments",
}
STOPWORDS = {
    "the",
    "and",
    "with",
    "from",
    "for",
    "into",
    "that",
    "this",
    "style",
    "illustration",
    "magazine",
    "retro",
    "cartoon",
    "hand",
    "inked",
    "lines",
    "colors",
    "satirical",
    "caricature",
    "art",
}


class IllustrationBuildError(Exception):
    """Raised when required input data is missing or invalid."""


@dataclass
class ImageJob:
    target: Path
    mirror_target: Path
    prompt: str
    note: str
    art_type: str
    job_type: str = "library_asset"
    page_number: int | None = None
    page_slug: str | None = None
    prompt_path: Path | None = None
    allow_reuse: bool = True


@dataclass(frozen=True)
class ComfyUIClient:
    base_url: str
    workflow_template: dict[str, Any]


@dataclass(frozen=True)
class ComfyUIRenderOptions:
    steps: int | None = None
    cfg: float | None = None
    sampler_name: str | None = None
    scheduler: str | None = None
    batch_size: int | None = None
    denoise: float | None = None
    seed: int | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate issue illustrations from image prompts.")
    parser.add_argument("--year", default="1978", help="Issue year to generate (default: 1978)")
    parser.add_argument("--page", type=int, help="Generate only one page number from image_prompts.json")
    parser.add_argument("--model", default="gpt-image-1", help="OpenAI image model (default: gpt-image-1)")
    parser.add_argument("--size", default="2048x2048", help="Image size (default: 2048x2048)")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate files even if they already exist")
    parser.add_argument("--force", action="store_true", help="Regenerate all images regardless of cache")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IllustrationBuildError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise IllustrationBuildError(f"Invalid JSON in {path}: {exc}") from exc


def sha256_digest(path: Path) -> str | None:
    if not path.exists():
        return None

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def is_placeholder_image(path: Path, placeholder_path: Path, placeholder_digest: str | None = None) -> bool:
    if not path.exists() or not placeholder_path.exists():
        return False

    if path.stat().st_size != placeholder_path.stat().st_size:
        return False

    expected = placeholder_digest or sha256_digest(placeholder_path)
    actual = sha256_digest(path)
    return expected is not None and actual == expected


def ensure_directories(root: Path, year_dir: Path) -> None:
    library_root = root / "art-library"
    for folder in ("backgrounds", "scenes", "environments"):
        (library_root / folder).mkdir(parents=True, exist_ok=True)

    art_dir = year_dir / "art"
    for folder in ("images", "pages", "collage", "comic", "parody", "fake_ads", "marginals", "feature", "cover", "departments"):
        (art_dir / folder).mkdir(parents=True, exist_ok=True)


def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[a-zA-Z0-9']+", text.lower())
    tokens: list[str] = []
    for token in raw:
        clean = token.strip("'")
        if not clean:
            continue
        if clean in STOPWORDS:
            continue
        if len(clean) < 3 and not clean.isdigit():
            continue
        tokens.append(clean)
    return tokens


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "asset"


def prompt_subject(prompt: str) -> str:
    tokens = [token for token in tokenize(prompt) if not token.isdigit()][:4]
    return "_".join(tokens) if tokens else "asset"


def build_library_filename(art_type: str, prompt: str, year: str) -> str:
    subject = slugify(prompt_subject(prompt))
    return f"{art_type}_{subject}_1970s_{year}.png"


def build_prompt(base_prompt: str, extra: str = "") -> str:
    guardrail = (
        "Do not render article paragraphs, magazine headlines, page titles, pull quotes, sidebars, chart or table text, "
        "or magazine layout elements into the artwork."
    )
    joined = " ".join(part.strip() for part in (STYLE_SUFFIX, base_prompt, extra, guardrail) if part and part.strip())
    return joined.strip()


def normalize_size(size: str) -> str:
    supported_sizes = {"1024x1024", "1024x1536", "1536x1024", "768x768", "768x1152", "1152x768", "512x512", "auto"}
    normalized_size = size.strip().lower()
    if normalized_size in supported_sizes:
        return normalized_size

    match = re.fullmatch(r"(\d+)x(\d+)", size.strip())
    if not match:
        raise IllustrationBuildError(f"Invalid image size: {size}")
    width = int(match.group(1))
    height = int(match.group(2))
    if 384 <= width <= 2048 and 384 <= height <= 2048 and width % 64 == 0 and height % 64 == 0:
        return f"{width}x{height}"
    if width > height:
        return "1536x1024"
    return "1024x1536"


def art_type_for_relpath(rel_path: str) -> str:
    if rel_path.startswith("issues/") and "/art/pages/" in rel_path:
        return "page"
    if rel_path.startswith("pages/"):
        return "page"
    if rel_path.startswith("cover/"):
        return "background"
    if rel_path.startswith("feature/") or rel_path.startswith("departments/"):
        return "scene"
    if rel_path.startswith("collage/"):
        return "collage"
    if rel_path.startswith("comic/"):
        return "comic"
    if rel_path.startswith("parody/"):
        return "parody"
    if rel_path.startswith("fake_ads/"):
        return "fake_ads"
    if rel_path.startswith("marginals/"):
        return "marginal"
    return "environment"


def reuse_allowed(art_type: str, overwrite: bool, allow_reuse: bool) -> bool:
    if not allow_reuse:
        return False
    if art_type in LIBRARY_ART_TYPES:
        return True
    if art_type in ISSUE_ART_TYPES:
        return not overwrite
    return not overwrite


def prompt_preview(prompt: str, limit: int = 120) -> str:
    compact = " ".join(prompt.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "..."


def load_prompt_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise IllustrationBuildError(f"Missing prompt file: {path}") from exc


def mirror_job_output(job: ImageJob) -> None:
    if not job.target.exists():
        return
    if job.mirror_target == job.target:
        return
    job.mirror_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(job.target, job.mirror_target)


def should_skip_job(job: ImageJob, force: bool, placeholder_path: Path, placeholder_digest: str | None) -> bool:
    if force:
        return False
    if not job.mirror_target.exists():
        return False
    if job.job_type == "page_prompt" and is_placeholder_image(job.mirror_target, placeholder_path, placeholder_digest):
        return False
    return True


def restore_from_canonical_cache(job: ImageJob) -> None:
    if job.target == job.mirror_target:
        return
    job.target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(job.mirror_target, job.target)


def legacy_layout_images_for_page(year_dir: Path, page_number: int, page_slug: str) -> list[Path]:
    layout_html = year_dir / "layout" / f"page_{page_number:02d}_{page_slug}.html"
    if not layout_html.exists():
        return []
    html = layout_html.read_text(encoding="utf-8")
    paths: list[Path] = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
        if not src.startswith("../art/"):
            continue
        resolved = (layout_html.parent / src).resolve(strict=False)
        if resolved.exists():
            paths.append(resolved)
    return paths


def seed_page_job(root: Path, year_dir: Path, job: ImageJob) -> tuple[bool, str | None]:
    if job.job_type != "page_prompt" or job.page_number is None or not job.page_slug:
        return False, None

    legacy_images = legacy_layout_images_for_page(year_dir, job.page_number, job.page_slug)
    if legacy_images:
        source = legacy_images[0]
        job.target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve(strict=False) != job.target.resolve(strict=False):
            shutil.copy2(source, job.target)
        return True, str(source.relative_to(root))

    placeholder = root / "assets" / "placeholder.png"
    if placeholder.exists():
        job.target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(placeholder, job.target)
        return True, str(placeholder.relative_to(root))

    return False, None


def build_jobs(year_dir: Path, prompts: dict[str, Any], year: str, page_filter: int | None = None) -> list[ImageJob]:
    root = year_dir.parents[1]
    rows = prompts.get("prompts")
    if not isinstance(rows, list):
        raise IllustrationBuildError("image_prompts.json must include prompts[].")

    jobs: list[ImageJob] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        page_number = row.get("page_number")
        page_slug = row.get("page_slug")
        prompt_path_value = row.get("prompt_path")
        if not isinstance(page_number, int) or not isinstance(page_slug, str) or not isinstance(prompt_path_value, str):
            continue
        if page_filter is not None and page_number != page_filter:
            continue

        prompt_path = root / prompt_path_value
        prompt_text = load_prompt_text(prompt_path)

        image_path_value = row.get("image_path")
        if isinstance(image_path_value, str) and image_path_value.strip():
            image_rel = image_path_value.strip()
            target = root / image_rel
        else:
            target = year_dir / "art" / "pages" / f"page_{page_number:02d}.png"

        jobs.append(
            ImageJob(
                target=target,
                mirror_target=target,
                prompt=prompt_text,
                note=f"page {page_number:02d} / {page_slug}",
                art_type="page",
                job_type="page_prompt",
                page_number=page_number,
                page_slug=page_slug,
                prompt_path=prompt_path,
                allow_reuse=False,
            )
        )

    unique_jobs: dict[Path, ImageJob] = {}
    for job in jobs:
        unique_jobs[job.target] = job
    return list(unique_jobs.values())


def load_workflow_template(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IllustrationBuildError(
            f"Missing ComfyUI workflow template: {path}. "
            "Create /Users/bobhopp/AI/workflows/retroverse_pipeline.json before running illustration generation."
        ) from exc
    except json.JSONDecodeError as exc:
        raise IllustrationBuildError(f"Invalid ComfyUI workflow JSON in {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise IllustrationBuildError(f"ComfyUI workflow template must be a JSON object: {path}")
    return payload


def create_comfyui_client() -> ComfyUIClient:
    workflow_template = load_workflow_template(COMFYUI_WORKFLOW_PATH)
    return ComfyUIClient(base_url=COMFYUI_BASE_URL, workflow_template=workflow_template)


def comfyui_request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib_request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib_request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except urllib_error.URLError as exc:
        raise IllustrationBuildError(
            f"Unable to reach local ComfyUI server at {COMFYUI_BASE_URL}. "
            "Start the service and verify http://127.0.0.1:8188 is responding."
        ) from exc

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise IllustrationBuildError(f"ComfyUI returned invalid JSON from {url}: {exc}") from exc


def comfyui_request_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib_request.Request(url, method="GET")
    try:
        with urllib_request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except urllib_error.URLError as exc:
        raise IllustrationBuildError(f"Unable to download generated image from ComfyUI: {url}") from exc


def workflow_dimensions(_size: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", _size)
    if match:
        return int(match.group(1)), int(match.group(2))
    if _size == "1536x1024":
        return 1536, 1024
    if _size == "1024x1536":
        return 1024, 1536
    return 1024, 1024


def find_node_id_by_class(workflow: dict[str, Any], *class_types: str) -> str | None:
    for node_id, node in workflow.items():
        if not isinstance(node, dict):
            continue
        if node.get("class_type") in class_types:
            return str(node_id)
    return None


def referenced_node_id(node: dict[str, Any], input_name: str) -> str | None:
    inputs = node.get("inputs")
    if not isinstance(inputs, dict):
        return None
    value = inputs.get(input_name)
    if isinstance(value, list) and value and isinstance(value[0], str):
        return value[0]
    return None


def set_prompt_node_text(node: dict[str, Any], prompt: str) -> bool:
    class_type = node.get("class_type")
    inputs = node.setdefault("inputs", {})
    if not isinstance(inputs, dict):
        raise IllustrationBuildError("ComfyUI prompt node inputs must be a JSON object.")

    if class_type == "CLIPTextEncode":
        inputs["text"] = prompt
        return True
    if class_type == "CLIPTextEncodeFlux":
        inputs["clip_l"] = prompt
        inputs["t5xxl"] = prompt
        return True
    return False


def build_comfyui_prompt(
    workflow_template: dict[str, Any],
    prompt: str,
    size: str,
    output_prefix: str,
    render_options: ComfyUIRenderOptions | None = None,
) -> dict[str, Any]:
    workflow = copy.deepcopy(workflow_template)
    render_options = render_options or ComfyUIRenderOptions()

    width, height = workflow_dimensions(size)
    sampler_id = find_node_id_by_class(workflow, "KSampler")
    save_image_id = find_node_id_by_class(workflow, "SaveImage")
    if sampler_id is None or save_image_id is None:
        raise IllustrationBuildError(
            f"ComfyUI workflow template is missing required nodes in {COMFYUI_WORKFLOW_PATH}: "
            "expected at least KSampler and SaveImage nodes."
        )

    sampler = workflow.get(sampler_id)
    save_image = workflow.get(save_image_id)
    if not isinstance(sampler, dict) or not isinstance(save_image, dict):
        raise IllustrationBuildError("ComfyUI workflow nodes must be JSON objects.")

    sampler_inputs = sampler.setdefault("inputs", {})
    save_inputs = save_image.setdefault("inputs", {})
    if not isinstance(sampler_inputs, dict) or not isinstance(save_inputs, dict):
        raise IllustrationBuildError("ComfyUI workflow node inputs must be JSON objects.")

    positive_id = referenced_node_id(sampler, "positive")
    negative_id = referenced_node_id(sampler, "negative")
    latent_id = referenced_node_id(sampler, "latent_image")

    if positive_id is None or latent_id is None:
        raise IllustrationBuildError(
            f"ComfyUI workflow template is missing positive conditioning or latent image references in {COMFYUI_WORKFLOW_PATH}."
        )

    positive_node = workflow.get(positive_id)
    if not isinstance(positive_node, dict) or not set_prompt_node_text(positive_node, prompt):
        raise IllustrationBuildError(
            f"ComfyUI workflow template must route KSampler positive conditioning through CLIPTextEncode or CLIPTextEncodeFlux in {COMFYUI_WORKFLOW_PATH}."
        )

    if negative_id is not None:
        negative_node = workflow.get(negative_id)
        if isinstance(negative_node, dict) and negative_node.get("class_type") == "CLIPTextEncode":
            negative_inputs = negative_node.setdefault("inputs", {})
            if isinstance(negative_inputs, dict) and not str(negative_inputs.get("text") or "").strip():
                negative_inputs["text"] = DEFAULT_NEGATIVE_PROMPT

    latent_node = workflow.get(latent_id)
    if isinstance(latent_node, dict):
        latent_inputs = latent_node.setdefault("inputs", {})
        if isinstance(latent_inputs, dict):
            if "width" in latent_inputs:
                latent_inputs["width"] = width
            if "height" in latent_inputs:
                latent_inputs["height"] = height
            if render_options.batch_size is not None and "batch_size" in latent_inputs:
                latent_inputs["batch_size"] = render_options.batch_size

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
    sampler_inputs["seed"] = render_options.seed if render_options.seed is not None else int.from_bytes(os.urandom(8), "big") % (2**31)
    save_inputs["filename_prefix"] = output_prefix
    return workflow


def extract_comfyui_image_ref(history_payload: dict[str, Any]) -> dict[str, str]:
    outputs = history_payload.get("outputs")
    if not isinstance(outputs, dict):
        raise IllustrationBuildError("ComfyUI history payload did not include outputs.")

    for node_output in outputs.values():
        if not isinstance(node_output, dict):
            continue
        images = node_output.get("images")
        if not isinstance(images, list) or not images:
            continue
        first = images[0]
        if not isinstance(first, dict):
            continue
        filename = first.get("filename")
        subfolder = first.get("subfolder", "")
        image_type = first.get("type", "output")
        if isinstance(filename, str) and filename:
            return {
                "filename": filename,
                "subfolder": str(subfolder),
                "type": str(image_type),
            }

    raise IllustrationBuildError("ComfyUI completed without returning any saved images.")


def generate_with_comfyui(
    client: ComfyUIClient,
    model: str,
    size: str,
    prompt: str,
    output_prefix: str,
    render_options: ComfyUIRenderOptions | None = None,
) -> bytes:
    prompt_id = queue_with_comfyui(
        client,
        model,
        size,
        prompt,
        output_prefix,
        render_options=render_options,
    )

    start_time = time.monotonic()
    while True:
        elapsed = time.monotonic() - start_time
        if elapsed > RENDER_TIMEOUT_SECONDS:
            raise TimeoutError(
                f"Render exceeded {RENDER_TIMEOUT_SECONDS}. The ComfyUI job may still be running."
            )

        history = comfyui_request_json("GET", f"{client.base_url}/history/{prompt_id}", timeout=30)
        run_payload = history.get(prompt_id)
        if isinstance(run_payload, dict):
            status = run_payload.get("status")
            if isinstance(status, dict) and status.get("status_str") == "error":
                raise IllustrationBuildError(f"ComfyUI generation failed: {status}")
            if "outputs" in run_payload:
                image_ref = extract_comfyui_image_ref(run_payload)
                query = urllib_parse.urlencode(image_ref)
                return comfyui_request_bytes(f"{client.base_url}/view?{query}", timeout=60)

        time.sleep(1)


def queue_with_comfyui(
    client: ComfyUIClient,
    model: str,
    size: str,
    prompt: str,
    output_prefix: str,
    render_options: ComfyUIRenderOptions | None = None,
) -> str:
    del model

    workflow = build_comfyui_prompt(client.workflow_template, prompt, size, output_prefix, render_options=render_options)
    client_id = f"retroverse-{uuid.uuid4().hex}"
    queue_response = comfyui_request_json(
        "POST",
        f"{client.base_url}/prompt",
        payload={"prompt": workflow, "client_id": client_id},
        timeout=30,
    )
    prompt_id = queue_response.get("prompt_id")
    if not isinstance(prompt_id, str) or not prompt_id:
        raise IllustrationBuildError(f"ComfyUI queue response did not include prompt_id: {queue_response!r}")
    return prompt_id


def find_reusable_asset(root: Path, prompt: str, art_type: str) -> Path | None:
    library_root = root / "art-library"
    if not library_root.exists():
        return None

    candidate_dirs: list[Path]
    if art_type in LIBRARY_TYPE_TO_DIR:
        candidate_dirs = [library_root / LIBRARY_TYPE_TO_DIR[art_type]]
    else:
        candidate_dirs = [
            library_root / "backgrounds",
            library_root / "scenes",
            library_root / "environments",
        ]

    prompt_tokens = set(tokenize(prompt))
    if not prompt_tokens:
        return None

    best_score = 0
    best_path: Path | None = None

    for directory in candidate_dirs:
        if not directory.exists():
            continue
        for file_path in directory.glob("*.png"):
            file_tokens = set(tokenize(file_path.stem.replace("_", " ")))
            score = len(prompt_tokens & file_tokens)
            if score > best_score:
                best_score = score
                best_path = file_path

    return best_path if best_score >= 2 else None


def store_library_asset(root: Path, image_bytes: bytes, prompt: str, art_type: str, year: str) -> Path | None:
    if art_type not in LIBRARY_TYPE_TO_DIR:
        return None

    library_dir = root / "art-library" / LIBRARY_TYPE_TO_DIR[art_type]
    library_dir.mkdir(parents=True, exist_ok=True)
    target = library_dir / build_library_filename(art_type, prompt, year)

    if target.exists():
        stem = target.stem
        suffix = target.suffix
        idx = 2
        while True:
            candidate = target.with_name(f"{stem}_{idx}{suffix}")
            if not candidate.exists():
                target = candidate
                break
            idx += 1

    target.write_bytes(image_bytes)
    return target


def main() -> int:
    args = parse_args()
    force = args.force or args.overwrite
    root = PROJECT_ROOT
    year = str(args.year)
    year_dir = root / "issues" / year
    art_dir = year_dir / "art"
    prompts_path = art_dir / "image_prompts.json"
    placeholder_path = root / "assets" / "placeholder.png"
    placeholder_digest = sha256_digest(placeholder_path)

    ensure_directories(root, year_dir)

    try:
        prompts = load_json(prompts_path)
        if not isinstance(prompts, dict):
            raise IllustrationBuildError("image_prompts.json root must be an object.")
        jobs = build_jobs(year_dir, prompts, year, page_filter=args.page)
        if args.page is not None and not jobs:
            raise IllustrationBuildError(f"No illustration jobs found for page {args.page}.")
    except IllustrationBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    client: ComfyUIClient | None = None
    generated = 0
    skipped = 0
    reused = 0
    failed: list[Path] = []

    for job in jobs:
        filename = job.target.name
        if should_skip_job(job, force, placeholder_path, placeholder_digest):
            restore_from_canonical_cache(job)
            skipped += 1
            print(f"[ISSUE GENERATE] Skipped existing page image: {filename}")
            continue

        seeded, seed_source = seed_page_job(root, year_dir, job) if not force else (False, None)
        if seeded:
            if is_placeholder_image(job.target, placeholder_path, placeholder_digest):
                print(f"[ISSUE GENERATE] Placeholder seed detected for {filename}; continuing to real generation")
            else:
                reused += 1
                print(f"[ISSUE GENERATE] Seeded page image: {filename} <- {seed_source}")
                continue

        job.target.parent.mkdir(parents=True, exist_ok=True)
        job.mirror_target.parent.mkdir(parents=True, exist_ok=True)

        if job.page_number is not None and job.page_slug:
            print(f"Generating illustration for page {job.page_number} ({job.page_slug})")
        elif job.page_number is not None:
            print(f"Generating illustration for page {job.page_number}")
        else:
            print(f"Generating illustration for asset {job.note}")
        print(f"Prompt preview: {prompt_preview(job.prompt)}")

        if reuse_allowed(job.art_type, force, job.allow_reuse) and job.job_type == "library_asset":
            reusable = find_reusable_asset(root, job.prompt, job.art_type)
            if reusable:
                shutil.copy2(reusable, job.target)
                mirror_job_output(job)
                reused += 1
                print(f"[LIBRARY REUSE] {filename} <- {reusable.name}")
                continue

        print(f"[ISSUE GENERATE] Generating: {filename}")
        try:
            if client is None:
                client = create_comfyui_client()
            relative_prefix = job.target.relative_to(root).with_suffix("").as_posix()
            output_prefix = f"retroverse/{relative_prefix}_{uuid.uuid4().hex[:8]}"
            image_bytes = generate_with_comfyui(client, args.model, normalize_size(args.size), job.prompt, output_prefix)
            job.target.write_bytes(image_bytes)
            mirror_job_output(job)
            generated += 1

            library_copy = store_library_asset(root, image_bytes, job.prompt, job.art_type, year)
            if library_copy is not None:
                print(f"[LIBRARY REUSE] Stored: {library_copy.name}")

            print(f"[ISSUE GENERATE] Generated: {filename}")
        except Exception as exc:
            failed.append(job.target)
            print(f"[ISSUE GENERATE] Failed: {filename} ({exc})")

    print("Illustration generation complete.")
    print(f"Generated: {generated}")
    print(f"Reused:    {reused}")
    print(f"Skipped:   {skipped}")
    print(f"Failed:    {len(failed)}")
    if failed:
        print("[ISSUE GENERATE] Failed files:")
        for path in failed:
            print(f"[ISSUE GENERATE]   - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
