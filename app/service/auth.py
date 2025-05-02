import os
import uuid
from dataclasses import dataclass
from datetime import timedelta, datetime, timezone
from typing import Annotated, Union
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from app.repository.user import UserRepository

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


@dataclass
class Token(BaseModel):
    access_token: str
    expire_at: str


@dataclass
class Credentials(BaseModel):
    username: str
    password: str


@dataclass
class User(BaseModel):
    username: str
    id: Union[str, None] = None
    secret_hash: Union[str, None] = None


def create_auth_token(user: User):
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user.username,
        "exp": expire_at
    }
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=access_token, expire_at=str(expire_at))


class AuthService:

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_repository = UserRepository()

    def register_user(self, username: str, password: str) -> UUID:
        user = self.user_repository.find_by_username(username)
        if user:
            raise HTTPException(
                status_code=409,
                detail=f"User with username '{username}' already exists"
            )
        user_id = uuid.uuid4()
        self.user_repository.create({
            "id": user_id,
            "username": username,
            "secret_hash": self.get_password_hash(password)
        })
        return user_id

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def authenticate(self, username: str, password: str):
        user = self.get_user(username)
        if not self.pwd_context.verify(password, user.secret_hash):
            raise HTTPException(status_code=401, detail=f"Password is wrong")
        return user

    def get_user_by_token(self, token: Annotated[str, Depends(oauth2_scheme)]):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Token is invalid")
        except InvalidTokenError as ex:
            raise HTTPException(status_code=401, detail="Token is invalid") from ex
        return self.get_user(username)

    def get_user(self, username: str) -> User:
        user = self.user_repository.find_by_username(username)
        if not user:
            raise HTTPException(
                status_code=401,
                detail=f"User with username '{username}' doesn't exist"
            )
        return user
