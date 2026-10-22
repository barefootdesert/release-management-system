"""View-функции страниц продуктов (JSON + SQLite)."""

from django.shortcuts import render

from db.database import get_connection
from models.products import find_product_by_id
from storage import load_products, load_releases


def products_list(request):
    """Список продуктов из SQLite (ПР7)."""
    connection = get_connection()
    try:
        products = connection.execute(
            """
            SELECT id, name
            FROM products
            ORDER BY name
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
    """Карточка продукта; 404, если продукт не найден."""
    products = load_products()
    product = find_product_by_id(products, product_id)
    related = []
    if product is not None:
        releases = load_releases(products)
        related = [
            item for item in releases if item.product.id == product.id
        ]
    status = 404 if product is None else 200
    return render(
        request,
        "products/product_detail.html",
        {"product": product, "related_releases": related},
        status=status,
    )


def available_products(request):
    """Продукты без активного релиза на выбранную дату (SQL)."""
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
