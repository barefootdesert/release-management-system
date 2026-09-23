"""Тесты функций работы с продуктами."""

import pytest

from products import (
    add_product,
    delete_product,
    find_product,
    sort_products,
)


def test_add_product():
    products = {}
    product_id = add_product(products, "Платёжный шлюз")
    assert product_id == 1
    assert len(products) == 1
    assert products[1]["name"] == "Платёжный шлюз"


def test_find_product():
    products = {}
    add_product(products, "Платёжный шлюз")
    add_product(products, "Личный кабинет")
    found = find_product(products, "шлюз")
    assert len(found) == 1
    assert 1 in found


def test_sort_products():
    products = {}
    add_product(products, "Личный кабинет")
    add_product(products, "Платёжный шлюз")
    names = [item["name"] for item in sort_products(products)]
    assert names[0] == "Личный кабинет"


def test_delete_product():
    products = {}
    product_id = add_product(products, "Временный продукт")
    deleted = delete_product(products, product_id, [])
    assert deleted["name"] == "Временный продукт"
    assert product_id not in products


def test_delete_product_with_active_release():
    products = {}
    product_id = add_product(products, "Платёжный шлюз")
    releases = [
        {
            "id": 1,
            "product_id": product_id,
            "status": "planned",
        }
    ]
    with pytest.raises(ValueError):
        delete_product(products, product_id, releases)
    assert product_id in products
