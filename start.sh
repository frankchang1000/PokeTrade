=#!/usr/bin/env bash
set -e  # Exit if any command fails

# If PORT is not set, default to 8000
if [ -z "$PORT" ]; then
  echo "PORT is not set. Defaulting to 8000."
  PORT=8000
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on port $PORT..."
gunicorn poketrade.wsgi:application --bind 0.0.0.0:$PORT
