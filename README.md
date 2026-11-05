# Система управления релизами

Приложение для учёта продуктов, релизов, команды и задач.
Консольная объектная модель (ПР3) дополнена веб-интерфейсом на Django
(ПР5), шаблонами (ПР6), SQLite (ПР7) и Django ORM (ПР9).

## Используемые технологии

- Python 3, Django 5.2, Django ORM, SQLite;
- HTML5 / CSS3 / JavaScript / шаблоны Django;
- pytest + pytest-django, flake8.

## Структура приложений

| Приложение | Модель | Назначение |
|---|---|---|
| `homepage` | — | главная страница, страница 404 |
| `products` | `Product` | продукты |
| `developers` | `Developer` | участники команды |
| `releases` | `Release` | релизы |
| `tasks` | `Task` | задачи разработчиков |

Классы ПР3 (`models/`) сохранены: правила публикации
`can_publish_release`, `get_release_status`, `classify_version`
используются свойствами модели `Release`.

## Модели и связи (ПР9)

- `Product`: `name`.
- `Developer`: `name`, `role`.
- `Release`: `product` → `Product` (`PROTECT`, `related_name="releases"`),
  `version`, `environment` (TextChoices test/staging/production),
  `tests_passed`, `is_hotfix`, `approvals_count`, `required_approvals`,
  `release_date`, `status`. Уникальная пара `product + version`.
- `Task`: `developer` → `Developer`, `product` → `Product`,
  `release` → `Release` (`SET_NULL`, необязательно), `status`.

Миграции `0001_initial` всех приложений хранятся в репозитории.

## Перенос данных из базы ПР7

Источник — `data/releases.sqlite` (создаётся из JSON), цель — `db.sqlite3`.

```bash
python -m db.import_json            # JSON → data/releases.sqlite (ПР7)
python db/inspect_source_db.py      # таблицы, столбцы, число записей
python manage.py migrate
python db/import_sqlite_to_orm.py   # SQLite ПР7 → модели Django
```

Перенос выполняется в `transaction.atomic()` через
`update_or_create(pk=...)`: идентификаторы и связи сохраняются, повторный
запуск не создаёт дублей.

## Страницы

- `/` — сводка (`count()` по моделям);
- `/products/` — продукты с числом релизов (`annotate(Count)`);
- `/products/<id>/` — карточка продукта (`get_object_or_404`);
- `/products/available/?date=` — продукты без активного релиза на дату
  (`values_list` + `exclude(pk__in=...)`);
- `/releases/` — активные релизы: фильтры `date`, `product`, `developer`,
  `environment`, сортировка `sort` (белый список), пагинация по 5
  (`Paginator`, `{% querystring %}`);
- `/releases/<id>/` — карточка релиза и его задачи (`select_related`);
- `/releases/ready/` — готовые к публикации (`Q`, `F`);
- `/releases/statistics/` — релизы по продуктам (`annotate`, порог `?min=`).

Поля выводятся HTML-элементами по типу поля модели (подпись
`data-field-type`): `DateField` → `<time>` / `input type="date"`,
`BooleanField` → чекбокс, счётчики согласований → `<meter>`,
`ForeignKey` и choices → `<select>`, идентификаторы → `<data>`.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python -m db.import_json
python db/import_sqlite_to_orm.py
python manage.py runserver
```

Открыть: http://127.0.0.1:8000/

Консоль (ПР3): `python main.py`

## Проверки

```bash
python manage.py check
python manage.py showmigrations
pytest -v
flake8 . --extend-exclude=venv
```

## План развития

- административная панель Django;
- формы создания и редактирования релизов;
- аутентификация пользователей;
- REST API и CI/CD.
