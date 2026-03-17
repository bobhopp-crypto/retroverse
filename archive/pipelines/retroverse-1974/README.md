# RetroVerse 1974 Illustrated Artifact Engine

System B pipeline for 1974 Weeks 29-32 (Top 10 each, 40 cards total).

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python pipeline/scripts/rv_run_batch.py --config pipeline/config/pipeline_1974_w29_w32_top10.yaml
```

## Rendering Credentials

Rendering uses OpenAI Images (`gpt-image-1`) when `OPENAI_API_KEY` is set.

- Set `OPENAI_API_KEY` in your shell or `.env`.
- Without credentials, the pipeline still runs extract/ambient/prompt/validation and logs `render_not_executed_missing_credentials` (dry-run render behavior).

## One-Command Batch

```bash
python pipeline/scripts/rv_run_batch.py --config pipeline/config/pipeline_1974_w29_w32_top10.yaml
```
