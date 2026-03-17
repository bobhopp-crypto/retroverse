# RetroVerse Tools Pipeline (Scaffold)

This folder contains a fresh, modular TypeScript pipeline scaffold. No business logic has been implemented yet; every module is a placeholder with `TODO` markers and waits for uploaded source data.

## Project layout
- `package.json` — isolated toolchain for the pipeline and service.
- `tsconfig.json` — TypeScript compiler settings (ES2022 modules).
- `src/index.ts` — entry point; loads config, diagnostics, and the orchestrator.
- `src/config/` — unified pipeline configuration loader and defaults (`pipeline.config.json` when present).
- `src/pipeline/` — orchestrator and shared pipeline types.
- `src/parsers/` — database.xml + playlist parsers (placeholders).
- `src/normalize/` — record normalization stage (placeholder).
- `src/match/` — fuzzy matcher/deduper stage (placeholder).
- `src/thumbnails/` — thumbnail generator stage (placeholder).
- `src/publish/` — R2 uploader stage (placeholder).
- `src/diagnostics/` — diagnostics logger facade.
- `src/services/` — lightweight Express service so the React app can trigger/check pipeline runs internally.

## Pipeline stages (intended flow)
1. **Parse sources** — ingest `database.xml`, `.m3u` playlists, and optional metadata JSON into structured records.  
   Inputs: uploaded XML/M3U files. Outputs: raw record collection.
2. **Normalize** — standardize fields, coerce types, and enrich with derived metadata.  
   Inputs: parsed records. Outputs: normalized items ready for matching.
3. **Fuzzy match / dedupe** — link related entries across sources using configurable similarity strategies.  
   Inputs: normalized items. Outputs: matched sets with confidence scores.
4. **Thumbnail generation** — produce preview images for matched media items.  
   Inputs: matched items + media references. Outputs: thumbnails stored under `storage.thumbnailsDir`.
5. **R2 upload** — push normalized data + thumbnails to Cloudflare R2.  
   Inputs: generated assets. Outputs: remote object URLs/keys.
6. **Diagnostics logging** — structured logs for every stage, emitted via `pino` (file transport TODO).  
   Inputs: pipeline events. Outputs: log files in `storage.diagnosticsDir` (pending implementation).

## Module interactions
- `src/index.ts` loads configuration (`pipeline.config.json` if present) and constructs diagnostics.
- `src/pipeline/orchestrator.ts` builds stage lists from each module and controls `prepare/execute/shutdown`.
- Each stage builder (`parsers`, `normalize`, `match`, `thumbnails`, `publish`) returns `PipelineStage` objects consumed by the orchestrator.
- The Express service (`src/services/server.ts`) exposes `/pipeline/run` and `/pipeline/status` so the React app can start the orchestrator and poll status.

## Configuration
- Optional `pipeline.config.json` at the root of this folder overrides defaults from `src/config/pipelineConfig.ts`.
- Key sections: `sources`, `storage`, `fuzzyMatch`, `thumbnail`, `diagnostics`, and optional `r2` credentials.
- TODO: add JSON schema validation and environment variable expansion.

## How to run (after logic is implemented)
```bash
cd tools
npm install
npm run dev          # runs src/index.ts
npm run service      # starts Express service on port 4040 by default
```

## Next steps (blocked until uploads arrive)
- Upload the required inputs: `database.xml`, playlist `.m3u` files, and any example media metadata.
- Decide the matching strategy and thresholds to finalize the fuzzy matcher.
- Provide R2 bucket credentials and thumbnail sizing preferences.
- Once inputs are available, we will implement each stage and wire status tracking in the service.
