"""Загрузка и сохранение данных проекта в JSON-файлах."""

import json
from pathlib import Path

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


def _load_indexed(path: Path) -> dict[int, dict]:
    """Загрузить список словарей в словарь по полю id."""
    raw = _load_json(path, [])
    items: dict[int, dict] = {}
    for item in raw:
        items[int(item["id"])] = item
    return items


def _save_indexed(path: Path, items: dict[int, dict]) -> None:
    """Сохранить словарь записей списком, упорядоченным по id."""
    payload = [items[key] for key in sorted(items)]
    _save_json(path, payload)


def load_products(filename: Path = PRODUCTS_FILE) -> dict[int, dict]:
    """Загрузить продукты из JSON-файла в словарь по id."""
    return _load_indexed(filename)


def save_products(
    products: dict[int, dict],
    filename: Path = PRODUCTS_FILE,
) -> None:
    """Сохранить продукты в JSON-файл."""
    _save_indexed(filename, products)


def load_releases(filename: Path = RELEASES_FILE) -> list[dict]:
    """Загрузить релизы из JSON-файла."""
    return list(_load_json(filename, []))


def save_releases(
    releases: list[dict],
    filename: Path = RELEASES_FILE,
) -> None:
    """Сохранить релизы в JSON-файл."""
    _save_json(filename, releases)


def load_developers(filename: Path = DEVELOPERS_FILE) -> dict[int, dict]:
    """Загрузить разработчиков из JSON-файла."""
    return _load_indexed(filename)


def save_developers(
    developers: dict[int, dict],
    filename: Path = DEVELOPERS_FILE,
) -> None:
    """Сохранить разработчиков в JSON-файл."""
    _save_indexed(filename, developers)


def load_tasks(filename: Path = TASKS_FILE) -> list[dict]:
    """Загрузить задачи из JSON-файла."""
    return list(_load_json(filename, []))


def save_tasks(tasks: list[dict], filename: Path = TASKS_FILE) -> None:
    """Сохранить задачи в JSON-файл."""
    _save_json(filename, tasks)
