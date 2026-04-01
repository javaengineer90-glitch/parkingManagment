"""
WSGI entry point for production servers (Gunicorn, uWSGI, etc.)
Usage: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app
from init_db import init_database

app = create_app()

# Ensure database is initialized in case init_db.py was not invoked in runtime container.
try:
    init_database()
except Exception:
    pass

if __name__ == '__main__':
    app.run()