# Fejlesztői útmutató – A FoodCompare backend részletes bemutatása

A FoodCompare alkalmazás backendje a Django webes keretrendszerre épül, Python 3 nyelven íródott, és SQLite adatbázist használ fejlesztési környezetben. A backend felelős az adatmodellek definiálásáért, az üzleti logika végrehajtásáért, a felhasználókezelésért, a jogosultsági rendszerért, az adatbázis-migrációkért, az adatimport-pipeline (scraper + management command) működtetéséért, valamint a szerveroldali, template-alapú URL-routing és nézet (view) réteg kiszolgálásáért. A rendszer négy saját Django alkalmazásból (app) áll: `catalog`, `billing`, `compare` és `users`, amelyeket a központi `foodcompare` projekt fog össze.

A backend funkcionálisan az alábbi fő területeket fedi le:

- Projektstruktúra és konfiguráció (`settings.py`, `urls.py`)
- Adatmodellek és relációk (ORM)
- Nézetek és üzleti logika (views)
- Jogosultsági rendszer és mixinek
- URL-routing és névterek
- Django Admin testreszabás
- Felhasználókezelés és űrlapok (forms)
- Adatimport pipeline: scraperek és management command
- Egyedi template tag-ek
- Biztonsági megoldások és middleware

Az alábbiakban mindegyik területet részletesen bemutatom, modellstruktúrával és a belső működés ismertetésével együtt.

---

## Projektstruktúra és konfiguráció

A projekt gyökérkönyvtárában a `manage.py` fájl a Django parancssori belépési pontja. A központi konfiguráció a `foodcompare/settings.py` fájlban található.

### Telepített alkalmazások

Az `INSTALLED_APPS` listában a Django saját moduljai mellett négy saját alkalmazás szerepel.

Mindegyik alkalmazásnak meghatározott felelőssége van:

| Alkalmazás | Felelősség |
|------------|-----------|
| `users` | Egyedi felhasználói modell (`Felhasznalo`), regisztráció, felhasználókezelés |
| `catalog` | Éttermek (`Etterem`) és ételek (`Etel`) katalógusa, keresési logika |
| `billing` | Rejtett költségek (`EtteremKoltseg`) kezelése |
| `compare` | Ár-összehasonlítás (`EtteremEtelInfo`), mentések (`Mentes`), termékoldal |

### Egyedi felhasználói modell

A Django alapértelmezett `User` modellje helyett a projekt egyedi felhasználói modellt használ (`AUTH_USER_MODEL = "users.Felhasznalo"`). Ez a beállítás kulcsfontosságú: a projekt teljes autentikációs rendszere erre a modellre épül, és minden `ForeignKey` hivatkozás a felhasználói modellre ezen keresztül történik.

### Adatbázis-konfiguráció

Fejlesztési környezetben SQLite adatbázis szolgál az adattárolásra. A `BASE_DIR` a projekt gyökérkönyvtárára mutat, amelyet a `Path(__file__).resolve().parent.parent` kifejezés határozza meg, és az adatbázis fájl a `db.sqlite3` néven a projekt gyökerében helyezkedik el.

### Middleware-sor

A middleware-sor a kérések és válaszok feldolgozásának rendjét határozza meg. A sorrend fontos: a `SessionMiddleware`-nak az `AuthenticationMiddleware` előtt kell állnia, hogy a munkamenet-alapú autentikáció megfelelően működjön. A `CsrfViewMiddleware` biztosítja a CSRF-védelmet minden POST-kérésnél, az `XFrameOptionsMiddleware` pedig megakadályozza az oldalak iframe-be ágyazását (clickjacking védelem).

### Lokalizáció és időzóna

Az alkalmazás magyar lokalizációval (`LANGUAGE_CODE = "hu-hu"`) és budapesti időzónával (`TIME_ZONE = "Europe/Budapest"`) működik. Az `USE_TZ = True` beállítás biztosítja, hogy minden `DateTimeField` időzóna-tudatos (timezone-aware) értékeket tároljon.

---

## Adatmodellek és relációk

A FoodCompare adatmodelljei négy alkalmazás között oszlanak meg. A főbb entitások és kapcsolataik:

- A `Felhasznalo` (users) opcionálisan hivatkozik egy `Etterem`-re (`kedvenc_etterem`, FK, nullable), és inverz kapcsolatban áll a `Mentes` modellel.
- Az `Etel` (catalog) inverz kapcsolatban áll az `EtteremEtelInfo`, `Mentes` és `EtteremKoltseg` modellekkel.
- Az `Etterem` (catalog) inverz kapcsolatban áll az `EtteremEtelInfo`, `EtteremKoltseg` és `Felhasznalo` modellekkel.
- Az `EtteremEtelInfo` (compare) az `Etel` és `Etterem` modellekre hivatkozik FK-val, `unique_together: (etel, etterem, platform)` megkötéssel.
- A `Mentes` (compare) a `Felhasznalo` és `Etel` modellekre hivatkozik FK-val, `unique_together: (felhasznalo, etel)` megkötéssel.
- Az `EtteremKoltseg` (billing) opcionálisan hivatkozik `Etterem`-re és `Etel`-re (mindkettő FK, nullable), és tartalmaz egy `platform` CharField mezőt.

