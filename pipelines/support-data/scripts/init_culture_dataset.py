#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

# === CONFIG ===
# Update this path if the cultural CSV is located elsewhere
SOURCE_CSV = Path.home() / "Downloads" / "retroverse_support_cultural_1958_2024_top10.csv"

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import get_dataset_path
from lineage_hook import run_with_lineage


DEST_CSV = get_dataset_path(
    "retroverse_support_cultural",
    fallback="data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv",
)
SUPPORT_DIR = DEST_CSV.parent


def main():
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"Could not find source cultural CSV at: {SOURCE_CSV}\n"
            "Update SOURCE_CSV path in the script if needed."
        )

    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy2(SOURCE_CSV, DEST_CSV)

    print("Cultural support folder created (if needed).")
    print(f"CSV copied to: {DEST_CSV}")


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
