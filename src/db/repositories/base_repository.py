import traceback
from sqlite3 import Cursor
from typing import TypeVar, Generic
from dataclasses import fields

from pypika import Query, Table
from pypika.queries import QueryBuilder
from pypika.terms import PseudoColumn

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, conn, table, model: ModelType):
        self._conn = conn
        self._cur: Cursor = conn.cursor()
        self.table: Table = Table(table)
        self._model: ModelType = model
        self._id_column: PseudoColumn = PseudoColumn(f"{fields(self._model)[-1].name}")

    def get_by_id(self, entity_id) -> ModelType | None:
        q: QueryBuilder = (
            Query.from_(self.table)
            .select(*[field.name for field in fields(self._model)])
            .where(self._id_column == entity_id)
        )
        query = q.get_sql()

        try:
            self._cur.execute(query)
            result = self._cur.fetchone()
            obj = self._model(*result)
            return obj
        except:
            traceback.print_exc()
            return None

    def get_all(self):  # TODO: return List[ModelType]
        q: QueryBuilder = (
            Query.from_(self.table)
            .select('*')
        )
        query = q.get_sql()

        try:
            self._cur.execute(query)
            result = self._cur.fetchall()
            return result
        except:
            traceback.print_exc()
            return None

    def get_obj_or_none(self, **kwargs) -> ModelType | None:
        q: QueryBuilder = (
            Query.from_(self.table)
            .select(*[field.name for field in fields(self._model)])
        )
        for key, value in kwargs.items():
            q = q.where(PseudoColumn(key) == value)

        query = q.get_sql()

        try:
            self._cur.execute(query)
            result = self._cur.fetchone()
            keys = self._model(*result)
            return keys
        except:
            traceback.print_exc()
            return None

    def create(self, model: ModelType) -> ModelType:
        model_fields = fields(model)
        column_names = [field.name for field in model_fields if field.default is not None]
        column_values = [getattr(model, field.name) for field in model_fields if field.default is not None]

        q: QueryBuilder = (
            Query.into(self.table)
            .columns(*column_names)
            .insert(*column_values)
        )
        table_fields = ', '.join(field.name for field in fields(self._model))
        query = q.get_sql() + f" RETURNING {table_fields}"

        try:
            self._cur.execute(query)
            result = self._model(*(self._cur.fetchone()))
            self._conn.commit()

            return result
        except:
            traceback.print_exc()
            return None

    def update(self, **kwargs):
        # TODO: working update
        q = Query.update(self.table)

        for field, value in kwargs.items():
            q = q.set(field, value)

        query = q.get_sql()
        self._cur.execute(query)
        # self._conn.commit()
        return True

    def delete(self, entity_id):
        q: QueryBuilder = (
            Query.from_(self.table)
            .delete()
            .where(self._id_column == entity_id)
        )
        query = q.get_sql()

        try:
            self._cur.execute(query)
            result = self._cur.fetchall()
            return result
        except:
            traceback.print_exc()
            return None