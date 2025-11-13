DOKUMENTÁCIÓ — Food Delivery Comparator
=======================================

Ez a dokumentáció átfogó, gondosan szerkesztett leírása a "Food Delivery Comparator" projektnek. Célja, hogy egy egyetemi/oktatási védésre és karbantartásra alkalmas, tanulható anyagot adjon: tartalmazza a projekt célját, architektúráját, részletes magyarázatot az adatmodellekről, a scraper- és import-pipeline-ról, a backend és frontend megoldásokról, az admin/RBAC megvalósításról, az env- és telepítési lépésekről, továbbá tipikus kérdések és jó válaszok (védéshez készülőknek).

A dokumentum felépítése
----------------------

1. Összefoglaló
2. Célkitűzések és követelmények
3. Architektúra áttekintés
4. Adatmodell és adatbázis
5. Scraper-ek és adatextrakció
6. Importer és idempotens feltöltés
7. Backend (Django) részletek
8. Frontend (projektben található) részletek
9. Admin felület és RBAC (jogosultságkezelés)
10. Környezeti beállítások és üzemeltetés (env-ek)
11. Migrációk, verziózás, CI javaslat
12. Hibakeresés és gyakori problémák (Playwright, PowerShell stb.)
13. Védésre szánt kérdések és mintaválaszok (Q&A)
14. Mellékletek: fontos fájlok és parancsok


1. Összefoglaló
----------------

A "Food Delivery Comparator" egy Django alapú alkalmazás, amely demonstrációs célból különböző étel-kiszállító platformok (például Wolt, Foodora) ajánlatait, áraikat és költségeit hasonlítja össze. A projekt célja kettős: (1) bemutatni egy adat-extraháló + importáló pipeline megvalósítását, és (2) egy tanulható, védésre alkalmas referencia megvalósítást adni, amely kiterjed az RBAC (Role-Based Access Control) megoldásra és adminisztrációra.

A rendszer két fő adatforrást használ: statikus HTML fájlokba épített demo-oldalakat (data/wolt.html, data/foodora.html), valamint headless böngészővel nyert runtime JavaScript objektumokat (Playwright). Az adatok JSON-ba kerülnek kinyerésre (`data/*.extracted.json`), majd a `python manage.py import_scraped` parancs idempotens módon importálja őket a Django modellekbe.


2. Célkitűzések és követelmények
--------------------------------

- Pontos és idempotens import a következő modellekre: Etterem (éttermek), Etel (ételek), EtteremKoltseg (rejtett költségek), EtteremEtelInfo (ajánlatok/összekapcsolások).
- Kétféle scraper: egyszerű HTML-extraktor (Wolt) és headless, JS-futtatást végző scraper (Foodora) a runtime `DATA` objektum kivonására.
- Jól dokumentált fejlesztői munkafolyamat (venv, Playwright, migrációk, commit szabályok).
- RBAC — adminok és jogosultságok: a management/admin felületen biztosítani, hogy bizonyos műveletek (pl. mások adatainak törlése) csak admin szintű felhasználóknak legyenek elérhetők.
- Oktatási/védési követelmények: a dokumentáció tartalmazza a védésnél várható kérdésekre adott, jól strukturált válaszokat.


3. Architektúra áttekintés
--------------------------

- Backend: Django (projekt gyökér: `foodcompare`/`manage.py`), alkalmazások: `catalog`, `compare`, `billing`, `users`, `registration`. A `catalog` kezeli az éttermek/ételek modelleket és az import parancsot.
- Adatforrások: `data/` könyvtárban található demo HTML fájlok és a generátor.
- Scraper és segédfájlok: `scripts/` könyvtárban (scrape_wolt.py, scrape_foodora.py, scrape_foodora_browser.py, extract_payload.py, generate_foodora_payload.py).
- Admin és RBAC: `users` appban egyedi user model és admin regisztráció; `mixins.py` és admin osztályok implementálnak jogosultság-ellenőrzéseket.
- Deployment / fejlesztői munkafolyamat: virtuális környezet, `requirements.txt`, Playwright telepítése (`python -m playwright install`), `makemigrations` → `migrate` → commit migrációk.


4. Adatmodell és adatbázis
-------------------------

Itt röviden összefoglaljuk a fontos modelleket és a közöttük lévő kapcsolatok logikáját. A részletes kód a `catalog/models.py`, `compare/models.py`, `billing/models.py` fájlokban található.

