#!/usr/bin/env python3
"""Generate dataset lineage documentation from data/registry/DATA_REGISTRY.yaml."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import REGISTRY_PATH, ROOT_DIR, load_registry


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_registry() -> dict[str, dict[str, Any]]:
    raw = load_registry()
    datasets = raw.get("datasets", {})
    if not isinstance(datasets, dict):
        raise ValueError("Registry datasets payload is not a mapping")

    normalized: dict[str, dict[str, Any]] = {}
    for dataset_id, meta in sorted(datasets.items()):
        meta_map = meta if isinstance(meta, dict) else {}
        normalized[str(dataset_id)] = {
            "type": str(meta_map.get("type", "")).strip() or "unknown",
            "path": str(meta_map.get("path", "")).strip(),
            "description": str(meta_map.get("description", "")).strip(),
            "owner": str(meta_map.get("owner_pipeline", "")).strip(),
            "inputs": _normalize_string_list(meta_map.get("inputs")),
            "consumers": _normalize_string_list(meta_map.get("consumers")),
        }
    return normalized


def _system_kind(system_id: str) -> str:
    if system_id.startswith("pipelines/"):
        return "pipeline"
    if system_id.startswith("apps/"):
        return "app"
    return "other"


def _dot_node_id(prefix: str, value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    return f"{prefix}_{safe or 'node'}"


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _dataset_label(dataset_id: str, meta: dict[str, Any]) -> str:
    parts = [dataset_id, f"type: {meta['type']}"]
    if meta["path"]:
        parts.append(meta["path"])
    return "\\n".join(parts)


def _system_label(system_id: str) -> str:
    return system_id


def _render_dot(datasets: dict[str, dict[str, Any]]) -> tuple[str, list[str]]:
    raw_ids = [dataset_id for dataset_id, meta in datasets.items() if meta["type"] == "raw"]
    derived_ids = [dataset_id for dataset_id, meta in datasets.items() if meta["type"] != "raw"]

    systems = {
        system_id
        for meta in datasets.values()
        for system_id in [meta.get("owner", ""), *meta.get("consumers", [])]
        if system_id
    }
    pipelines = sorted(system_id for system_id in systems if _system_kind(system_id) == "pipeline")
    apps = sorted(system_id for system_id in systems if _system_kind(system_id) == "app")
    other_systems = sorted(system_id for system_id in systems if _system_kind(system_id) == "other")

    unresolved_inputs: list[str] = []
    layer_order: list[str] = []
    lines = [
        "digraph data_lineage {",
        '  graph [rankdir=TB, fontname="Helvetica", fontsize=10, splines=true, overlap=false, nodesep=0.4, ranksep=0.8, newrank=true];',
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, color="#475569", fillcolor="#ffffff"];',
        '  edge [fontname="Helvetica", fontsize=9, color="#4b5563"];',
        "",
    ]

    if raw_ids:
        layer_order.append("layer_raw")
        lines.extend([
            "  subgraph cluster_raw {",
            '    label="Raw Datasets";',
            '    style="filled,rounded";',
            '    color="#bfdbfe";',
            '    fillcolor="#eff6ff";',
            '    layer_raw [label="", shape=point, width=0, height=0, style=invis];',
        ])
        for dataset_id in raw_ids:
            meta = datasets[dataset_id]
            lines.append(
                f'    {_dot_node_id("dataset", dataset_id)} '
                f'[fillcolor="#dbeafe", color="#60a5fa", label="{_dot_escape(_dataset_label(dataset_id, meta))}"];'
            )
        rank_nodes = " ".join([f"layer_raw", *[_dot_node_id("dataset", dataset_id) for dataset_id in raw_ids]])
        lines.append(f"    {{ rank=same; {rank_nodes}; }}")
        lines.extend(["  }", ""])

    if pipelines:
        layer_order.append("layer_pipelines")
        lines.extend([
            "  subgraph cluster_pipelines {",
            '    label="Pipelines";',
            '    style="filled,rounded";',
            '    color="#cbd5e1";',
            '    fillcolor="#f8fafc";',
            '    layer_pipelines [label="", shape=point, width=0, height=0, style=invis];',
        ])
        for system_id in pipelines:
            lines.append(
                f'    {_dot_node_id("system", system_id)} '
                f'[fillcolor="#e2e8f0", color="#94a3b8", label="{_dot_escape(_system_label(system_id))}"];'
            )
        rank_nodes = " ".join([f"layer_pipelines", *[_dot_node_id("system", system_id) for system_id in pipelines]])
        lines.append(f"    {{ rank=same; {rank_nodes}; }}")
        lines.extend(["  }", ""])

    if derived_ids:
        layer_order.append("layer_derived")
        lines.extend([
            "  subgraph cluster_derived {",
            '    label="Derived Datasets";',
            '    style="filled,rounded";',
            '    color="#fde68a";',
            '    fillcolor="#fffbeb";',
            '    layer_derived [label="", shape=point, width=0, height=0, style=invis];',
        ])
        for dataset_id in derived_ids:
            meta = datasets[dataset_id]
            lines.append(
                f'    {_dot_node_id("dataset", dataset_id)} '
                f'[fillcolor="#fef3c7", color="#f59e0b", label="{_dot_escape(_dataset_label(dataset_id, meta))}"];'
            )
        rank_nodes = " ".join([f"layer_derived", *[_dot_node_id("dataset", dataset_id) for dataset_id in derived_ids]])
        lines.append(f"    {{ rank=same; {rank_nodes}; }}")
        lines.extend(["  }", ""])

    if apps:
        layer_order.append("layer_apps")
        lines.extend([
            "  subgraph cluster_apps {",
            '    label="Applications";',
            '    style="filled,rounded";',
            '    color="#bbf7d0";',
            '    fillcolor="#f0fdf4";',
            '    layer_apps [label="", shape=point, width=0, height=0, style=invis];',
        ])
        for system_id in apps:
            lines.append(
                f'    {_dot_node_id("system", system_id)} '
                f'[fillcolor="#dcfce7", color="#4ade80", label="{_dot_escape(_system_label(system_id))}"];'
            )
        rank_nodes = " ".join([f"layer_apps", *[_dot_node_id("system", system_id) for system_id in apps]])
        lines.append(f"    {{ rank=same; {rank_nodes}; }}")
        lines.extend(["  }", ""])

    if other_systems:
        for system_id in other_systems:
            lines.append(
                f'  {_dot_node_id("system", system_id)} '
                f'[fillcolor="#f8fafc", color="#cbd5e1", label="{_dot_escape(_system_label(system_id))}"];'
            )
        lines.append("")

    for left, right in zip(layer_order, layer_order[1:]):
        lines.append(f"  {left} -> {right} [style=invis, weight=200];")
    if layer_order:
        lines.append("")

    for dataset_id, meta in datasets.items():
        dataset_node = _dot_node_id("dataset", dataset_id)
        owner = meta.get("owner", "")
        if owner:
            owner_node = _dot_node_id("system", owner)
            relation = "produces" if meta["type"] != "raw" else "maintains"
            style = "solid" if meta["type"] != "raw" else "dashed"
            lines.append(
                f'  {owner_node} -> {dataset_node} [label="{relation}", style="{style}", color="#2563eb"];'
            )

        for input_id in meta.get("inputs", []):
            if input_id not in datasets:
                unresolved_inputs.append(f"{dataset_id}: missing input dataset '{input_id}'")
                continue
            input_node = _dot_node_id("dataset", input_id)
            if owner:
                owner_node = _dot_node_id("system", owner)
                lines.append(
                    f'  {input_node} -> {owner_node} [label="input", color="#7c3aed"];'
                )
            else:
                lines.append(
                    f'  {input_node} -> {dataset_node} [label="upstream", style="dashed", color="#7c3aed"];'
                )

        for consumer in meta.get("consumers", []):
            consumer_node = _dot_node_id("system", consumer)
            lines.append(
                f'  {dataset_node} -> {consumer_node} [label="consumed by", color="#059669"];'
            )

    lines.append("}")
    return "\n".join(lines) + "\n", unresolved_inputs


def _render_markdown(
    datasets: dict[str, dict[str, Any]],
    unresolved_inputs: list[str],
    dot_path: Path,
    svg_path: Path,
    svg_rendered: bool,
) -> str:
    raw_ids = [dataset_id for dataset_id, meta in datasets.items() if meta["type"] == "raw"]
    derived_ids = [dataset_id for dataset_id, meta in datasets.items() if meta["type"] != "raw"]
    systems = {
        system_id
        for meta in datasets.values()
        for system_id in [meta.get("owner", ""), *meta.get("consumers", [])]
        if system_id
    }
    pipeline_ids = sorted(system_id for system_id in systems if _system_kind(system_id) == "pipeline")
    app_ids = sorted(system_id for system_id in systems if _system_kind(system_id) == "app")

    lines: list[str] = [
        "# Data Lineage",
        "",
        f"Generated from `{REGISTRY_PATH.relative_to(ROOT_DIR)}`.",
        "",
        "## Summary",
        "",
        f"- Datasets: {len(datasets)}",
        f"- Raw datasets: {len(raw_ids)}",
        f"- Derived datasets: {len(derived_ids)}",
        f"- Pipelines referenced: {len(pipeline_ids)}",
        f"- Apps referenced: {len(app_ids)}",
        f"- Graph file: `{dot_path.relative_to(ROOT_DIR)}`",
        f"- SVG file: `{svg_path.relative_to(ROOT_DIR)}`" if svg_rendered else "- SVG file: not rendered (Graphviz `dot` unavailable)",
        "",
        "The `inputs` field captures only registered internal dataset dependencies. External APIs, manual editorial inputs, and unregistered transient sources are not represented here.",
        "",
        "## Raw Datasets",
        "",
        "| Dataset | Owner | Consumers | Path |",
        "|---|---|---|---|",
    ]

    for dataset_id in raw_ids:
        meta = datasets[dataset_id]
        owner = meta.get("owner", "") or "unowned"
        consumers = ", ".join(meta.get("consumers", [])) or "none"
        path = meta.get("path", "") or "missing"
        lines.append(f"| `{dataset_id}` | `{owner}` | `{consumers}` | `{path}` |")

    lines.extend([
        "",
        "## Derived Datasets",
        "",
        "| Dataset | Owner | Inputs | Consumers | Path |",
        "|---|---|---|---|---|",
    ])

    for dataset_id in derived_ids:
        meta = datasets[dataset_id]
        owner = meta.get("owner", "") or "unowned"
        inputs = ", ".join(f"`{dataset}`" for dataset in meta.get("inputs", [])) or "none registered"
        consumers = ", ".join(meta.get("consumers", [])) or "none"
        path = meta.get("path", "") or "missing"
        lines.append(f"| `{dataset_id}` | `{owner}` | {inputs} | `{consumers}` | `{path}` |")

    lines.extend([
        "",
        "## Producer And Consumer Map",
        "",
    ])

    for system_id in sorted(systems):
        produced = [
            dataset_id
            for dataset_id, meta in datasets.items()
            if meta.get("owner", "") == system_id
        ]
        consumed = [
            dataset_id
            for dataset_id, meta in datasets.items()
            if system_id in meta.get("consumers", [])
        ]
        role = _system_kind(system_id)
        lines.append(f"### `{system_id}`")
        lines.append("")
        lines.append(f"- Kind: `{role}`")
        lines.append(f"- Produces or maintains: {', '.join(f'`{dataset}`' for dataset in produced) if produced else 'none'}")
        lines.append(f"- Consumes: {', '.join(f'`{dataset}`' for dataset in consumed) if consumed else 'none'}")
        lines.append("")

    if unresolved_inputs:
        lines.extend([
            "## Unresolved Input References",
            "",
        ])
        for message in unresolved_inputs:
            lines.append(f"- {message}")
        lines.append("")

    lines.extend([
        "## Automatic Lineage Generation",
        "",
        "The lineage graph is regenerated automatically at the end of successful runs for the support-data, media-index, and cards-1974 pipeline entrypoints.",
        f"The Graphviz DOT file at `{dot_path.relative_to(ROOT_DIR)}` is the canonical lineage artifact.",
        (
            f"The SVG companion at `{svg_path.relative_to(ROOT_DIR)}` is rendered automatically when Graphviz is installed."
            if svg_rendered
            else "The SVG companion is rendered automatically when Graphviz is installed; this run left the DOT file as the canonical artifact because `dot` was unavailable."
        ),
        "",
        "## Graph Rendering",
        "",
        "Render or refresh the SVG manually with:",
        "",
        "```bash",
        f"dot -Tsvg {dot_path.relative_to(ROOT_DIR)} -o {svg_path.relative_to(ROOT_DIR)}",
        "```",
        "",
    ])

    return "\n".join(lines)


def _render_svg(dot_path: Path, svg_path: Path) -> bool:
    dot_binary = shutil.which("dot")
    if dot_binary is None:
        print(
            "Graphviz 'dot' was not found. Install Graphviz to render SVG automatically "
            "(macOS: `brew install graphviz`, Ubuntu/Debian: `sudo apt-get install graphviz`)."
        )
        return False

    subprocess.run([dot_binary, "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True, cwd=ROOT_DIR)
    print(f"SVG graph written to: {svg_path}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate data lineage docs from DATA_REGISTRY.yaml")
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=ROOT_DIR / "docs" / "DATA_LINEAGE.md",
        help="Path to write the Markdown lineage report",
    )
    parser.add_argument(
        "--dot-out",
        type=Path,
        default=ROOT_DIR / "docs" / "DATA_LINEAGE_GRAPH.dot",
        help="Path to write the Graphviz DOT file",
    )
    parser.add_argument(
        "--svg-out",
        type=Path,
        default=None,
        help="Optional path to write the rendered SVG graph",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dot_path = args.dot_out.resolve()
    svg_path = args.svg_out.resolve() if args.svg_out else dot_path.with_suffix(".svg")
    datasets = _normalize_registry()
    dot_body, unresolved_inputs = _render_dot(datasets)

    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    dot_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.parent.mkdir(parents=True, exist_ok=True)

    dot_path.write_text(dot_body, encoding="utf-8")
    svg_rendered = _render_svg(dot_path, svg_path)
    markdown_body = _render_markdown(datasets, unresolved_inputs, dot_path, svg_path, svg_rendered)
    args.markdown_out.write_text(markdown_body, encoding="utf-8")

    print(f"Markdown lineage report written to: {args.markdown_out}")
    print(f"DOT graph written to: {dot_path}")
    if unresolved_inputs:
        print(f"Unresolved input references: {len(unresolved_inputs)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
