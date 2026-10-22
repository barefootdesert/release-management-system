"""Импорт данных из JSON-файлов в SQLite (ПР7)."""

from __future__ import annotations

import json
import sqlite3

from db.database import BASE_DIR, DB_PATH, get_connection

DATA_DIR = BASE_DIR / "data"
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"


def _load_json(name: str) -> list[dict]:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as file:
        return list(json.load(file))


def import_data() -> None:
    """Пересоздать схему и загрузить данные из JSON."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    connection = get_connection()
    try:
        connection.executescript(schema)

        products = _load_json("products.json")
        developers = _load_json("developers.json")
        releases = _load_json("releases.json")
        tasks = _load_json("tasks.json")

        connection.executemany(
            "INSERT INTO products (id, name) VALUES (?, ?)",
            [(int(item["id"]), str(item["name"])) for item in products],
        )
        connection.executemany(
            "INSERT INTO developers (id, name, role) VALUES (?, ?, ?)",
            [
                (int(item["id"]), str(item["name"]), str(item["role"]))
                for item in developers
            ],
        )
        connection.executemany(
            """
            INSERT INTO releases (
                id, product_id, version, environment,
                tests_passed, approvals_count, required_approvals,
                is_hotfix, release_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    int(item["id"]),
                    int(item["product_id"]),
                    str(item["version"]),
                    str(item["environment"]),
                    1 if item["tests_passed"] else 0,
                    int(item["approvals_count"]),
                    int(item["required_approvals"]),
                    1 if item["is_hotfix"] else 0,
                    str(item["release_date"]),
                    str(item["status"]),
                )
                for item in releases
            ],
        )
        connection.executemany(
            """
            INSERT INTO tasks (
                id, title, developer_id, product_id, release_id, status
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    int(item["id"]),
                    str(item["title"]),
                    int(item["developer_id"]),
                    int(item["product_id"]),
                    (
                        int(item["release_id"])
                        if item.get("release_id") is not None
                        else None
                    ),
                    str(item["status"]),
                )
                for item in tasks
            ],
        )
        connection.commit()
        print(f"Импорт завершён: {DB_PATH}")
        print(
            "products={p}, developers={d}, releases={r}, tasks={t}".format(
                p=len(products),
                d=len(developers),
                r=len(releases),
                t=len(tasks),
            )
        )
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    import_data()
