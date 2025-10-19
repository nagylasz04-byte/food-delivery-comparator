#!/usr/bin/env python3
"""
scrape_wolt.py

Simple wrapper that extracts payload from data/wolt.html and writes data/wolt.extracted.json
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'wolt.html'
OUTPUT = ROOT / 'data' / 'wolt.html.extracted.json'

# Import the extractor module
sys.path.insert(0, str(ROOT / 'scripts'))
from extract_payload import extract_from_html

html = INPUT.read_text(encoding='utf-8')
payload = extract_from_html(html)
OUTPUT.write_text(__import__('json').dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wolt: extracted keys: {list(payload.keys())} -> {OUTPUT}')
