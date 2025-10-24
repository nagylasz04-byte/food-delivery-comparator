Food Delivery Comparator — Használati útmutató
===============================================

Ez a dokumentum lépésről-lépésre bemutatja, hogyan állítsd be, futtasd és használd a "food-delivery-comparator" projektet egy új gépen (Windows / PowerShell környezetre optimalizálva). Tartalmazza továbbá a scraping pipeline futtatását, az adatbázis alapműveleteket (reset, migrációk), és hibaelhárítási tippeket.

Fentebb szerepelt egy részletes Docker-es beállítási útmutató, ezt eltávolítottuk a repo-ból. A következők maradnak itt, amelyek a helyi indításhoz és üzemeltetéshez szükségesek.

Rövid indítási és üzemeltetési parancsok
---------------------------------------

- Migrációk és admin felhasználó létrehozása:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

- Scraping (kimeneti fájlok a `data/` mappában):

```powershell
python scripts/scrape_wolt.py
# Foodora: véletlenszerű payload generálása --regen opcióval
python scripts/scrape_foodora.py --regen
```

- Importálás a Django DB-be:

```powershell
python manage.py import_scraped
```

- Fejlesztői szerver indítása:

```powershell
python manage.py runserver
# majd böngészőben: http://127.0.0.1:8000/
```

Hasznos gyorsparancsok és hibaelhárítás
-------------------------------------

- Ellenőrizd a projektet (Django check):

```powershell
python manage.py check
```

- Ha új csomagokat adtál hozzá, frissítsd a `requirements.txt` fájlt:

```powershell
pip freeze > requirements.txt
```

- Adatbázis törlése (reset):

```powershell
# Állj a projekt gyökérkönyvtárába
Remove-Item db.sqlite3  # vagy rm db.sqlite3
python manage.py migrate
```

1) A scraping futtatása (helyi fixtures):

```powershell
# Példa: futtasd a wrapper scriptet, amely létrehozza a data/*.extracted.json fájlokat
python scripts/scrape_wolt.py
# A Foodora scraper most képes véletlenszerű payload-ot generálni is. Ha
# mindig friss (random) adatot akarsz, add meg a --regen flag-et:
python scripts/scrape_foodora.py --regen

# A generátor kód itt található: scripts/generate_foodora_payload.py
# A scrapper a kibontott JSON-t a projektben a következő fájlokba írja:
#   data/wolt.html.extracted.json
#   data/foodora.html.extracted.json
```

2) Az import futtatása (a scraped JSON fájlokból a Django adatbázisba):

```powershell
python manage.py import_scraped
```

Ezzel a `catalog`, `compare` és `billing` modellekbe kerülnek az adatok (etterem, etel, etterem_koltseg, etterem_etel_info).

Teljes pipeline (scrape + import):
Ha elkészült a `scripts/run_pipeline.py` vagy a `run_scrape_and_import.ps1`, használhatod őket:

```powershell
# PowerShell wrapper (ha megvan)
.\run_scrape_and_import.ps1
# vagy Python runner
python scripts/run_pipeline.py
```

Hasznos parancsok
- Django rendszer ellenőrzés:
```powershell
python manage.py check
```
- Migrations létrehozása + alkalmazása:
```powershell
python manage.py makemigrations
python manage.py migrate
```
- Admin felület:
  - Hozz létre admin usert: `python manage.py createsuperuser`
  - Majd nyisd: http://127.0.0.1:8000/admin/

- Adatbázis dump/restore (SQLite például):
  - Egyszerű mentés: másold a `db.sqlite3` fájlt
  - Visszaállítás: cseréld le a `db.sqlite3` fájlt, majd futtasd `python manage.py migrate` ha szükséges

Gyakori problémák és megoldások
- Hiba: "You have X unapplied migration(s)"
  - Futtasd: `python manage.py migrate`
- Hiba: template/field "no such column" — ha új modellt vagy mezőt adtál hozzá és nem futtattad a migrációt
  - Futtasd: `python manage.py migrate`

- Ha a scraping nem adja be a várt mezőket, ellenőrizd a `data/*.extracted.json` fájlokat: ezek tartalmazzák a géppel olvasható payload-ot.

Fejlesztési tippek
- Ha új Python-csomagot adsz hozzá, frissítsd a `requirements.txt`-et:
```powershell
pip freeze > requirements.txt
```

- Ha SQL vagy egyedi migrációt írsz, mindig futtasd le a `python manage.py migrate --plan` vagy `python manage.py makemigrations` parancsot tesztelésként.

Docker használat (röviden)
---------------------------------
Hozzáadtam egy egyszerű `Dockerfile`-t és `docker-compose.yml`-t a fejlesztési környezethez. Az `entrypoint.sh` induláskor automatikusan lefuttatja a migrációkat és (ha vannak) importálja a `data/*.extracted.json` fájlokat.

Indítás:
```powershell
docker compose build
docker compose up
```

A konténer indításkor az `entrypoint.sh` lefut:
- `python manage.py migrate --noinput`
- ha talál `data/*.extracted.json` fájlokat a repo `data/` mappájában, akkor futtatja az `python manage.py import_scraped`-et

Hasznos parancsok konténerben:
```powershell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py import_scraped
docker compose exec web python manage.py createsuperuser
```

Részletes Docker használat
--------------------------
1) .env fájl (ajánlott)
Helyezd a projekt gyökerébe a `.env` fájlt a következő tartalommal (ne commitold):

```text
DATABASE_URL=postgres://foodcompare:password@db:5432/foodcompare
DJANGO_SECRET_KEY=replace-me
DEBUG=True
```

`foodcompare/settings.py` már olvassa a `.env`-et, így a docker-compose által biztosított `DATABASE_URL`-t is.

2) Indítás és migrációk

```powershell
docker compose build
docker compose up -d

# majd (ha kell):
docker compose logs -f
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

3) Adatbázis reset Docker-rel (Postgres volume törlése)

```powershell
docker compose down -v   # leállítja a stack-et és törli a postgres volume-t
docker compose up -d
docker compose exec web python manage.py migrate
```

4) Import futtatása konténerben

Ha a `data/*.extracted.json` fájlok a repo `data/` könyvtárában vannak, az entrypoint automatikusan megpróbálja futtatni az `import_scraped` parancsot az indításkor. Manuálisan is futtathatod:

```powershell
docker compose exec web python manage.py import_scraped
```

5) Ha hibát látsz

- Ellenőrizd a konténer logokat: `docker compose logs web`
- Győződj meg róla, hogy a `.env` és a `DATABASE_URL` helyes
- Ha a migrációk miatt van gond, futtasd `docker compose exec web python manage.py migrate --verbosity 2` a részletesebb kimenetért

Ez az útmutató elég részletesen lefedi a Dockeres fejlesztési munkafolyamat tipikus lépéseit. Ha szeretnéd, beállítok egy `Makefile`-t vagy PowerShell scriptet, amely automatizálja a gyakori lépéseket (`docker-compose build && up && migrate`).


További help
- Ha szeretnéd, készítek:
  - Egy `docker-compose.yml` fájlt fejlesztéshez és adat-szinkronizációhoz
  - Automatikus teszteket a `import_scraped` parancshoz
  - Egy scriptet, ami a meglévő `EtteremKoltseg` sorokból automatikusan áthelyez bizonyos adatokat `etel` mezőbe a szabályaid szerint

————————————————————————
Ha szeretnéd, most létrehozok még:
- Egy `requirements.txt` frissítést (pip freeze alapján),
- Vagy felveszem a README-be még részletesebb platform-specifikus példákat a scraping futtatására.

Jelöld meg, melyiket csináljam következőként.