Fő modellek (sorrend és logika):
- Etterem (étterem): alap adatok (id, név, cím, platform). Primer kulcs: id.
- Etel (étel): id, név, leírás, kategória, kép URL.
- EtteremKoltseg (rejtett költség): minden egyes étteremhez tartozó költség-típusok (szállítás, csomagolás, borravaló). Kapcsolat: N:1 Etterem.
- EtteremEtelInfo (ajánlat): kapcsolja össze az ételeket és éttermeket, tartalmaz árat, promóciót, szállítási időt, értékelést, és referenciákat (_food, _restaurant, _costs a JSON importból). Ez a tábla használatos a compare funkcióhoz.

Kapcsolatok (példák):
- Egy `Etterem` több `EtteremEtelInfo`-val rendelkezhet (1:N).
- Egy `Etel` több `EtteremEtelInfo`-hoz kapcsolódhat (1:N).
- `EtteremKoltseg` 1:N kapcsolatban van az éttermekkel.

Adat-integritás és idempotencia az importnál:
- Az `import_scraped` management command úgy működik, hogy beazonosítja az entitásokat külső azonosítók alapján (pl. `id` vagy egyedi slug), és CREATE-or-UPDATE logikát alkalmaz. Ez biztosítja, hogy a többszöri futtatás nem hoz létre duplikátumokat.


5. Scraper-ek és adatextrakció
------------------------------

A projekt két megközelítést használ:

A) Wolt — statikus / inline JSON
- `scripts/scrape_wolt.py` és `scripts/extract_payload.py`: ezek a fájlok a HTML-be ágyazott JSON-t keresik (pl. `<script id="scrape_payload" type="application/json">` vagy inline JS objektumok), kinyerik és normalizálják azt JSON formátumba.
- Előny: gyors, determinisztikus, nincs szükség böngészőre.
- Hátrány: működik csak ha az oldal beágyazott JSON-t tartalmaz.

