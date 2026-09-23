"""Функции для работы с разработчиками."""


def add_developer(
    developers: dict[int, dict],
    name: str,
    role: str,
) -> int:
    """Добавить разработчика и вернуть его id."""
    developer_id = 1
    if developers:
        developer_id = max(developers) + 1
    developers[developer_id] = {
        "id": developer_id,
        "name": name,
        "role": role,
    }
    return developer_id


def find_developer(
    developers: dict[int, dict],
    query: str,
) -> dict[int, dict]:
    """Найти разработчиков по подстроке имени или роли."""
    needle = query.strip().lower()
    found: dict[int, dict] = {}
    for developer_id, developer in developers.items():
        name = str(developer["name"]).lower()
        role = str(developer["role"]).lower()
        if needle in name or needle in role:
            found[developer_id] = developer
    return found


def get_developer(
    developers: dict[int, dict],
    developer_id: int,
) -> dict | None:
    """Вернуть разработчика по идентификатору или None."""
    return developers.get(developer_id)


def sort_developers(developers: dict[int, dict]) -> list[dict]:
    """Вернуть разработчиков, упорядоченных по имени."""
    return sorted(
        developers.values(),
        key=lambda item: str(item["name"]).lower(),
    )


def has_open_tasks(tasks: list[dict], developer_id: int) -> bool:
    """Проверить, есть ли у разработчика незакрытые задачи."""
    for item in tasks:
        same_dev = item["developer_id"] == developer_id
        open_status = item["status"] in {"todo", "in_progress"}
        if same_dev and open_status:
            return True
    return False


def delete_developer(
    developers: dict[int, dict],
    developer_id: int,
    tasks: list[dict],
) -> dict:
    """Удалить разработчика, если нет открытых задач."""
    if developer_id not in developers:
        raise KeyError("Разработчик не найден")
    if has_open_tasks(tasks, developer_id):
        raise ValueError("Сначала закройте задачи этого разработчика")
    return developers.pop(developer_id)
