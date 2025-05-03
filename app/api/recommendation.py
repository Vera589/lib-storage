from fastapi import APIRouter

from app.service.review import ReviewService

router = APIRouter()

service = ReviewService()

@router.get("/recommendations")
def read_reviews():
    return service.top_rated_books()
