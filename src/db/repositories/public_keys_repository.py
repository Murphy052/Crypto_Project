import traceback
from dataclasses import fields

from pypika import Query
from pypika.queries import QueryBuilder, Table
from pypika.terms import PseudoColumn

from . import BaseRepository
from src.db import get_db
from src.schemas import PublicKeys


class PublicKeysRepository(BaseRepository):
    def __init__(self, conn):
        super().__init__(conn=conn, table="public_keys", model=PublicKeys)

    def get_key_by_user_id(self, user_id: int):
        pseudo_column: PseudoColumn = PseudoColumn("user_id")
        q: QueryBuilder = (
            Query.from_(self.table)
            .select(*[field.name for field in fields(self._model)])
            .where(pseudo_column == user_id)
        )
        query: str = q.get_sql()

        try:
            self._cur.execute(query)
            result = self._cur.fetchone()
            keys = self._model(*result)
            return keys
        except:
            traceback.print_exc()
            return None

    def get_keys_pair_by_username(self, username: str):
        user_table = Table("user")
        q: QueryBuilder = (
            Query.from_(self.table)
            .join(user_table)
            .on(self.table.user_id == user_table.user_id)
            .select(self.table.public_key_exp, self.table.public_key_n)
            .where(user_table.username == username)
        )
        query: str = q.get_sql()

        try:
            self._cur.execute(query)
            result = self._cur.fetchone()
            return result
        except:
            traceback.print_exc()
            return None

try:
    with get_db() as db:
        public_keys_repository = PublicKeysRepository(conn=db.conn)
except Exception as e:
    # logging.error("An error occurred during UserRepository initialization:")
    # logging.error(traceback.format_exc())
    raise
