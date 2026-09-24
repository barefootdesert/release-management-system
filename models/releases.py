"""Класс Release и функции работы с коллекцией релизов.

Функции get_release_status, can_publish_release, classify_version
и describe_release_deadline перенесены из сценария ПР1 и используются
методами объекта Release.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from .products import Product

ENVIRONMENTS = ("test", "staging", "production")
VALID_ENVIRONMENTS = set(ENVIRONMENTS)


def get_release_status(
    tests_passed: bool,
    approvals_count: int,
    required_approvals: int,
) -> str:
    """Вернуть текстовый статус релиза по тестам и согласованиям."""
    if not tests_passed:
        return "заблокирован: тесты не пройдены"
    if approvals_count < required_approvals:
        return "ожидает согласования"
    return "готов к публикации"


def can_publish_release(
    environment: str,
    tests_passed: bool,
    approvals_count: int,
    required_approvals: int,
    is_hotfix: bool,
) -> bool:
    """Проверить, допускается ли публикация в указанное окружение."""
    if not tests_passed:
        return False

    if environment == "test":
        return True

    if environment == "staging":
        return approvals_count >= 1 or is_hotfix

    if environment == "production":
        return approvals_count >= required_approvals

    return False


def classify_version(version: str) -> str:
    """Определить тип версии по номерам major и patch."""
    first_dot_index = version.find(".")
    last_dot_index = version.rfind(".")
    major = int(version[:first_dot_index])
    patch = int(version[last_dot_index + 1 :])

    if major == 0:
        return "предрелизная версия"
    if patch == 0:
        return "minor-релиз"
    return "patch-релиз"


def describe_release_deadline(release_date: date, today: date) -> str:
    """Описать, сколько дней осталось до запланированной даты релиза."""
    days_left = (release_date - today).days

    if days_left < 0:
        return "дата релиза уже прошла"
    if days_left == 0:
        return "релиз запланирован на сегодня"
    return f"до релиза осталось {days_left} дн."


class Release:
    """Конкретная версия продукта, готовящаяся к публикации."""

    def __init__(
        self,
        release_id: int,
        product: Product,
        version: str,
        environment: str,
        tests_passed: bool,
        approvals_count: int,
        required_approvals: int,
        is_hotfix: bool,
        release_date: date,
        status: str = "planned",
    ) -> None:
        """Создать объект релиза, связанный с продуктом."""
        self.id = release_id
        self.product = product
        self.version = version
        self.environment = environment
        self.tests_passed = tests_passed
        self.approvals_count = approvals_count
        self.required_approvals = required_approvals
        self.is_hotfix = is_hotfix
        self.release_date = release_date
        self._status = status

    @property
    def status(self) -> str:
        """Вернуть текущее состояние релиза."""
        return self._status

    @property
    def is_cancelled(self) -> bool:
        """Проверить, отменён ли релиз."""
        return self._status == "cancelled"

    @property
    def is_active(self) -> bool:
        """Проверить, блокирует ли релиз удаление продукта."""
        return self._status in {"planned", "published"}

    @property
    def readiness(self) -> str:
        """Вернуть текстовую готовность по правилам ПР1."""
        return get_release_status(
            self.tests_passed,
            self.approvals_count,
            self.required_approvals,
        )

    @staticmethod
    def validate_environment(environment: str) -> bool:
        """Проверить, что окружение допустимо."""
        return environment in VALID_ENVIRONMENTS

    @classmethod
    def from_data(cls, data: dict, product: Product) -> Release:
        """Создать релиз из словаря JSON и объекта продукта."""
        return cls(
            int(data["id"]),
            product,
            str(data["version"]),
            str(data["environment"]),
            bool(data["tests_passed"]),
            int(data["approvals_count"]),
            int(data["required_approvals"]),
            bool(data["is_hotfix"]),
            date.fromisoformat(str(data["release_date"])),
            str(data.get("status", "planned")),
        )

    def can_publish(self) -> bool:
        """Проверить, можно ли публиковать этот релиз."""
        if self._status != "planned":
            return False
        return can_publish_release(
            self.environment,
            self.tests_passed,
            self.approvals_count,
            self.required_approvals,
            self.is_hotfix,
        )

    def classify(self) -> str:
        """Определить тип версии текущего релиза."""
        return classify_version(self.version)

    def describe_deadline(self, today: date | None = None) -> str:
        """Описать срок до даты выпуска."""
        if today is None:
            today = date.today()
        return describe_release_deadline(self.release_date, today)

    def publish(self) -> None:
        """Опубликовать релиз, изменив его состояние."""
        if self._status == "cancelled":
            raise ValueError("Нельзя публиковать отменённый релиз")
        if self._status == "published":
            raise ValueError("Релиз уже опубликован")
        if not self.can_publish():
            raise ValueError("Релиз не готов к публикации")
        self._status = "published"

    def cancel(self) -> None:
        """Отменить запланированный релиз, не удаляя объект."""
        if self._status == "published":
            raise ValueError("Опубликованный релиз нельзя отменить")
        if self._status == "cancelled":
            raise ValueError("Релиз уже отменён")
        self._status = "cancelled"

    def to_data(self) -> dict[str, Any]:
        """Преобразовать релиз в данные JSON (product → product_id)."""
        return {
            "id": self.id,
            "product_id": self.product.id,
            "version": self.version,
            "environment": self.environment,
            "tests_passed": self.tests_passed,
            "approvals_count": self.approvals_count,
            "required_approvals": self.required_approvals,
            "is_hotfix": self.is_hotfix,
            "release_date": self.release_date.isoformat(),
            "status": self._status,
        }

    def __str__(self) -> str:
        """Вернуть карточку релиза для консоли."""
        kind = "hotfix" if self.is_hotfix else "обычный"
        return (
            f"[{self.id}] {self.product.name} {self.version} "
            f"({self.classify()}, {kind}); "
            f"окружение: {self.environment}; "
            f"состояние: {self.status}; "
            f"готовность: {self.readiness}; "
            f"дата: {self.release_date}; {self.describe_deadline()}"
        )


def _next_release_id(releases: list[Release]) -> int:
    """Вернуть следующий идентификатор релиза."""
    if not releases:
        return 1
    return max(item.id for item in releases) + 1


def create_release(
    releases: list[Release],
    product: Product,
    version: str,
    environment: str,
    tests_passed: bool,
    approvals_count: int,
    required_approvals: int,
    is_hotfix: bool,
    release_date: date,
) -> Release:
    """Создать объект Release, добавить в коллекцию и вернуть его."""
    if not Release.validate_environment(environment):
        raise ValueError("Неизвестное окружение")
    if required_approvals < 0 or approvals_count < 0:
        raise ValueError("Число согласований не может быть отрицательным")

    item = Release(
        _next_release_id(releases),
        product,
        version,
        environment,
        tests_passed,
        approvals_count,
        required_approvals,
        is_hotfix,
        release_date,
    )
    releases.append(item)
    return item


def find_release(
    releases: list[Release],
    release_id: int,
) -> Release | None:
    """Найти релиз по идентификатору."""
    for item in releases:
        if item.id == release_id:
            return item
    return None


def find_releases_by_version(
    releases: list[Release],
    query: str,
) -> list[Release]:
    """Найти релизы по подстроке версии."""
    needle = query.strip().lower()
    found: list[Release] = []
    for item in releases:
        if needle in item.version.lower():
            found.append(item)
    return found


def is_release_publishable(item: Release) -> bool:
    """Проверить, можно ли публиковать конкретный релиз."""
    return item.can_publish()


def publish_release(releases: list[Release], release_id: int) -> Release:
    """Найти релиз и вызвать его метод publish()."""
    item = find_release(releases, release_id)
    if item is None:
        raise KeyError("Релиз не найден")
    item.publish()
    return item


def cancel_release(releases: list[Release], release_id: int) -> Release:
    """Найти релиз и вызвать его метод cancel()."""
    item = find_release(releases, release_id)
    if item is None:
        raise KeyError("Релиз не найден")
    item.cancel()
    return item


def filter_releases_by_environment(
    releases: list[Release],
    environment: str,
):
    """Вернуть генератор релизов выбранного окружения."""
    return (item for item in releases if item.environment == environment)


def sort_releases(releases: list[Release]) -> list[Release]:
    """Отсортировать релизы по дате выпуска."""
    return sorted(releases, key=lambda item: item.release_date)


def collect_statistics(releases: list[Release]) -> dict[str, int]:
    """Посчитать количество релизов по статусам и готовности."""
    stats = {
        "всего": len(releases),
        "запланировано": 0,
        "опубликовано": 0,
        "отменено": 0,
        "готовы к публикации": 0,
    }
    for item in releases:
        if item.status == "planned":
            stats["запланировано"] += 1
        elif item.status == "published":
            stats["опубликовано"] += 1
        elif item.status == "cancelled":
            stats["отменено"] += 1
        if item.can_publish():
            stats["готовы к публикации"] += 1
    return stats


def show_releases(releases: list[Release]) -> None:
    """Вывести список релизов."""
    if not releases:
        print("Релизы ещё не добавлены.")
        return
    print("Релизы:")
    for item in sort_releases(releases):
        print(f"  {item}")
