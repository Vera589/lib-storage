from typing import Union

from pydantic import BaseModel


class User(BaseModel):
    id: Union[str, None] = None
    username: Union[str, None] = None
    secret_hash: Union[str, None] = None
