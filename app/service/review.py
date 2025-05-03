import statistics
from typing import Any, Union, Dict, List

from fastapi import HTTPException
from pydantic import BaseModel

from app.repository.book import BookRepository
from app.repository.review import ReviewRepository
from app.repository.user import UserRepository

MAX_WEIGHTED_REVIEW_NUM = 10
REVIEW_NUM_INFLUENCE_RATE = 20
TOP_RATED_BOOKS_NUM = 5


class Review(BaseModel):
    book_id: Union[str, None] = None
    rating: Union[int, None] = None
    review: Union[str, None] = None


class ReviewService:

    def __init__(self):
        self.review_repository = ReviewRepository()
        self.book_repository = BookRepository()
        self.user_repository = UserRepository()

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

    def get_recommendations(self) -> list[dict[str, Any]]:
        top_rated_book_ids = self.top_rated_books()
        return self.book_repository.find_all_by_id(top_rated_book_ids)

    def top_rated_books(self) -> List[str]:
        all_reviews = self.review_repository.find_all()
        print("All reviews " + str(len(all_reviews)))
        all_reviews_by_book: Dict[List] = {}
        for reviews in all_reviews:
            book_id = reviews["book_id"]
            if book_id in all_reviews_by_book:
                all_reviews_by_book[book_id].append(reviews)
            else:
                all_reviews_by_book[book_id] = [reviews]
        all_books_weighted_rating: List[Dict] = []
        for book_id, reviews in all_reviews_by_book.items():
            median_rating = self.__median_rating(reviews)
            weighted_rating = self.__weighted_rating(median_rating, len(reviews))
            all_books_weighted_rating.append(
                {"book_id": book_id, "value": weighted_rating}
            )
        print("All weighted ratings " + str(len(all_books_weighted_rating)))
        top_rated_books = sorted(
            all_books_weighted_rating,
            key=lambda r: r["value"],
            reverse=True
        )[:TOP_RATED_BOOKS_NUM]
        return list(map(lambda b: b["book_id"], top_rated_books))

    def __median_rating(self, reviews: List[Dict]):
        all_ratings = []
        for review in reviews:
            all_ratings.append(review["rating"])
        return statistics.median(all_ratings)

    def __weighted_rating(self, rating: int, review_num: int):
        base_rate = (100 - REVIEW_NUM_INFLUENCE_RATE) / 100
        review_num_dependant_rate = 1 - base_rate
        return rating * (
                base_rate
                + review_num_dependant_rate
                * MAX_WEIGHTED_REVIEW_NUM / max(review_num, MAX_WEIGHTED_REVIEW_NUM)
        )
