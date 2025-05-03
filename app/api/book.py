from typing import Union

from fastapi import APIRouter

from app.service.book import BookService, Book, BookFilter

router = APIRouter(
    prefix="/books",
    tags=["books"]
)

service = BookService()


@router.post("/", status_code=201)
def add_book(req: Book):
    return {"book_id": service.add_book(req)}


@router.get("/")
def get_books(title: Union[str, None] = None):
    return service.get_books(BookFilter(title=title))


@router.get("/{book_id}")
def get_book(book_id: str):
    return service.get_book(book_id)


@router.patch("/{book_id}", status_code=204)
def update_book(book_id: str, req: Book):
    service.update_book(book_id, req)


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: str):
    service.delete_book(book_id)
