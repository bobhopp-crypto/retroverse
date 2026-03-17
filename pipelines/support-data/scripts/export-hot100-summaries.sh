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

DB_PATH="$(resolve_dataset_path "billboard_hot_100" "data/raw/charts/billboard-hot-100.db")"
WEB_PUBLIC_DATA_DIR="$(resolve_dataset_path "web_public_data" "apps/web/public/data")"
OUT_DIR="${WEB_PUBLIC_DATA_DIR}/charts"

START_YEAR="${1:-1958}"
END_YEAR="${2:-2024}"

table_has_column() {
  local table_name="$1"
  local column_name="$2"
  sqlite3 "${DB_PATH}" "SELECT 1 FROM pragma_table_info('${table_name}') WHERE name='${column_name}' LIMIT 1;" | grep -q '^1$'
}

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

QUERY_MODE=""
SOURCE_LABEL=""
SOURCE_TABLE=""
DATE_COLUMN=""
ARTIST_COLUMN=""
TITLE_COLUMN=""
RANK_COLUMN=""

if table_has_column "charts" "date" && table_has_column "charts" "artist" && table_has_column "charts" "title" && table_has_column "charts" "rank"; then
  QUERY_MODE="flat"
  SOURCE_LABEL="charts"
  SOURCE_TABLE="charts"
  DATE_COLUMN="date"
  ARTIST_COLUMN="artist"
  TITLE_COLUMN="title"
  RANK_COLUMN="rank"
elif table_has_column "chart_positions" "issue_date" && table_has_column "chart_positions" "artist" && table_has_column "chart_positions" "title" && table_has_column "chart_positions" "rank"; then
  POSITION_YEAR_COUNT="$(sqlite3 "${DB_PATH}" "SELECT COUNT(DISTINCT substr(issue_date, 1, 4)) FROM chart_positions WHERE issue_date IS NOT NULL AND issue_date <> '';" | tr -d '[:space:]')"
  if [[ "${POSITION_YEAR_COUNT:-0}" =~ ^[0-9]+$ ]] && (( POSITION_YEAR_COUNT >= 5 )); then
    QUERY_MODE="flat"
    SOURCE_LABEL="chart_positions"
    SOURCE_TABLE="chart_positions"
    DATE_COLUMN="issue_date"
    ARTIST_COLUMN="artist"
    TITLE_COLUMN="title"
    RANK_COLUMN="rank"
  fi
fi

if [[ -z "${QUERY_MODE}" ]] && table_has_column "event_entry" "event_id" && table_has_column "event_entry" "work_id" && table_has_column "event_entry" "rank" && table_has_column "event" "event_id" && table_has_column "event" "issue_date" && table_has_column "work" "work_id" && table_has_column "work" "title_display" && table_has_column "work" "primary_person_id" && table_has_column "person" "person_id" && table_has_column "person" "name_display"; then
  QUERY_MODE="normalized"
  SOURCE_LABEL="event/event_entry/work/person"
fi

if [[ -z "${QUERY_MODE}" ]]; then
  echo "Error: could not find a compatible source table/columns for Hot 100 summaries." >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

for YEAR in $(seq "${START_YEAR}" "${END_YEAR}"); do
  OUTPUT_FILE="${OUT_DIR}/${YEAR}.json"
  TEMP_FILE="$(mktemp "${OUT_DIR}/${YEAR}.json.tmp.XXXXXX")"

  if [[ "${QUERY_MODE}" == "flat" ]]; then
    sqlite3 -json "${DB_PATH}" "
SELECT
  ${ARTIST_COLUMN} AS artist,
  ${TITLE_COLUMN} AS title,
  MIN(CAST(${RANK_COLUMN} AS INTEGER)) AS peak,
  COUNT(*) AS weeks
FROM ${SOURCE_TABLE}
WHERE ${DATE_COLUMN} BETWEEN '${YEAR}-01-01' AND '${YEAR}-12-31'
GROUP BY ${ARTIST_COLUMN}, ${TITLE_COLUMN}
ORDER BY peak
LIMIT 100;
" > "${TEMP_FILE}"
  else
    sqlite3 -json "${DB_PATH}" "
SELECT
  COALESCE(p.name_display, 'Unknown Artist') AS artist,
  w.title_display AS title,
  MIN(CAST(ee.rank AS INTEGER)) AS peak,
  COUNT(*) AS weeks
FROM event_entry ee
JOIN event e ON e.event_id = ee.event_id
JOIN work w ON w.work_id = ee.work_id
LEFT JOIN person p ON p.person_id = w.primary_person_id
WHERE e.issue_date BETWEEN '${YEAR}-01-01' AND '${YEAR}-12-31'
GROUP BY artist, title
ORDER BY peak
LIMIT 100;
" > "${TEMP_FILE}"
  fi

  if [[ ! -s "${TEMP_FILE}" ]]; then
    printf '[]\n' > "${TEMP_FILE}"
  fi

  mv "${TEMP_FILE}" "${OUTPUT_FILE}"
  echo "Wrote ${OUTPUT_FILE}"
done

echo "Source mode: ${QUERY_MODE} (${SOURCE_LABEL})"
echo "Hot 100 summaries exported for years ${START_YEAR}-${END_YEAR}."
run_lineage_generation
