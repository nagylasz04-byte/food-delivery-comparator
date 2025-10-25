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
import argparse
import traceback

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'foodora.html'
OUTPUT = ROOT / 'data' / 'foodora.html.extracted.json'


def fallback_run():
    # fallback to existing script
    print('playwright not available, falling back to scrape_foodora.py')
    import subprocess
    subprocess.check_call([sys.executable, str(ROOT / 'scripts' / 'scrape_foodora.py')])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='path to input HTML file', default=str(INPUT))
    parser.add_argument('--headful', help='launch browser with GUI (headful) for debugging', action='store_true')
    parser.add_argument('--screenshot', help='save a screenshot and debug HTML to the data/ folder', action='store_true')
    args = parser.parse_args()
    # don't shadow the module-level INPUT constant (causes UnboundLocalError)
    input_path = Path(args.file)

    def try_import_playwright():
        try:
            from playwright.sync_api import sync_playwright
            return sync_playwright
        except Exception as e:
            print('Playwright import error:')
            traceback.print_exc()
            return None

    def auto_install_playwright():
        """Try to install playwright and browser binaries into the active env.
        This is a convenience: it runs `pip install playwright` and
        `python -m playwright install`. It may fail if there's no network or
        permissions; in that case we fall back to the static extractor.
        """
        import subprocess
        print('Playwright not found — attempting to install it into the active venv...')
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'playwright'])
        except Exception as e:
            print('Failed to pip-install playwright:', e)
            return False
        try:
            subprocess.check_call([sys.executable, '-m', 'playwright', 'install'])
        except Exception as e:
            print('Failed to install Playwright browser binaries:', e)
            return False
        return True

    sync_playwright = try_import_playwright()
    if sync_playwright is None:
        ok = auto_install_playwright()
        if not ok:
            print('playwright install not possible in this environment — falling back')
            fallback_run()
            return
        # try import again
        sync_playwright = try_import_playwright()
        if sync_playwright is None:
            print('Import failed even after installation — falling back')
            fallback_run()
            return

    url = input_path.resolve().as_uri()
    with sync_playwright() as p:
        # allow optional debug mode via CLI flag
        browser = p.chromium.launch(headless=(not args.headful))
        page = browser.new_page()
        # navigate and wait for network to be mostly idle — gives SPA scripts time to run
        page.goto(url, wait_until='networkidle')

        # wait until the page has created table rows (the demo populates #offers tbody)
        try:
            # wait for at least one row in the offers table; more robust than window.DATA which
            # may be declared with `let DATA = ...` (not a property of window)
            page.wait_for_selector('#offers tbody tr', timeout=15000)
        except Exception:
            # give it a little more time for very slow environments
            try:
                page.wait_for_selector('#offers tbody tr', timeout=5000)
            except Exception:
                print('Timed out waiting for offers table rows on the page; falling back to static extractor')
                try:
                    browser.close()
                except Exception:
                    pass
                fallback_run()
                return

        # optionally save a screenshot + HTML for debugging
        if args.screenshot:
            try:
                ss_path = ROOT / 'data' / 'foodora.debug.png'
                html_path = ROOT / 'data' / 'foodora.debug.html'
                page.screenshot(path=str(ss_path), full_page=True)
                html = page.content()
                html_path.write_text(html, encoding='utf-8')
                print(f'Debug: screenshot -> {ss_path}, html -> {html_path}')
            except Exception:
                print('Failed to write debug screenshot/html')

        # build payload inside the page to ensure we use the exact runtime objects (try several strategies)
        payload = page.evaluate('''() => {
            // find the in-memory dataset using multiple strategies
            let D = null;
            try { if (typeof DATA !== 'undefined') D = DATA; } catch(e) {}
            try { if (!D && (window.DATA || globalThis.DATA)) D = window.DATA || globalThis.DATA; } catch(e) {}
            try { if (!D && typeof buildDataset === 'function') D = buildDataset(); } catch(e) {}

            // if we have a dataset object, derive koltseg and info
            if (D && D.offers) {
                const restaurants = D.restaurants || [];
                const foods = D.foods || [];
                const offers = D.offers || [];

                // construct etterem_koltseg from offers' embedded costs if present
                const costsByRestaurant = {};
                offers.forEach(o => { if (o._costs) costsByRestaurant[o._restaurant.id] = o._costs; });
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
            }

            // final fallback: reconstruct minimal info from the DOM table rows
            const rows = Array.from(document.querySelectorAll('#offers tbody tr'));
            const offers = rows.map(tr => {
                const cells = Array.from(tr.children);
                const foodName = cells[0].querySelector('div') ? cells[0].querySelector('div').textContent.trim() : '';
                const restaurantName = cells[2].querySelector('b') ? cells[2].querySelector('b').textContent.trim() : '';
                const arText = cells[3] ? cells[3].textContent.trim() : '';
                const totalText = cells[8] ? cells[8].textContent.trim() : '';
                return { foodName, restaurantName, arText, totalText };
            });
            return { etterem: [], etterem_koltseg: [], etel: [], etterem_etel_info: offers };
        }''')

        try:
            browser.close()
        except Exception:
            pass

    # write output
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Foodora (browser): extracted keys: {list(payload.keys())} -> {OUTPUT}')


if __name__ == '__main__':
    main()
