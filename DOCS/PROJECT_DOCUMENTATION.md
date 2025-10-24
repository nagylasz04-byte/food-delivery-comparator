# Food Delivery Comparator — Részletes projekt dokumentáció

Ez a dokumentum a "food-delivery-comparator" projekt teljes, tanulható és védésre (szóbeli/bizonyítási) felkészítő dokumentációja.
Kezdőtől a haladóig mindent tartalmaz: célok, architektúra, adatmodellek, scraping pipeline, import, jogosultságkezelés (RBAC), admin felület működése, környezeti változók, backend és frontend részletek, valamint egy kérdések–válaszok (Q&A) rész védéshez.

Az olvasó célja: aki ezt áttanulmányozza, meg kell, hogy értse a projekt felépítését, működését, és képes legyen a projektet futtatni, karbantartani és továbbfejleszteni.

## 1. Rövid áttekintés

Food Delivery Comparator egy kísérleti Django alapú alkalmazás, amely helyi HTML fixture-eken (Foodora / Wolt demo oldalak) keresztül bemutatja a különböző ételszolgáltatók (platformok) ajánlatait és rejtett költségeit. A projekt célja kettős:

- oktatási és demonstrációs: hogyan lehet web-architektúrákat, scraping pipeline-t és adatimportot megvalósítani; és
- gyakorlati: összehasonlítani ételek árait különböző platformok/éttermek alapján.

Fő komponensek:
- Django alkalmazás (apps: `catalog`, `compare`, `billing`, `users`)
- HTML fixture fájlok: `data/foodora.html`, `data/wolt.html`
- Scraper/helper scriptek: `scripts/`
- Import management parancs: `catalog/management/commands/import_scraped.py`
- Admin felület és jogosultságkezelés (egyszerű RBAC a projektben)

## 2. Architektúra és adatmodellek

Magas szintű komponensek:

- Frontend (demo HTML fixture oldal, admin felület, Django sablonok)
- Backend (Django: modellek, nézetek, management parancsok)
- Scraping & ETL (HTML -> JSON -> DB import)

Főbb modellek (röviden):
- `catalog.Etel` — étel, mezők: `nev`, `leiras`, `kategoria`, `kep_url` stb.
- `catalog.Etterem` — étterem, mezők: `nev`, `cim`, `platform`, `platform_url`
- `catalog.EtteremEtelInfo` — egy adott étel ajánlata egy étteremnél/platformnál (ár, promóció, értékelés, szállítási idő).
- `billing.EtteremKoltseg` — rejtett költségek, lehet `etterem` FK-hoz vagy opcionálisan `etel` FK-hoz kapcsolva; támogat platform-szintű költségeket is.

Relációk: általában 1:N kapcsolat `Etterem` -> `EtteremEtelInfo` (egy étteremnek sok ajánlata lehet). `Etel` és `Etterem` között gyakori az N:M (több étterem kínálhat ugyanazt az ételt), ezért `EtteremEtelInfo` gyakorlatilag join-táblaként viselkedik.

## 3. Scraping pipeline (hogyan lesz a HTML-ből DB)

Folyamat:

1. Fixture oldal (például `data/wolt.html`) tartalmaz egy géppel olvasható JSON blokkját (`<script id="scrape_payload" type="application/json">`) vagy inline JS objektumot. Foodora demo inkább generátort használ (`--regen`).
2. `scripts/extract_payload.py` — helper, amely először megkeresi a `#scrape_payload` script tag-et, ha nincs, próbál heuristikusan kinyerni JSON-t.
3. `scripts/scrape_wolt.py` és `scripts/scrape_foodora.py` — wrapper szkriptek, amik hívják az extractor-t; Foodora esetén a `--regen` opció meghívja a szerver-oldali generátort (`scripts/generate_foodora_payload.py`). Kimenet: `data/*.extracted.json` (pl. `data/wolt.html.extracted.json`).
4. `python manage.py import_scraped` — a Django management parancs beolvassa a `data/*.extracted.json` fájlokat és idempotens módon létrehozza/frissíti az adatbázis entitásokat: `Etterem`, `Etel`, `EtteremKoltseg`, `EtteremEtelInfo`.

Import fontos tulajdonságai:
- Idempotencia: többszöri futtatás nem hoz létre duplikátumokat; meglévő sorok frissíthetők.
- Platform és étel-költségek elkülönítése: a `EtteremKoltseg` sorok lehetnek platform-szintűek, étel-szintűek, vagy étterem-szintűek. Az importer logikája ennek megfelelően helyezi el az adatokat.

## 4. A generátor (Foodora) és miért van rá szükség

Foodora fixture-hez van egy szerver-oldali generátor (`scripts/generate_foodora_payload.py`), amely véletlenszerű, de konzisztens payload-ot állít elő. Ez azért kényelmes, mert a demo oldalon levő UI dinamikus marad anélkül, hogy statikus JSON-t kellene beépíteni.

