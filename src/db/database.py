import sqlite3

from contextlib import contextmanager
from sqlite3 import Connection

from src.core import settings


class Database:
    def __init__(self):
        self.conn: Connection | None = self.connect()

    def connect(self):
        try:
            db_conn = sqlite3.connect(settings.DB_PATH)

            return db_conn
        except:
            return None

    def close(self):
        self.conn.close()


db = Database()


@contextmanager
def get_db():
    try:
        yield db
    finally:
        pass