### Etel modell (catalog alkalmazás)

Az `Etel` modell egy ételt reprezentál, platformfüggetlenül. Ugyanaz az étel (például „Margherita pizza") több étteremben és több platformon is elérhető lehet.

| Mező | Típus | Leírás |
|------|-------|--------|
| `nev` | `CharField(150)` | Az étel neve (kötelező) |
| `leiras` | `TextField` | Szabad szöveges leírás (opcionális) |
| `kategoria` | `CharField(50)` | Kategória, pl. „Pizza", „Burger" (opcionális) |
| `kep_url` | `URLField` | Az étel képének URL-je (opcionális) |

Az `Etel` modellnek nincs platform-kötöttsége — ez a szándékos tervezési döntés teszi lehetővé, hogy ugyanazt az ételt több platform ajánlatával is összekapcsoljuk.

### Etterem modell (catalog alkalmazás)

Az `Etterem` modell egy éttermet reprezentál egy adott platformon. Ugyanaz az étterem különböző platformokon különböző rekordként jelenik meg.

A `PLATFORMOK` tuple a Django `choices` mechanizmusával biztosítja, hogy a `platform` mező csak előre meghatározott értékeket vehessen fel (`"wolt"`, `"foodora"`, `"bolt"`, `"egyeb"`). A `get_platform_display()` metódus automatikusan a felhasználóbarát nevet adja vissza (pl. `"wolt"` → `"Wolt"`).

#### Segédmetódusok

Az `Etterem` modell három fontos segédmetódust definiál:

**`get_platform_logo_url()`** — Visszaadja a platform logójának URL-jét. Ha a `platform_logo_url` mező ki van töltve, azt használja; egyébként egy beépített alapértelmezett URL-t ad vissza platformonként.

**`get_platform_url()`** — Hasonló elven működik: ha a `platform_url` mező ki van töltve, azt használja, egyébként a platform alapértelmezett weboldalát adja vissza.

**`get_city()`** — A `cim` (cím) mezőből kinyeri a várost. A logika figyelembe veszi, hogy a cím irányítószámmal kezdődhet-e: ha az első token numerikus irányítószám, a következő tokent használja városnévként. Fallbackként a „Budapest" szót keresi a szövegben. Ez a metódus kulcsfontosságú a keresőoldal városszűrő funkciójához — a frontend a `get_city()` visszatérési értékei alapján állítja össze a dinamikus városlistát.

### EtteremEtelInfo modell (compare alkalmazás)

Ez a modell az alkalmazás központi összekötő táblája: egy adott étel egy adott étteremben és platformon elérhető ajánlatát tárolja.

| Mező | Típus | Leírás |
|------|-------|--------|
| `etel` | `ForeignKey(Etel)` | Az étel, amelyre az ajánlat vonatkozik |
| `etterem` | `ForeignKey(Etterem)` | Az étterem, amely az ételt kínálja |
| `platform` | `CharField(choices)` | A platform (Wolt, Foodora stb.) |
| `ar` | `DecimalField` | Az étel bruttó ára forintban |
| `szallitas_ido` | `DurationField` | Becsült szállítási idő (pl. 30 perc) |
| `felhaszn_ertekelesek` | `DecimalField` | Felhasználói értékelések átlaga (1.00–5.00) |
| `promocio` | `CharField` | Akciós szöveg (opcionális) |

A `unique_together = ("etel", "etterem", "platform")` megkötés biztosítja, hogy ugyanaz az étel–étterem pár platformonként legfeljebb egyszer szerepeljen.

Az `indexes` lista három egyedi indexet definiál a leggyakrabban szűrt mezőkre, ami jelentősen gyorsítja a keresési és összehasonlítási lekérdezéseket.

### EtteremKoltseg modell (billing alkalmazás)

A rejtett költségek modellje háromféle szinthez csatolhat költségeket. A költségtípusok: `"szallitas"` (Szállítás), `"csomagolas"` (Csomagolás), `"borravalo"` (Borravaló) és `"egyeb"` (Egyéb).

A háromszintű csatolás logikája:

| Szint | Feltétel | Jelentés |
|-------|----------|---------|
| Étterem-szintű | `etterem` kitöltve | Egy konkrét étteremre vonatkozó költség |
| Platform-szintű | `etterem` üres, `platform` kitöltve | Egy teljes platform összes rendelésére vonatkozó költség |
| Étel-szintű | `etel` kitöltve | Egy konkrét ételhez rendelt költség |

A `__str__` metódus dinamikusan dönti el a megjelenítést: ha az `etel` mező ki van töltve, az étel nevét mutatja; ha az `etterem` mező van kitöltve, az étterem nevét; egyébként a platform megjelenített nevét használja.

### Mentes modell (compare alkalmazás)

A `Mentes` modell a felhasználók kedvenc ételeinek mentését kezeli. A `unique_together = ("felhasznalo", "etel")` megkötés biztosítja, hogy egy felhasználó egy ételt legfeljebb egyszer menthessen el. Az `ordering = ["-letrehozva"]` alapértelmezett rendezés a legfrissebb mentéseket helyezi előtérbe.

### Felhasznalo modell (users alkalmazás)

Az egyedi felhasználói modell a Django `AbstractUser` osztályból öröklődik, kibővítve két egyedi mezővel: `nev` (CharField, max. 150 karakter, opcionális) és `kedvenc_etterem` (ForeignKey az `Etterem` modellre, nullable). Az `AbstractUser` örökléssel a modell megkapja a Django teljes autentikációs rendszerét (username, password, email, is_staff, is_active, is_superuser stb.), és ezen felül a `nev` és `kedvenc_etterem` mezőkkel bővül. A `kedvenc_etterem` mező `on_delete=models.SET_NULL` beállítása biztosítja, hogy ha egy éttermet törölnek, a felhasználó rekordja ne vesszen el — a mező értéke egyszerűen `NULL`-ra áll.

---

## Nézetek és üzleti logika

A nézetek (views) a Django osztály-alapú nézeteire (Class-Based Views, CBV) épülnek. Az alkalmazás a Django beépített generikus nézeteit (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, `TemplateView`) használja, kiegészítve egyedi mixinekkel a jogosultságkezeléshez.

### SiteIndexView — Főoldal

A főoldal nézete a `foodcompare/views.py` fájlban található. Staff felhasználók számára az összes elérhető URL-útvonalat listázza, míg a nem-staff és vendég felhasználókat automatikusan a keresőoldalra irányítja.

A `get_resolver()` hívás a Django URL-resolver objektumát adja vissza, amelyen a `walk()` rekurzív függvény végigiterál. A parametrikus útvonalakat (amelyek `<` jelet tartalmaznak) és az admin útvonalakat kiszűri, csak a statikus, közvetlenül meglátogatható URL-eket listázva.

### EtelSearchView — Keresési logika

A keresőoldal nézete az alkalmazás legkomplexebb backend-logikáját tartalmazza. A `catalog/views.py` fájlban található `EtelSearchView` a `ListView`-ból öröklődik, és a `get_queryset()` metódusban építi fel a lekérdezést.

#### Az összesített ár számítása Subquery-vel

A keresőoldal minden ételnél megjeleníti a legkedvezőbb összesített árat (termékár + rejtett költségek). Ennek kiszámítása összetett ORM-lekérdezésekkel történik.

A két `Subquery` egymástól függetlenül számítja az étterem-szintű és a platform-szintű rejtett költségek összegét. A `Coalesce` függvény biztosítja, hogy ha nincs költség, az érték 0 legyen (és ne `NULL`).

A `Case`/`When` kifejezés a költség-prioritást valósítja meg: ha létezik platform-szintű költség (`_plat_sum > 0`), azt használja; egyébként az étterem-szintű költségre esik vissza. Az `order_by('total_price').values('total_price')[:1]` a legolcsóbb ajánlat összesített árát adja vissza — ez lesz a `min_total_price` annotáció.

#### Szöveges keresés Q-objektumokkal

A szöveges keresés a Django `Q` objektumaival történik, `icontains` lookup-pal (kis-nagybetű érzéketlen részstring-keresés). A három `Q` objektumot `|` (VAGY) operátorral kötjük össze, így a keresés az étel nevében, leírásában és kategóriájában egyaránt keres.

#### Városszűrés

A városszűrő a `get_city()` metódusra épülő dinamikus listát használ. A `distinct()` hívás megakadályozza a duplikátumok létrejöttét, amelyeket a kapcsolódó táblákon keresztüli szűrés okozhat.

#### Rendezési leképezések

Az öt rendezési mód egy Python szótárral van definiálva: `"alap"` (név), `"olcso"` (legolcsóbb összesített ár), `"draga"` (legdrágább), `"ertekeles"` (értékelés csökkenő) és `"nev"` (ábécérend). Minden rendezési mód másodlagos rendezési kulcsként a nevet használja, biztosítva a determinisztikus sorrendet azonos elsődleges értékek esetén.

#### Kontextus-kiegészítés

A `get_context_data()` metódus a sablon számára szükséges további adatokat adja át: a keresési paramétereket (`q`, `sort`, `city`), az elérhető városok dinamikus listáját és a bejelentkezett felhasználó mentett ételeinek ID-jait. A `saved_etel_ids` egy `set` típusú adat, amely lehetővé teszi a sablonban az O(1) időbonyolultságú tagság-ellenőrzést (`etel.id in saved_etel_ids`), így a „Mentés" / „Eltávolítás" gomb megjelenítése hatékony.

### OffersForEtelView — Termékoldal (ár-összehasonlítás)

A termékoldal az alkalmazás legfontosabb nézete: egy adott étel összes platformon és étteremben elérhető ajánlatát jeleníti meg, az összesített árat (termékár + rejtett költségek) kiszámítva. A `compare/views.py` fájlban található.

#### Az ajánlatok annotálása

Az összesített ár kiszámítása az ajánlatok szintjén történik, a keresőoldaléhoz hasonló `Subquery` logikával. A `select_related("etterem", "etel")` hívás egyetlen SQL JOIN-nal betölti a kapcsolódó `Etterem` és `Etel` objektumokat, elkerülve az N+1 lekérdezés problémát.

#### Dinamikus rendezés

A termékoldal táblázata oszlopfejlécre kattintva rendezhető. A `sort` és `dir` GET-paraméterek kombinációja négy rendezési irányt tesz lehetővé (ár növekvő/csökkenő, szállítási idő növekvő/csökkenő).

#### Rejtett költségek csoportosítása

A termékoldal megjeleníti az egyes ajánlatokhoz tartozó rejtett költségek részletezését is. A költségek két szótárba vannak csoportosítva: `koltsegek_by_etterem` (étterem-szintű) és `koltsegek_by_platform` (platform-szintű). A sablon a `dict_extras.dict_get` template filterrel fér hozzá ezekhez az adatokhoz.

### toggle_save — Mentés/eltávolítás

A mentés/eltávolítás funkció egy egyszerű function-based view, amelyet a `@login_required` dekorátor véd. A toggle logika egyszerű: ha a mentés már létezik, törli; ha nem létezik, létrehozza. A `next` paraméter lehetővé teszi, hogy a felhasználó visszakerüljön arra az oldalra, ahonnan a műveletet kezdeményezte.

### scraped_or_redirect — Scraped HTML kiszolgálása

Ez a nézet a termékoldal „Irány a bolt" gombjának hátterében működik.

A működés logikája:
1. Megkeresi az étterem platformjához tartozó statikus HTML fájlt a `data/` mappában (pl. `data/wolt.html`)
2. Ha létezik, a fájl tartalmát közvetlenül HTML válaszként szolgálja ki
3. Ha nem létezik, átirányít az étterem platform URL-jére

Ez a megoldás fejlesztési és bemutatási céllal is hasznos: internetkapcsolat nélkül a scraped HTML-ek szimulálják a platform weboldalát.

### CRUD nézetek

Az alkalmazás négy entitáshoz biztosít teljes CRUD (Create, Read, Update, Delete) funkcionalitást, egységes mintázattal.

Minden CRUD nézet ugyanazt a mintát követi:
- A **lista** nézet `StaffRequired` mixinnel van védve
- A **részletes** nézet mindenki számára elérhető
- A **létrehozás**, **szerkesztés** és **törlés** nézetek `LoginRequired` és `WritePermissionRequired` mixinekkel vannak védve
- A `success_url` mindig `reverse_lazy()`-vel van definiálva, ami a URL-t csak a kérés feldolgozásakor oldja fel (nem az importáláskor)

Ez a minta azonos elvek alapján működik az ételek, költségek, étterem–étel információk és felhasználók CRUD nézeteinél is.

---

## Jogosultsági rendszer és mixinek

A jogosultsági rendszer három egyedi mixinre épül, amelyek a `foodcompare/mixins.py` fájlban vannak definiálva.

### LoginRequired mixin

Ez a mixin a Django beépített `LoginRequiredMixin`-jéből öröklődik. Ha egy nem bejelentkezett felhasználó védett oldalt próbál elérni, a mixin közvetlenül az admin bejelentkezési oldalra (`/admin/login/`) irányítja. Ettől függetlenül a projekt globális frontend bejelentkezési útvonala külön is definiálva van (`/login/`). A `redirect_field_name = None` beállítás letiltja a `?next=` paramétert az átirányítási URL-ben.

### WritePermissionRequired mixin

Ez a mixin az írási műveleteket (Create, Update, Delete) védi: csak bejelentkezett staff felhasználók hajthatnak végre módosítást.

### StaffRequired mixin

A `StaffRequired` mixin különösen fontos: ha egy nem-staff felhasználó adminisztrációs felületet próbál elérni, nem hibaoldalt kap, hanem a keresőoldalra irányítódik — ez egy barátságos, felhasználó számára értelmezett átirányítás.

### Jogosultsági szintek összefoglalása

| Szint | Jogosultságok |
|-------|--------------|
| Vendég (nem bejelentkezett) | Keresőoldal és termékoldal megtekintése |
| Bejelentkezett, nem-staff | Fentiek + ételek mentése/eltávolítása, mentett ételek listája |
| Staff (adminisztrátor) | Teljes CRUD minden modulban, Django admin hozzáférés |

---

## URL-routing és névterek

Az alkalmazás URL-konfigurációja moduláris: minden alkalmazás saját `urls.py` fájllal rendelkezik, amelyeket a központi `foodcompare/urls.py` fog össze.

### Központi URL-konfiguráció

Az `include()` hívások prefix nélkül (`""`) illesztik be az alkalmazások URL-jeit, ezért az alkalmazásokon belüli útvonalak közvetlenül a gyökérről indulnak (pl. `/etterem/`, `/koltseg/`).

### Alkalmazás-névterek

Minden alkalmazás `app_name` attribútumot definiál, amely a Django névtereit (namespace) határozza meg: `catalog`, `billing`, `compare` és `users`. A névterek lehetővé teszik az egyértelmű URL-hivatkozást a sablonokban és nézetekben: `{% url 'catalog:kereses' %}`, `reverse("compare:offers_for_etel", etel_id=42)`.

### Teljes URL-térkép

| URL-minta | Nézet | Alkalmazás | Hozzáférés |
|-----------|-------|-----------|------------|
| `/` | `SiteIndexView` | foodcompare | Staff: site index; egyéb: redirect keresőre |
| `/login/` | `LoginView` | Django auth | Nyilvános |
| `/logout/` | `simple_logout` | foodcompare | Nyilvános |
| `/register/` | `RegisterView` | users | Nyilvános |
| `/kereses/` | `EtelSearchView` | catalog | Nyilvános |
| `/etterem/` | `EtteremListView` | catalog | Staff |
| `/etterem/<pk>/` | `EtteremDetailView` | catalog | Nyilvános |
| `/etterem/uj/` | `EtteremCreateView` | catalog | Staff |
| `/etterem/<pk>/szerkesztes/` | `EtteremUpdateView` | catalog | Staff |
| `/etterem/<pk>/torles/` | `EtteremDeleteView` | catalog | Staff |
| `/etel/` | `EtelListView` | catalog | Staff |
| `/etel/<pk>/` | `EtelDetailView` | catalog | Nyilvános |
| `/etel/uj/` | `EtelCreateView` | catalog | Staff |
| `/etel/<pk>/szerkesztes/` | `EtelUpdateView` | catalog | Staff |
| `/etel/<pk>/torles/` | `EtelDeleteView` | catalog | Staff |
| `/termek/<etel_id>/` | `OffersForEtelView` | compare | Nyilvános |
| `/termek/<etel_id>/mentes-toggle/` | `toggle_save` | compare | Bejelentkezés szükséges |
| `/mentett-etelek/` | `SavedFoodsView` | compare | Bejelentkezés szükséges |
| `/mentes/<pk>/torles/` | `MentesDeleteView` | compare | Bejelentkezés szükséges |
| `/info/` | `InfoListView` | compare | Staff |
| `/info/<pk>/` | `InfoDetailView` | compare | Nyilvános |
| `/info/uj/` | `InfoCreateView` | compare | Staff |
| `/info/<pk>/szerkesztes/` | `InfoUpdateView` | compare | Staff |
| `/info/<pk>/torles/` | `InfoDeleteView` | compare | Staff |
| `/koltseg/` | `KoltsegListView` | billing | Staff |
| `/koltseg/<pk>/` | `KoltsegDetailView` | billing | Nyilvános |
| `/koltseg/uj/` | `KoltsegCreateView` | billing | Staff |
| `/koltseg/<pk>/szerkeszt/` | `KoltsegUpdateView` | billing | Staff |
| `/koltseg/<pk>/torles/` | `KoltsegDeleteView` | billing | Staff |
| `/felhasznalo/` | `FelhasznaloListView` | users | Staff |
| `/felhasznalo/<pk>/` | `FelhasznaloDetailView` | users | Nyilvános |
| `/felhasznalo/uj/` | `FelhasznaloCreateView` | users | Staff |
| `/felhasznalo/<pk>/szerkesztes/` | `FelhasznaloUpdateView` | users | Staff |
| `/felhasznalo/<pk>/torles/` | `FelhasznaloDeleteView` | users | Staff |
| `/scraped/<etterem_id>/` | `scraped_or_redirect` | foodcompare | Nyilvános |
| `/admin/` | Django admin | Django | Superuser |

---

## Django Admin testreszabás

Minden modell regisztrálva van a Django admin felületen, egyedi konfigurációval.

### Etterem Admin

Az `EtteremAdmin` a `list_display`-ben a nevet, címet és platformot mutatja. A `search_fields` beállítás különösen fontos: ez teszi lehetővé az `autocomplete_fields` használatát más modellek admin felületén, amelyek `ForeignKey`-ként hivatkoznak az `Etterem`-re.

### Etel Admin

Az `EtelAdmin` egyedi `thumbnail()` metódust definiál, amely az étel képét kis bélyegképként jeleníti meg a lista nézetben. Az `allow_tags = True` beállítás engedélyezi a HTML-renderelést.

### EtteremEtelInfo Admin

Az `EtteremEtelInfoAdmin` az `autocomplete_fields = ("etel", "etterem")` beállítással a Django admin felületen AJAX-alapú keresőmezőt jelenít meg a `ForeignKey` mezőkhöz, ahelyett hogy az összes lehetőséget egy legördülő listában mutatná. Ez nagyméretű adatbázis esetén jelentősen javítja a teljesítményt és a felhasználói élményt. Az `autocomplete_fields` működéséhez az érintett modellek admin osztályaiban `search_fields` beállítás szükséges.

### Felhasznalo Admin

A `FelhasznaloAdmin` a felhasználók listáját mutatja (`username`, `nev`, `email`, `kedvenc_etterem`, `is_active`, `is_staff`), szűrhető az aktív, staff és superuser státusz alapján, és az `autocomplete_fields` segítségével az étterem-választás is keresőmezővel történik.

---

## Felhasználókezelés és űrlapok

### FelhasznaloCreationForm — Regisztrációs űrlap

A `UserCreationForm` az alap Django form, amely a `password1` és `password2` mezőket (jelszó és jelszó megerősítése) biztosítja, beépített jelszóvalidátorokkal (minimum hossz, komplexitás). A `kedvenc_etterem` mező opcionálissá tétele az `__init__` metódusban történik. Az űrlap mezői: `username`, `nev`, `email` és `kedvenc_etterem`.

### FelhasznaloUpdateForm — Felhasználó szerkesztési űrlap

A szerkesztési űrlap fontos jellemzője, hogy a jelszó mező opcionális (`required=False`). Ha a mező üres, a jelszó változatlan marad. Ha ki van töltve, a `set_password()` metódus a Django beépített jelszó-hash algoritmusával (alapértelmezetten PBKDF2) tárolja a jelszót. Az űrlap mezői: `username`, `nev`, `email`, `kedvenc_etterem`, `is_active` és `is_staff`.

### RegisterView — Publikus regisztrációs nézet

A `dispatch()` metódus felülírása biztosítja, hogy már bejelentkezett felhasználók ne érhessék el a regisztrációs oldalt — automatikusan a főoldalra irányítja őket. Sikeres regisztráció után a felhasználó a bejelentkezési oldalra kerül (`success_url = reverse_lazy("login")`).

### Bejelentkezés és kijelentkezés

A bejelentkezés a Django beépített `LoginView`-ját használja. A `redirect_authenticated_user=True` beállítás megakadályozza, hogy a már bejelentkezett felhasználók ismét elérjék a bejelentkezési oldalt.

A kijelentkezés egyedi nézet (`simple_logout`), amely GET-kéréssel is működik. A GET-támogatás azért fontos, mert a navigációs sáv linkjei GET-kéréseket küldenek.

---

## Adatimport pipeline

Az alkalmazás adatforrásai statikus HTML snapshot fájlok, amelyeket scraperek dolgoznak fel és egy Django management command importál az adatbázisba. A pipeline három fő szakaszból áll:

`data/*.html` → `scripts/scrape_*.py` → `data/*.extracted.json` → `manage.py import_scraped` → DB

### HTML snapshot fájlok

A `data/` könyvtárban két statikus HTML fájl található:
- `data/wolt.html` — A Wolt platform egyik étterem-oldalának mentett HTML-je
- `data/foodora.html` — A Foodora platform egyik étterem-oldalának mentett HTML-je

Ezek a fájlok az adatforrásul szolgáló „pillanatfelvételek", amelyekből a scraperek kinyerik a strukturált adatokat.

### extract_payload.py — HTML payload kinyerő

Az `scripts/extract_payload.py` fájl az újrafelhasználható kinyerő logikát tartalmazza. A BeautifulSoup4 könyvtárral parsolja a HTML-t, és háromféle stratégiával próbálja megtalálni a beágyazott JSON adatot:

1. Explicit JSON payload keresése: `<script id="scrape_payload" type="application/json">` tag
2. Fallback: `INLINE_WOLT_DATA` vagy hasonló JavaScript változó keresése regex segítségével
3. Heurisztikus: az első nagy (200+ karakter) JSON-szerű objektum keresése a script tag-ekben

A `js_object_to_json()` segédfüggvény a JavaScript objektum-szintaxist JSON-ra konvertálja (pl. egyszeres idézőjelek cseréje dupla idézőjelekre, nem idézett kulcsok idézése, záró vesszők eltávolítása).

### scrape_wolt.py — Wolt scraper

A scraper egyszerűen betölti a `data/wolt.html` fájlt, kinyeri a payload-ot az `extract_from_html()` függvénnyel, és a `data/wolt.html.extracted.json` fájlba írja.

### scrape_foodora.py — Foodora scraper

A Foodora scraper összetettebb: ha az extrakció sikertelen, fallback mechanizmusként friss payload-ot generál a `generate_foodora_payload.build_dataset()` segítségével. A `--regen` kapcsolóval expliciten kérhető a friss payload generálása.

### generate_foodora_payload.py — Payload generátor

A `build_dataset()` függvény programatikusan generál egy realisztikus Foodora-szerű adathalmazt: éttermeket, ételeket, rejtett költségeket és ajánlatokat. Az opcionális `seed` paraméter determinisztikus generálást tesz lehetővé, ami hasznos teszteléshez és CI-futtatásokhoz.

### run_pipeline.py — Pipeline orchestrátor

A teljes pipeline egyetlen Python szkripttel futtatható. A `subprocess.run()` segítségével szekvenciálisan futtatja a Wolt scrapert, a Foodora scrapert, majd az `import_scraped` management command-ot.

### import_scraped management command

A `catalog/management/commands/import_scraped.py` fájl a Django management command, amely a kinyert JSON fájlokat importálja az adatbázisba. A command négy lépésben dolgozik:

#### 1. Éttermek importálása

A deduplikáció kétlépcsős: először `platform_url` alapján keres egyezést, majd az étterem neve és platformja alapján. Ez megakadályozza a duplikátumok keletkezését ismételt importálás során.

#### 2. Ételek importálása (normalizált névvel)

A `normalize_name()` függvény a név normalizálását végzi: kisbetűsít, eltávolítja a felesleges szóközöket, és a Unicode ékezeteket leválasztja (NFKD normalizáció). Ez biztosítja, hogy a „Margherita Pizza" és a „margherita pizza" ugyanazt az ételt jelölje — platform-függetlenül.

#### 3. Rejtett költségek importálása

A `get_or_create()` hívás biztosítja, hogy ismételt importálás során ne keletkezzenek duplikált költségrekordok — ha már létezik az adott étterem–költségtípus pár, csak az összeg frissül.

#### 4. Ajánlatok importálása

A `parse_duration()` segédfüggvény a szöveges szállítási időt (pl. „25–35 perc") Django `DurationField`-kompatibilis `timedelta` objektummá konvertálja. A regex a szövegben található első számot kiragadja, majd az „óra", „nap" vagy alapértelmezetten „perc" egység alapján határozza meg az időtartamot.

Az ajánlatok importálása az `EtteremEtelInfo.unique_together` megkötés mentén történik a `get_or_create()` segítségével.

---

## Egyedi template tag-ek

A `compare/templatetags/dict_extras.py` fájl egyetlen egyedi template filtert definiál: `dict_get`. Ez a filter a sablonokban szükséges a Python szótárak dinamikus kulcsú lekérdezéséhez. A Django template nyelv nem támogatja a `dict[variable]` szintaxist, ezért a `{{ koltsegek_by_etterem|dict_get:offer.etterem_id }}` konstrukció szükséges a rejtett költségek termékoldalon történő megjelenítéséhez.

---

## Biztonsági megoldások

### CSRF-védelem

Minden POST-kérést tartalmazó űrlapban a `{% csrf_token %}` template tag generál egy egyedi tokent. A `CsrfViewMiddleware` middleware automatikusan ellenőrzi a token jelenlétét és érvényességét.

### Clickjacking-védelem

Az `XFrameOptionsMiddleware` az `X-Frame-Options` biztonsági fejlécet állítja be minden válaszon, megakadályozva vagy korlátozva az oldalak `<iframe>` elembe ágyazását (clickjacking elleni védelem).

### Jelszókezelés

A jelszavak hash formában kerülnek tárolásra az adatbázisban. A Django alapértelmezett jelszó-hash algoritmusa a PBKDF2 (Password-Based Key Derivation Function 2), amely a `AUTH_PASSWORD_VALIDATORS` beállítás szerint a következő validátorokat alkalmazza:

- `UserAttributeSimilarityValidator` — a jelszó nem hasonlíthat a felhasználónévre
- `MinimumLengthValidator` — minimum jelszóhossz
- `CommonPasswordValidator` — gyakori jelszavak tiltása
- `NumericPasswordValidator` — kizárólag numerikus jelszavak tiltása

### Session-kezelés

A Django beépített session-kezelése cookie-alapú, a `SessionMiddleware` biztosítja. A munkamenet-adatokat az adatbázis tárolja (`django_session` tábla), a kliens oldalon csak egy session ID cookie (`sessionid`) létezik.

---

## Migrációk

A Django migrációs rendszere az adatbázis-séma verziókezelését biztosítja. Minden alkalmazás `migrations/` könyvtárában megtalálhatók a migrációs fájlok, amelyek az adatmodellek változásait írják le deklaratív módon.

### Migrációs fájlok áttekintése

| Alkalmazás | Migráció | Leírás |
|------------|---------|--------|
| `users` | `0001_initial` | `Felhasznalo` modell létrehozása |
| `catalog` | `0001_initial` | `Etel` és `Etterem` modellek létrehozása |
| `catalog` | `0002_alter_*` | Meta opciók módosítása |
| `catalog` | `0003_alter_*` | Platform és URL mezők hozzáadása |
| `billing` | `0001_initial` | `EtteremKoltseg` modell létrehozása |
| `billing` | `0002_alter_*` | Opciók módosítása |
| `billing` | `0003_add_platform` | Platform mező hozzáadása |
| `billing` | `0004_add_etel` | Étel mező hozzáadása |
| `compare` | `0001_initial` | Alapmodell(ek) létrehozása |
| `compare` | `0002_initial` | `EtteremEtelInfo` és `Mentes` modellek |
| `compare` | `0003_add_platform` | Platform mező hozzáadása |
| `compare` | `0004_rename_*` | Index-átnevezés |

### Migrációk futtatása

A migrációk ellenőrzése a `python manage.py makemigrations --dry-run --verbosity 3` paranccsal, alkalmazása a `python manage.py migrate` paranccsal történik.

---

## Fejlesztői munkafolyamatok

### Teljes fejlesztői ciklus

1. Virtuális környezet létrehozása és aktiválása (`python -m venv .venv`, `.\.venv\Scripts\Activate.ps1`)
2. Függőségek telepítése (`pip install -r requirements.txt`)
3. Adatbázis migrációk (`python manage.py migrate`)
4. Scraperek futtatása (`python scripts/scrape_wolt.py`, `python scripts/scrape_foodora.py`)
5. Adatok importálása (`python manage.py import_scraped`)
6. Szerver indítása (`python manage.py runserver`)

### Gyorsbillentyűk

- Teljes reset és újraindítás: `.\run_dev.ps1 -ResetDB -Regen -RunServer`
- Csak scraperek és import: `.\run_scrape_and_import.ps1`
- Python-alapú pipeline (PowerShell nélkül): `python scripts/run_pipeline.py`

### Modellváltozás utáni teendők

1. Modell módosítása a megfelelő `models.py` fájlban
2. Migrációk generálása: `python manage.py makemigrations`
3. Migrációk ellenőrzése: `python manage.py makemigrations --dry-run --verbosity 3`
4. Migrációk alkalmazása: `python manage.py migrate`
5. Rendszerellenőrzés: `python manage.py check`

---

## Összefoglalás

A FoodCompare backend a Django keretrendszer lehetőségeit kihasználva egy moduláris, biztonságos és jól karbantartható szerveroldali architektúrát valósít meg. A négy alkalmazás (`catalog`, `billing`, `compare`, `users`) világos felelősségi körökkel rendelkezik, és az iparágban megszokott tervezési mintákat követi (Class-Based Views, mixin-alapú jogosultságkezelés, namespace-alapú URL-routing). Az adatimport pipeline automatizálja a külső platform-adatok kinyerését és adatbázisba töltését, míg a Django ORM komplex annotációi és subquery-jei lehetővé teszik az összesített árak hatékony, adatbázis-szintű kiszámítását. A jogosultsági rendszer három szintje (vendég, felhasználó, staff) biztosítja a hozzáférés-vezérlést, a Django beépített biztonsági mechanizmusai (CSRF, jelszó-hashing, clickjacking-védelem) pedig az alkalmazás biztonságát szavatolják.
