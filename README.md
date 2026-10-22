# Система управления релизами

Приложение для учёта продуктов и управления релизами.
Консольная объектная модель (ПР3) дополнена веб-интерфейсом на Django
(ПР5), шаблонами (ПР6) и SQLite (ПР7).

## Используемые технологии

- Python 3;
- Django 5.2;
- HTML / CSS / Bootstrap 5.3 / шаблоны Django;
- SQLite + библиотека `sqlite3`;
- pytest, flake8.

## Страницы веб-интерфейса

- `/` — главная;
- `/products/` — список продуктов;
- `/products/<id>/` — карточка продукта;
- `/products/available/` — продукты без активного релиза на дату (SQL);
- `/releases/` — список релизов;
- `/releases/<id>/` — карточка релиза;
- `/releases/statistics/` — статистика по SQL.

## Шаблоны (ПР6)

- базовый шаблон `templates/base.html` (`extends` / `block`);
- навигация `templates/includes/navigation.html` (`{% include %}`, `{% url %}`);
- карточки и статусы через `{% include %}`;
- фильтры `|length`, `|default`, `|date`;
- статика: `homepage/static/homepage/{css,js,img}`.

## База данных SQLite (ПР7)

Файл: `data/releases.sqlite`.

Таблицы: `products`, `developers`, `releases`, `tasks`
(первичные и внешние ключи в `sql/schema.sql`).

Импорт из JSON:

```bash
python -m db.import_json
```

Запросы: `sql/queries.sql`. Подключение: `db/database.py`.

## Запуск

```bash
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python -m db.import_json
python manage.py runserver
```

Открыть: http://127.0.0.1:8000/

Консоль (ПР3): `python main.py`

## Тесты

```bash
pytest -v --ignore=tests/test_api.py
flake8 .
```

## План развития

- Django ORM и миграции моделей;
- формы создания/редактирования;
- аутентификация пользователей;
- REST API и CI/CD.
