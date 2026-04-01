from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db


class User(UserMixin):
    def __init__(self, id, name, email, password_hash, flat_number, phone, role, is_active, created_at):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.flat_number = flat_number
        self.phone = phone
        self.role = role
        self._is_active = is_active
        self.created_at = created_at

    @property
    def is_active(self):
        return bool(self._is_active)

    @property
    def is_admin(self):
        return self.role == 'admin'


def row_to_user(row):
    if row is None:
        return None
    return User(
        id=row['id'], name=row['name'], email=row['email'],
        password_hash=row['password_hash'], flat_number=row['flat_number'],
        phone=row['phone'], role=row['role'], is_active=row['is_active'],
        created_at=row['created_at']
    )


def get_user_by_id(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return row_to_user(row)


def get_user_by_email(email):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return row_to_user(row)


def create_user(name, email, password, flat_number, phone, role='resident'):
    db = get_db()
    db.execute(
        "INSERT INTO users (name, email, password_hash, flat_number, phone, role) VALUES (?, ?, ?, ?, ?, ?)",
        (name, email, generate_password_hash(password, method='pbkdf2:sha256'), flat_number, phone, role)
    )
    db.commit()


def get_all_users():
    db = get_db()
    rows = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    return [row_to_user(r) for r in rows]


def toggle_user_active(user_id):
    db = get_db()
    db.execute("UPDATE users SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?", (user_id,))
    db.commit()


def verify_password(user, password):
    return check_password_hash(user.password_hash, password)
