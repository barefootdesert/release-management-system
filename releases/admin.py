from django.contrib import admin

from tasks.admin import TaskInReleaseInline

from .models import Release


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "version",
        "environment",
        "release_date",
        "status",
        "tests_passed",
        "approvals",
        "approved",
        "is_hotfix",
    )
    list_display_links = ("id", "version")
    list_editable = ("status",)
    list_filter = (
        "status",
        "environment",
        "tests_passed",
        "is_hotfix",
        "release_date",
        "product",
    )
    search_fields = ("version", "product__name", "tasks__developer__name")
    date_hierarchy = "release_date"
    list_select_related = ("product",)
    ordering = ("release_date", "id")
    list_per_page = 10
    autocomplete_fields = ("product",)
    readonly_fields = ("is_approved",)
    fieldsets = (
        (None, {"fields": ("product", "version", "release_date", "status")}),
        (
            "Проверки перед публикацией",
            {
                "fields": (
                    "environment",
                    "tests_passed",
                    "is_hotfix",
                    "approvals_count",
                    "required_approvals",
                    "is_approved",
                ),
            },
        ),
    )
    inlines = (TaskInReleaseInline,)
    actions = ("mark_completed", "mark_cancelled", "mark_active")

    @admin.display(description="согласования", ordering="approvals_count")
    def approvals(self, obj):
        return f"{obj.approvals_count} / {obj.required_approvals}"

    @admin.display(
        description="согласован",
        boolean=True,
        ordering="is_approved",
    )
    def approved(self, obj):
        return obj.is_approved

    def _set_status(self, request, queryset, status):
        updated = queryset.update(status=status)
        label = Release.Status(status).label
        self.message_user(request, f"Статус «{label}»: {updated} релиз(ов).")

    @admin.action(description="Отметить как опубликованные")
    def mark_completed(self, request, queryset):
        self._set_status(request, queryset, Release.Status.COMPLETED)

    @admin.action(description="Отменить выбранные релизы")
    def mark_cancelled(self, request, queryset):
        self._set_status(request, queryset, Release.Status.CANCELLED)

    @admin.action(description="Вернуть в запланированные")
    def mark_active(self, request, queryset):
        self._set_status(request, queryset, Release.Status.ACTIVE)
