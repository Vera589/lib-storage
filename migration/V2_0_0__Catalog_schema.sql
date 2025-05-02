CREATE SCHEMA catalog;

CREATE TABLE IF NOT EXISTS catalog.book
(
    id          uuid PRIMARY KEY,
    title       text NOT NULL,
    description text
);

CREATE TABLE IF NOT EXISTS catalog.book_review
(
    book_id uuid REFERENCES catalog.book (id) ON DELETE CASCADE,
    user_id uuid REFERENCES users.identity (id) ON DELETE CASCADE,
    rating  int4 NOT NULL,
    CHECK (rating >= 0 AND rating <= 100),
    review  text
);