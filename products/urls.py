"""Маршруты приложения products."""

from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.products_list, name="products"),
    path("available/", views.available_products, name="available"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
]
