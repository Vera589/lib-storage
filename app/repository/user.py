from typing import Optional

from psycopg import sql

from app.repository.db import BaseRepository
from app.service.auth import User


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__('users', 'identity')

    def find_by_username(self, username: str) -> Optional[User]:
        query = sql.SQL("SELECT * FROM users.identity WHERE username = %(username)s").format()
        result = self.execute_query(query, {"username": username})
        if result:
            data = result[0]
            return User(id=str(data['id']), username=data['username'], secret_hash=data['secret_hash'])
        return None
