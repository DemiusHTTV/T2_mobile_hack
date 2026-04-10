#!/usr/bin/env sh
set -eu

cd /app

if ! python manage.py migrate --noinput; then
  echo "Migrate failed. Recreating sqlite database..." 1>&2
  if [ -n "${DB_NAME:-}" ] && [ -f "${DB_NAME}" ]; then
    rm -f "${DB_NAME}"
  fi
  python manage.py migrate --noinput
fi
python manage.py seed_demo
python manage.py collectstatic --noinput || true

exec gunicorn t2.wsgi:application --bind 0.0.0.0:3000 --workers 2 --threads 4
