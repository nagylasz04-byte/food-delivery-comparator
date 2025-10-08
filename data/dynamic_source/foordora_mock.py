from flask import Flask, jsonify
import random

app = Flask(__name__)

# 🏪 Webshop adatok (ID, Név, Cím)
webshops = [
    {"id": 1, "name": "Pizza Forte", "address": "Budapest, Andrássy út 12."},
    {"id": 2, "name": "Burger King", "address": "Debrecen, Piac utca 45."},
    {"id": 3, "name": "Gyros City", "address": "Szeged, Kossuth tér 3."},
    {"id": 4, "name": "Saláta Bár", "address": "Pécs, Irgalmasok utcája 8."},
    {"id": 5, "name": "Sushi World", "address": "Győr, Baross út 22."}
]

# 🍽️ Étel adatok (ID, Név, Leírás, Kategória, Allergén, Kép URL)
foods = [
    {
        "id": 101,
        "name": "Margherita pizza",
        "description": "Paradicsomos alap, mozzarella, bazsalikom",
        "category": "pizza",
        "allergens": ["glutén", "laktóz"],
        "image_url": "https://example.com/margherita.jpg"
    },
    {
        "id": 102,
        "name": "Whopper Menü",
        "description": "Marhahúsos burger, sült krumpli, üdítő",
        "category": "burger",
        "allergens": ["glutén", "laktóz", "tojás"],
        "image_url": "https://example.com/whopper.jpg"
    },
    {
        "id": 103,
        "name": "Gyros tál",
        "description": "Csirkehús, pita, tzatziki, saláta",
        "category": "gyros",
        "allergens": ["glutén", "tej"],
        "image_url": "https://example.com/gyros.jpg"
    },
    {
        "id": 104,
        "name": "Cézár saláta",
        "description": "Római saláta, csirkemell, parmezán, kruton",
        "category": "saláta",
        "allergens": ["glutén", "hal"],
        "image_url": "https://example.com/cezar.jpg"
    },
    {
        "id": 105,
        "name": "Sushi menü",
        "description": "Maki, nigiri, wasabi, szójaszósz",
        "category": "sushi",
        "allergens": ["hal", "szója"],
        "image_url": "https://example.com/sushi.jpg"
    }
]

# 💸 Rejtett költségek (szállítás, csomagolás, borravaló)
cost_types = ["szállítás", "csomagolás", "borravaló"]
cost_amounts = [390, 490, 590, 0, 150, 200, 300]

# 📦 Webshop-étel kapcsolat (Ár, Szállítási idő, Értékelés, Promóció)
delivery_times = ["30 perc", "1 óra", "2 nap"]
ratings = [4.2, 4.5, 4.8, 5.0]
promotions = ["-10%", "Ingyenes szállítás", "Ajándék üdítő", ""]

@app.route('/api/foodora/prices', methods=['GET'])
def get_foodora_prices():
    data = []

    for _ in range(5):  # 5 véletlenszerű étel-webshop páros
        food = random.choice(foods)
        webshop = random.choice(webshops)

        # Webshop-étel info
        price = random.randint(2500, 4500)
        delivery_time = random.choice(delivery_times)
        rating = random.choice(ratings)
        promo = random.choice(promotions)

        # Rejtett költségek
        hidden_costs = []
        total_hidden = 0
        for cost_type in cost_types:
            amount = random.choice(cost_amounts)
            hidden_costs.append({
                "type": cost_type,
                "amount": amount
            })
            total_hidden += amount

        total_cost = price + total_hidden

        data.append({
            "platform": "Foodora",
            "webshop": {
                "id": webshop["id"],
                "name": webshop["name"],
                "address": webshop["address"]
            },
            "food": {
                "id": food["id"],
                "name": food["name"],
                "description": food["description"],
                "category": food["category"],
                "allergens": food["allergens"],
                "image_url": food["image_url"]
            },
            "webshop_food_info": {
                "price": price,
                "delivery_time": delivery_time,
                "rating": rating,
                "promotion": promo
            },
            "hidden_costs": hidden_costs,
            "total_cost": total_cost
        })

    return jsonify(data)

if __name__ == "__main__":
    print("Flask Mock Server elindult a http://127.0.0.1:5002/api/foodora/prices címen.")
    app.run(port=5002, debug=True)
