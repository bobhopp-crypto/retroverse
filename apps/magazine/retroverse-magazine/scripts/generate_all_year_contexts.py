import sqlite3
import subprocess

DB_PATH = "../../../data/raw/charts/billboard-hot-100.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

years = cur.execute("""
SELECT DISTINCT strftime('%Y', chart_date)
FROM hot100
ORDER BY chart_date
""").fetchall()

years = [y[0] for y in years]

print(f"Generating context files for {len(years)} years...")

for year in years:

    print(f"Processing {year}")

    subprocess.run([
        "python3",
        "generate_year_context.py",
        year
    ])

print("All year context files generated.")
