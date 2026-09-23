"""Функции для работы с продуктами."""


def add_product(products: dict[int, dict], product_name: str) -> int:
    """Добавить продукт в словарь products и вернуть его id."""
    product_id = 1
    if products:
        product_id = max(products) + 1
    products[product_id] = {
        "id": product_id,
        "name": product_name,
    }
    return product_id


def find_product(products: dict[int, dict], query: str) -> dict[int, dict]:
    """Найти продукты по подстроке названия без учёта регистра."""
    needle = query.strip().lower()
    found: dict[int, dict] = {}
    for product_id, product in products.items():
        name = str(product["name"]).lower()
        if needle in name:
            found[product_id] = product
    return found


def get_product(products: dict[int, dict], product_id: int) -> dict | None:
    """Вернуть продукт по идентификатору или None."""
    return products.get(product_id)


def sort_products(products: dict[int, dict]) -> list[dict]:
    """Вернуть продукты, упорядоченные по названию."""
    return sorted(
        products.values(),
        key=lambda item: str(item["name"]).lower(),
    )


def has_active_releases(releases: list[dict], product_id: int) -> bool:
    """Проверить, есть ли у продукта незавершённые релизы."""
    for item in releases:
        same_product = item["product_id"] == product_id
        active = item["status"] in {"planned", "published"}
        if same_product and active:
            return True
    return False


def delete_product(
    products: dict[int, dict],
    product_id: int,
    releases: list[dict],
) -> dict:
    """Удалить продукт, если у него нет активных релизов."""
    if product_id not in products:
        raise KeyError("Продукт не найден")
    if has_active_releases(releases, product_id):
        raise ValueError(
            "Сначала отмените запланированные релизы этого продукта"
        )
    return products.pop(product_id)
