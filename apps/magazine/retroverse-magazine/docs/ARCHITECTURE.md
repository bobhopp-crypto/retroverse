# RetroVerse Magazine Architecture

## Data Layer
Billboard + cultural datasets.

## Editorial Layer
AI writers assigned to staff personas.

## Art Layer
Illustrations created after articles.

## Layout Layer
Magazine pages assembled.

## Supervisor Layer
`editorial_supervisor.py` coordinates workflow.

## Data Flow
Data Source Map
-> Data Inventory
-> Year Context Generator
-> Editorial Supervisor
-> Staff Writers
-> Art Director
-> Illustration Generator
-> Layout Builder

Internal RetroVerse datasets are authoritative for chart facts.
External research, if used later, is supplemental only.

## Music Data Layers
Hot 100 -> singles dominance.
Billboard 200 -> album dominance.
Audio features -> sonic fingerprint.

## Screen & Culture Warehouse
RetroVerse maintains a dedicated screen/culture warehouse under:
`/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/`

### Source Layering
- `canonical_local`: RetroVerse internal datasets and curated local foundations.
- `licensed_or_official`: Structured official/licensed bulk files (for example IMDb local datasets).
- `direct_api`: API enrichment layers (for example TMDb or OMDb) when configured.
- `reference_derived`: Lower-confidence reference tables and archive-derived metadata.
- `missing`: Explicit marker when no source populated a field.

### Trust Hierarchy
Field merges follow a strict hierarchy and do not overwrite stronger sources with weaker ones.
All record and field updates preserve provenance entries.

### Provenance Tracking
Every record stores:
- record-level provenance entries
- field-level provenance entries
- trust labels on merged values

Each provenance entry captures source name, source type, source identifier/URL, and trust level.

### Popularity vs Critical Acclaim
- Popularity signals: box office, ranking signals, audience/viewership proxies, platform popularity metrics.
- Critical/acclaim signals: critic scores (for example Metacritic/Rotten Tomatoes) and awards/acclaim summaries.

These dimensions are intentionally separate and can be sparse independently.

### TV Coverage Constraints
Open historical television viewership data is less standardized than movie box-office/ratings data.
The warehouse supports sparse viewership fields with explicit provenance and missing markers so downstream editorial systems can handle partial coverage safely.
