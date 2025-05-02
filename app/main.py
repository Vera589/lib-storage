from fastapi import FastAPI

from .api import book, user, reviews, recommendation

app = FastAPI()

app.include_router(book.router)
app.include_router(user.router)
app.include_router(reviews.router)
app.include_router(recommendation.router)
