"""View-функции страниц продуктов (данные из SQLite)."""

from django.shortcuts import render

from db.database import get_connection


def products_list(request):
    """Список продуктов из SQLite (SELECT + LEFT JOIN + COUNT)."""
    connection = get_connection()
    try:
        products = connection.execute(
            """
            SELECT
                p.id,
                p.name,
                COUNT(r.id) AS releases_count
            FROM products AS p
            LEFT JOIN releases AS r ON r.product_id = p.id
            GROUP BY p.id, p.name
            ORDER BY p.name
            """
        ).fetchall()
    finally:
        connection.close()
    return render(
        request,
        "products/product_list.html",
        {"products": products},
    )


def product_detail(request, product_id):
    """Карточка продукта из SQLite; 404, если запись не найдена."""
    connection = get_connection()
    try:
        product = connection.execute(
            """
            SELECT id, name
            FROM products
            WHERE id = ?
            """,
            [product_id],
        ).fetchone()
        related = []
        if product is not None:
            related = connection.execute(
                """
                SELECT
                    id,
                    version,
                    environment,
                    status,
                    release_date,
                    tests_passed,
                    approvals_count,
                    required_approvals,
                    is_hotfix
                FROM releases
                WHERE product_id = ?
                ORDER BY release_date
                """,
                [product_id],
            ).fetchall()
    finally:
        connection.close()
    status = 404 if product is None else 200
    return render(
        request,
        "products/product_detail.html",
        {"product": product, "related_releases": related},
        status=status,
    )


def available_products(request):
    """Продукты без активного релиза на выбранную дату (NOT IN)."""
    release_date = request.GET.get("date")
    products = []
    if release_date:
        connection = get_connection()
        try:
            products = connection.execute(
                """
                SELECT p.id, p.name
                FROM products AS p
                WHERE p.id NOT IN (
                    SELECT product_id
                    FROM releases
                    WHERE release_date = ?
                      AND status != 'cancelled'
                )
                ORDER BY p.name
                """,
                [release_date],
            ).fetchall()
        finally:
            connection.close()
    return render(
        request,
        "products/available.html",
        {
            "products": products,
            "release_date": release_date,
        },
    )