Ha `data/foodora.html` nem tartalmaz `#scrape_payload` blokkot, futtasd:

```powershell
python scripts/scrape_foodora.py --regen
```

Ez új `data/foodora.html.extracted.json` fájlt készít, amit az `import_scraped` be tud olvasni.

## 5. Jogosultságok (RBAC) — részletes magyarázat

A jogosultságkezelés a projekt egyik kulcstémája, és az egyik olyan pont, ami gyakran felmerül a védés során. Itt részletesen magyarázom a megközelítést, a backend és frontend kapcsolódásait, valamint a mérlegeléseket.

Jelenlegi állapot (a repo alapján):

- Egyszerű, pragmatikus RBAC: a fontos írási/kezelési műveletekhez alapvetően `user.is_staff` ellenőrzést használunk (mixinekben vagy dekorátorokban), ami a Django beépített flag-je. Ez gyors és egyszerű a fejlesztéshez.
- A projekt tartalmaz `Jog` és `FelhJog` (egyéni jogosultság/táblák) modelleket, amelyek opcionálisan használhatók finomabb vezérlésre (pl. egyedi jogosultságok hozzárendelése felhasználókhoz), de a működő ellenőrzéshez a jelenlegi implementációban ez nincs teljesen integrálva (jegyzet: ez tervezett fejlesztés).

Konkrét példa a feltett kérdésekből (idézetként):

"belekérdezett 1 részbe konkrétan miután nagyjából vegigmondtam mindent
Zoli
konkrétan az rbac megoldasomba, mert mutattam neki h masnak az adatbázis entry-jet csak admin tudja torolni
Zoli
aztan backend es frontend megoldást kellett elmagyarázjam
Zoli
tobbinel bologatott,Bemutattam neki az appot, annyit kerdezett hogy a typeracer jatekhoz honnan szedi a code snippeteket
Roland
Megmutatod neki es kesz"

Magyarázat erre a helyzetre (hogyan válaszolnánk a védésen):

- Backend megoldás: a törlési/írási végpontokat olyan dekorátorral vagy mixinnel védjük, amely ellenőrzi, hogy a kérést indító felhasználó `is_staff` (vagy rendelkezik a megfelelő `Jog`/`FelhJog` joggal). Például a DeleteView-hez hozzáadott ellenőrzés csak engedélyezi a törlést, ha user.is_staff == True. Ha szeretnénk finomabb szabályokat (pl. csak a saját entitás törlése), akkor további jogosultság-check-eket (objektumszintű) vezetünk be.
- Frontend megoldás: UI elemek (pl. Törlés gomb) csak akkor jelennek meg, ha a megjelenített felhasználó session-je rendelkezik a szükséges jogosultsággal; ez egy UX-level védelmi réteg (de nem helyettesíti a backend ellenőrzést).
- Példa: ha megmutatunk egy másik felhasználó bejegyzését az adminban, a törlés csak `admin` (staff) felhasználó által érhető el — ezt mind a frontend (gomb rejtése), mind a backend (view/dekorátor) biztosítja.

Tippek a védésnél:

- Mutasd meg a `users/forms.py` változtatását (pl. `kedvenc_etterem` required=False) mint példát, hogy hogyan alakítod a form-ok viselkedését.
- Mutasd meg a `users/views.py`-ben bevezetett `RegisterView`-t, és magyarázd el, hogy a publikus regisztrációt miért tettétek elérhetővé, és miért marad néhány funkció (írás) staff-re korlátozva.

Kiterjesztési javaslatok (jobb RBAC):

- Integrálni Django beépített permissions-t (model-level perms) és csoportokat (Groups) — ez skálázható és jól integrálható az admin felülettel.
- Objektumszintű jogosultságokhoz használjunk `django-guardian`-t (vagy egy saját objektum-szintű mixint), ha per-objektum jogosultságokra van szükség.

## 6. Admin felület — miért fontos és hogyan működik

Miért hangsúlyos: az admin a projektben nem csak a DB tartalom gyors szerkesztésére szolgál, hanem demonstrálja a jogosultságkezelést is (ki mit lát, ki mit törölhet).

Működés:

- Django admin regisztrálva van a modellekkel (`catalog.admin`, `billing.admin`, `users.admin`).
- Képek megjelenítése az adminban: az admin template-ek kiterjeszthetők, így a `Etel` model admin list nézetében thumbnail-ek jeleníthetők meg (ha `kep_url` mező van).

Fontos: az admin felület önmagában nem helyettesíti az alkalmazás jogosultságkezelését — az admin a staff felhasználók számára van fenntartva.

## 7. Környezeti változók (env-ek) és konfiguráció

Hol és miért?