B) Foodora — runtime JS (headless)
- `scripts/scrape_foodora_browser.py`: Playwright használatával megnyitja a `data/foodora.html` fájlt, lefuttatja a kliens-oldali JavaScriptet, és kinyeri a futás közben létrejött adatszerkezetet.
- A demó HTML `let DATA = buildDataset()` formában hozza létre az adatot (tehát nem feltétlenül lesz `window.DATA`). Ezért a scraper több stratégiát próbál:
  1) közvetlenül ellenőrzi `DATA`-t (top-level),
  2) megnézi `window.DATA`/`globalThis.DATA`-t,
  3) ha elérhető, meghívja `buildDataset()`-et,
  4) végső esetben rekonstruálja a táblázat tartalmát a DOM-ból (#offers tbody tr).
- A script képes automatikus telepítésre, ha Playwright hiányzik (megpróbál `pip install playwright` és `python -m playwright install` futtatni), de célszerű a fejlesztőnek manuálisan telepíteni a függőséget offline/korlátozott környezetek miatt.

Futtatás és output:
- Mindkét scraper JSON fájlokat ír a `data/` könyvtárba: pl. `data/wolt.html.extracted.json`, `data/foodora.html.extracted.json`.
- Ezeket a `python manage.py import_scraped` parancs dolgozza fel a következő lépésben.


6. Importer és idempotens feltöltés
----------------------------------

A `catalog/management/commands/import_scraped.py` parancs felelős az extrahált JSON fájlok feldolgozásáért és a Django modellek feltöltéséért. Fontos viselkedés:
- Idempotencia: ellenőrzi, hogy egy entitás már létezik-e a céltáblában (külső azonosító vagy név/megegyezés alapján) és frissíti azt CREATE helyett.
- Normalizáció: ha a JSON fájl beágyazott referenciákat (pl. `_food`, `_restaurant`) tartalmaz, azokból kinyerjük a szükséges adatokat (pl. Etel, Etterem) és külön sorokat hozunk létre, majd a kapcsolódó info rekordot.
- Költségek és összegképzés: `EtteremKoltseg`-et generáljuk az `offers`-ból található `_costs` mezők alapján.

Verziókövetés és rollback: mivel a parancs módosításokat végez az adatbázison, fejlesztés és védés előtt javasolt teszt adatbázison kipróbálni a parancsot és ellenőrizni a hatásokat (pl. először futtasd `--dry-run` opciót, ha van ilyen, vagy készíts DB backupot).


7. Backend (Django) részletek
----------------------------

- Project konfiguráció: `foodcompare/settings.py` tartalmazza az alkalmazás-beállításokat. Fontos beállítások: `AUTH_USER_MODEL` (egyedi felhasználó modell), `INSTALLED_APPS` és adatbázis beállítások (alapértelmezett sqlite3 a projektben).
- Admin: a `admin.py` fájlokban regisztráljuk a modelleket. A projekt korábbi verzióiban külön `Jog` és `FelhJog` modellek is szerepeltek, de ezek eltávolításra kerültek; a dokumentáció további hivatkozásai frissítve lettek. Az admin felületet kiegészítjük egyedi `ModelAdmin` osztályokkal, ahol szükséges jogosultság-ellenőrzést végzünk (lásd RBAC rész).
- Management parancsok: `import_scraped` a `catalog` alatt található. A `scripts/` mappában lévő szkriptek a fejlesztői pipeline-t szolgálják.
- Tesztek: kisebb unit tesztek vannak az alkalmazások `tests.py` fájljaiban; javasolt további teszteket írni az importer és a RBAC kritikus pontokra.


8. Frontend (projektben található) részletek
-------------------------------------------

A projekt frontend része egyszerű, szerver-oldali renderelt Django sablonokra épül (a `templates/` könyvtárban). A demo HTML oldalak (`data/*.html`) a scraping és demonstráció célját szolgálják — nem részei egy publikusan elérhető production frontendnek, hanem a scrapper és importer fejlesztéséhez készített példák.

Főbb fájlok:
- `templates/compare/offers_for_etel.html`, `templates/compare/saved_foods.html` stb. — a sablonok, ahol a compare funkció megjelenik.
- A sablonok és a CBV/FBV nézetek (`views.py`) közötti kapcsolat egyszerű: a view lekéri a modelleket és átadja a sablonnak a megjelenítéshez.


9. Admin felület és RBAC (jogosultságkezelés)
---------------------------------------------

Ez a rész különösen fontos a védés szempontjából — itt részletesen leírjuk az RBAC-ot és megindokoljuk a döntéseket.

Cél: biztosítani, hogy bizonyos műveletek (például egy másik felhasználó vagy étterem rekordjainak törlése) kizárólag magasabb jogosultságú felhasználók (adminok) számára legyenek elérhetők.

Megoldás összefoglalása:
- Egyedi `AUTH_USER_MODEL` és a `users` app: a felhasználóknak szerepeket/jogosultságokat rendelünk (például staff/admin flag, vagy tetszőleges `Permission` modellek használata).
- Admin felület: a `ModelAdmin`-okban felügyeltük a törlési és módosítási jogosultságokat. Például a `has_delete_permission` override-dal megakadályozhatjuk, hogy egy normál staff user töröljön olyan rekordot, ami más felhasználóhoz kapcsolódik.
- Backend ellenőrzés: minden kritikus műveletnél (például REST endpoint vagy management művelet) a nézet/függvény ellenőrzi a felhasználó jogosultságát; nem csak a frontendre hagyatkozunk. Ez védi a rendszert ha valaki közvetlen API hívásokat küld.

Konkrét példa (Zoli kérdésére a védésen):
- Kérdés: "Más felhasználó adatbázis bejegyzését miért csak admin törölheti?"
- Válasz (összefoglalva a védésben): az adat-tulajdon (data ownership) biztosítása érdekében bizonyos rekordoknál (például egy mentett étel vagy mentés, vagy egy érzékeny költség rekord) csak azok az entitások (vagy adminok) rendelkezhetnek törlési joggal, hogy megakadályozzuk az adatok véletlen vagy rosszindulatú törlését. A megvalósítás a következő lépésekben történik:
  1) a `ModelAdmin`-ban `has_delete_permission(self, request, obj=None)` felülírás,
  2) backend nézeteknél explicit ellenőrzés: `if not request.user.is_staff and obj.owner != request.user: raise PermissionDenied()`
  3) audit logolás (opcionális): minden törlés eseményt naplózunk admin audit célokra.

Miért ez jó a védésnél:
- A védésednél bemutathatod a koncepciót: principle of least privilege (minimális jogosultság), defense-in-depth (többszintű ellenőrzés: frontend + backend + admin) és auditálhatóság.

Frontend és backend munka megosztása a jogosultság kezelésnél:
- Frontend: gombok/akcók elrejtése a nem jogosult felhasználók elől (UX javítása).
- Backend: minden kritikus műveletnél ellenőrizni a jogosultságot, mert a front-end nem számít biztonsági határvonalnak.


