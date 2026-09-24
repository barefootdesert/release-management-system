"""Тесты класса Developer и функций работы с разработчиками."""

import pytest

from models import Developer, Product, Task
from models.developers import add_developer, delete_developer, find_developer
from models.tasks import add_task


def test_developer_creation():
    developer = Developer(1, "Анна Козлова", "backend")
    assert developer.id == 1
    assert developer.name == "Анна Козлова"
    assert developer.role == "backend"
    assert "Анна Козлова" in str(developer)


def test_developer_from_data():
    developer = Developer.from_data(
        {"id": 2, "name": "Иван Петров", "role": "qa"}
    )
    assert developer.id == 2
    assert developer.role == "qa"


def test_add_and_find_developer():
    developers: list[Developer] = []
    developer = add_developer(developers, "Анна Козлова", "backend")
    assert developer.id == 1
    found = find_developer(developers, "анна")
    assert found[0] is developer


def test_delete_developer_with_open_task():
    developers: list[Developer] = []
    developer = add_developer(developers, "Иван Петров", "qa")
    product = Product(1, "Платёжный шлюз")
    tasks: list[Task] = []
    add_task(tasks, "Проверить релиз", developer, product, None)
    with pytest.raises(ValueError):
        delete_developer(developers, developer.id, tasks)
    assert developer in developers
