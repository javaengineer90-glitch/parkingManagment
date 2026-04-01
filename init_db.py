import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'parking.db')
SCHEMA = os.path.join(BASE_DIR, 'schema.sql')


def init_database():
    conn = sqlite3.connect(DATABASE)
    with open(SCHEMA, 'r') as f:
        conn.executescript(f.read())

    # Create default admin user
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@society.com',))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, flat_number, phone, role) VALUES (?, ?, ?, ?, ?, ?)",
            ('Admin', 'admin@society.com', generate_password_hash('admin123', method='pbkdf2:sha256'), 'ADMIN', '0000000000', 'admin')
        )
        print("Default admin created: admin@society.com / admin123")

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


if __name__ == '__main__':
    init_database()
