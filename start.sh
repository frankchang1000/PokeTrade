#!/usr/bin/env bash

# Run migrations
python manage.py migrate --noinput

# Collect static
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn poketrade.wsgi:application --bind 0.0.0.0:$PORT
