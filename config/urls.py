"""Корневая маршрутизация Django-проекта."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Система управления релизами"
admin.site.site_title = "Администрирование релизов"
admin.site.index_title = "Продукты, релизы и команда"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("products/", include("products.urls")),
    path("releases/", include("releases.urls")),
]

if settings.USE_DEBUG_TOOLBAR:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()

handler404 = "homepage.views.page_not_found"
