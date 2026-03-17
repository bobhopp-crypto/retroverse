# RetroVerse Cultural Support Generator

Builds one CSV row per year for `1958..2024` with:
- `top_film_1..10`
- `top_tv_program_1..10`
- `headline_event_1..15`

Output path default:
- `/Users/bobhopp/Sites/retroverse/retroverse-output/retroverse_support_cultural_1958_2024_top10.csv`

## Setup

```bash
cd /Users/bobhopp/Sites/retroverse/retroverse-output
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
cd /Users/bobhopp/Sites/retroverse/retroverse-output
source .venv/bin/activate
python build_retroverse_support_1958_2024.py
```

## Common Commands

Run a range:

```bash
python build_retroverse_support_1958_2024.py --start 1958 --end 1969
```

Force recompute (ignores resume-skip):

```bash
python build_retroverse_support_1958_2024.py --start 1958 --end 1960 --force
```

Smoke test (`1958..1960`):

```bash
python build_retroverse_support_1958_2024.py --smoke --force
```

Custom output/log/rate:

```bash
python build_retroverse_support_1958_2024.py \
  --out /Users/bobhopp/Sites/retroverse/retroverse-output/retroverse_support_cultural_1958_2024_top10.csv \
  --log /Users/bobhopp/Sites/retroverse/retroverse-output/retroverse_support_cultural_1958_2024_top10.log \
  --rate-limit 0.6
```
