"""Тесты функций работы с релизами."""

from datetime import date

from releases import (
    can_publish_release,
    cancel_release,
    classify_version,
    create_release,
    get_release_status,
    is_release_publishable,
    publish_release,
)


def test_get_release_status():
    assert get_release_status(True, 2, 2) == "готов к публикации"
    assert get_release_status(False, 2, 2) == (
        "заблокирован: тесты не пройдены"
    )


def test_can_publish_release():
    assert can_publish_release("production", True, 2, 2, False)
    assert not can_publish_release("production", True, 1, 2, False)


def test_classify_version():
    assert classify_version("2.1.0") == "minor-релиз"
    assert classify_version("0.9.1") == "предрелизная версия"


def test_create_and_publish_release():
    releases = []
    item = create_release(
        releases,
        1,
        "2.1.0",
        "production",
        True,
        2,
        2,
        False,
        date(2026, 9, 20),
    )
    assert len(releases) == 1
    assert is_release_publishable(item)
    publish_release(releases, item["id"])
    assert item["status"] == "published"


def test_cancel_release():
    releases = []
    item = create_release(
        releases,
        1,
        "1.0.1",
        "test",
        True,
        0,
        1,
        False,
        date(2026, 9, 21),
    )
    cancel_release(releases, item["id"])
    assert item["status"] == "cancelled"
    assert not is_release_publishable(item)
