"""Загрузка и сохранение объектов предметной области в JSON."""

from __future__ import annotations

import json
from pathlib import Path

from models import Developer, Product, Release, Task
from models.developers import get_developer
from models.products import get_product
from models.releases import find_release

DATA_DIR = Path("data")
PRODUCTS_FILE = DATA_DIR / "products.json"
RELEASES_FILE = DATA_DIR / "releases.json"
DEVELOPERS_FILE = DATA_DIR / "developers.json"
TASKS_FILE = DATA_DIR / "tasks.json"


def _load_json(path: Path, default):
    """Прочитать JSON-файл; при ошибке вернуть значение по умолчанию."""
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(f"Файл {path} повреждён, используются пустые данные.")
        return default


def _save_json(path: Path, payload) -> None:
    """Записать данные в JSON-файл через контекстный менеджер."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def load_products(filename: Path = PRODUCTS_FILE) -> list[Product]:
    """Загрузить продукты из JSON и создать объекты Product."""
    raw = _load_json(filename, [])
    products: list[Product] = []
    for data in raw:
        products.append(Product.from_data(data))
    return products


def save_products(
    products: list[Product],
    filename: Path = PRODUCTS_FILE,
) -> None:
    """Сохранить объекты Product в JSON."""
    payload = [item.to_data() for item in sorted(products, key=lambda p: p.id)]
    _save_json(filename, payload)


def load_developers(filename: Path = DEVELOPERS_FILE) -> list[Developer]:
    """Загрузить разработчиков из JSON и создать объекты Developer."""
    raw = _load_json(filename, [])
    developers: list[Developer] = []
    for data in raw:
        developers.append(Developer.from_data(data))
    return developers


def save_developers(
    developers: list[Developer],
    filename: Path = DEVELOPERS_FILE,
) -> None:
    """Сохранить объекты Developer в JSON."""
    payload = [
        item.to_data() for item in sorted(developers, key=lambda d: d.id)
    ]
    _save_json(filename, payload)


def load_releases(
    products: list[Product],
    filename: Path = RELEASES_FILE,
) -> list[Release]:
    """Загрузить релизы и восстановить ссылки на объекты Product."""
    raw = _load_json(filename, [])
    releases: list[Release] = []
    for data in raw:
        product = get_product(products, int(data["product_id"]))
        if product is None:
            continue
        releases.append(Release.from_data(data, product))
    return releases


def save_releases(
    releases: list[Release],
    filename: Path = RELEASES_FILE,
) -> None:
    """Сохранить объекты Release; продукт записывается как product_id."""
    payload = [item.to_data() for item in sorted(releases, key=lambda r: r.id)]
    _save_json(filename, payload)


def load_tasks(
    products: list[Product],
    developers: list[Developer],
    releases: list[Release],
    filename: Path = TASKS_FILE,
) -> list[Task]:
    """Загрузить задачи и восстановить ссылки на связанные объекты."""
    raw = _load_json(filename, [])
    tasks: list[Task] = []
    for data in raw:
        developer = get_developer(developers, int(data["developer_id"]))
        product = get_product(products, int(data["product_id"]))
        if developer is None or product is None:
            continue
        release_id = data.get("release_id")
        release = None
        if release_id is not None:
            release = find_release(releases, int(release_id))
        tasks.append(Task.from_data(data, developer, product, release))
    return tasks


def save_tasks(tasks: list[Task], filename: Path = TASKS_FILE) -> None:
    """Сохранить объекты Task; связи записываются идентификаторами."""
    payload = [item.to_data() for item in sorted(tasks, key=lambda t: t.id)]
    _save_json(filename, payload)
