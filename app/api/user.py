from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.service.auth import AuthService, create_auth_token, Token

auth_service = AuthService()

router = APIRouter(
    tags=["users"]
)


@router.post("/auth")
async def auth(creds: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = auth_service.authenticate(creds.username, creds.password)
    return create_auth_token(user)


@router.post("/register", status_code=201)
def register(creds: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_id = auth_service.register_user(creds.username, creds.password)
    return {"user_id": user_id}
