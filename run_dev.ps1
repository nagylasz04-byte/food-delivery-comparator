<#
run_dev.ps1 - Development helper for food-delivery-comparator

Usage examples:
  # run default pipeline (does NOT delete DB)
  .\run_dev.ps1

  # reset DB, migrate, run scrapers (Foodora regen), import, and start server
  .\run_dev.ps1 -ResetDB -Regen

This script assumes Python is on PATH and you run it in PowerShell on Windows.
It changes directory to the repository root (the script location) to avoid "No such file" or
module import errors when `python manage.py` or `scripts/...` are invoked from other folders.
#>

param(
    [switch]$ResetDB,
    [switch]$Regen,
    [switch]$RunServer
)

try {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    Write-Host "Switching to project directory: $ScriptDir"
    Set-Location -Path $ScriptDir
} catch {
    Write-Error "Failed to determine script directory. Ensure you run the script from disk (not paste)."
    exit 2
}

# Optional reset DB
if ($ResetDB) {
    if (Test-Path .\db.sqlite3) {
        Write-Host "Removing existing db.sqlite3..."
        Remove-Item .\db.sqlite3 -Force
        Write-Host "db.sqlite3 removed"
    } else {
        Write-Host "No db.sqlite3 found, skipping removal" -ForegroundColor Yellow
    }
}

Write-Host "Running migrations..."
python manage.py migrate
if ($LASTEXITCODE -ne 0) { Write-Error "migrate failed (exit $LASTEXITCODE)"; exit $LASTEXITCODE }

Write-Host "Running scrapers..."
if (Test-Path .\scripts\scrape_wolt.py) {
    python scripts/scrape_wolt.py
    if ($LASTEXITCODE -ne 0) { Write-Error "scrape_wolt.py failed (exit $LASTEXITCODE)"; exit $LASTEXITCODE }
} else {
    Write-Warning "scripts/scrape_wolt.py not found; skipping Wolt scraper"
}

if (Test-Path .\scripts\scrape_foodora.py) {
    if ($Regen) {
        Write-Host "Running Foodora scraper with --regen (server-side generator)"
        python scripts/scrape_foodora.py --regen
    } else {
        Write-Host "Running Foodora scraper (no --regen)"
        python scripts/scrape_foodora.py
    }
    if ($LASTEXITCODE -ne 0) { Write-Error "scrape_foodora.py failed (exit $LASTEXITCODE)"; exit $LASTEXITCODE }
} else {
    Write-Warning "scripts/scrape_foodora.py not found; skipping Foodora scraper"
}

Write-Host "Importing scraped JSON into Django..."
python manage.py import_scraped
if ($LASTEXITCODE -ne 0) { Write-Error "import_scraped failed (exit $LASTEXITCODE)"; exit $LASTEXITCODE }

Write-Host "Import completed successfully." -ForegroundColor Green

if ($RunServer) {
    Write-Host "Starting development server (runserver) - open http://127.0.0.1:8000/ in a browser"
    python manage.py runserver
}

Write-Host "Done. If you want to start the dev server, re-run with -RunServer."
