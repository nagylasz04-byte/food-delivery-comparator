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
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
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

C
# kimenet: data/foodora.html.extracted.json
```
python .\scripts\scrape_foodora_browser.py

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

Migrations workflow — hogyan kerüld el a "model changes not reflected in a migration" hibát
--------------------------------------------------------------------------

Gyakori hiba: megváltoztatod a modelleket (mezők, indexek, choices, verbose_name), de elfelejted létrehozni a migrációs fájlokat és commitolni őket. Ennek eredménye a Django figyelmeztetése: "Your models in app(s) have changes that are not yet reflected in a migration".

Kövesd ezeket a lépéseket minden model-változtatás után és minden PR-ben, hogy a probléma ne forduljon elő:

1) Előnézet (dry-run) — nézd meg mit tenne a `makemigrations`:

```powershell
python manage.py makemigrations --dry-run --verbosity 3
# Vagy konkrét appra:
python manage.py makemigrations compare --dry-run --verbosity 3
```

2) Hozd létre a migrációt:

```powershell
python manage.py makemigrations
# vagy csak a módosított appokra:
python manage.py makemigrations compare
```

3) Alkalmazd az adatbázisra:

```powershell
python manage.py migrate
```

4) Ellenőrizd, hogy a migrációk alkalmazva lettek:

```powershell
python manage.py showmigrations compare
```

5) Commitolj és pusholj minden új migrációs fájlt (`<app>/migrations/000X_*.py`) a PR-edbe — NE hagyd ki a migrations mappát a commitból!

Példa git lépések:

```powershell
git add compare/migrations/
git commit -m "compare: add migration for platform/index change"
git push
```

CI javaslat (ajánlott): add hozzá a `makemigrations --check` lépést a CI pipeline-hoz, így a PR nem mehet át, ha kimaradt egy migráció:

```yaml
# példa GitHub Actions step
- name: Check migrations
  run: python manage.py makemigrations --check
```

Tippek a speciális esetekhez:
- Ha a dry-run `RenameIndex` vagy `AlterField` műveletet javasol (mint az előző példa), az általában rendben van — hozd létre a migrációt és alkalmazd.
- Ha véletlenül módosítottad a modellkódot (pl. elgépelés), állítsd vissza a kódot és futtasd újra a dry-run-t mielőtt migrációt készítesz.

Ezzel a folyamattal elkerülöd, hogy a modellek és az adatbázis sémája szinkronon kívül legyenek, és a csapatod minden tagja ugyanazokat a migrációs fájlokat kapja meg a PR-ben.


További megjegyzések
--------------------

- A `run_dev.ps1` (ha jelen van) automatizálhatja a migrate → scrape → import → runserver lépéseket.
- A `DOCS/PROJECT_DOCUMENTATION.md` és `DOCS/DOKUMENTACIO.md` részletesen leírják a pipeline-t, a RBAC döntéseket és a védéshez használható Q&A részt.

Ha szeretnéd, hozzáadok még egy rövid szakaszt a CI beállításáról (GitHub Actions) vagy létrehozok egy `run_pipeline.ps1` scriptet, ami egy parancsból végigviszi a teljes folyamatot (scrape → import → sanity-check). Jelezd, melyiket csináljam következőnek.
``` 