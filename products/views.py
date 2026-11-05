"""View-функции страниц продуктов (Django ORM)."""

from datetime import datetime

from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from products.models import Product
from releases.models import Release


def products_list(request):
    """Список продуктов с количеством релизов (annotate + Count)."""
    products = (
        Product.objects.annotate(releases_count=Count("releases"))
        .values("id", "name", "slug", "releases_count")
        .order_by("name")
    )
    return render(
        request,
        "products/product_list.html",
        {"products": products},
    )


def product_detail(request, slug):
    """Карточка продукта по slug и его релизы; 404, если продукта нет."""
    product = get_object_or_404(Product, slug=slug)
    related_releases = product.releases.order_by("release_date", "id")
    return render(
        request,
        "products/product_detail.html",
        {"product": product, "related_releases": related_releases},
    )


def available_products(request):
    """Продукты без активного релиза на выбранную дату.

    Отменённые и опубликованные релизы продукт не занимают.
    """
    release_date = request.GET.get("date", "").strip()
    products = Product.objects.none()
    error = None

    if release_date:
        try:
            selected_date = datetime.strptime(
                release_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            busy_ids = (
                Release.objects.active()
                .for_date(selected_date)
                .values_list("product_id", flat=True)
            )
            products = Product.objects.exclude(pk__in=busy_ids).order_by(
                "name"
            )

    return render(
        request,
        "products/available.html",
        {
            "products": products,
            "release_date": release_date,
            "error": error,
        },
    )
