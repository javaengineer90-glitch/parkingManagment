import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g, current_app


class PostgresDB:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def execute(self, query, params=None):
        cur = self.cursor()
        cur.execute(query, params or ())
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_db():
    if 'db' not in g:
        database_url = current_app.config['DATABASE']
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
