#!/usr/bin/env python3
"""
extract_payload.py

Reusable helper that finds a <script id="scrape_payload" type="application/json"> tag in an HTML file
and writes the parsed JSON to an output path. If not found, it will try to find embedded JS objects
like INLINE_WOLT_DATA or a global variable named DATA and will attempt to eval/parse safely.

Usage:
  python scripts/extract_payload.py input.html output.json

This script is intentionally lightweight and avoids network calls.
"""
import sys
import json
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except Exception:
    print("BeautifulSoup4 not installed. Please run: pip install beautifulsoup4")
    sys.exit(2)


def extract_from_html(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")

    # 1) Prefer explicit JSON payload with id="scrape_payload"
    tag = soup.find('script', attrs={"id": "scrape_payload"})
    if tag and tag.string:
        try:
            return json.loads(tag.string)
        except Exception as e:
            raise ValueError(f"Found #scrape_payload but JSON parse failed: {e}")

    # 2) Fallback: try to find INLINE_WOLT_DATA or similar JS object definitions
    # Look for var/const/let NAME = { ... };
    js_text = "\n".join([s.get_text() for s in soup.find_all('script') if s.get_text()])

    # Try to find INLINE_WOLT_DATA or INLINE_*_DATA
    m = re.search(r"(INLINE_[A-Z0-9_]+_DATA)\s*=\s*(\{[\s\S]*?\})\s*;", js_text)
    if m:
        name, objtext = m.groups()
        try:
            # attempt to convert JS object to JSON by replacing unquoted keys with quoted ones
            json_text = js_object_to_json(objtext)
            return json.loads(json_text)
        except Exception as e:
            raise ValueError(f"Found {name} but parsing failed: {e}")

    # 3) Very simple heuristic: find first large JSON-like object and parse
    m2 = re.search(r"(\{[\s\S]{200,}\})", js_text)
    if m2:
        candidate = m2.group(1)
        try:
            json_text = js_object_to_json(candidate)
            return json.loads(json_text)
        except Exception:
            pass

    raise ValueError("No extractable JSON payload found in HTML")


def js_object_to_json(js_text: str) -> str:
    # Very small heuristic-converter:
    # - replace single quotes with double quotes
    # - add double quotes around unquoted keys (simple case)
    # - remove trailing commas
    s = js_text
    # replace JS unicode escape sequences preserved as-is
    s = s.replace("\r", "\\r").replace("\n", "\\n")
    # remove JS comments
    s = re.sub(r"//.*?$", "", s, flags=re.MULTILINE)
    s = re.sub(r"/\*[\s\S]*?\*/", "", s)
    # replace single quotes with double quotes (careful)
    s = re.sub(r"'([^']*)'", lambda m: '"' + m.group(1).replace('"', '\\"') + '"', s)
    # quote keys: any occurrence of { <ws> keyName:  --> { "keyName":
    s = re.sub(r"([\{,\n\s])(\s*)([A-Za-z0-9_\-]+)\s*:\s*", lambda m: m.group(1) + m.group(2) + '"' + m.group(3) + '": ', s)
    # remove trailing commas before } or ]
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/extract_payload.py input.html output.json")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Input file does not exist: {input_path}")
        sys.exit(2)

    html_text = input_path.read_text(encoding='utf-8')

    try:
        payload = extract_from_html(html_text)
    except Exception as e:
        print("Error extracting payload:", e)
        sys.exit(3)

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote payload to {output_path} (top-level keys: {list(payload.keys())})")


if __name__ == '__main__':
    main()
