"""Функции для работы с релизами.

Функции get_release_status, can_publish_release, classify_version
и describe_release_deadline перенесены из сценария ПР1.
"""

from datetime import date

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


def _next_release_id(releases: list[dict]) -> int:
    """Вернуть следующий идентификатор релиза."""
    if not releases:
        return 1
    return max(item["id"] for item in releases) + 1


def create_release(
    releases: list[dict],
    product_id: int,
    version: str,
    environment: str,
    tests_passed: bool,
    approvals_count: int,
    required_approvals: int,
    is_hotfix: bool,
    release_date: date,
) -> dict:
    """Создать новый релиз и добавить его в список releases."""
    if environment not in VALID_ENVIRONMENTS:
        raise ValueError("Неизвестное окружение")
    if required_approvals < 0 or approvals_count < 0:
        raise ValueError("Число согласований не может быть отрицательным")

    item = {
        "id": _next_release_id(releases),
        "product_id": product_id,
        "version": version,
        "environment": environment,
        "tests_passed": tests_passed,
        "approvals_count": approvals_count,
        "required_approvals": required_approvals,
        "is_hotfix": is_hotfix,
        "release_date": release_date.isoformat(),
        "status": "planned",
    }
    releases.append(item)
    return item


def find_release(releases: list[dict], release_id: int) -> dict | None:
    """Найти релиз по идентификатору."""
    for item in releases:
        if item["id"] == release_id:
            return item
    return None


def find_releases_by_version(
    releases: list[dict],
    query: str,
) -> list[dict]:
    """Найти релизы по подстроке версии."""
    needle = query.strip().lower()
    found: list[dict] = []
    for item in releases:
        if needle in str(item["version"]).lower():
            found.append(item)
    return found


def is_release_publishable(item: dict) -> bool:
    """Проверить, можно ли публиковать конкретный релиз."""
    if item["status"] != "planned":
        return False
    return can_publish_release(
        item["environment"],
        item["tests_passed"],
        item["approvals_count"],
        item["required_approvals"],
        item["is_hotfix"],
    )


def publish_release(releases: list[dict], release_id: int) -> dict:
    """Опубликовать релиз, если он готов к выкладке."""
    item = find_release(releases, release_id)
    if item is None:
        raise KeyError("Релиз не найден")
    if item["status"] == "cancelled":
        raise ValueError("Нельзя публиковать отменённый релиз")
    if item["status"] == "published":
        raise ValueError("Релиз уже опубликован")
    if not is_release_publishable(item):
        raise ValueError("Релиз не готов к публикации")
    item["status"] = "published"
    return item


def cancel_release(releases: list[dict], release_id: int) -> dict:
    """Отменить запланированный релиз."""
    item = find_release(releases, release_id)
    if item is None:
        raise KeyError("Релиз не найден")
    if item["status"] == "published":
        raise ValueError("Опубликованный релиз нельзя отменить")
    if item["status"] == "cancelled":
        raise ValueError("Релиз уже отменён")
    item["status"] = "cancelled"
    return item


def filter_releases_by_environment(
    releases: list[dict],
    environment: str,
):
    """Вернуть генератор релизов выбранного окружения."""
    return (item for item in releases if item["environment"] == environment)


def sort_releases(releases: list[dict]) -> list[dict]:
    """Отсортировать релизы по дате выпуска."""
    return sorted(
        releases,
        key=lambda item: item["release_date"],
    )


def collect_statistics(releases: list[dict]) -> dict[str, int]:
    """Посчитать количество релизов по статусам и готовности."""
    stats = {
        "всего": len(releases),
        "запланировано": 0,
        "опубликовано": 0,
        "отменено": 0,
        "готовы к публикации": 0,
    }
    for item in releases:
        status = item["status"]
        if status == "planned":
            stats["запланировано"] += 1
        elif status == "published":
            stats["опубликовано"] += 1
        elif status == "cancelled":
            stats["отменено"] += 1
        if is_release_publishable(item):
            stats["готовы к публикации"] += 1
    return stats
