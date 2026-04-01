#!/bin/sh
set -e

# Initialize database schema and admin user
python init_db.py || true

# Determine runtime port (Render sets PORT). 5000 fallback for local dev.
PORT_TO_BIND=${PORT:-5000}

# Start app
exec gunicorn --bind 0.0.0.0:${PORT_TO_BIND} --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
