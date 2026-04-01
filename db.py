import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g, current_app


def _normalize_sqlite_path(database_url: str) -> str:
    if database_url.startswith('sqlite:////'):
        return database_url[len('sqlite:////') - 1:]
    if database_url.startswith('sqlite:///'):
        return database_url[len('sqlite:///'):]
    if database_url.startswith('sqlite://'):
        return database_url[len('sqlite://'):]
    return database_url


class SQLiteDB:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=None):
        cur = self.conn.cursor()
        try:
            cur.execute(query, params or ())
        except Exception as e:
            raise RuntimeError(f"SQLite query failed: {e} | query={query} | params={params}") from e
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class PostgresDB:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def execute(self, query, params=None):
        cur = self.cursor()
        try:
            cur.execute(query, params or ())
        except Exception as e:
            raise RuntimeError(f"Postgres query failed: {e} | query={query} | params={params}") from e
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_db():
    if 'db' not in g:
        database_url = current_app.config['DATABASE']
        if database_url.startswith('sqlite:') or database_url.endswith('.db'):
            sqlite_path = _normalize_sqlite_path(database_url)
            abs_path = os.path.abspath(sqlite_path)
            db_dir = os.path.dirname(abs_path)
            try:
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
            except PermissionError:
                # fallback to tmp path if /app/data is not writable in cloud environment
                abs_path = '/tmp/parking.db'
                db_dir = os.path.dirname(abs_path)
                if not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)

            conn = sqlite3.connect(abs_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            g.db = SQLiteDB(conn)
        else:
            conn = psycopg2.connect(database_url)
            conn.autocommit = False
            g.db = PostgresDB(conn)
    return g.db


def close_db(e=None):
    db_obj = g.pop('db', None)
    if db_obj is not None:
        db_obj.close()


def init_app(app):
    app.teardown_appcontext(close_db)
