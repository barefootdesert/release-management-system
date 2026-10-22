"""Подключение к SQLite-базе индивидуального проекта."""

from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "releases.sqlite"


def get_connection() -> sqlite3.Connection:
    """Открыть соединение с включёнными внешними ключами."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
