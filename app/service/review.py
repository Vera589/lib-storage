from typing import Any, Union

from fastapi import HTTPException
from pydantic import BaseModel

from app.repository.book import BookRepository
from app.repository.review import ReviewRepository


class Review(BaseModel):
    book_id: Union[str, None] = None
    rating: Union[int, None] = None
    review: Union[str, None] = None


class ReviewService:

    def __init__(self):
        self.review_repository = ReviewRepository()
        self.book_repository = BookRepository()

    def add_review(self, user_id: str, review: Review) -> None:
        if self.review_repository.find_by_user_id_and_book_id(user_id, review.book_id) is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Review for book {review.book_id} already exists"
            )
        if review.book_id is None:
            raise HTTPException(status_code=400, detail="Review should have a book_id")
        if review.rating is None:
            raise HTTPException(status_code=400, detail="Review should have a rating")
        if review.rating < 0 or review.rating > 100:
            raise HTTPException(
                status_code=400,
                detail="Review rating should be in range [0, 100]"
            )
        if len(review.review) > 500:
            raise HTTPException(status_code=400, detail="Review text should not exceed 500 symbols")
        book = self.book_repository.find_by_id(review.book_id)
        if book is None:
            raise HTTPException(
                status_code=400,
                detail=f"Book with id '{review.book_id}' not found"
            )
        self.review_repository.create({
            "book_id": review.book_id,
            "user_id": user_id,
            "rating": review.rating,
            "review": review.review
        })

    def get_review(self, user_id: str, book_id: str) -> dict[str, Any]:
        book = self.book_repository.find_by_id(book_id)
        if book is None:
            raise HTTPException(status_code=400, detail=f"Book with id '{book_id}' not found")
        review = self.review_repository.find_by_user_id_and_book_id(user_id, book_id)
        if review is None:
            raise HTTPException(status_code=404, detail=f"Review of the book '{book_id}' not found")
        return review

    def get_all_reviews(self, user_id: str) -> list[dict[str, Any]]:
        return self.review_repository.find_by_user_id(user_id)

    def update_review(self, user_id: str, book_id: str, updated_review: Review) -> None:
        self.get_review(user_id, book_id)
        updated_fields = {}
        if updated_review.rating is not None:
            if updated_review.rating < 0 or updated_review.rating > 100:
                raise HTTPException(
                    status_code=400,
                    detail="Review rating should be in range [0, 100]"
                )
            updated_fields["rating"] = updated_review.rating
        if updated_review.review is not None:
            if len(updated_review.review) > 500:
                raise HTTPException(
                    status_code=400,
                    detail="Review text should not exceed 500 symbols"
                )
            updated_fields["review"] = updated_review.review
        self.review_repository.update_by_user_id_and_book_id(user_id, book_id, updated_fields)

    def delete_review(self, user_id: str, book_id: str) -> None:
        self.review_repository.delete_by_user_id_and_book_id(user_id, book_id)
