"""Функции для работы с задачами релиза."""

TASK_STATUSES = ("todo", "in_progress", "done")
VALID_TASK_STATUSES = set(TASK_STATUSES)


def _next_task_id(tasks: list[dict]) -> int:
    """Вернуть следующий идентификатор задачи."""
    if not tasks:
        return 1
    return max(item["id"] for item in tasks) + 1


def add_task(
    tasks: list[dict],
    title: str,
    developer_id: int,
    product_id: int,
    release_id: int | None = None,
) -> dict:
    """Добавить задачу в список tasks."""
    if not title.strip():
        raise ValueError("Название задачи не может быть пустым")
    item = {
        "id": _next_task_id(tasks),
        "title": title.strip(),
        "developer_id": developer_id,
        "product_id": product_id,
        "release_id": release_id,
        "status": "todo",
    }
    tasks.append(item)
    return item


def find_task(tasks: list[dict], task_id: int) -> dict | None:
    """Найти задачу по идентификатору."""
    for item in tasks:
        if item["id"] == task_id:
            return item
    return None


def find_tasks_by_title(tasks: list[dict], query: str) -> list[dict]:
    """Найти задачи по подстроке названия."""
    needle = query.strip().lower()
    found: list[dict] = []
    for item in tasks:
        if needle in str(item["title"]).lower():
            found.append(item)
    return found


def filter_tasks_by_developer(tasks: list[dict], developer_id: int):
    """Вернуть генератор задач выбранного разработчика."""
    return (item for item in tasks if item["developer_id"] == developer_id)


def sort_tasks(tasks: list[dict]) -> list[dict]:
    """Отсортировать задачи по статусу и названию."""
    order = {"todo": 0, "in_progress": 1, "done": 2}
    return sorted(
        tasks,
        key=lambda item: (
            order.get(item["status"], 9),
            str(item["title"]).lower(),
        ),
    )


def set_task_status(tasks: list[dict], task_id: int, status: str) -> dict:
    """Изменить статус задачи."""
    if status not in VALID_TASK_STATUSES:
        raise ValueError("Неизвестный статус задачи")
    item = find_task(tasks, task_id)
    if item is None:
        raise KeyError("Задача не найдена")
    item["status"] = status
    return item
