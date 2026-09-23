"""Тесты функций работы с разработчиками и задачами."""

import pytest

from developers import add_developer, delete_developer, find_developer
from tasks import add_task, set_task_status


def test_add_and_find_developer():
    developers = {}
    developer_id = add_developer(developers, "Анна Козлова", "backend")
    assert developer_id == 1
    found = find_developer(developers, "анна")
    assert developer_id in found


def test_add_and_close_task():
    tasks = []
    item = add_task(tasks, "Исправить таймаут", 1, 1, 1)
    assert item["status"] == "todo"
    set_task_status(tasks, item["id"], "done")
    assert item["status"] == "done"


def test_delete_developer_with_open_task():
    developers = {}
    developer_id = add_developer(developers, "Иван Петров", "qa")
    tasks = []
    add_task(tasks, "Проверить релиз", developer_id, 1, None)
    with pytest.raises(ValueError):
        delete_developer(developers, developer_id, tasks)
    assert developer_id in developers
