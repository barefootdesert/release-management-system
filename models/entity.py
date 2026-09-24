"""Базовый класс именованной сущности."""

from typing import Any


class Entity:
    """Общий предок для объектов с идентификатором и названием.

    Product и Developer являются такими сущностями, поэтому
    наследуют id, name и строковое представление.
    """

    def __init__(self, entity_id: int, name: str) -> None:
        """Сохранить идентификатор и название объекта."""
        self.id = entity_id
        self.name = name

    def matches(self, query: str) -> bool:
        """Проверить, содержит ли название подстроку запроса."""
        return query.strip().lower() in self.name.lower()

    def to_data(self) -> dict[str, Any]:
        """Вернуть данные объекта для сохранения в JSON."""
        return {"id": self.id, "name": self.name}

    def __str__(self) -> str:
        """Вернуть краткое строковое представление сущности."""
        return f"{self.name} (#{self.id})"
