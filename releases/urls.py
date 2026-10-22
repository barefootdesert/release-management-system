"""Маршруты приложения releases."""

from django.urls import path

from . import views

app_name = "releases"

urlpatterns = [
    path("", views.releases_list, name="releases"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:release_id>/", views.release_detail, name="release_detail"),
]
