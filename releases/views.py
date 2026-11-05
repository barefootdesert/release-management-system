"""View-функции страниц релизов (данные из SQLite)."""

from django.shortcuts import render

from db.database import get_connection


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
                r.tests_passed,
                r.approvals_count,
                r.required_approvals,
                r.is_hotfix,
                p.id AS product_id,
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
    """Карточка релиза из SQLite; 404, если запись не найдена."""
    connection = get_connection()
    try:
        release = connection.execute(
            """
            SELECT
                r.id,
                r.product_id,
                r.version,
                r.environment,
                r.status,
                r.release_date,
                r.tests_passed,
                r.approvals_count,
                r.required_approvals,
                r.is_hotfix,
                p.name AS product_name
            FROM releases AS r
            JOIN products AS p ON p.id = r.product_id
            WHERE r.id = ?
            """,
            [release_id],
        ).fetchone()
    finally:
        connection.close()
    status = 404 if release is None else 200
    return render(
        request,
        "releases/release_detail.html",
        {"release": release},
        status=status,
    )


def ready_releases(request):
    """Релизы, готовые к публикации (WHERE по нескольким полям)."""
    connection = get_connection()
    try:
        releases = connection.execute(
            """
            SELECT
                r.id,
                p.name AS product_name,
                r.version,
                r.environment,
                r.release_date,
                r.approvals_count,
                r.required_approvals,
                r.is_hotfix
            FROM releases AS r
            JOIN products AS p ON p.id = r.product_id
            WHERE r.status = 'planned'
              AND r.tests_passed = 1
              AND (
                    r.environment = 'test'
                 OR (r.environment = 'staging'
                     AND (r.approvals_count >= 1 OR r.is_hotfix = 1))
                 OR (r.environment = 'production'
                     AND r.approvals_count >= r.required_approvals)
              )
            ORDER BY r.release_date
            """
        ).fetchall()
    finally:
        connection.close()
    return render(
        request,
        "releases/ready.html",
        {"releases": releases},
    )


def statistics(request):
    """Статистика релизов: GROUP BY и опциональный HAVING."""
    min_raw = request.GET.get("min", "")
    min_count = None
    if min_raw not in (None, ""):
        try:
            min_count = int(min_raw)
        except ValueError:
            min_count = None

    connection = get_connection()
    try:
        if min_count is None:
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
        else:
            stats = connection.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    COUNT(r.id) AS releases_count
                FROM products AS p
                LEFT JOIN releases AS r ON r.product_id = p.id
                GROUP BY p.id, p.name
                HAVING COUNT(r.id) >= ?
                ORDER BY releases_count DESC, p.name
                """,
                [min_count],
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

    max_count = 0
    for item in stats:
        if item["releases_count"] > max_count:
            max_count = item["releases_count"]

    return render(
        request,
        "releases/statistics.html",
        {
            "statistics": stats,
            "total_active": total_active["releases_count"],
            "min_count": min_count,
            "max_count": max_count or 1,
        },
    )
