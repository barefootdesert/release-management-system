"""View-функции главной страницы."""

from django.shortcuts import render

from db.database import get_connection


def index(request):
    """Главная страница: краткая сводка из SQLite."""
    connection = get_connection()
    try:
        products_count = connection.execute(
            "SELECT COUNT(*) AS n FROM products"
        ).fetchone()["n"]
        releases_count = connection.execute(
            """
            SELECT COUNT(*) AS n
            FROM releases
            WHERE status != 'cancelled'
            """
        ).fetchone()["n"]
        developers_count = connection.execute(
            "SELECT COUNT(*) AS n FROM developers"
        ).fetchone()["n"]
        tasks_count = connection.execute(
            "SELECT COUNT(*) AS n FROM tasks"
        ).fetchone()["n"]
    finally:
        connection.close()
    return render(
        request,
        "homepage/index.html",
        {
            "products_count": products_count,
            "releases_count": releases_count,
            "developers_count": developers_count,
            "tasks_count": tasks_count,
        },
    )


def page_not_found(request, exception):
    """Собственная страница ошибки 404."""
    return render(request, "homepage/404.html", status=404)