10. Környezeti beállítások és üzemeltetés (env-ek)
--------------------------------------------------

Fontos, hogy a projekt reprodukálható legyen fejlesztői gépen. Alap lépések:

1) Virtuális környezet
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1  # PowerShell (dot-source!)
# vagy Windows cmd: .venv\Scripts\activate.bat
```

2) Függőségek
```powershell
pip install -r requirements.txt
```

3) Playwright (csak ha headless scraping kell)
```powershell
pip install playwright
python -m playwright install
```

4) Környezeti változók (példa `.env` / helyi config)
- SECRET_KEY: Django titkos kulcs (soha ne töltsd fel VCS-be)
- DJANGO_DEBUG: True/False
- DATABASE_URL: (ha nem sqlite)
- PLAYWRIGHT_BROWSERS_PATH: opció a Playwright offline telepítésnél

A dokumentációban található `DOCS/POWERSHELL_ACTIVATION.md` leírja a PowerShell-specifikus hibákat és megoldásokat (ExecutionPolicy, dot-source stb.).


11. Migrációk, verziózás, CI javaslat
------------------------------------

- Folyamat: minden model változtatás után futtasd a `makemigrations`-t, majd `migrate`-et, majd commitold a migration fájlokat.

Példa parancsok (PowerShell):
```powershell
python manage.py makemigrations --dry-run --verbosity 3
python manage.py makemigrations
python manage.py migrate
```

CI javaslat: add egy lépést mely lefuttatja `python manage.py makemigrations --check` — ez meghiúsítja a buildet, ha kimaradt egy migráció.

Version control: minden kód és migráció commitolva legyen; `data/` példafájlok lehetnek, de ha valós userdata keletkezik belőle, azt kezelni kell `.gitignore`-lal.


12. Hibakeresés és gyakori problémák
------------------------------------

Playwright / PowerShell problémák:
- Hiba: "'.\\.venv\\Scripts\\Activate.ps1' is not recognized" — ok: rossz aktiválás, vagy ExecutionPolicy blokkolja. Megoldás: dot-source `. .\.venv\Scripts\Activate.ps1` és ha kell `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force`.
- Hiba: Playwright import fail / browser binaries hiányoznak — megoldás: `pip install playwright` és `python -m playwright install`.
- Ha offline gépen dolgozol, a script automatikus pip-install-je meghiúsul — ilyenkor a generátort (`--regen`) vagy előre letöltött binárakat használj.

Scraper timeout-ok:
- A Foodora demó oldala `let DATA = buildDataset()`-et használ. Ez nem lesz `window.DATA`, ezért a korábbi megközelítés, ami `window.DATA`-ra várt, timeout-olt. A javított scraper most több stratégiát alkalmaz (DATA, window.DATA, buildDataset() call, vagy DOM rekonstrukció), így ez a probléma megoldva.

Import hibák / idempotencia:
- Ha duplikátumok keletkeznek: ellenőrizd az import key-t (milyen mező alapján azonosítjuk az entitást). Javasolt egyedi külső azonosító használata (pl. provider-id vagy slug).


13. Védésre szánt kérdések és mintaválaszok (Q&A)
--------------------------------------------------

Az alábbiakban gyakori, a védésen várható kérdések és rövid, pontos válaszok találhatók. Használd őket úgy, hogy a védés során részletesen kifejted a rövid választ.

Q1: Mi a projekt célja? (röviden)
A1: Versenytárselemzés demonstrációs célból: több food-delivery platform ajánlatait összehasonlítjuk egy egységes modell mentén, automatizált scraping és idempotens import pipeline segítségével.

Q2: Miért kétféle scraper szükséges?
A2: Különböző oldalak különböző módszerekkel szolgáltatják az adatot. Néhány oldal inline JSON-t ad (Wolt), mások a kliens-oldali JS által generált runtime objektumot használják (Foodora). A headless módszer biztosítja, hogy a JS által előállított adatok is kinyerhetők.

Q3: Hogyan biztosítod, hogy az import idempotens?
A3: Az importer egyedi kulcs alapján keres (pl. provider-side id), és ha létezik, frissíti a rekordot helyette. Így többszöri futtatás nem hoz létre duplikátumot.

Q4 (Zoli kérdése): Miért csak admin törölheti mások bejegyzését? Hogyan néz ki ez a backendben és a frontendben?
A4: Koncepció: adat tulajdonlás és biztonság. Backend: `ModelAdmin.has_delete_permission` és nézet-szintű ellenőrzés (`if obj.owner != request.user and not request.user.is_staff: raise PermissionDenied`). Frontend: a törlés gomb rejtése, de ez csak UX; a végső védelmet a backend adja.

Q5: Hol vannak a jogosultságok definiálva? Használtál-e Django permissions-t vagy custom megoldást?
A5: A projekt az alap Django felhasználói/jogosultsági rendszert használja (is_staff / is_superuser), és a `users` app kiegészíti a modellt. Kritikus helyeken explicit ellenőrzést végzünk; szükség esetén a Django `Permission` modeljét is lehet használni további finom jogosultságokra.

Q6: Mi történik, ha a scraping forrás szerkezete megváltozik?
A6: A scraper hibát jelez (timeout, nem található JSON), és fallback-el a generátorra. A produkciós scraper-eket érdemes monitorozni és unit/integration tesztekkel védeni. Verziózás és gyors patch-elés javasolt.

Q7: Milyen mérlegelési szempontok voltak a fejlesztésnél (miért Django stb.)?
A7: Django gyors fejlesztést, beépített admin-t és robusztus ORM-et ad; jól illeszkedik az oktatási célhoz. A cél nem volt mikroservices-architektúra, hanem egy monolit, amiből könnyű demonstrálni a teljes adatfolyamot.

Q8: Hogyan lehet a rendszer biztonságát növelni production környezetben?
A8: HTTPS minden kapcsolatnál, erős SECRET_KEY menedzsment (környezeti változók/vault), DB jogosultságok korlátozása, audit naplók, rate-limiting az importoknál, és CI lint/tests előtti deploy lépések.


14. Mellékletek: fontos fájlok, parancsok és hivatkozások
---------------------------------------------------------

Fontos fájlok a repo-ban:
- `manage.py` — Django manage parancsok
- `foodcompare/settings.py` — projektbeállítások
- `catalog/management/commands/import_scraped.py` — importer
- `scripts/scrape_foodora_browser.py` — Playwright alapú scraper
- `scripts/scrape_wolt.py`, `scripts/extract_payload.py` — Wolt extractor
- `data/foodora.html`, `data/wolt.html` — demo források
- `templates/` — Django sablonok
- `DOCS/POWERSHELL_ACTIVATION.md` — PowerShell venv hiba és megoldás

Gyakori parancsok (PowerShell):
```powershell
# venv és aktiválás
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
. .\.venv\Scripts\Activate.ps1

