from fastapi import APIRouter

from app.service.auth import AuthService, create_auth_token, Token, Credentials

auth_service = AuthService()

router = APIRouter(
    tags=["users"]
)


@router.post("/auth")
async def auth(creds: Credentials) -> Token:
    user = auth_service.authenticate(creds.username, creds.password)
    return create_auth_token(user)


@router.post("/register", status_code=201)
def register(creds: Credentials):
    user_id = auth_service.register_user(creds.username, creds.password)
    return {"user_id": user_id}
