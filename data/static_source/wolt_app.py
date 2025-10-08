# wolt_app.py
# Ez a fájl egy "mock" szerverként szolgál, ami statikus adatokat szolgáltat,
# szimulálva egy valós külső API (pl. Wolt) viselkedését.

import json
from pathlib import Path
from flask import Flask, jsonify, request

# 1. Flask alkalmazás inicializálása
app = Flask(__name__)

# 2. A statikus adatok betöltése a JSON fájlból
# A DATA_FILE elérési útja most a szkript könyvtárához képest van feloldva,
# így független lesz attól, honnan indítod a Python folyamatot.
DATA_FILE = Path(__file__).parent / 'wolt_data.json'

try:
    # A try blokk megpróbálja beolvasni a fájlt, hogy elkerülje az alkalmazás összeomlását, ha a fájl hiányzik vagy hibás.
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        # Megnyitja a JSON fájlt olvasásra (r) UTF-8 kódolással.
        WOLT_MOCK_DATA = json.load(f)
        # Beolvassa a JSON fájl teljes tartalmát, és Python szótárként eltárolja a WOLT_MOCK_DATA változóban.
except FileNotFoundError:
    # Akkor fut le, ha a DATA_FILE nem található a megadott helyen.
    # Hibaüzenet, ha a JSON fájl nem található. Megadjuk a teljes elérési utat is, hogy könnyebb legyen debugolni.
    WOLT_MOCK_DATA = {"error": f"A(z) {DATA_FILE.name} fájl nem található ({str(DATA_FILE)}). Győződj meg róla, hogy a megfelelő helyen van."}
    # Hibaüzenettel tölti fel a WOLT_MOCK_DATA-t, hogy a szerver ezt adja vissza.
except json.JSONDecodeError as e:
    # Akkor fut le, ha a fájl megtalálható, de a tartalma nem érvényes JSON.
    # Hibaüzenet, ha a JSON fájl hibás — a kivétel üzenetét is csatoljuk a könnyebb diagnosztikához.
    WOLT_MOCK_DATA = {"error": f"Hiba a(z) {DATA_FILE.name} JSON formátumában: {e}"}
    # Hibaüzenettel tölti fel a WOLT_MOCK_DATA-t.

# 3. API Végpont definiálása
# Ez a végpont adja vissza a teljes statikus adatot
@app.route('/api/wolt/prices', methods=['GET'])
def get_wolt_prices():
    """
    Visszaadja a statikus wolt_data.json tartalmát. 
    A Scraper (scrape_runner.py) ezt a végpontot hívja meg.
    """
    if "error" in WOLT_MOCK_DATA:
        # Ellenőrzi, hogy a WOLT_MOCK_DATA tartalmaz-e hibát (a beolvasási szakaszból).
        # Hiba esetén 500-as státuszkóddal tér vissza
        return jsonify(WOLT_MOCK_DATA), 500

    # Sikeres válasz 200-as státuszkóval
    return jsonify(WOLT_MOCK_DATA), 200


# 4. Szerver indítása
if __name__ == '__main__':
    # Ez a Python standard szerkezet biztosítja, hogy a kód csak akkor fusson le, ha a fájlt közvetlenül indítjuk.
    # A debug=True beállítással automatikusan újraindul, ha változtatunk a kódon.
    print(f"Flask Mock Server elindult a http://127.0.0.1:5000/api/wolt/prices címen.")
    # Konzolra írja a szerver elérésének URL-jét.
    app.run(port=5000, debug=True)
    # Elindítja a Flask szervert alapértelmezett 5000-es porton, engedélyezve a debug módot.
