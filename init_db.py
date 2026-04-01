import os
import psycopg2
from werkzeug.security import generate_password_hash
from config import get_config

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCHEMA = os.path.join(BASE_DIR, 'schema.sql')


def init_database():
    config = get_config()
    database_url = config.DATABASE

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
