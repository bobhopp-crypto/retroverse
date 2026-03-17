# Retroverse Project Rules

## Project Overview

This repository contains the Retroverse cultural time machine platform.

Major systems:

1. **retroverse_chart/**

   * Next.js web application
   * Displays Billboard chart history
   * Uses data from `/public/data/charts`

2. **retroverse-magazine/**

   * AI-generated retro magazine pipeline
   * Scripts generate cultural year issues

3. **public/**

   * Static site output
   * Contains deployable website assets

4. **scripts/**

   * Data ingestion pipelines
   * Billboard harvesting
   * cultural dataset processing

---

# Key Commands

## Run chart web app

cd retroverse_chart
npm install
npm run dev

## Build production charts site

cd retroverse_chart
npm run build

## Generate magazine issue

cd retroverse-magazine
python scripts/build_issue.py --year 1978

## Run full magazine pipeline

cd retroverse-magazine
python scripts/magazine_pipeline.py

## Update Billboard data

python scripts/harvest_billboard.py

---

# Data Locations

Charts data:
public/data/charts/

Magazine content:
retroverse-magazine/issues/

Magazine templates:
retroverse-magazine/templates/

---

# Development Guidelines

* Prefer editing TypeScript in `retroverse_chart`
* Avoid modifying archived code in `archive/`
* Output web content only inside `/public`
* Magazine generation scripts must remain deterministic

---

# Typical Tasks

### Fix chart UI bugs

Work inside:
retroverse_chart/components/

### Add new chart data

Modify:
scripts/harvest_billboard.py

### Update magazine layout

Edit:
retroverse-magazine/templates/

### Rebuild a specific issue

Run:
python scripts/build_issue.py --year <YEAR>

---

# Important

The repository contains archived prototype code in:

retroverse-magazine/archive/

These files are historical artifacts and should not be modified.
