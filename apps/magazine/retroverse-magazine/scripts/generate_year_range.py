#!/usr/bin/env python3
"""Generate RetroVerse issues across a year range with failure-tolerant orchestration."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SUPERVISOR_SCRIPT = SCRIPTS_DIR / "editorial_supervisor.py"
CONTEXT_DIR = PROJECT_ROOT / "issues" / "context"
PLANS_DIR = PROJECT_ROOT / "issues" / "plans"
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_PATH = LOGS_DIR / "year_generation_log.json"
SUMMARY_PATH = LOGS_DIR / "year_generation_summary.md"

WAREHOUSE_ROOT = Path("/Users/bobhopp/Sites/retroverse/data/raw/screen-culture/warehouse")
MOVIES_BY_YEAR_PATH = WAREHOUSE_ROOT / "movies_by_year.json"
TELEVISION_BY_YEAR_PATH = WAREHOUSE_ROOT / "television_by_year.json"


def parse_args() -> argparse.Namespace:
    current_year = datetime.now().year
    parser = argparse.ArgumentParser(description="Generate RetroVerse issues safely across a year range.")
    parser.add_argument("--start-year", type=int, default=1958, help="First issue year (default: 1958)")
    parser.add_argument(
        "--end-year",
        type=int,
        default=current_year,
        help=f"Last issue year (default: {current_year})",
    )
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_year_warehouse_map(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = read_json(path)
    except json.JSONDecodeError:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def check_required_inputs(year: int) -> tuple[bool, list[str]]:
    warnings: list[str] = []

    context_path = CONTEXT_DIR / f"{year}_context.json"
    plan_path = PLANS_DIR / f"{year}_narrative_plan.json"

    context_ok = context_path.exists()
    plan_ok = plan_path.exists()

    if not context_ok:
        warnings.append("context_file_not_found")
    if not plan_ok:
        warnings.append("narrative_plan_file_not_found")

    return context_ok and plan_ok, warnings


def check_optional_coverage(
    year: int,
    movies_by_year: dict[str, Any] | None,
    television_by_year: dict[str, Any] | None,
) -> list[str]:
    warnings: list[str] = []
    year_key = str(year)

    if movies_by_year is None:
        warnings.append("screen_culture_movies_unavailable")
    elif year_key not in movies_by_year:
        warnings.append("screen_culture_movies_missing_year")

    if television_by_year is None:
        warnings.append("screen_culture_television_unavailable")
    elif year_key not in television_by_year:
        warnings.append("screen_culture_television_missing_year")

    return warnings


def parse_articles_generated(output: str) -> int:
    patterns = [
        r"Articles finalized:\s*(\d+)",
        r"Articles generated:\s*(\d+)",
    ]
    for pattern in patterns:
        matches = list(re.finditer(pattern, output))
        if matches:
            return int(matches[-1].group(1))
    return 0


def parse_supervisor_warnings(output: str) -> list[str]:
    warnings: list[str] = []
    lowered = output.lower()

    if "screen/culture coverage is below thresholds" in lowered:
        warnings.append("screen_culture_coverage_incomplete")
    if "canonical music layer degraded" in lowered:
        warnings.append("canonical_music_layer_degraded")

    for raw_line in output.splitlines():
        line = raw_line.strip()
        line_lower = line.lower()
        if line.startswith("ERROR:"):
            warnings.append("pipeline_error_reported")
        if "screen/culture coverage is below thresholds" in line_lower:
            warnings.append("screen_culture_coverage_incomplete")
        if "canonical music layer degraded" in line_lower:
            warnings.append("canonical_music_layer_degraded")
        if line.startswith("- "):
            if "screen/culture" in line_lower:
                warnings.append("screen_culture_coverage_incomplete")
            if "billboard hot 100" in line_lower or "billboard 200" in line_lower or "audio features" in line_lower:
                warnings.append("canonical_music_layer_degraded")

    # Keep stable order while de-duplicating
    seen: set[str] = set()
    unique: list[str] = []
    for warning in warnings:
        if warning in seen:
            continue
        seen.add(warning)
        unique.append(warning)
    return unique


def run_supervisor_for_year(year: int) -> tuple[str, int, list[str], str]:
    cmd = [sys.executable, str(SUPERVISOR_SCRIPT), "--year", str(year)]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)

    output_parts = []
    if result.stdout:
        output_parts.append(result.stdout.strip())
    if result.stderr:
        output_parts.append(result.stderr.strip())
    output = "\n".join(part for part in output_parts if part)

    articles_generated = parse_articles_generated(output)
    warnings = parse_supervisor_warnings(output)

    if result.returncode == 0:
        return "SUCCESS", articles_generated, warnings, output
    return "FAILED_PIPELINE", 0, warnings, output


def now_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def summary_notes(warnings: list[str]) -> str:
    if not warnings:
        return "—"
    return "; ".join(warnings)


def render_summary(entries: list[dict[str, Any]]) -> str:
    attempted = len(entries)
    successful = sum(1 for entry in entries if entry["status"] == "SUCCESS")
    skipped = sum(1 for entry in entries if entry["status"].startswith("SKIPPED"))
    failed = sum(1 for entry in entries if entry["status"].startswith("FAILED"))

    lines: list[str] = []
    lines.append("# RetroVerse Year Generation Summary")
    lines.append("")
    lines.append(f"- Years attempted: {attempted}")
    lines.append(f"- Successful issues: {successful}")
    lines.append(f"- Skipped years: {skipped}")
    lines.append(f"- Failed years: {failed}")
    lines.append("")
    lines.append("| Year | Status | Articles | Notes |")
    lines.append("| ---- | ------ | -------- | ----- |")

    for entry in entries:
        status = str(entry.get("status", ""))
        if status == "SKIPPED_MISSING_CONTEXT":
            display_status = "SKIPPED"
        elif status == "FAILED_PIPELINE":
            display_status = "FAILED"
        else:
            display_status = status

        lines.append(
            f"| {entry['year']} | {display_status} | {entry['articles_generated']} | {summary_notes(entry.get('warnings', []))} |"
        )

    lines.append("")
    return "\n".join(lines)


def write_logs(entries: list[dict[str, Any]]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SUMMARY_PATH.write_text(render_summary(entries), encoding="utf-8")


def run_year_range(start_year: int, end_year: int) -> int:
    if start_year > end_year:
        print(f"ERROR: start year {start_year} must be <= end year {end_year}", file=sys.stderr)
        return 1

    movies_by_year = load_year_warehouse_map(MOVIES_BY_YEAR_PATH)
    television_by_year = load_year_warehouse_map(TELEVISION_BY_YEAR_PATH)

    entries: list[dict[str, Any]] = []

    for year in range(start_year, end_year + 1):
        print(f"Generating RetroVerse issue: {year}")

        required_ok, required_warnings = check_required_inputs(year)
        optional_warnings = check_optional_coverage(year, movies_by_year, television_by_year)

        if not required_ok:
            entry = {
                "year": year,
                "status": "SKIPPED_MISSING_CONTEXT",
                "articles_generated": 0,
                "warnings": required_warnings + optional_warnings,
                "timestamp": now_timestamp(),
            }
            entries.append(entry)
            print("Status: SKIPPED_MISSING_CONTEXT")
            print("Articles: 0")
            continue

        try:
            status, articles_generated, supervisor_warnings, _ = run_supervisor_for_year(year)
        except Exception as exc:  # pragma: no cover - defensive catch for controller safety
            status = "FAILED_PIPELINE"
            articles_generated = 0
            supervisor_warnings = [f"supervisor_exception:{type(exc).__name__}"]

        warnings = required_warnings + optional_warnings + supervisor_warnings
        # keep stable order and de-duplicate
        seen: set[str] = set()
        deduped: list[str] = []
        for warning in warnings:
            if warning in seen:
                continue
            seen.add(warning)
            deduped.append(warning)

        entry = {
            "year": year,
            "status": status,
            "articles_generated": articles_generated,
            "warnings": deduped,
            "timestamp": now_timestamp(),
        }
        entries.append(entry)

        print(f"Status: {status}")
        print(f"Articles: {articles_generated}")

    write_logs(entries)

    attempted = len(entries)
    successful = sum(1 for entry in entries if entry["status"] == "SUCCESS")
    skipped = sum(1 for entry in entries if entry["status"].startswith("SKIPPED"))
    failed = sum(1 for entry in entries if entry["status"].startswith("FAILED"))

    print("")
    print("RetroVerse generation complete")
    print(f"Years attempted: {attempted}")
    print(f"Successful issues: {successful}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")

    return 0


def main() -> int:
    args = parse_args()
    return run_year_range(args.start_year, args.end_year)


if __name__ == "__main__":
    raise SystemExit(main())
