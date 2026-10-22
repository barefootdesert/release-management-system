"""View-функции страниц релизов (JSON + SQLite)."""

from django.shortcuts import render

from db.database import get_connection
from models.releases import find_release_by_id
from storage import load_products, load_releases


def releases_list(request):
    """Список активных релизов из SQLite с JOIN (ПР7)."""
    connection = get_connection()
    try:
        releases = connection.execute(
            """
            SELECT
                r.id,
                r.version,
                r.environment,
                r.status,
                r.release_date,
                p.name AS product_name
            FROM releases AS r
            JOIN products AS p ON p.id = r.product_id
            WHERE r.status != 'cancelled'
            ORDER BY r.release_date
            """
        ).fetchall()
    finally:
        connection.close()
    return render(
        request,
        "releases/release_list.html",
        {"releases": releases},
    )


def release_detail(request, release_id):
    """Карточка релиза; 404, если релиз не найден."""
    products = load_products()
    releases = load_releases(products)
    release = find_release_by_id(releases, release_id)
    status = 404 if release is None else 200
    return render(
        request,
        "releases/release_detail.html",
        {"release": release},
        status=status,
    )


def statistics(request):
    """Статистика числа релизов по продуктам (SQL GROUP BY)."""
    connection = get_connection()
    try:
        stats = connection.execute(
            """
            SELECT
                p.id,
                p.name,
                COUNT(r.id) AS releases_count
            FROM products AS p
            LEFT JOIN releases AS r ON r.product_id = p.id
            GROUP BY p.id, p.name
            ORDER BY releases_count DESC, p.name
            """
        ).fetchall()
        total_active = connection.execute(
            """
            SELECT COUNT(*) AS releases_count
            FROM releases
            WHERE status != 'cancelled'
            """
        ).fetchone()
    finally:
        connection.close()
    return render(
        request,
        "releases/statistics.html",
        {
            "statistics": stats,
            "total_active": total_active["releases_count"],
        },
    )
