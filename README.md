# Система управления релизами

Приложение для учёта продуктов и управления релизами.
Консольная объектная модель (ПР3) дополнена веб-интерфейсом на Django
(ПР5), шаблонами (ПР6) и SQLite (ПР7).

## Используемые технологии

- Python 3;
- Django 5.2;
- HTML5 / CSS3 / JavaScript / шаблоны Django;
- SQLite + библиотека `sqlite3`;
- pytest, flake8.

## Страницы веб-интерфейса

- `/` — главная, сводка `COUNT(*)` из SQLite;
- `/products/` — список продуктов (SELECT + GROUP BY);
- `/products/<id>/` — карточка продукта;
- `/products/available/` — продукты без активного релиза на дату;
- `/releases/` — активные релизы (JOIN);
- `/releases/<id>/` — карточка релиза (JOIN);
- `/releases/ready/` — релизы, готовые к публикации;
- `/releases/statistics/` — статистика (GROUP BY, HAVING).

## HTML и типы SQLite (ПР7)

Поля таблиц выводятся элементами, которые соответствуют типу колонки:

| Тип SQLite | HTML |
|---|---|
| INTEGER (id, COUNT) | `<data value="...">` |
| TEXT (name, version, status) | заголовок, ячейка, `<span>` |
| TEXT даты YYYY-MM-DD | `<time datetime="...">`, `<input type="date">` |
| INTEGER 0/1 (tests_passed, is_hotfix) | `<input type="checkbox" disabled>` |
| INTEGER счётчики согласований | `<meter min max value>` |
| порог HAVING | `<input type="number">` |

Тип колонки дублируется атрибутом `data-sql-type` и подписью в шапке таблицы.

## Шаблоны (ПР6)

- базовый шаблон `templates/base.html` (`extends` / `block`);
- навигация `templates/includes/navigation.html` (`{% include %}`, `{% url %}`);
- карточки и статусы через `{% include %}`;
- фильтры `|length`, `|default`;
- статика: `homepage/static/homepage/{css,js,img}`.

## База данных SQLite (ПР7)

Файл: `data/releases.sqlite`.

Таблицы: `products`, `developers`, `releases`, `tasks`
(первичные и внешние ключи в `sql/schema.sql`).

Импорт из JSON:

```bash
python -m db.import_json
```

Запросы: `sql/queries.sql`. Подключение: `db/database.py`
(`PRAGMA foreign_keys = ON`, `sqlite3.Row`).

Значения в SQL передаются параметрами `?`, без f-строк.

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

## Текущий этап разработки

На ПР7 данные перенесены из JSON в SQLite:

- создана база `data/releases.sqlite`;
- таблицы созданы скриптом `sql/schema.sql`;
- данные перенесены скриптом `db/import_json.py`;
- SQL-запросы сохранены в `sql/queries.sql`;
- Django-представления получают данные из SQLite;
- страницы списков, поиска свободных продуктов, готовых релизов
  и статистики работают с базой.

JSON-файлы и классы ПР3 сохранены. Django ORM не используется.

## План развития

- Django ORM и миграции моделей;
- формы создания/редактирования;
- аутентификация пользователей;
- REST API и CI/CD.
