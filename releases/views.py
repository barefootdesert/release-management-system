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
    "version",
    "environment",
    "release_date",
    "tests_passed",
    "approvals_count",
    "required_approvals",
    "is_hotfix",
    "status",
)

SORT_FIELDS = {
    "date": "release_date",
    "product": "product__name",
    "version": "version",
    "approvals": "-approvals_count",
}


def releases_list(request):
    """Активные релизы с фильтрами, сортировкой и пагинацией."""
    release_date = request.GET.get("date", "").strip()
    product_id = request.GET.get("product", "").strip()
    developer_id = request.GET.get("developer", "").strip()
    environment = request.GET.get("environment", "").strip()
    sort = request.GET.get("sort", "date")
    error = None

    releases = Release.objects.exclude(status="cancelled")

    if release_date:
        try:
            selected_date = datetime.strptime(
                release_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            releases = releases.filter(release_date=selected_date)

    if product_id.isdigit():
        releases = releases.filter(product_id=int(product_id))
    if developer_id.isdigit():
        releases = releases.filter(
            tasks__developer_id=int(developer_id)
        ).distinct()
    if environment in Release.Environment.values:
        releases = releases.filter(environment=environment)

    sort_field = SORT_FIELDS.get(sort, "release_date")
    releases = (
        releases.annotate(product_name=F("product__name"))
        .values(*RELEASE_FIELDS)
        .order_by(sort_field, "id")
    )

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
        Release.objects.select_related("product"),
        pk=release_id,
    )
    tasks = release.tasks.select_related("developer").order_by("id")
    return render(
        request,
        "releases/release_detail.html",
        {"release": release, "tasks": tasks},
    )


def ready_releases(request):
    """Релизы, готовые к публикации (Q-условия и сравнение полей F)."""
    publish_rules = (
        Q(environment=Release.Environment.TEST)
        | Q(environment=Release.Environment.STAGING)
        & (Q(approvals_count__gte=1) | Q(is_hotfix=True))
        | Q(
            environment=Release.Environment.PRODUCTION,
            approvals_count__gte=F("required_approvals"),
        )
    )
    releases = (
        Release.objects.filter(status="planned", tests_passed=True)
        .filter(publish_rules)
        .annotate(product_name=F("product__name"))
        .values(*RELEASE_FIELDS)
        .order_by("release_date", "id")
    )
    return render(request, "releases/ready.html", {"releases": releases})


def statistics(request):
    """Статистика: annotate(Count) по продуктам и фильтр по агрегату."""
    min_raw = request.GET.get("min", "").strip()
    min_count = int(min_raw) if min_raw.isdigit() else None

    stats = Product.objects.annotate(
        releases_count=Count("releases"),
        active_count=Count(
            "releases",
            filter=~Q(releases__status="cancelled"),
        ),
    )
    if min_count is not None:
        stats = stats.filter(releases_count__gte=min_count)
    stats = stats.values(
        "id", "name", "releases_count", "active_count"
    ).order_by("-releases_count", "name")

    max_count = max((item["releases_count"] for item in stats), default=0)

    return render(
        request,
        "releases/statistics.html",
        {
            "statistics": stats,
            "total_active": Release.objects.exclude(
                status="cancelled"
            ).count(),
            "min_count": min_count,
            "max_count": max_count or 1,
        },
    )
