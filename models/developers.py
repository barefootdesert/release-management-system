"""Класс Developer и функции работы с коллекцией разработчиков."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .entity import Entity

if TYPE_CHECKING:
    from .tasks import Task


class Developer(Entity):
    """Участник команды, которому назначают задачи."""

    def __init__(self, developer_id: int, name: str, role: str) -> None:
        """Создать объект разработчика."""
        super().__init__(developer_id, name)
        self.role = role

    def matches(self, query: str) -> bool:
        """Проверить совпадение по имени или роли."""
        needle = query.strip().lower()
        return needle in self.name.lower() or needle in self.role.lower()

    @classmethod
    def from_data(cls, data: dict) -> Developer:
        """Создать разработчика из словаря JSON."""
        return cls(
            int(data["id"]),
            str(data["name"]),
            str(data["role"]),
        )

    def to_data(self) -> dict[str, Any]:
        """Вернуть данные разработчика для JSON."""
        payload = super().to_data()
        payload["role"] = self.role
        return payload

    def __str__(self) -> str:
        """Вернуть строковое представление разработчика."""
        return f"{self.id}. {self.name} ({self.role})"


def add_developer(
    developers: list[Developer],
    name: str,
    role: str,
) -> Developer:
    """Создать разработчика, добавить в коллекцию и вернуть объект."""
    if not name.strip() or not role.strip():
        raise ValueError("Имя и роль не могут быть пустыми")
    developer_id = 1
    if developers:
        developer_id = max(item.id for item in developers) + 1
    developer = Developer(developer_id, name.strip(), role.strip())
    developers.append(developer)
    return developer


def find_developer(
    developers: list[Developer],
    query: str,
) -> list[Developer]:
    """Найти разработчиков по подстроке имени или роли."""
    return [item for item in developers if item.matches(query)]


def get_developer(
    developers: list[Developer],
    developer_id: int,
) -> Developer | None:
    """Вернуть разработчика по идентификатору или None."""
    for item in developers:
        if item.id == developer_id:
            return item
    return None


def sort_developers(developers: list[Developer]) -> list[Developer]:
    """Вернуть разработчиков, упорядоченных по имени."""
    return sorted(developers, key=lambda item: item.name.lower())


def has_open_tasks(tasks: list[Task], developer: Developer) -> bool:
    """Проверить, есть ли у разработчика незакрытые задачи."""
    for item in tasks:
        if item.developer.id == developer.id and item.is_open:
            return True
    return False


def delete_developer(
    developers: list[Developer],
    developer_id: int,
    tasks: list[Task],
) -> Developer:
    """Удалить разработчика, если нет открытых задач."""
    developer = get_developer(developers, developer_id)
    if developer is None:
        raise KeyError("Разработчик не найден")
    if has_open_tasks(tasks, developer):
        raise ValueError("Сначала закройте задачи этого разработчика")
    developers.remove(developer)
    return developer


def show_developers(developers: list[Developer]) -> None:
    """Вывести список разработчиков."""
    if not developers:
        print("Разработчики ещё не добавлены.")
        return
    print("Разработчики:")
    for item in sort_developers(developers):
        print(f"  {item}")
