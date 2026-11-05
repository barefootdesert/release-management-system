"""View-функции главной страницы."""

from django.shortcuts import render

from developers.models import Developer
from products.models import Product
from releases.models import Release
from tasks.models import Task


def index(request):
    """Главная страница: краткая сводка через ORM (count)."""
    return render(
        request,
        "homepage/index.html",
        {
            "products_count": Product.objects.count(),
            "releases_count": Release.objects.active().count(),
            "developers_count": Developer.objects.count(),
            "tasks_count": Task.objects.count(),
        },
    )


def page_not_found(request, exception):
    """Собственная страница ошибки 404."""
    return render(request, "homepage/404.html", status=404)
