from django.contrib import admin
from django.db.models import Count

from tasks.admin import TaskInDeveloperInline

from .models import Developer


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "role", "tasks_count")
    list_display_links = ("id", "name")
    list_editable = ("role",)
    list_filter = ("role",)
    search_fields = ("name", "role")
    ordering = ("name",)
    list_per_page = 20
    inlines = (TaskInDeveloperInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(tasks_total=Count("tasks"))
        )

    @admin.display(description="задач", ordering="tasks_total")
    def tasks_count(self, obj):
        return obj.tasks_total
