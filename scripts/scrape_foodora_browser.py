#!/usr/bin/env python3
"""
scrape_foodora_browser.py

Headless-browser scraper for `data/foodora.html` that executes the page JS and
extracts the generated DATA object (restaurants, foods, offers). This is the
"screen-scraper" variant which reads what's actually rendered by the page.

Requires: playwright (pip install playwright) and `playwright install` once.

Usage:
  python scripts/scrape_foodora_browser.py [--file|-f path/to/data/foodora.html]

If playwright is not available, the script falls back to `scrape_foodora.py`.
"""
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'foodora.html'
OUTPUT = ROOT / 'data' / 'foodora.html.extracted.json'


def fallback_run():
    # fallback to existing script
    print('playwright not available, falling back to scrape_foodora.py')
    import subprocess
    subprocess.check_call([sys.executable, str(ROOT / 'scripts' / 'scrape_foodora.py')])


def main():
    # optional input override
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-f', '--file') and len(sys.argv) > 2:
            global INPUT
            INPUT = Path(sys.argv[2])

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        fallback_run()
        return

    url = INPUT.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # wait until the page has created DATA (the page's JS sets DATA = buildDataset())
        try:
            page.wait_for_function('window.DATA !== undefined && window.DATA.offers && window.DATA.offers.length > 0', timeout=3000)
        except Exception:
            # give it one more second
            try:
                page.wait_for_function('window.DATA !== undefined', timeout=2000)
            except Exception:
                print('Timed out waiting for DATA on the page; falling back to static extractor')
                browser.close()
                fallback_run()
                return

        # build payload inside the page to ensure we use the exact runtime objects
        payload = page.evaluate('''() => {
            const data = window.DATA || {};
            const restaurants = data.restaurants || [];
            const foods = data.foods || [];
            const offers = data.offers || [];

            // construct etterem_koltseg from offers' embedded costs if present
            const costsByRestaurant = {};
            offers.forEach(o => {
                if (o._costs) costsByRestaurant[o._restaurant.id] = o._costs;
            });
            let k_id = 1;
            const koltseg = [];
            Object.keys(costsByRestaurant).forEach(rid => {
                const c = costsByRestaurant[rid];
                koltseg.push({ id: k_id++, etterem_id: Number(rid), koltseg_tipus: 'szallitas', osszeg: c.szallitas });
                koltseg.push({ id: k_id++, etterem_id: Number(rid), koltseg_tipus: 'csomagolas', osszeg: c.csomagolas });
                koltseg.push({ id: k_id++, etterem_id: Number(rid), koltseg_tipus: 'borravalo', osszeg: c.borravalo });
            });

            const info = offers.map(o => ({
                id: o.id,
                etel_id: o.etel_id || (o._food && o._food.id),
                etterem_id: o.etterem_id || (o._restaurant && o._restaurant.id),
                platform: (o.platform || (o._restaurant && o._restaurant.platform) || 'foodora').toLowerCase(),
                ar: o.ar,
                szallitas_ido: o.szallitas_ido,
                felhaszn_ertekeles: o.ertekeles || o.ertekeles,
                promocio: o.promo || o.promocio || 0
            }));

            return { etterem: restaurants, etterem_koltseg: koltseg, etel: foods, etterem_etel_info: info };
        }''')

        browser.close()

    # write output
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Foodora (browser): extracted keys: {list(payload.keys())} -> {OUTPUT}')


if __name__ == '__main__':
    main()
