"""View-функции страниц релизов (Django ORM)."""

from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, render

from developers.models import Developer
from products.models import Product
from releases.models import Release

RELEASE_FIELDS = (
    "id",
    "product_id",
    "product_name",
    "product_slug",
    "version",
    "environment",
    "release_date",
    "tests_passed",
    "approvals_count",
    "required_approvals",
    "is_hotfix",
    "is_approved",
    "status",
)

SORT_FIELDS = {
    "date": "release_date",
    "product": "product__name",
    "version": "version",
    "approvals": "-approvals_count",
}


def with_product_fields(releases):
    return releases.annotate(
        product_name=F("product__name"),
        product_slug=F("product__slug"),
    ).values(*RELEASE_FIELDS)


def releases_list(request):
    """Активные релизы с фильтрами, сортировкой и пагинацией."""
    release_date = request.GET.get("date", "").strip()
    product_id = request.GET.get("product", "").strip()
    developer_id = request.GET.get("developer", "").strip()
    environment = request.GET.get("environment", "").strip()
    sort = request.GET.get("sort", "date")
    error = None

    releases = Release.objects.active()

    if release_date:
        try:
            selected_date = datetime.strptime(
                release_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            releases = releases.for_date(selected_date)

    if product_id.isdigit():
        releases = releases.filter(product_id=int(product_id))
    if developer_id.isdigit():
        releases = releases.filter(
            tasks__developer_id=int(developer_id)
        ).distinct()
    if environment in Release.Environment.values:
        releases = releases.filter(environment=environment)

    sort_field = SORT_FIELDS.get(sort, "release_date")
    releases = with_product_fields(releases).order_by(sort_field, "id")

    paginator = Paginator(releases, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "releases": page_obj.object_list,
        "release_date": release_date,
        "selected_product": product_id,
        "selected_developer": developer_id,
        "selected_environment": environment,
        "sort": sort,
        "products": Product.objects.order_by("name"),
        "developers": Developer.objects.order_by("name"),
        "environments": Release.Environment.choices,
        "error": error,
    }
    return render(request, "releases/release_list.html", context)


def release_detail(request, release_id):
    """Карточка релиза; 404, если запись не найдена."""
    release = get_object_or_404(
        Release.objects.with_product(),
        pk=release_id,
    )
    tasks = release.tasks.select_related("developer").order_by("id")
    return render(
        request,
        "releases/release_detail.html",
        {"release": release, "tasks": tasks},
    )


def ready_releases(request):
    """Релизы, готовые к публикации (метод менеджера ready_to_publish)."""
    releases = with_product_fields(
        Release.objects.ready_to_publish()
    ).order_by("release_date", "id")
    return render(request, "releases/ready.html", {"releases": releases})


def statistics(request):
    """Статистика по статусам (aggregate) и по продуктам (annotate)."""
    min_raw = request.GET.get("min", "").strip()
    min_count = int(min_raw) if min_raw.isdigit() else None

    by_status = Release.objects.aggregate(
        total=Count("id"),
        active=Count("id", filter=Q(status=Release.Status.ACTIVE)),
        cancelled=Count("id", filter=Q(status=Release.Status.CANCELLED)),
        completed=Count("id", filter=Q(status=Release.Status.COMPLETED)),
    )

    stats = Product.objects.annotate(
        releases_count=Count("releases"),
        active_count=Count(
            "releases",
            filter=Q(releases__status=Release.Status.ACTIVE),
        ),
    )
    if min_count is not None:
        stats = stats.filter(releases_count__gte=min_count)
    stats = stats.values(
        "id", "name", "slug", "releases_count", "active_count"
    ).order_by("-releases_count", "name")

    max_count = max((item["releases_count"] for item in stats), default=0)

    return render(
        request,
        "releases/statistics.html",
        {
            "by_status": by_status,
            "statistics": stats,
            "min_count": min_count,
            "max_count": max_count or 1,
        },
    )