- `foodcompare/settings.py` olvassa a `.env` fájlt (ha van) a bizalmas beállításokért (pl. `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DEBUG`). Ez a legjobb gyakorlat: ne tarts érzékeny adatot a repo-ban.

Ajánlott `.env` mezők (példa):

```
DJANGO_SECRET_KEY=replace-me
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # vagy Postgres URL
```

Tippek:

- Soha ne commitold a `.env`-t magas jogú kulcsokkal.
- Lokálisan használhatsz sqlite-ot, CI-ben/production-ban Postgres-t.

## 8. Backend részletek — kulcs fájlok és logika

- `catalog/models.py` — adatmodellt mutatja be; olvasd át mező definíciókat, FK-kat, __str__ metódusokat.
- `catalog/management/commands/import_scraped.py` — nagyon fontos: felelőssége a `data/*.extracted.json` beolvasása, mapping és idempotens DB műveletek végrehajtása. Itt történik a kulcs logika, hogy mit tekintünk új entitásnak és mit frissítünk.
- `billing/models.py` — `EtteremKoltseg` módosítások: tartalmaz `platform` mezőt és opcionális `etel` FK-t.

Érdemes megnézni a `get_or_create` használatát és a tranzakciókezelést import közben (ha nem történik meg, érdemes bevezetni, hogy részleges import ne hagyjon inkonzisztens állapotot).

## 9. Frontend részletek — demo oldalak és sablonok

- A demo HTML fixture-ek (`data/foodora.html`, `data/wolt.html`) önálló statikus oldalak JS-sel, amelyek vagy beágyazott JSON payload-ot tartalmaznak, vagy dinamikusan generálható payload-ot (Foodora generator). Ezek a lapok szolgálnak „fixtures”-ként a scrapper számára.
- Django sablonok: `templates/` mappa tartalmaz admin-szerű és alkalmazás nézeteket (`catalog/`, `billing/`, `compare/`). A formok általában `{{ form.as_p }}`-ben jelennek meg, de fontos oldalakon egyedi HTML lehet.

## 10. Biztonság: alapelvek és konkrét teendők

Alapelvek:

- Kettős védelmi réteg: frontend UX rejti a nem jogosult műveleteket; backend végpontok ellenőrzik a jogosultságot (kötelező!).
- Soha ne bízz a kliensoldalban: mindig ellenőrizd a jogosultságot a szerveren.
- Érzékeny konfigurációk `.env`-ben, ne kerüljön a VCS-be.

Konkrét javaslatok a projekt biztonságához:

1. Hardening: `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT` és a sesszió cookie-k biztonságos beállítása production esetén.
2. Input validáció: minden importált JSON mezőt validálj (típus, tartomány, kötelező mezők), és használj `try / except` blokkokat, tranzakciót.
3. Rate limiting és CSRF: API végpontokhoz (ha lesznek) rate limit és CSRF védelem.

## 11. Kérdések és válaszok a védésre (Q&A)

Az alábbi rész célja, hogy a védésre készülő diák egy gyakorlatias Q&A gyűjteményt kapjon. Minden kérdés mellé javasolt válaszpontokat adok.

Q: Mi az alkalmazás célja és milyen komponensekből áll?
A: (lásd 1. fejezet) — ismertesd a scraping pipeline-t, a generátort, az importer-t és a Django alkalmazást.

Q: Hogyan biztosítod, hogy a scraping/import idempotens legyen?
A: Az importer `get_or_create` mintát alkalmazza, egyedi kulcsok (pl. platform+etterem+etel) alapján keres és frissít; a management parancs logikai checks-eket futtat, hogy ne hozzon létre duplikátumot. (Mutasd meg a kódot és magyarázd el a kulcs-elképzeléseket.)

Q: Miért van szükség a `generate_foodora_payload.py`-ra?
A: A demo oldalak teszteléséhez kényelmes, hogy véletlenszerű, de konzisztens adathalmaz álljon rendelkezésre anélkül, hogy a HTML-ba statikus JSON-t kellene beépíteni. A generator segít reprodukálható, kontrollált, ugyanakkor változatos adatok előállításában.

Q: Hogyan kezelitek a jogosultságokat (RBAC)? Mi a hátránya az `is_staff`-alapú megközelítésnek?
A: Jelenleg `is_staff` ellenőrzést használunk fontos írási műveletekre. Ez egyszerű, de nem granuláris. Hátrány: nincs per-model vagy per-objektum jogosultság. Javaslat: `django.contrib.auth` permissions és `Groups` használata, vagy `django-guardian` objektumszintű jogosultságokhoz.

Q: Mit mutattál Zolinak a védés közben?
A: Elmagyaráztam a RBAC megoldást: a példában másnak az adatbázis entry-jét csak admin tudta törölni. Ezt backend (view-decorator) és frontend gombmegjelenítés kombinációja biztosítja. (Mutasd meg a DeleteView/permission mixin kódját.)

