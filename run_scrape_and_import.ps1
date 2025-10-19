# PowerShell helper: run both scrapers then import to Django
$here = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Push-Location $here
python .\scripts\scrape_wolt.py
python .\scripts\scrape_foodora.py
python .\manage.py import_scraped
Pop-Location
