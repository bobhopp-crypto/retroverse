#!/usr/bin/env python3
"""Print suggested macOS instructions for daily data inventory refresh."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    script_path = project_root / "scripts" / "update_data_inventory.py"
    cron_line = f"0 3 * * * /usr/bin/python3 {script_path.as_posix()} --write"

    print("Suggested cron entry for daily data inventory refresh:")
    print(cron_line)
    print("")
    print("Note: launchd is another macOS-native scheduling option if you prefer plist-based jobs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
