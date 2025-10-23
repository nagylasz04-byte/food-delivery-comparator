#!/usr/bin/env python3
"""
scrape_foodora.py

Simple wrapper that extracts payload from data/foodora.html and writes data/foodora.html.extracted.json
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'foodora.html'
OUTPUT = ROOT / 'data' / 'foodora.html.extracted.json'

# Import the extractor module
sys.path.insert(0, str(ROOT / 'scripts'))
from extract_payload import extract_from_html

html = INPUT.read_text(encoding='utf-8')
payload = None
try:
	payload = extract_from_html(html)
except Exception:
	# if extraction fails, we'll generate a fresh payload
	payload = None

# allow explicit regeneration
import sys
regen = '--regen' in sys.argv
if payload is None or regen:
	# generate a random payload server-side (mirror of the page JS)
	try:
		from generate_foodora_payload import build_dataset
		payload = build_dataset()
		print('Foodora: generated fresh payload via generate_foodora_payload')
	except Exception as e:
		print('Foodora: generation failed:', e)
		raise

OUTPUT.write_text(__import__('json').dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Foodora: extracted keys: {list(payload.keys())} -> {OUTPUT}')
