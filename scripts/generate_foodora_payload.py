#!/usr/bin/env python3
"""Generate a random Foodora-like payload (same structure as the in-page JSON in data/foodora.html).

This mirrors the JS generator embedded in the fixture so the scraper can produce fresh data each run.
"""
from __future__ import annotations
import random
from typing import Dict, List


def rnd(min_v: int, max_v: int) -> int:
    return random.randint(min_v, max_v)


def rnd_float(min_v: float, max_v: float, d: int = 1) -> float:
    return round(random.uniform(min_v, max_v), d)


def gen_costs_for_restaurant(etterem_id: int) -> Dict:
    return {
        "etterem_id": etterem_id,
        "szallitas": rnd(490, 1490),
        "csomagolas": rnd(0, 390),
        "borravalo": rnd(0, 590),
    }


def gen_offer_for(food: Dict, restaurant: Dict, costs: Dict) -> Dict:
    ar = rnd(1490, 5890)
    szall_ido = ["25–35 perc", "30–45 perc", "40–55 perc"][random.randrange(0, 3)]
    ertekeles = rnd_float(3.8, 4.9, 1)
    promo = random.choice([0, 0, 0, 300, 500])
    vegosszeg = ar + costs["szallitas"] + costs["csomagolas"] + costs["borravalo"] - promo
    return {
        "id": f"{restaurant['id']}-{food['id']}",
        "etel_id": food["id"],
        "etterem_id": restaurant["id"],
        "platform": restaurant.get("platform", "foodora").lower(),
        "ar": ar,
        "szallitas_ido": szall_ido,
        "felhaszn_ertekeles": ertekeles,
        "promocio": promo,
    }


def build_dataset(seed: int | None = None) -> Dict:
    """Return a payload dict similar to the in-page JSON."""
    if seed is not None:
        random.seed(seed)

    RESTAURANTS = [
        {"id": 1, "nev": "Pizza Bella", "cim": "Budapest, VI. kerület, Andrássy út 12.", "platform": "foodora", "platform_url": "https://foodora.example/restaurant/1"},
        {"id": 2, "nev": "Burger Mester", "cim": "Budapest, VII. kerület, Rákóczi út 33.", "platform": "foodora", "platform_url": "https://foodora.example/restaurant/2"},
        {"id": 3, "nev": "Sushi Go", "cim": "Budapest, XIII. kerület, Váci út 8.", "platform": "foodora", "platform_url": "https://foodora.example/restaurant/3"},
    ]

    FOODS = [
        {"id": 1, "nev": "Margherita pizza", "leiras": "Paradicsom, mozzarella, bazsalikom", "kategoria": "pizza", "kep_url": "https://picsum.photos/seed/pizza/400"},
        {"id": 2, "nev": "Dupla sajtburger", "leiras": "Marhahús, sajt, savanyú uborka", "kategoria": "burger", "kep_url": "https://picsum.photos/seed/burger/400"},
        {"id": 3, "nev": "Csirke ramen", "leiras": "Csirke, tészta, tojás", "kategoria": "leves", "kep_url": "https://picsum.photos/seed/ramen/400"},
        {"id": 4, "nev": "Tonhal maki", "leiras": "Tonhal, rizs, nori", "kategoria": "sushi", "kep_url": "https://picsum.photos/seed/sushi/400"},
        {"id": 5, "nev": "Vega bowl", "leiras": "Quinoa, zöldségek, tahini", "kategoria": "vega", "kep_url": "https://picsum.photos/seed/bowl/400"},
    ]

    # costs map by restaurant id
    costs_map = {r["id"]: gen_costs_for_restaurant(r["id"]) for r in RESTAURANTS}

    # chosen pairs as in the JS fixture
    chosen_pairs = [(1, 1), (2, 2), (3, 3), (1, 4), (2, 5)]

    offers = [
        gen_offer_for(
            next(f for f in FOODS if f["id"] == fid),
            next(r for r in RESTAURANTS if r["id"] == rid),
            costs_map[rid],
        )
        for (rid, fid) in chosen_pairs
    ]

    # Build etterem_koltseg list (id increments)
    koltseg_list: List[Dict] = []
    k_id = 1
    for r in RESTAURANTS:
        c = costs_map[r["id"]]
        koltseg_list.append({"id": k_id, "etterem_id": r["id"], "koltseg_tipus": "szallitas", "osszeg": c["szallitas"]}); k_id += 1
        koltseg_list.append({"id": k_id, "etterem_id": r["id"], "koltseg_tipus": "csomagolas", "osszeg": c["csomagolas"]}); k_id += 1
        koltseg_list.append({"id": k_id, "etterem_id": r["id"], "koltseg_tipus": "borravalo", "osszeg": c["borravalo"]}); k_id += 1

    payload = {
        "etterem": RESTAURANTS,
        "etterem_koltseg": koltseg_list,
        "etel": FOODS,
        "etterem_etel_info": offers,
    }

    return payload


if __name__ == '__main__':
    import json
    import sys
    seed = None
    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except Exception:
            seed = None
    payload = build_dataset(seed)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
