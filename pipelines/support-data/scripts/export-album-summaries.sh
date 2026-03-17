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

DB_PATH="$(resolve_dataset_path "billboard_200_albums" "data/raw/charts/billboard-200-albums-charts.db")"
WEB_PUBLIC_DATA_DIR="$(resolve_dataset_path "web_public_data" "apps/web/public/data")"
OUT_DIR="${WEB_PUBLIC_DATA_DIR}/albums"

START_YEAR="${1:-1960}"
END_YEAR="${2:-2024}"

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "Error: sqlite3 is required but not installed." >&2
  exit 1
fi

if [[ ! -f "${DB_PATH}" ]]; then
  echo "Error: database file not found: ${DB_PATH}" >&2
  exit 1
fi

if [[ ! "${START_YEAR}" =~ ^[0-9]{4}$ || ! "${END_YEAR}" =~ ^[0-9]{4}$ ]]; then
  echo "Error: start/end years must be 4-digit numbers." >&2
  exit 1
fi

if (( START_YEAR > END_YEAR )); then
  echo "Error: start year must be <= end year." >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

for YEAR in $(seq "${START_YEAR}" "${END_YEAR}"); do
  OUTPUT_FILE="${OUT_DIR}/${YEAR}.json"

  sqlite3 -json "${DB_PATH}" "
SELECT
  artist,
  album,
  MIN(CAST(rank AS INTEGER)) AS peak,
  COUNT(*) AS weeks
FROM albums
WHERE date BETWEEN '${YEAR}-01-01' AND '${YEAR}-12-31'
GROUP BY artist, album
ORDER BY peak
LIMIT 100;
" > "${OUTPUT_FILE}"

  if [[ ! -s "${OUTPUT_FILE}" ]]; then
    printf '[]\n' > "${OUTPUT_FILE}"
  fi

  echo "Wrote ${OUTPUT_FILE}"
done

echo "Album summaries exported for years ${START_YEAR}-${END_YEAR}."
run_lineage_generation
