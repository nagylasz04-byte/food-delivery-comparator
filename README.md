Food Delivery Comparator — Használati útmutató
===============================================

Ez a dokumentum lépésről-lépésre bemutatja, hogyan állítsd be, futtasd és használd a "food-delivery-comparator" projektet egy új gépen (Windows / PowerShell környezetre optimalizálva). Tartalmazza továbbá a scraping pipeline futtatását, az adatbázis alapműveleteket (reset, migrációk), és hibaelhárítási tippeket.

Tartalom
- Követelmények
- Gyors kezdés (helyi fejlesztés)
- Teljes telepítés és környezet létrehozása új gépen
- Adatbázis kezelése (reset törléssel)
- Scraping pipeline futtatása
- Hasznos parancsok
- Hibakeresés és tippek

Követelmények
- Python 3.10+ telepítve
- pip
- (Ajánlott) virtuális környezet (venv)
- SQLite (alapértelmezés szerint a projekt használja)

Gyors kezdés (helyi fejlesztés)
1) Klónozd a repót és lépj be a mappába

```powershell
git clone <repo-url>
cd food-delivery-comparator
```

2) Hozz létre és aktiválj egy virtuális környezetet (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Telepítsd a függőségeket
(Nincsen külön requirements.txt? Ha van, telepítsd azt; ha nincs, a projekt alap függőségei a Django és BeautifulSoup lehetnek.)

```powershell
pip install -r requirements.txt
# ha nincs requirements.txt
pip install django beautifulsoup4 requests
```

4) Migrációk futtatása és alapadatok

```powershell
python manage.py migrate
python manage.py createsuperuser  # ha admin felhasználót akarsz
```

5) Fejlesztői szerver indítása

```powershell
python manage.py runserver
# majd böngészőben: http://127.0.0.1:8000/
```

Teljes telepítés (új gép)
1) Kövesd a fenti lépéseket (klón, venv, függőségek).
2) Ha a projekt külön fájlokban tárolt titkokat/konfigurációt igényel, állítsd be a környezeti változókat vagy a `foodcompare/settings.py` megfelelő részeit.

Adatbázis kezelése
- Az alkalmazás alapértelmezés szerint SQLite-ot használ (`db.sqlite3`).
- Az adatbázis teljes törlése (reset) — ha vissza akarod állítani tiszta állapotra, egyszerűen töröld a fájlt és futtasd újra a migrációkat:

```powershell
# Állj a projekt gyökérkönyvtárába
rm db.sqlite3
python manage.py migrate
```

Megjegyzés Windows PowerShell-ben: `rm` működik, vagy `Remove-Item db.sqlite3`.

Scraping pipeline (lokális HTML fixtures és import)
A projekt tartalmazott egyszerű scrapper/Extractor scriptet, ami a `data/` könyvtárban lévő HTML fájlokat dolgozza fel.

1) A scraping futtatása (helyi fixtures):

```powershell
# Példa: futtasd a wrapper scriptet, amely létrehozza a data/*.extracted.json fájlokat
python scripts/scrape_wolt.py
python scripts/scrape_foodora.py
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