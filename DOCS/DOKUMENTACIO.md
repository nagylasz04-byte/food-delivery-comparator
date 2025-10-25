% DOKUMENTÁCIÓ - Food Delivery Comparator

Ez a dokumentáció a "food-delivery-comparator" projekt teljes, szakdolgozatszerű, ugyanakkor könnyen tanulható ismertetése.
Cél: aki ezt áttanulmányozza, értse a rendszer architektúráját, adatmodelljét, jogosultságkezelését (RBAC), a scrapperek/átalakító import folyamatot, a fejlesztői környezetet és választ tud adni a védésen felmerülő kérdésekre.

## Rövid összefoglaló

A projekt célja: több magyarországi ételszállító-platform (például Wolt, Foodora) HTML mintáiból kinyerni egy egységes, géppel feldolgozható JSON formátumot, majd ezt az adatot idempotens importfolyamat segítségével feltölteni egy Django alapú rendszert. A rendszer modellezi az éttermeket, ételeket, platform- és étterem-szintű költségeket, valamint az egyes ételekhez tartozó platform-specifikus információkat.

Kiemelt szempontok:
- Idempotens import (ismételt futtatás nem hoz létre duplikátumot).
- Kétféle scraping megközelítés: beágyazott JSON kinyerése (Wolt) és kliens-oldali JS futtatás utáni kinyerés (Foodora — headless browser / Playwright). 
- Egyszerű RBAC (role-based access control) és admin felület a jogosultságok kezelésére.

## Célközönség és tanulási célok

Ez a dokumentáció olyan hallgatónak, vizsgázónak vagy fejlesztőnek készült, aki:
- meg akarja érteni a teljes adatáramlást (HTML fixture -> extracted JSON -> import -> DB),
- képes reprodukálni a fejlesztői környezetet és futtatni a scraping + import folyamatot,
- meg akarja érteni a jogosultságkezelés és admin felület megvalósítását (backend + frontend okok és döntések),
- felkészülne a védésen (Q&A rész a dokumentumban).

## Fájl- és komponensáttekintés (magas szinten)

- Projekt gyökér: a Django projekt (manage.py, settings.py).
- Alkalmazások (apps):
  - `catalog` — az éttermek/ételek/kapcsolódó import logika (models, admin, import parancsok).
  - `billing` — költségek modelljei (`EtteremKoltseg`) és költség-típusok.
  - `compare` — összehasonlító nézetek és sablonok (pl. ajánlatok listázása étekhez).
  - `users` — egyedi user modell (`Felhasznalo`), és egyszerű RBAC entitások (`Jog`, `FelhJog`).
- Scripts: `scripts/` mappában találhatóak a scrapper és generator segédeszközök (pl. `scrape_wolt.py`, `scrape_foodora_browser.py`, `generate_foodora_payload.py`, `extract_payload.py`).
- Import: a `catalog/management/commands/import_scraped.py` fájl végzi az extracted JSON fájlok adatbázisba töltését.

## Részletes architektúra

1) Adatforrások és scrapperek

- Wolt: a `data/wolt.html` tartalmaz beágyazott, olvasható JSON-t (`INLINE_WOLT_DATA` és/vagy `<script id="scrape_payload">`). Ehhez a `scripts/scrape_wolt.py` egy gyors kinyerő, amely a beágyazott JSON-t extractálja és `data/wolt.html.extracted.json`-t hoz létre.
- Foodora: a demo oldal kliens-oldali JS futtatásával generál véletlenszerű `DATA` objektumot. Két megközelítés használható:
  - Headless scraping: `scripts/scrape_foodora_browser.py` megnyitja a `foodora.html`-t egy headless böngészőben (Playwright) és kiértékeli a futó `DATA` objektumot, majd JSON fájlt ír.
  - Generátor: `scripts/generate_foodora_payload.py` képes szerver-oldalonhoz hasonló, determinisztikus vagy véletlenszerű payload-ot előállítani (`--seed` opció ajánlott, ha reprodukálható eredményt akarunk).

2) Extractor és JSON forma

- A projekt `scripts/extract_payload.py` heurisztikusan keres `id="scrape_payload"` script blokkot (application/json) és további eshetőségeket (INLINE_*_DATA, JS objektumok) támogat. A cél, hogy egy közös, kanonikus payload jöjjön létre az import számára.
- A canonical payload kulcsai (példa):
  - `etterem`: lista az éttermekről (id, nev, cim, platform, platform_url, platform_logo_url)
  - `etel`: lista az ételekről (id, nev, leiras, kategoria, kep_url)
  - `etterem_koltseg`: platform- vagy etterem-szintű költségek (etterem_id vagy platform, koltseg_tipus, osszeg)
  - `etterem_etel_info`: kapcsoló tábla, amely megadja, hogy melyik etterem melyik etelt árulja és milyen platform_url/id-vel

