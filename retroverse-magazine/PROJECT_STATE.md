# RetroVerse Magazine Project State

## Purpose
RetroVerse Magazine is an annual cultural magazine generated from structured data sources including Billboard charts and cultural event datasets.

Each issue represents a single year.

Example:
1978 issue = cultural highlights of 1978.

-------------------------------------

## Data Sources

Billboard charts database  
raw-data/billboard-hot-100.db

Billboard album charts  
raw-data/billboard-200-albums-charts.db

RetroVerse year master dataset  
retroverse-output/retroverse_year_master_1958_2024.json

Year-end chart exports  
retroverse-output/*.csv

Cultural events datasets  
cultural_events_*.json

Chart statistics
artifacts/output/billboard/

-------------------------------------

## Data Inventory

The full RetroVerse data inventory is documented in:

DATA_INVENTORY.md

All scripts that need to locate datasets should consult:
1. DATA_SOURCES.yaml for canonical paths
2. DATA_INVENTORY.md for discovered files and notes

Articles must be grounded in RetroVerse datasets.
External research may be used later for background context, but chart facts must always come from the internal database.

## Data Update Policy

The data inventory should be refreshable by script.
Issue context files are generated from canonical data sources and should be considered build artifacts.

## Data Brain Status

Data Brain v0 complete.
Billboard 200 integration added.
Sonic profile system added.
Source integrity reporting added.

## Screen & Culture Warehouse

RetroVerse now includes a dedicated screen/culture warehouse layer for movies and television data under:

/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/

### Source Layering

- canonical_local
- licensed_or_official
- direct_api
- reference_derived
- missing

### Trust + Provenance Rules

Stronger trust layers are never silently overwritten by weaker ones.
Each record and major field stores provenance entries including source name, source type, source identifier/URL, and trust level.

### Popularity vs Critical Signals

Popularity signals and critical/acclaim signals are tracked separately.
This allows editorial planning to distinguish audience reach from critical reception.

### Coverage Caveat

Historical TV viewership data is often patchier in open datasets than movie data.
Sparse TV metrics are acceptable when clearly labeled with provenance and missing markers.

-------------------------------------

## Editorial Staff

Editor in Chief  
BJ Lovestreet

Music Features Editor  
A.J. Hunter

Charts Narrator  
Kevin Casey

Culture Columnist  
Professor Wheeler

Film Editor
Charles Cursor

Television Editor
Emily Bennet

Humor & Comics  
Nick Nitro
Sections: jokes, fake ads, letters to editor, cartoon captions

Art Director  
Daisy Delgado

-------------------------------------

## Magazine Structure

1 Cover  
2 Editor Letter  
3 Charts Overview  
4–13 Top 10 Songs of the Year  
14 Movies of the Year  
15 Television of the Year  
16 Culture Feature  
17 Retro Advertisements  
18 Comic Page  
19 Arcade / Technology  
20 Letters  
21 Back Page

-------------------------------------

## Generation Rules

Articles must use real historical data.

Data should be pulled from existing RetroVerse datasets.

Illustrations are created AFTER articles are written.

Art style should match the article subject.

Avoid MAD magazine imitation style.

Use simple editorial illustrations that match the content.
