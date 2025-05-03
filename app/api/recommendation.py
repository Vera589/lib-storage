from fastapi import APIRouter

from app.service.review import ReviewService

router = APIRouter(
    tags=["recommendations"]
)

service = ReviewService()


@router.get("/recommendations")
def read_reviews():
    return service.get_recommendations()
