from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from releases.models import Release

from .models import Product


class ReleaseInline(admin.TabularInline):
    model = Release
    fields = (
        "version",
        "environment",
        "release_date",
        "status",
        "tests_passed",
        "approvals_count",
        "required_approvals",
    )
    extra = 0
    ordering = ("release_date",)
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "releases_count", "site_link")
    list_display_links = ("id", "name")
    search_fields = ("name", "slug")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("slug",)
    inlines = (ReleaseInline,)
    view_on_site = True

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(releases_total=Count("releases"))
        )

    @admin.display(description="релизов", ordering="releases_total")
    def releases_count(self, obj):
        return obj.releases_total

    @admin.display(description="на сайте")
    def site_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">открыть</a>',
            obj.get_absolute_url(),
        )
