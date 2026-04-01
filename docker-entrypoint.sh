#!/bin/sh
set -e

# Wait for Postgres readiness
until python - <<'PY'
import os
import psycopg2
from urllib.parse import urlparse

url = urlparse(os.environ.get('DATABASE_URL'))

try:
    conn = psycopg2.connect(
        dbname=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port or 5432,
    )
    conn.close()
    print('Postgres ready')
except Exception as e:
    raise SystemExit(1)
PY
 do
  echo "Waiting for Postgres..."
  sleep 2
done

# Initialize database schema and admin user
python init_db.py || true

# Start app
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
