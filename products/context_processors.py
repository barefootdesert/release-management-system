"""Общие данные для всех шаблонов проекта."""

from products.models import Product
from releases.models import Release


def release_context(request):
    return {
        "site_name": "Система управления релизами",
        "products_total": Product.objects.count(),
        "active_releases_total": Release.objects.active().count(),
    }
