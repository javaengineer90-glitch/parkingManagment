import os
import sqlite3
import psycopg2
from werkzeug.security import generate_password_hash
from config import get_config

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCHEMA = os.path.join(BASE_DIR, 'schema.sql')


def _normalize_sqlite_path(database_url: str) -> str:
    if database_url.startswith('sqlite:////'):
        return database_url[len('sqlite:////') - 1:]
    if database_url.startswith('sqlite:///'):
        return database_url[len('sqlite:///'):]
    if database_url.startswith('sqlite://'):
        return database_url[len('sqlite://'):]
    return database_url


def init_database():
    config = get_config()
    database_url = config.DATABASE

    if database_url.startswith('sqlite:') or database_url.endswith('.db'):
        sqlite_path = _normalize_sqlite_path(database_url)
        abs_path = os.path.abspath(sqlite_path)
        db_dir = os.path.dirname(abs_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(abs_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        with open(SCHEMA, 'r') as f:
            cursor.executescript(f.read())

        cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@society.com',))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, flat_number, phone, role) VALUES (?, ?, ?, ?, ?, ?)",
                ('Admin', 'admin@society.com', generate_password_hash('admin123', method='pbkdf2:sha256'), 'ADMIN', '0000000000', 'admin')
            )
            print("Default admin created: admin@society.com / admin123")

        conn.commit()
        cursor.close()
        conn.close()

    else:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        with open(SCHEMA, 'r') as f:
            cursor.execute(f.read())

        cursor.execute("SELECT id FROM users WHERE email = %s", ('admin@society.com',))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, flat_number, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                ('Admin', 'admin@society.com', generate_password_hash('admin123', method='pbkdf2:sha256'), 'ADMIN', '0000000000', 'admin')
            )
            print("Default admin created: admin@society.com / admin123")

        conn.commit()
        cursor.close()
        conn.close()

    print("Database initialized successfully!")


if __name__ == '__main__':
    init_database()
