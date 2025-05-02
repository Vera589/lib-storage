import uuid
from dataclasses import dataclass
from typing import Any, Optional, Union
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel

from app.repository.book import BookRepository

@dataclass
class Book(BaseModel):
    id: Union[str, None] = None
    title: Union[str, None] = None
    description: Union[str, None] = None

@dataclass
class BookFilter(BaseModel):
    title: Union[str, None] = None


class BookService:

    def __init__(self):
        self.repository = BookRepository()

    def add_book(self, book: Book) -> UUID:
        book_id = uuid.uuid4()
        if book.title is None:
            raise HTTPException(status_code=400, detail="Book should have a title")
        self.repository.create({
            "id": book_id,
            "title": book.title,
            "description": book.description
        })
        return book_id

    def get_books(self, book_filter: BookFilter) -> list[dict[str, Any]]:
        if book_filter.title is None:
            return self.repository.find_all()
        return self.repository.find_by_title(book_filter.title)

    def get_book(self, book_id: str) -> Optional[dict[str, Any]]:
        book = self.repository.find_by_id(book_id)
        if book is None:
            raise HTTPException(status_code=404, detail=f"Book with id '{book_id}' not found")
        return book

    def update_book(self, book_id: str, updated_book: Book) -> None:
        self.get_book(book_id)
        updated_fields = {}
        if updated_book.title is not None:
            updated_fields["title"] = updated_book.title
        if updated_book.description is not None:
            updated_fields["description"] = updated_book.description
        self.repository.update(book_id, updated_fields)

    def delete_book(self, book_id: str) -> None:
        self.repository.delete(book_id)
