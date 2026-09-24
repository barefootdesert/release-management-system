"""Тесты класса Task и взаимодействия объектов."""

from datetime import date

from models import Developer, Product, Release, Task
from models.tasks import add_task, set_task_status


def test_task_creation():
    product = Product(1, "Платёжный шлюз")
    developer = Developer(1, "Анна Козлова", "backend")
    release = Release(
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
    task = Task(1, "Исправить таймаут", developer, product, release)
    assert task.id == 1
    assert task.developer is developer
    assert task.product is product
    assert task.release is release
    assert task.status == "todo"
    assert task.developer.name == "Анна Козлова"
    assert task.release.product.name == "Платёжный шлюз"
    assert "Исправить таймаут" in str(task)


def test_add_and_close_task():
    product = Product(1, "Платёжный шлюз")
    developer = Developer(1, "Анна Козлова", "backend")
    tasks: list[Task] = []
    item = add_task(tasks, "Исправить таймаут", developer, product, None)
    assert item.status == "todo"
    set_task_status(tasks, item.id, "done")
    assert item.status == "done"
    assert not item.is_open


def test_cancelled_release_stays_in_collection():
    product = Product(1, "Платёжный шлюз")
    release = Release(
        1,
        product,
        "2.1.0",
        "test",
        True,
        0,
        1,
        False,
        date(2026, 9, 21),
    )
    releases = [release]
    release.cancel()
    assert release in releases
    assert release.is_cancelled
