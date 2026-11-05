from django.contrib import admin

from .models import Task


class TaskInReleaseInline(admin.TabularInline):
    model = Task
    fields = ("title", "developer", "product", "status")
    autocomplete_fields = ("developer", "product")
    extra = 0
    show_change_link = True


class TaskInDeveloperInline(admin.TabularInline):
    model = Task
    fields = ("title", "product", "release", "status")
    autocomplete_fields = ("product", "release")
    extra = 0
    show_change_link = True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "developer", "product", "release", "status")
    list_display_links = ("id", "title")
    list_editable = ("status",)
    list_filter = ("status", "product", "developer")
    search_fields = ("title", "developer__name", "product__name")
    list_select_related = ("developer", "product", "release__product")
    autocomplete_fields = ("developer", "product", "release")
    ordering = ("id",)
    list_per_page = 20
