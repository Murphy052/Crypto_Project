from pypika import Query, Table


class BaseRepository:
    def __init__(self, conn, table):
        self._conn = conn
        self._cur = conn.cursor()
        self.table = Table(table)

    def get_by_id(self, entity_id):
        q = Query.from_(self.table).select('*').where(self.table.sequence_id == entity_id)
        query = q.get_sql()
        self._cur.execute(query)
        result = self._cur.fetchall()[0]
        return result

    def get_all(self):
        q = Query.from_(self.table).select('*')
        query = q.get_sql()
        self._cur.execute(query)
        result = self._cur.fetchall()
        return result

    def create(self, **kwargs):
        pass

    def update(self, **kwargs):
        q = Query.update(self.table)

        for field, value in kwargs.items():
            q = q.set(field, value)

        query = q.get_sql()
        self._cur.execute(query)
        # self._conn.commit()
        return True

    def delete(self, entity_id):
        q = Query.from_(self.table).delete().where(self.table.sequence_id == entity_id)
        query = q.get_sql()
        self._cur.execute(query)
        result = self._cur.fetchall()
        return result