3) Import logika

- A `catalog/management/commands/import_scraped.py` olvassa a `data/*.extracted.json` fájlokat, és idempotensen hozza létre vagy frissíti az alábbi entitásokat:
  - `Etterem` (név, platform, cím, platform_url, platform_logo_url)
  - `Etel` (név, leírás, kategória, kép URL)
  - `EtteremKoltseg` (etterem-rendezett vagy platform-szintű költség)
  - `EtteremEtelInfo` (összekapcsolás: melyik étterem árulja a terméket — ár, platform link stb.)

- Az import prioritása: ha létezik match (név normalizálva), akkor frissít; különben létrehoz. Az import során platform- és etterem-szintű költségeket megfelelően párosítjuk.

4) Adatmodell részletek (főbb mezők)

- `catalog.Etel`: nev, leiras, kategoria, kep_url
- `catalog.Etterem`: nev, cim, platform, platform_logo_url, platform_url (platform a `PLATFORMOK` choices: wolt/foodora/bolt/egyeb)
- `billing.EtteremKoltseg`: etterem (nullable), etel (nullable), platform (ha etterem None), koltseg_tipus (szallitas/csomagolas/borravalo/egyeb), osszeg
- `users.Felhasznalo`: egyedi user modell, tartalmaz `kedvenc_etterem` FK-t
- RBAC entitások: `users.Jog` és `users.FelhJog` — ezek admin-kezelt domain-jogok, de az alap írási jogosultságok (Create/Update/Delete) a `WritePermissionRequired` mixin alapján `is_staff` mezőhöz kötöttek.

## Jogosultságkezelés (RBAC) — részletesen

Tervezési elv: egyszerű, áttekinthető, és oktatási célra jól demonstrálható RBAC réteg.

1) Modellezés: `Jog` és `FelhJog`
- `Jog`: domain-szintű jog megnevezése (pl. "sajat_objektum_torlese").
- `FelhJog`: kapcsoló tábla, amely hozzárendeli a `Jog`-okat felhasználókhoz.

2) Írási jogok és admin-szintű tiltások
- A szerző által hozott döntés: minden írási művelet (Create/Update/Delete) csak akkor engedélyezett, ha a felhasználó `is_staff` (vagy superuser). Ezt a `foodcompare.mixins.WritePermissionRequired` osztály valósítja meg: a `test_func()` metódus ellenőrzi `user.is_staff` és `user.is_authenticated`.
- Emellett a Class-based views `permission_required` mezői használják a Django beépített permission-okat (pl. `users.add_jog`, `users.change_felhjog`), így a belső API a Django-permission rendszert is támogathatja.

3) Admin felület szerepe
- A projekt admin-oldala (`/admin/`) a jogosultságok fő kezelőfelülete: itt lehet `Jog`-okat létrehozni, felhasználók `is_staff` vagy `is_superuser` jelölését beállítani, és FelhJog kapcsolatokat hozzárendelni.
- Fontos: az admin felület egyszerre ad lehetőséget finomhangolásra és auditálásra (ki-mihez fér hozzá). A `users.admin.FelhasznaloAdmin`-ban szerepel az `autocomplete_fields = ('kedvenc_etterem',)` beállítás, ami könnyíti a kapcsolatok kezelését.

4) Minta eset a védésben (hogyan válaszold)
- Kérdés: "Mi garantálja, hogy más felhasználók bejegyzését ne tudja bárki törölni?"
  - Válasz: A projekt választása az volt, hogy a write (Create/Update/Delete) útvonalakat csak staff felhasználók hajthatják végre. Ez a `WritePermissionRequired` mixinben van definiálva (UserPassesTestMixin, ahol a test a `user.is_staff`). A CRUD view-k (CreateView/UpdateView/DeleteView) öröklik a mixint és a `permission_required` stringekkel együtt biztosítják a Django permission-rendszer és a staff-szűrés kettős védelmét. További finomhangolásként a `Jog`/`FelhJog` segítségével domain-specifikus jogokat lehet adminisztrálni és később middleware/Decorator segítségével érvényesíteni a runtime-on.

## Frontend és backend integráció — hogyan működik együtt a két réteg

