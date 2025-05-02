from typing import List

from psycopg import sql
from psycopg.rows import DictRow

from app.repository.db import BaseRepository


class BookRepository(BaseRepository):
    def __init__(self):
        super().__init__('catalog', 'book')

    def find_by_title(self, title: str) -> List[DictRow]:
        query = sql.SQL("SELECT * FROM catalog.book WHERE title = %(title)s").format()
        return self.execute_query(query, {"title": title})
