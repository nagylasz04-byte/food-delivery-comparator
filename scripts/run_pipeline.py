"""Run scraping for both Wolt and Foodora, then import into Django DB.

Usage: python scripts/run_pipeline.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

def run(cmd, desc):
    print('\n==> ' + desc)
    print('CMD:', cmd)
    res = subprocess.run(cmd, shell=True, cwd=str(ROOT))
    if res.returncode != 0:
        raise SystemExit(f'Command failed: {cmd} (exit {res.returncode})')

if __name__ == '__main__':
    # Run scrapers
    run(f'{PY} "{ROOT / "scripts" / "scrape_wolt.py"}"', 'Scrape Wolt')
    run(f'{PY} "{ROOT / "scripts" / "scrape_foodora.py"}"', 'Scrape Foodora')

    # Run import
    run(f'{PY} "{ROOT / "manage.py"}" import_scraped', 'Import into Django DB')
