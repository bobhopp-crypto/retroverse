#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

run_lineage_generation() {
  python3 "${ROOT_DIR}/pipelines/support-data/scripts/generate_data_lineage.py"
}

resolve_dataset_path() {
  local dataset_id="$1"
  local fallback="$2"
  python3 - "${ROOT_DIR}" "${dataset_id}" "${fallback}" <<'PY'
from pathlib import Path
import sys

root_dir = Path(sys.argv[1])
dataset_id = sys.argv[2]
fallback = sys.argv[3]
lib_dir = root_dir / "pipelines" / "support-data" / "lib"
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

from registry_loader import get_dataset_path

print(get_dataset_path(dataset_id, fallback=fallback))
PY
}

MEDIA_INDEX_DIR="$(resolve_dataset_path "media_index" "data/derived/media-index")"
DEST_DIR="$(resolve_dataset_path "web_public_data" "apps/web/public/data")"
SOURCE_FILE="${MEDIA_INDEX_DIR}/output/video-index.json"
DEST_FILE="${DEST_DIR}/video-index.json"
SPLIT_SCRIPT="${ROOT_DIR}/pipelines/media-index/scripts/split-video-index-by-decade.mjs"

if [[ ! -f "${SOURCE_FILE}" ]]; then
  echo "Error: source file not found: ${SOURCE_FILE}" >&2
  exit 1
fi

mkdir -p "${DEST_DIR}"
cp "${SOURCE_FILE}" "${DEST_FILE}"
RETROVERSE_SKIP_LINEAGE=1 node "${SPLIT_SCRIPT}" "${DEST_FILE}" "${DEST_DIR}"

echo "Synced ${SOURCE_FILE} -> ${DEST_FILE}"
run_lineage_generation
