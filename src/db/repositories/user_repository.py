import traceback
from dataclasses import fields

from pypika import Query

from . import BaseRepository
from src.db import get_db
from src.schemas.user import User


class UserRepository(BaseRepository):
    def __init__(self, conn):
        super().__init__(conn=conn, table="user")

    def create(self, model: User):
        model_fields = fields(model)
        column_names = [field.name for field in model_fields if field.default is not None]
        column_values = [getattr(model, field.name) for field in model_fields if field.default is not None]

        q = Query.into(self.table).columns(*column_names).insert(*column_values)
        query = q.get_sql()
        try:
            self._cur.execute(query)
            self._conn.commit()

            return self.get_user(username=model.username)
        except:
            traceback.print_exc()
            return None

    def get_user(self, username):
        q = Query.from_(self.table).select(self.table.username, self.table.password, self.table.user_id).where(self.table.username == username)
        query = q.get_sql()
        self._cur.execute(query)
        result = self._cur.fetchall()
        try:
            user = User(*(result[0]))
            return user
        except:
            return None


try:
    with get_db() as db:
        user_repository = UserRepository(conn=db.conn)
except Exception as e:
    # logging.error("An error occurred during UserRepository initialization:")
    # logging.error(traceback.format_exc())
    raise
