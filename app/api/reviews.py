from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import Response

from app.model.user import User
from app.service.auth import AuthService
from app.service.review import ReviewService, Review

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

service = ReviewService()
auth_service = AuthService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/", status_code=201)
def create_review(
        user: Annotated[User, Depends(auth_service.get_user_by_token)],
        req: Review
):
    service.add_review(user.id, req)
    return Response(status_code=201)


@router.get("/{book_id}")
def get_review(
        user: Annotated[User, Depends(auth_service.get_user_by_token)],
        book_id: str
):
    return service.get_review(user.id, book_id)


@router.get("/")
def get_all_reviews(
        user: Annotated[User, Depends(auth_service.get_user_by_token)]
):
    return service.get_all_reviews(user.id)


@router.patch("/{book_id}", status_code=204)
def update_review(
        user: Annotated[User, Depends(auth_service.get_user_by_token)],
        book_id: str,
        req: Review
):
    service.update_review(user.id, book_id, req)


@router.delete("/{book_id}", status_code=204)
def delete_review(
        user: Annotated[User, Depends(auth_service.get_user_by_token)],
        book_id: str
):
    service.delete_review(user.id, book_id)