- Backend: Django CBV-k (ListView/DetailView/CreateView/UpdateView/DeleteView) + mixins a jogosultságokhoz. A backend adja a sablonokat és API-szerű endpoinokat.
- Frontend: szerver-sablonok (Django templates) + minimális JS (például a demo `data/foodora.html` generátor). A projekt nem tartalmaz SPA-t — cél a egyszerű, oktatási jellegű, szerver-oldali renderelt webapp.
- Példa kérdés a védésen: "Hogyan kezeli a frontend a jogosultságokat?"
  - Válasz: A frontend a backend által előállított sablonokra épít; írási űrlapok csak olyan felhasználóknak érhetők el, akiket a backend engedélyez (a view-okon keresztül). Az admin felület elkülönítetten biztosít szerkesztési lehetőséget.

## Admin felület fontossága

- Az admin felület a projekt központi kezelőfelülete: itt igazítjuk a `Jog`/`FelhJog` relációkat, jelöljük staff/superuser felhasználókat, és ellenőrizzük a rendszer adatállapotát (Etterem/Etel lista, költségek). Az admin könnyen használható, és a `catalog`/`users` admin-osztályai testreszabott listák, keresők és autocomplete mezők révén egyszerűsítik a kezelést.

## Környezeti változók és deployment tanácsok

- Jelenlegi `settings.py` fejlesztői módra van optimalizálva:
  - `SECRET_KEY` a repo-ban van (development convenience). Productionben ezt környezeti változóként kell ellátni.
  - `DATABASES` alapértelmezésben SQLite (`db.sqlite3`). Productionhez javasoljuk PostgreSQL/managed DB használatát és `DATABASE_URL` használatát.
  - `DEBUG = True` fejlesztői beállítás; productionben `DEBUG=False` és `ALLOWED_HOSTS` fentebb konfigurált.

Ajánlott env-ek és beállítások (ajánlás — jelenlegi repo nem tartalmaz `.env` betöltőt):
- SECRET_KEY — titkos kulcs
- DATABASE_URL — production DB kapcsolati string
- DEBUG — 0/1 vagy True/False
- ALLOWED_HOSTS — production hostok

Windows PowerShell példa (fejlesztés, lokálisan):

```powershell
$env:SECRET_KEY = "replace-for-local"
$env:DEBUG = "1"
python manage.py migrate
```

Megjegyzés: a projekt tartalmaz egy `run_dev.ps1` segédscriptet, amely gyakori fejlesztői lépéseket automatizál (migrate, scrapers, import, fejlesztői szerver indítása).

## Biztonsági megfontolások

- Titkok: sose hagyjuk a production SECRET_KEY-t a repo-ban.
- CSRF: Django alapértelmezetten védi a formokat a CSRF middleware-el (`CsrfViewMiddleware` be van kapcsolva a `settings.py`-ban).
- Jogosultságok: a projekt jelenlegi döntése a write-permissionek centralizálása `is_staff`-en keresztül. Ha finomabb RBAC kell, a `Jog`/`FelhJog` modellek használhatók runtime ellenőrzésekre (decorator/middleware vagy object-level permission check implementálható).
- Input validáció: a scrapperek által létrehozott JSON nem megbízható forrás (különösen ha valódi web scraping-ból származik) — érdemes sanitizálni és felülvizsgálni bemeneti mezőket, és korlátozni pl. image URL-ek méretét, elérhetőségét.

## Tesztelés és minőségbiztosítás

- Javaslat: írjunk egységteszteket az `import_scraped` parancshoz (happy path + 1-2 edge-case: platform-szintű költség vs etterem-szintű költség), és functional tests a jogosultságokra.
- A `todo` listában szerepel `catalog/tests/test_import_scraped.py` és `compare/tests/test_offers_for_etel.py` fájlok létrehozása.

## Működés reprodukálása — lépésről-lépésre

1) Klónozd a repót és lépj a projekt gyökérbe.
2) (Ajánlott) hozz létre virtuális környezetet és telepítsd a csomagokat.
3) Migrálj: `python manage.py migrate`.
4) Generálj vagy scrappel: 
   - Wolt: `python scripts/scrape_wolt.py` (kimenet: `data/wolt.html.extracted.json`).
   - Foodora (headless): `python scripts/scrape_foodora_browser.py` — előfeltétel: `playwright` és böngésző binárisok telepítve (`pip install playwright` és `playwright install`).
   - Vagy generálj reproducible payload-ot: `python scripts/generate_foodora_payload.py --seed 42`.
5) Importáld a JSON fájlokat: `python manage.py import_scraped`.
6) Futtasd a fejlesztői szervert: `python manage.py runserver` és böngészőben nézd meg az admin felületet (`/admin/`) és a felhasználói nézeteket.

## Hogyan adjunk hozzá új HTML fixture-et (összefoglaló)

