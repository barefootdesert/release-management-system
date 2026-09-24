"""Класс Product и функции работы с коллекцией продуктов."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .entity import Entity

if TYPE_CHECKING:
    from .releases import Release


class Product(Entity):
    """Программный продукт, для которого готовят релизы."""

    def __init__(self, product_id: int, name: str) -> None:
        """Создать объект продукта."""
        super().__init__(product_id, name)

    @staticmethod
    def validate_name(name: str) -> bool:
        """Проверить, что название продукта непустое."""
        return bool(name.strip())

    @classmethod
    def from_data(cls, data: dict) -> Product:
        """Создать продукт из словаря JSON."""
        return cls(int(data["id"]), str(data["name"]))

    def __str__(self) -> str:
        """Вернуть строковое представление продукта."""
        return f"{self.id}. {self.name}"


def add_product(products: list[Product], product_name: str) -> Product:
    """Создать продукт, добавить в коллекцию и вернуть объект."""
    if not Product.validate_name(product_name):
        raise ValueError("Название не может быть пустым")
    product_id = 1
    if products:
        product_id = max(item.id for item in products) + 1
    product = Product(product_id, product_name.strip())
    products.append(product)
    return product


def find_product(products: list[Product], query: str) -> list[Product]:
    """Найти продукты по подстроке названия без учёта регистра."""
    return [item for item in products if item.matches(query)]


def get_product(
    products: list[Product],
    product_id: int,
) -> Product | None:
    """Вернуть продукт по идентификатору или None."""
    for item in products:
        if item.id == product_id:
            return item
    return None


def sort_products(products: list[Product]) -> list[Product]:
    """Вернуть продукты, упорядоченные по названию."""
    return sorted(products, key=lambda item: item.name.lower())


def has_active_releases(
    releases: list[Release],
    product: Product,
) -> bool:
    """Проверить, есть ли у продукта незавершённые релизы."""
    for item in releases:
        if item.product.id == product.id and item.is_active:
            return True
    return False


def delete_product(
    products: list[Product],
    product_id: int,
    releases: list[Release],
) -> Product:
    """Удалить продукт, если у него нет активных релизов."""
    product = get_product(products, product_id)
    if product is None:
        raise KeyError("Продукт не найден")
    if has_active_releases(releases, product):
        raise ValueError(
            "Сначала отмените запланированные релизы этого продукта"
        )
    products.remove(product)
    return product


def show_products(products: list[Product]) -> None:
    """Вывести список продуктов."""
    if not products:
        print("Продукты ещё не добавлены.")
        return
    print("Продукты:")
    for product in sort_products(products):
        print(f"  {product}")
