#!/bin/sh
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Optionally import scraped data if present
if [ -f /app/data/foodora.html.extracted.json ] || [ -f /app/data/wolt.html.extracted.json ]; then
  echo "Importing scraped JSON payloads..."
  python manage.py import_scraped || true
fi

# Exec given command (default: runserver)
exec "$@"
