# Retroverse Common Tasks

## Generate Magazine Issue

Run:

python scripts/build_issue.py --year <YEAR>

Output location:

retroverse-magazine/issues/<YEAR>/

---

## Generate Illustrations

python scripts/generate_illustrations.py --year <YEAR>

Images are cached to prevent regeneration.

---

## Update Cultural Data

Run ingestion scripts located in:

scripts/

These scripts update datasets in:

public/data/

---

## Run Chart Application

cd retroverse_chart

npm install
npm run dev

---

## Deploy Application

Build the application:

npm run build

Output is deployed to static hosting.

---

## Important

Do not regenerate images or magazine assets unless explicitly requested with a force flag.
