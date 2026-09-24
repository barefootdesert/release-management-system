"""Класс Task и функции работы с коллекцией задач."""

from __future__ import annotations

from typing import Any

from .developers import Developer
from .products import Product
from .releases import Release

TASK_STATUSES = ("todo", "in_progress", "done")
VALID_TASK_STATUSES = set(TASK_STATUSES)


class Task:
    """Работа по продукту, связанная с разработчиком и релизом."""

    def __init__(
        self,
        task_id: int,
        title: str,
        developer: Developer,
        product: Product,
        release: Release | None = None,
        status: str = "todo",
    ) -> None:
        """Создать объект задачи со ссылками на связанные объекты."""
        self.id = task_id
        self.title = title
        self.developer = developer
        self.product = product
        self.release = release
        self._status = status

    @property
    def status(self) -> str:
        """Вернуть текущий статус задачи."""
        return self._status

    @property
    def is_open(self) -> bool:
        """Проверить, что задача ещё не закрыта."""
        return self._status in {"todo", "in_progress"}

    @staticmethod
    def validate_status(status: str) -> bool:
        """Проверить, что статус задачи допустим."""
        return status in VALID_TASK_STATUSES

    @classmethod
    def from_data(
        cls,
        data: dict,
        developer: Developer,
        product: Product,
        release: Release | None,
    ) -> Task:
        """Создать задачу из словаря JSON и связанных объектов."""
        return cls(
            int(data["id"]),
            str(data["title"]),
            developer,
            product,
            release,
            str(data.get("status", "todo")),
        )

    def set_status(self, status: str) -> None:
        """Изменить статус этой задачи."""
        if not Task.validate_status(status):
            raise ValueError("Неизвестный статус задачи")
        self._status = status

    def to_data(self) -> dict[str, Any]:
        """Преобразовать задачу в данные JSON (объекты → id)."""
        release_id = None
        if self.release is not None:
            release_id = self.release.id
        return {
            "id": self.id,
            "title": self.title,
            "developer_id": self.developer.id,
            "product_id": self.product.id,
            "release_id": release_id,
            "status": self._status,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление задачи."""
        if self.release is None:
            release_text = "без релиза"
        else:
            release_text = f"релиз #{self.release.id}"
        return (
            f"[{self.id}] {self.title} — {self.status}; "
            f"{self.developer.name}; {self.product.name}; {release_text}"
        )


def _next_task_id(tasks: list[Task]) -> int:
    """Вернуть следующий идентификатор задачи."""
    if not tasks:
        return 1
    return max(item.id for item in tasks) + 1


def add_task(
    tasks: list[Task],
    title: str,
    developer: Developer,
    product: Product,
    release: Release | None = None,
) -> Task:
    """Создать задачу, добавить в коллекцию и вернуть объект."""
    if not title.strip():
        raise ValueError("Название задачи не может быть пустым")
    item = Task(
        _next_task_id(tasks),
        title.strip(),
        developer,
        product,
        release,
    )
    tasks.append(item)
    return item


def find_task(tasks: list[Task], task_id: int) -> Task | None:
    """Найти задачу по идентификатору."""
    for item in tasks:
        if item.id == task_id:
            return item
    return None


def find_tasks_by_title(tasks: list[Task], query: str) -> list[Task]:
    """Найти задачи по подстроке названия."""
    needle = query.strip().lower()
    found: list[Task] = []
    for item in tasks:
        if needle in item.title.lower():
            found.append(item)
    return found


def filter_tasks_by_developer(tasks: list[Task], developer: Developer):
    """Вернуть генератор задач выбранного разработчика."""
    return (item for item in tasks if item.developer.id == developer.id)


def sort_tasks(tasks: list[Task]) -> list[Task]:
    """Отсортировать задачи по статусу и названию."""
    order = {"todo": 0, "in_progress": 1, "done": 2}
    return sorted(
        tasks,
        key=lambda item: (
            order.get(item.status, 9),
            item.title.lower(),
        ),
    )


def set_task_status(
    tasks: list[Task],
    task_id: int,
    status: str,
) -> Task:
    """Найти задачу и изменить её статус методом объекта."""
    item = find_task(tasks, task_id)
    if item is None:
        raise KeyError("Задача не найдена")
    item.set_status(status)
    return item


def show_tasks(tasks: list[Task]) -> None:
    """Вывести список задач."""
    if not tasks:
        print("Задачи ещё не добавлены.")
        return
    print("Задачи:")
    for item in sort_tasks(tasks):
        print(f"  {item}")
