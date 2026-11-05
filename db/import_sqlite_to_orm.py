"""Перенос данных из SQLite-базы ПР7 в базу Django через ORM (ПР9).

Запуск из корня проекта после ``python manage.py migrate``:

    python db/import_sqlite_to_orm.py
"""

import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

SOURCE_DB = BASE_DIR / "data" / "releases.sqlite"

STATUS_CODES = {
    "planned": "active",
    "published": "completed",
    "cancelled": "cancelled",
}

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from developers.models import Developer  # noqa: E402
from products.models import Product  # noqa: E402
from releases.models import Release  # noqa: E402
from tasks.models import Task  # noqa: E402


def read_source():
    """Прочитать все таблицы исходной базы (только чтение)."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"Исходная база не найдена: {SOURCE_DB}. "
            "Создайте её командой: python -m db.import_json"
        )
    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        return {
            "products": connection.execute(
                "SELECT id, name FROM products ORDER BY id"
            ).fetchall(),
            "developers": connection.execute(
                "SELECT id, name, role FROM developers ORDER BY id"
            ).fetchall(),
            "releases": connection.execute(
                """
                SELECT
                    id, product_id, version, environment,
                    tests_passed, approvals_count, required_approvals,
                    is_hotfix, release_date, status
                FROM releases
                ORDER BY id
                """
            ).fetchall(),
            "tasks": connection.execute(
                """
                SELECT id, title, developer_id, product_id,
                       release_id, status
                FROM tasks
                ORDER BY id
                """
            ).fetchall(),
        }


def main():
    source = read_source()

    with transaction.atomic():
        for row in source["products"]:
            Product.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"]},
            )

        for row in source["developers"]:
            Developer.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"], "role": row["role"]},
            )

        for row in source["releases"]:
            Release.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "product_id": row["product_id"],
                    "version": row["version"],
                    "environment": row["environment"],
                    "tests_passed": bool(row["tests_passed"]),
                    "approvals_count": row["approvals_count"],
                    "required_approvals": row["required_approvals"],
                    "is_hotfix": bool(row["is_hotfix"]),
                    "release_date": date.fromisoformat(row["release_date"]),
                    "status": STATUS_CODES.get(row["status"], row["status"]),
                },
            )

        for row in source["tasks"]:
            Task.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "title": row["title"],
                    "developer_id": row["developer_id"],
                    "product_id": row["product_id"],
                    "release_id": row["release_id"],
                    "status": row["status"],
                },
            )

    print("Перенос данных завершён.")
    print(f"Продуктов: {Product.objects.count()}")
    print(f"Разработчиков: {Developer.objects.count()}")
    print(f"Релизов: {Release.objects.count()}")
    print(f"Задач: {Task.objects.count()}")


if __name__ == "__main__":
    main()
