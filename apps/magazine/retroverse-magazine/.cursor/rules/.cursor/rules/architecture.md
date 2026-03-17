# Retroverse Architecture

Retroverse is a cultural time-machine platform composed of three main layers.

## 1. Data Layer

Canonical cultural data sources.

Primary datasets:

* Billboard Hot 100 chart history
* Movie and television metadata
* Video library metadata
* Cultural timeline events

Data scripts live in:
scripts/

Generated data is stored in:
public/data/

The data layer should be treated as the canonical source of truth.

---

## 2. Generation Layer

This layer produces generated artifacts from the data.

Example outputs:

* RetroVerse magazine issues
* illustration prompts
* curated playlists
* cultural summaries

Code for this layer lives in:

retroverse-magazine/

Important directories:

retroverse-magazine/scripts/
retroverse-magazine/templates/
retroverse-magazine/issues/

---

## 3. Application Layer

The application layer presents the data and generated content to users.

Primary web application:

retroverse_chart/

This application reads static datasets from:

public/data/

The web app should never directly modify the canonical data.

---

## Development Philosophy

1. Data must be deterministic.
2. Generation pipelines should be reproducible.
3. The web application is a presentation layer only.
4. Archived experiments should not be modified.

---

## Core Principle

Data → Generation → Application

Changes should flow in that direction only.
