"""Тесты класса Product и функций работы с продуктами."""

import pytest

from models import Product, Release
from models.products import (
    add_product,
    delete_product,
    find_product,
    sort_products,
)


def test_product_creation():
    product = Product(1, "Платёжный шлюз")
    assert product.id == 1
    assert product.name == "Платёжный шлюз"
    assert "Платёжный шлюз" in str(product)


def test_product_from_data():
    product = Product.from_data({"id": 2, "name": "Личный кабинет"})
    assert product.id == 2
    assert product.name == "Личный кабинет"
    assert product.to_data()["name"] == "Личный кабинет"


def test_add_product():
    products: list[Product] = []
    product = add_product(products, "Платёжный шлюз")
    assert product.id == 1
    assert len(products) == 1
    assert products[0].name == "Платёжный шлюз"


def test_find_product():
    products: list[Product] = []
    add_product(products, "Платёжный шлюз")
    add_product(products, "Личный кабинет")
    found = find_product(products, "шлюз")
    assert len(found) == 1
    assert found[0].id == 1


def test_sort_products():
    products: list[Product] = []
    add_product(products, "Личный кабинет")
    add_product(products, "Платёжный шлюз")
    names = [item.name for item in sort_products(products)]
    assert names[0] == "Личный кабинет"


def test_delete_product():
    products: list[Product] = []
    product = add_product(products, "Временный продукт")
    deleted = delete_product(products, product.id, [])
    assert deleted.name == "Временный продукт"
    assert product not in products


def test_delete_product_with_active_release():
    products: list[Product] = []
    product = add_product(products, "Платёжный шлюз")
    from datetime import date

    releases = [
        Release(
            1,
            product,
            "2.1.0",
            "production",
            True,
            2,
            2,
            False,
            date(2026, 9, 20),
        )
    ]
    with pytest.raises(ValueError):
        delete_product(products, product.id, releases)
    assert product in products
