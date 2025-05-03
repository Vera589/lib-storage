-- 100 users
INSERT INTO users.identity (id, username, secret_hash)
SELECT
    gen_random_uuid(),
    'user_' || n,
    -- bcrypt hash of "password123" with cost 12
    '$2a$12$6H5DyG0O4R29W3XUWMB.0eWY9Q9Xv9z6LWJZ9Xl1vQ6J1YV5X5X5W'
FROM generate_series(1, 100) AS n;

-- 100 books
INSERT INTO catalog.book (id, title, description)
SELECT
    gen_random_uuid(),
    'Book Title ' || n,
    CASE
        WHEN n % 5 = 0 THEN 'A classic novel'
        WHEN n % 5 = 1 THEN 'Science fiction masterpiece'
        WHEN n % 5 = 2 THEN 'Historical documentation'
        WHEN n % 5 = 3 THEN 'Biography of famous person'
        ELSE 'Contemporary literature'
    END
FROM generate_series(1, 100) AS n;

-- Generate 5000 review
INSERT INTO catalog.book_review (book_id, user_id, rating, review)
WITH
-- Get all book IDs in random order with row numbers
book_ids AS (
    SELECT id, row_number() OVER () % 100 + 1 AS book_group
    FROM catalog.book
    ORDER BY random()
),
-- Get all user IDs in random order
user_ids AS (
    SELECT id
    FROM users.identity
    ORDER BY random()
),
review_records AS (
    SELECT
        (SELECT id FROM book_ids WHERE book_group = (n % 100 + 1) LIMIT 1) AS book_id,
        (SELECT id FROM user_ids OFFSET (n % 100) LIMIT 1) AS user_id,
        floor(random() * 101)::int AS rating,
        CASE
            WHEN random() < 0.3 THEN 'Excellent book, highly recommended!'
            WHEN random() < 0.6 THEN 'Good read, but could be better'
            WHEN random() < 0.8 THEN 'Average quality'
            ELSE 'Not my favorite'
        END AS review
    FROM generate_series(1, 5000) AS n
)
SELECT book_id, user_id, rating, review FROM review_records;
