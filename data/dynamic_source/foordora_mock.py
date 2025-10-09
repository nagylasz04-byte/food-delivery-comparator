from flask import Flask, jsonify, request
import random
import time

app = Flask(__name__)

# Konstans minták (magyar nevek és címötletek)
SAMPLE_WEBSHOP_NEVEK = [
    "Pizza Forte", "Burger King", "Gyros City", "Saláta Bár", "Sushi World", "Tésztamánia"
]
SAMPLE_UTCAK = [
    "Andrássy út", "Kossuth Lajos utca", "Baross utca", "Piac utca", "Rákóczi út", "Fő utca"
]

SAMPLE_FOOD = [
    ("Margherita pizza", "Paradicsomos alap, mozzarella, bazsalikom", "pizza"),
    ("Pepperoni pizza", "Parmezán, pepperoni, paradicsom", "pizza"),
    ("Whopper Menü", "Marhahúsos burger, sült krumpli, üdítő", "burger"),
    ("Gyros tál", "Csirkehús, pita, tzatziki, saláta", "gyros"),
    ("Cézár saláta", "Római saláta, csirkemell, parmezán", "saláta"),
    ("Sushi menü", "Maki, nigiri, wasabi", "sushi")
]

COST_TYPES = ["szállítás", "csomagolás", "borravaló"]
DELIVERY_TIMES = ["30 perc", "45 perc", "1 óra", "2 óra"]
PROMOTIONS = ["", "-10%", "Ingyenes szállítás", "Ajándék üdítő"]


def seeded_random(seed_value=None):
    """Return a random.Random instance seeded either with given seed_value or current time."""
    if seed_value is None:
        return random.Random()
    try:
        s = int(seed_value)
    except Exception:
        s = hash(seed_value) & 0xFFFFFFFF
    return random.Random(s)


@app.route('/api/foodora/prices', methods=['GET'])
def get_foodora_prices():
    # Optionalis seed query param: ?seed=1234 => reprodukálható adatok
    seed = request.args.get('seed')
    rnd = seeded_random(seed)

    # Webshopok száma: 2..5
    num_webshops = rnd.randint(2, min(6, len(SAMPLE_WEBSHOP_NEVEK)))
    WEBSHOP = []
    for i in range(num_webshops):
        name = SAMPLE_WEBSHOP_NEVEK[i % len(SAMPLE_WEBSHOP_NEVEK)]
        addr = f"{rnd.randint(1,200)} {rnd.choice(SAMPLE_UTCAK)}, {rnd.choice(['Budapest','Debrecen','Szeged','Pécs','Győr'])}"
        WEBSHOP.append({"ID": i + 1, "Név": name, "Cím": addr})

    # Ételek: 4..8
    num_foods = rnd.randint(4, min(8, len(SAMPLE_FOOD)))
    ÉTEL = []
    next_food_id = 101
    for i in range(num_foods):
        fname, descr, cat = SAMPLE_FOOD[i % len(SAMPLE_FOOD)]
        image = f"https://example.com/{fname.replace(' ','_').lower()}.jpg"
        ÉTEL.append({"ID": next_food_id, "Név": fname, "Leírás": descr, "Kategória": cat, "Kép_url": image})
        next_food_id += 1

    # WEBSHOP_KÖLTSÉG: minden webshophoz 0..3 költség
    WEBSHOP_KÖLTSÉG = []
    next_cost_id = 1
    for ws in WEBSHOP:
        for ct in COST_TYPES:
            # lokális döntés: legyen-e költség (70% eséllyel)
            if rnd.random() < 0.7:
                amount = rnd.choice([0, 150, 250, 350, 390, 490, 590])
                WEBSHOP_KÖLTSÉG.append({"ID": next_cost_id, "WEBSHOP_ID": ws['ID'], "Költség_típus": ct, "Összeg": amount})
                next_cost_id += 1

    # WEBSHOP_ÉTEL_INFO: minden webshophoz 1..min(4,num_foods) étel
    WEBSHOP_ÉTEL_INFO = []
    next_wi_id = 1
    food_ids = [f['ID'] for f in ÉTEL]
    for ws in WEBSHOP:
        take = rnd.randint(1, min(4, len(food_ids)))
        chosen = rnd.sample(food_ids, k=take)
        for fid in chosen:
            price = rnd.randint(800, 4990)
            delivery = rnd.choice(DELIVERY_TIMES)
            rating = round(rnd.uniform(3.5, 5.0), 1)
            promo = rnd.choice(PROMOTIONS)
            WEBSHOP_ÉTEL_INFO.append({
                "ID": next_wi_id,
                "ÉTEL_ID": fid,
                "WEBSHOP_ID": ws['ID'],
                "Ár": price,
                "Szállítási_idő": delivery,
                "Felhaszn_értékelések": rating,
                "Promóció": promo
            })
            next_wi_id += 1

    result = {
        "WEBSHOP": WEBSHOP,
        "WEBSHOP_KÖLTSÉG": WEBSHOP_KÖLTSÉG,
        "ÉTEL": ÉTEL,
        "WEBSHOP_ÉTEL_INFO": WEBSHOP_ÉTEL_INFO
    }
    return jsonify(result)


if __name__ == '__main__':
    print('Foodora mock szerver elindult: http://127.0.0.1:5002/api/foodora/prices')
    app.run(port=5002, debug=True)
