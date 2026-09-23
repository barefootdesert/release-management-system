"""Вспомогательные функции ввода с обработкой ошибок."""

from datetime import date, datetime

from releases import ENVIRONMENTS


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Введите целое число.")


def input_date(prompt: str) -> date:
    """Запросить дату в формате ДД.ММ.ГГГГ или ГГГГ-ММ-ДД."""
    while True:
        raw = input(prompt).strip()
        for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        print("Некорректная дата. Пример: 20.09.2026")


def input_bool(prompt: str) -> bool:
    """Запросить ответ да/нет и вернуть логическое значение."""
    while True:
        raw = input(f"{prompt} (да/нет): ").strip().lower()
        if raw in {"да", "д", "yes", "y", "1"}:
            return True
        if raw in {"нет", "н", "no", "n", "0"}:
            return False
        print("Введите да или нет.")


def input_environment(prompt: str) -> str:
    """Запросить одно из допустимых окружений."""
    allowed = "/".join(ENVIRONMENTS)
    while True:
        raw = input(f"{prompt} ({allowed}): ").strip().lower()
        if raw in ENVIRONMENTS:
            return raw
        print(f"Допустимые значения: {allowed}")


def input_optional_int(prompt: str) -> int | None:
    """Запросить число; пустая строка или 0 означает отсутствие."""
    while True:
        raw = input(prompt).strip()
        if raw in {"", "0"}:
            return None
        try:
            return int(raw)
        except ValueError:
            print("Введите целое число или 0, если не нужно.")
