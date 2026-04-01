"""
WSGI entry point for production servers (Gunicorn, uWSGI, etc.)
Usage: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

app = create_app()

# Database is initialized by init_db.py during deployment.
# Ensure db file exists and schema is created before running Gunicorn.

if __name__ == '__main__':
    app.run()