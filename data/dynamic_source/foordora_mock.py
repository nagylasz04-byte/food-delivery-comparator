from flask import Flask, jsonify
import random

app = Flask(__name__)

# Minták az ételekre és éttermekre
foods = ["Margherita pizza", "Whopper Menü", "Gyros tál", "Cézár saláta", "Sushi menü"]
restaurants = ["Pizza Forte", "Burger King", "Gyros City", "Saláta Bár", "Sushi World"]

@app.route('/api/foodora/prices', methods=['GET'])
def get_foodora_prices():
    data = []
    for _ in range(5):  # 5 étel random generálása
        food = random.choice(foods)
        restaurant = random.choice(restaurants)
        price = random.randint(2500, 4500)           # alapár 2500-4500 Ft
        delivery_fee = random.choice([390, 490, 590]) # szállítási díj
        packaging_fee = random.choice([0, 150, 200])  # csomagolási díj

        data.append({
            "platform": "Foodora",
            "restaurant": restaurant,
            "food_name": food,
            "price": price,
            "delivery_fee": delivery_fee,
            "packaging_fee": packaging_fee,
            "total_cost": price + delivery_fee + packaging_fee
        })
    return jsonify(data)

if __name__ == "__main__":
    print(f"Flask Mock Server elindult a http://127.0.0.1:5005/api/foodora/prices címen.")
    app.run(port=5002, debug=True)

