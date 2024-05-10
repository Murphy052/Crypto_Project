import traceback
from dataclasses import fields

from pypika import Query
from pypika.queries import QueryBuilder

from . import BaseRepository
from src.db import get_db
from src.schemas.user import User


class UserRepository(BaseRepository):
    def __init__(self, conn):
        super().__init__(conn=conn, table="user", model=User)

    def get_user(self, username):
        q: QueryBuilder = (
            Query.from_(self.table)
            .select(self.table.username, self.table.password, self.table.user_id)
            .where(self.table.username == username)
        )
        query = q.get_sql()

        try:
            self._cur.execute(query)
            result = self._cur.fetchone()
            user = self._model(*result)
            return user
        except:
            traceback.print_exc()
            return None


try:
    with get_db() as db:
        user_repository = UserRepository(conn=db.conn)
except Exception as e:
    # logging.error("An error occurred during UserRepository initialization:")
    # logging.error(traceback.format_exc())
    raise
