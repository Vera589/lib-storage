from typing import List, Dict

from psycopg import sql
from psycopg.rows import DictRow

from app.repository.db import BaseRepository


class ReviewRepository(BaseRepository):

    def __init__(self):
        super().__init__('catalog', 'book_review')

    def find_by_user_id_and_book_id(self, user_id: str, book_id: str) -> DictRow:
        query = sql.SQL(
            "SELECT * "
            "FROM catalog.book_review "
            "WHERE book_id = %(book_id)s AND user_id = %(user_id)s"
        ).format()
        result = self.execute_query(query, {"book_id": book_id, "user_id": user_id})
        return result[0] if result else None

    def find_by_user_id(self, user_id: str) -> List[DictRow]:
        query = sql.SQL("SELECT * FROM catalog.book_review WHERE user_id = %(user_id)s").format()
        return self.execute_query(query, {"user_id": user_id})

    def update_by_user_id_and_book_id(self, user_id: str, book_id: str, data: Dict) -> None:
        set_clause = self.build_update_params(data)

        query = sql.SQL(
            "UPDATE {} SET {} "
            "WHERE user_id = %(user_id)s book_id = %(book_id)s"
        ).format(
            sql.Identifier(self.schema_name, self.table_name),
            set_clause
        )
        params = {"user_id": user_id, "book_id": book_id, **data}
        self.execute_command(query, params)

    def delete_by_user_id_and_book_id(self, user_id: str, book_id: str) -> None:
        query = sql.SQL(
            "DELETE FROM catalog.book_review "
            "WHERE book_id = %(book_id)s AND user_id = %(user_id)s"
        ).format()
        self.execute_command(query, {"book_id": book_id, "user_id": user_id})