1) Helyezd a HTML fájlt a `data/` mappába (pl. `data/ujplatform.html`).
2) Ellenőrizd, tartalmaz-e beágyazott JSON-t (`<script id="scrape_payload">`), vagy kliens-oldali JS generál-e adatot.
3) Ha van beágyazott JSON, készíts egy `scripts/scrape_<platform>.py` fájlt, amely a `extract_payload.py`-t használja.
4) Ha a platform JS-t futtat, írj egy headless scraper scriptet (Playwright vagy Puppeteer), amely megvárja a `window.DATA` vagy hasonló runtime objektumot és JSON-t ír.
5) Teszteld: futtasd a scraper-t és ellenőrizd a létrejövő `data/*.extracted.json` fájlt; majd futtasd az importot és nézd meg az adminban az entitásokat.

## Védésre felkészítő Q&A (példák és válasz-javaslatok)

- K: Hogyan biztosítod, hogy az import idempotens?
  - V: Az import kód `get_or_create` mintát használ, normalizált nevekkel és logikával, amely megpróbál meglévő rekordokat találni (etterem_by_normalized_name, etel cache stb.). Ha találat van, frissíti a mezőket, különben létrehozza őket. Így a többszöri import sem hoz duplikátumot.

- K: Miért van kétféle scraper a projektben?
  - V: A valós weboldalak sokszor generálnak adatot kliens-oldalon (Foodora-demo), míg mások inline JSON-t tartalmaznak (Wolt). A headless browser egy általános megoldás a runtime adat lekérésére; a beágyazott JSON gyorsabb és egyszerűbb, ha elérhető.

- K: A jogosultságokat hogyan implementáltad?
  - V: Kombinált megközelítést használok: Django built-in permissions (permission_required stringek a view-okon), admin-kezelés `Jog`/`FelhJog` modellekkel, és egy egyszerű mixin (`WritePermissionRequired`) amely staff-only írást tesz lehetővé. Ez csökkenti a felület komplexitását és megkönnyíti a védést.

- K: (konkrét dialógusrészlet beépítve a védésre):
  - Kérdező (Zoli): "Konkrétan az RBAC megoldásomba kérdezett: mert mutattam neki hogy másnak az adatbázis entry-jét csak admin tudja törölni. Aztán backend és frontend megoldást kellett elmagyarázzam."
  - Javasolt válasz: "A backend oldalon a `WritePermissionRequired` mixin biztosítja, hogy a Create/Update/Delete műveletek csak `is_staff` felhasználóknak legyenek elérhetők. A Django CBV-k `permission_required` attribútumai tovább korlátozzák a műveleteket a beépített permission-ok alapján. A frontend pedig ezekre az útvonalakra épít — az űrlap/link csak akkor jelenik meg a sablonban, ha a backend logikája engedélyezi (vagy a sablonban `if request.user.is_staff` feltétellel kontrolláljuk a gombok megjelenítését)."

- K: "A Typeracer játékhoz honnan szedi a code snippeteket?" (Roland kérdése — példa a védésre)
  - V: A projekt ezzel közvetlenül nem foglalkozik; ha demó vagy integráció van, akkor ezek a snippetek lehetnek statikus forrásból (fájl) vagy kisebb generátor scriptből (`scripts/` alatt). A válasz tehát: "Mutasd meg a forrásfájlt, ahonnan a snippet jön (például a `data/` mappát vagy egy dedikált `snippets/` fájlt)" — és röviden navigálj a kódba.

## Konkrét fájlok és helyük

- Scraper-ek: `scripts/`
- Extractor: `scripts/extract_payload.py`
- Import: `catalog/management/commands/import_scraped.py`
- RBAC modellek és admin: `users/models.py`, `users/admin.py`, `foodcompare/mixins.py`
- Beállítások: `foodcompare/settings.py`

## Fejlesztési javaslatok és további lépések

- Finomabb object-level permissions implementálása (pl. egy egyedi decorator, amely a `Jog`-okat használja runtime visszaigazolásra).
- Teljes tesztkészlet: importer unit tests, views permission tests.
- Dokumentált `requirements.txt` és CI pipeline, amely futtatja a migrációkat és a teszteket PR-enként.

## Összefoglalás

Ez a projekt oktatási célból készült arra, hogy bemutassa a modern web scraping → adat-transzformáció → idempotens adatbázis-import mintát, közben egyszerű és jól érthető jogosultságkezeléssel és admin felülettel. A dokumentum célja, hogy a vizsgázó teljesen felkészült legyen a védésre: technikai részletek, tervezési döntések és példaválaszok szerepelnek benne.

Ha szeretnéd, hogy ezt a fájlt angolul is elkészítsem, vagy kibővítsem diagramokkal/ERD-vel és kódrészletekkel (példák: import_scraped részletei), jelezd és hozzáadom.
