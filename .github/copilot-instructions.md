## Quick orientation

This repository is a small Django project (SQLite by default) that compares food-delivery menus/prices.
Primary components:
- Django apps: `users`, `catalog`, `billing`, `compare` (see `foodcompare/settings.py` INSTALLED_APPS).
- Scrapers & pipeline: `scripts/` produces JSON payloads under `data/` and `manage.py import_scraped` imports them.
- Dev helpers: `run_dev.ps1` and `run_scrape_and_import.ps1` orchestrate migrate → scrape → import → runserver.

## Big picture architecture (why/how)
- Data source: static HTML snapshots are in `data/` (e.g. `wolt.html`, `foodora.html`). The scrapers extract a JSON-like payload and write `*.extracted.json` files.
- Ingestion: `manage.py import_scraped` (Django management command) reads `data/*.extracted.json` and creates/updates DB models under `catalog`/`compare`.
- UI: Django templates live in the project `templates/` folder; `foodcompare/settings.py` adds that directory to `TEMPLATES['DIRS']`.

## Developer workflows you should follow (explicit)
- Run everything from the project root (scripts use relative paths).
- Typical dev flow (PowerShell):
  - create & activate venv; install `requirements.txt`.
  - `python manage.py migrate`
  - `python scripts/scrape_wolt.py` and `python scripts/scrape_foodora.py` (or use Playwright-based `scrape_foodora_browser.py` if available)
  - `python manage.py import_scraped`
  - `python manage.py runserver`

Key convenience commands (refer to `run_dev.ps1`):
- `.
un_dev.ps1 -ResetDB -Regen -RunServer` — resets DB, regenerates Foodora payload, runs scrapers, imports, and starts server.
- `.
un_scrape_and_import.ps1` — runs both scrapers and then `import_scraped`.

## Project-specific conventions & gotchas
- Language/locale: CODE uses Hungarian locale (`LANGUAGE_CODE = "hu-hu"`) and many templates/strings are Hungarian. Prefer concise English comments in new code, but be mindful of display strings.
- Custom user model: `AUTH_USER_MODEL = 'users.Felhasznalo'` — use `get_user_model()` where possible.
- Migrations are authoritative: always run `makemigrations --dry-run --verbosity 3` after model changes and commit migration files in `<app>/migrations/`. CI expects migrations included.
- Templates: templates are in project-level `templates/` plus app `templates/` dirs (Django `APP_DIRS=True`).

## Scrapers & integration points (practical notes)
- Wolt: `scripts/scrape_wolt.py` extracts embedded JSON from `data/wolt.html` and writes `data/wolt.html.extracted.json`.
- Foodora: `scripts/scrape_foodora.py` uses `scripts/extract_payload.py`; it falls back to `scripts/generate_foodora_payload.py` with `--regen` if extraction fails. There's also `scrape_foodora_browser.py` (Playwright) for JS-rendered pages.
- Pipeline helper: `scripts/run_pipeline.py` runs both scrapers then runs `manage.py import_scraped` — useful for CI-style runs.

## Files to inspect for common tasks
- Runbook / onboarding: `README.md` (contains the exact PowerShell commands and migration guidance).
- Dev orchestration: `run_dev.ps1`, `run_scrape_and_import.ps1`.
- Scrapers: `scripts/scrape_wolt.py`, `scripts/scrape_foodora.py`, `scripts/scrape_foodora_browser.py`, `scripts/extract_payload.py`, `scripts/generate_foodora_payload.py`.
- DB & settings: `foodcompare/settings.py`, `manage.py`.

## Minimal examples you can use when editing code
- To regenerate Foodora payload locally (no Playwright):
  - `python scripts/scrape_foodora.py --regen`
- To run full pipeline from Python (non-PS):
  - `python scripts/run_pipeline.py`
- To check migrations before committing:
  - `python manage.py makemigrations --dry-run --verbosity 3`

## Safety & testing notes for AI edits
- Don’t modify migration files unless adding a new migration for a model change you made and tested locally.
- Prefer small, focused changes and run `python manage.py check` and `python manage.py migrate` locally after edits.

If any section is unclear or you want the file to include a CI snippet / GitHub Actions example, tell me which CI provider and I’ll add a tailored step. 
