```markdown
Food Delivery Comparator — Használati útmutató
=============================================

Ez a dokumentum lépésről lépésre bemutatja, hogyan állítsd be és használd a projektet (Windows / PowerShell). Kiemelten tartalmazza a két scraping módot, azok telepítési követelményeit és példaparancsokat.

Rövid összefoglaló a scraper-ekről
----------------------------------

- Wolt: az oldalba beágyazott (inline) JSON/JS adatot használjuk — ez gyors, API‑szerű kinyerés. A script: `scripts/scrape_wolt.py`.
- Foodora: a demo oldal kliens-oldali JS-t futtat és `window.DATA` objektumot hoz létre. Két lehetőség:
  - Headless (screen-scraper) — `scripts/scrape_foodora_browser.py` (Playwright szükséges): a böngésző futtatja a JS-t és a ténylegesen renderelt adatot olvassa ki.
  - Fallback / generator — `scripts/scrape_foodora.py --regen`: ha nincs Playwright, vagy reprodukálható random adatra van szükség.

Előkészületek
-------------

1) Klónozd a repót és lépj a projekt gyökérkönyvtárába.
2) Hozz létre virtuális környezetet és aktiváld (PowerShell példa):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Telepítsd a projekt függőségeit (ha van `requirements.txt`):

```powershell
pip install -r requirements.txt
```

Ha Playwright-ot használod a Foodora headless scrapperhez:

```powershell
pip install playwright
python -m playwright install
```

Alapvető parancsok (PowerShell)
-------------------------------

Migrációk és admin:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

Scrape — Wolt (beágyazott JSON):

```powershell
python .\scripts\scrape_wolt.py
# kimenet: data/wolt.html.extracted.json
```

Scrape — Foodora (headless / a megjelenített adatokból):

```powershell
# csak egyszer: telepítsd a böngésző binárisokat
python -m pip install playwright
python -m playwright install

python .\scripts\scrape_foodora_browser.py
# kimenet: data/foodora.html.extracted.json
```

Scrape — Foodora (fallback / szerver-oldali generátor):

```powershell
python .\scripts\scrape_foodora.py --regen
# kimenet: data/foodora.html.extracted.json
```

Importálás az adatbázisba:

```powershell
python manage.py import_scraped
```

Fejlesztői szerver:

```powershell
python manage.py runserver
# majd böngészőben: http://127.0.0.1:8000/
```

Hol vannak az outputok?
- A scraper-ek `data/` könyvtárba írják az extracted JSON fájlokat (pl. `data/wolt.html.extracted.json`, `data/foodora.html.extracted.json`). Ezeket a `import_scraped` parancs dolgozza fel.

Tippek és gyakori hibák
-----------------------

- Ha a Foodora headless scraper nem talál `window.DATA`-t (timeout), a `scrape_foodora_browser.py` fallback-el a `scrape_foodora.py`-t hívja.
- Mindig a projekt gyökeréből futtasd a scriptet, mert az utak relatív módon vannak beállítva a `scripts/`-hez.
- Ha nem használod a headless módot, a `--regen` opcióval reprodukálható, szerver-oldali payload-ot készíthetsz.

Gyors ellenőrzés:

```powershell
python manage.py check
```

Ha a `requirements.txt` hiányzik, telepítsd a szükséges csomagokat, majd mentsd a környezetet:

```powershell
pip freeze > requirements.txt
```

Adatbázis reset (fejlesztés alatt):

```powershell
# Windows PowerShell
Remove-Item db.sqlite3
python manage.py migrate
```

További megjegyzések
--------------------

- A `run_dev.ps1` (ha jelen van) automatizálhatja a migrate → scrape → import → runserver lépéseket.
- A `DOCS/PROJECT_DOCUMENTATION.md` és `DOCS/DOKUMENTACIO.md` részletesen leírják a pipeline-t, a RBAC döntéseket és a védéshez használható Q&A részt.

Ha szeretnéd, hozzáadok még egy rövid szakaszt a CI beállításáról (GitHub Actions) vagy létrehozok egy `run_pipeline.ps1` scriptet, ami egy parancsból végigviszi a teljes folyamatot (scrape → import → sanity-check). Jelezd, melyiket csináljam következőnek.
``` 