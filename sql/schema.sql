-- Схема БД системы управления релизами (ПР7)

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS releases;
DROP TABLE IF EXISTS developers;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE developers (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE releases (
    id                  INTEGER PRIMARY KEY,
    product_id          INTEGER NOT NULL,
    version             TEXT NOT NULL,
    environment         TEXT NOT NULL,
    tests_passed        INTEGER NOT NULL DEFAULT 0,
    approvals_count     INTEGER NOT NULL DEFAULT 0,
    required_approvals  INTEGER NOT NULL DEFAULT 0,
    is_hotfix           INTEGER NOT NULL DEFAULT 0,
    release_date        TEXT NOT NULL,
    status              TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE tasks (
    id           INTEGER PRIMARY KEY,
    title        TEXT NOT NULL,
    developer_id INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    release_id   INTEGER,
    status       TEXT NOT NULL,
    FOREIGN KEY (developer_id) REFERENCES developers(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (release_id) REFERENCES releases(id)
);
