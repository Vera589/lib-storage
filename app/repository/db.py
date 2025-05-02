import os
from contextlib import contextmanager
from typing import Dict, List, Optional, Union

import psycopg
from psycopg import sql
from psycopg.rows import DictRow
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

db_pool = ConnectionPool(
    conninfo=(
        f"host={os.getenv('DB_HOST')} "
        f"port={os.getenv('DB_PORT')} "
        f"dbname={os.getenv('DB_NAME')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASSWORD')} "
    ),
    min_size=1,
    max_size=10,
    timeout=5,
    kwargs={"row_factory": dict_row}
)


class BaseRepository:

    def __init__(self, schema_name: str, table_name: str):
        self.schema_name = schema_name
        self.table_name = table_name

    @contextmanager
    def _get_connection(self) -> psycopg.Connection[DictRow]:
        conn = None
        try:
            with db_pool.connection() as conn:
                yield conn
                conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e

    def execute_query(self, query: Union[str, sql.Composed], params: Optional[Dict] = None) -> List[DictRow]:
        with self._get_connection() as conn:
            conn.row_factory = dict_row
            return conn.execute(query, params).fetchall()

    def execute_command(self, command: Union[str, sql.Composed], params: Optional[Dict] = None) -> None:
        with self._get_connection() as conn:
            conn.execute(command, params)

    def find_by_id(self, id: str) -> Optional[DictRow]:
        query = sql.SQL("SELECT * FROM {} WHERE id = %(id)s").format(
            sql.Identifier(self.schema_name, self.table_name)
        )
        result = self.execute_query(query, {"id": id})
        return result[0] if result else None

    def find_all(self) -> List[DictRow]:
        query = sql.SQL("SELECT * FROM {}").format(
            sql.Identifier(self.schema_name, self.table_name)
        )
        return self.execute_query(query)

    def create(self, data: Dict) -> None:
        columns = sql.SQL(', ').join(map(sql.Identifier, data.keys()))
        placeholders = sql.SQL(', ').join(
            sql.Placeholder(key) for key in data.keys()
        )
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(self.schema_name, self.table_name),
            columns,
            placeholders
        )
        self.execute_command(query, data)

    def update(self, id: str, data: Dict) -> None:
        set_clause = sql.SQL(', ').join(
            sql.SQL("{} = {}").format(
                sql.Identifier(key),
                sql.Placeholder(key)
            ) for key in data.keys()
        )

        query = sql.SQL("UPDATE {} SET {} WHERE id = %(id)s").format(
            sql.Identifier(self.schema_name, self.table_name),
            set_clause
        )
        params = {"id": id, **data}
        self.execute_command(query, params)

    def delete(self, id: str) -> None:
        query = sql.SQL("DELETE FROM {} WHERE id = %(id)s").format(
            sql.Identifier(self.schema_name, self.table_name)
        )
        self.execute_command(query, {"id": id})