# függőségek
pip install -r requirements.txt
python -m playwright install

# scrappek
python .\scripts\scrape_wolt.py
python .\scripts\scrape_foodora_browser.py --headful --screenshot
# vagy fallback generátor
python .\scripts\scrape_foodora.py --regen

# import
python manage.py import_scraped

# migráció workflow
python manage.py makemigrations --dry-run --verbosity 3
python manage.py makemigrations
python manage.py migrate
```

Védési tanácsok / prezentációs javaslatok
----------------------------------------

- Kezdd a bemutatót egy rövid, 2-3 diás áttekintéssel: mi a cél, hogyan épül fel az adatfolyam (scrape → extract → import → compare → admin).
- Mutasd meg a kód főbb fájljait (importer, scraper, models), majd indítsd el a `scrape_foodora_browser.py --headful --screenshot`-et, hogy élőben lássák a runtime adatképzést.
- RBAC demo: mutasd meg egy non-admin és admin felhasználó próbálkozását a törlésre; magyarázd el a backend-ellenőrzést és a `has_delete_permission` működését.
- Készülj tipikus kérdésekre (DB normalizáció, idempotencia, hibakezelés, offline telepítés esetén mit csinálsz).


Összegzés
---------

Ez a dokumentáció célzottan részletes és tantárgyi/védésre optimalizált: végigvezet a projekt felépítésén, a kritikus tervezési döntéseken (RBAC, idempotens import), és tartalmazza a parancsokat, amelyekkel egy fejlesztő reprodukálhatja a környezetet és az adatfolyamot. Ha szeretnéd, a következő iterációban hozzáadok diagramokat (ER-diagram, architektúra diagram), vagy bővítem a Q&A szekciót további, a vizsgáztatók által gyakran feltett kérdésekkel.