Q: Hogyan validálod és kezeled az env-konfigurációkat?
A: A `settings.py` környezeti változókat olvas (pl. `.env`) és ezek alapján állít be DB kapcsolatot, secret key-t és debug módot. A `.env`-t soha nem committeljük.

Q: Hogyan működik a typeracer snippet-ek ellátása? (idézet: Zoli kérdése)
A: Az említett funkciót (példa) a demo adatok generátora vagy egy külső forrás (pl. snippet-adatbázis) szolgáltathatja. Konkrét implementáció: a generator vagy a `data/wolt_data.json` tartalmazhat snippet mezőket; a frontend betölti őket és megjeleníti a játékban.

Q: Mi történik, ha a scraping fájl hibás JSON-t ad vissza?
A: Az `extract_payload.py` először megpróbál jól formázott `#scrape_payload` blokkot olvasni, és ha a JSON parse hibába ütközik, hibát dob és logol. Az importer validálás nélkül nem fut; így az operátor észreveszi és javítja a fixture-t. Javasolt fejlesztés: bevezetni schema-validációt (pl. JSON Schema) a pipeline elején.

## 12. Hogyan futtasd és teszteld a projektet (gyakorlati lépések)

1) Klónozd a repót, állj a projekt gyökérbe.
2) Hozz létre a virtuális környezetet és telepítsd a függőségeket (locally). Ha nincs `requirements.txt`, telepítsd a szükséges csomagokat: Django, beautifulsoup4, requests, stb.

Példák (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # ha van
python manage.py migrate
python manage.py createsuperuser
```

Scraping és import:

```powershell
python scripts/scrape_wolt.py
python scripts/scrape_foodora.py --regen
python manage.py import_scraped
python manage.py runserver
```

Ellenőrzés:

```powershell
python manage.py check
python manage.py test  # ha vannak tesztek
```

## 13. Tesztelés és minőségbiztosítás

- Ajánlott egység- és integrációs tesztek: importer idempotencia, OffersForEtelView aggregációs logika.
- CI: GitHub Actions workflow, ami lefuttatja a migrációt és a teszteket push/PR eseményeknél.

## 14. Fejlesztési javaslatok és következő lépések

- Integrálni Django permissions + Groups vagy `django-guardian` az RBAC finomítása érdekében.
- Írni `attach_koltseg_to_etel` adat-migrációs parancsot a meglévő `EtteremKoltseg` sorok etel-re történő hozzárendeléséhez.
- Tesztek: `catalog/tests/test_import_scraped.py` és `compare/tests/test_offers_for_etel.py`.
- Ha offline/állandó képekre van szükség: mozgatni a képeket `static/fixtures_images/` mappába és a `kep_url`-eket helyi linkekre cserélni.

## 15. Melléklet: Védésre hasznos idézet és magyarázat (kérés szerint)

Idézet a védésről (szerkesztett):

"Belekérdezett egy részbe (Zoli): konkrétan az RBAC megoldásomba — mutattam neki, hogy másnak az adatbázis entry-jét csak admin tudja törölni. Aztán backend és frontend megoldást kellett elmagyaráznom. Néhányan bólintottak. Bemutattam az appot; annyit kérdezett, hogy a 'typeracer' játéknál honnan szedi a code snippet-eket. (Roland: Megmutatod neki és kész.)"

Magyarázat a védésre: ez a pillanat jó demonstrációs alkalom arra, hogy:

- megmutasd a DeleteView és a permission mixin implementációját (backend védelmi réteg),
- mutasd meg a frontend gomb elrejtését, ha a felhasználó nem jogosult,
- beszélj a jövőbeli fejlesztési lehetőségekről (pl. objektumszintű jogosultságok). És ha a 'typeracer' játékról kérdeznek, mutasd meg a generator vagy a `wolt_data.json`-ban tárolt snippet-forrást.

## 16. Záró gondolatok

Ez a dokumentáció célja, hogy a projektet teljesen átláthatóvá tegye — a védésre készülő diák pontosan tudja, hol mutassa meg a projekt erősségeit (idempotens import, admin & RBAC, generator), és hogyan tud válaszolni a kritikus kérdésekre (security, env-kezelés, adatmodell). A dokumentum nem csak leírás: ad lépésről-lépésre parancsokat, fejlesztési javaslatokat és védéshez használható Q&A-t.

Ha szeretnéd, létrehozok egy rövidebb védés-sablont (pptx vagy PDF) ebből a dokumentumból, illetve beleteszem a kulcs kódrészleteket és parancsokat külön appendix fájlba.

---

Dokumentum vége. (Fájl: `DOCS/PROJECT_DOCUMENTATION.md`)
