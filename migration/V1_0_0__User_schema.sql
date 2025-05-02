CREATE SCHEMA users;

CREATE TABLE IF NOT EXISTS users.identity
(
    id          uuid PRIMARY KEY,
    username    text NOT NULL UNIQUE,
    secret_hash text NOT NULL
);