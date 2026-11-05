# Система управления релизами

Приложение для учёта продуктов, релизов, команды и задач.
Консольная объектная модель (ПР3) дополнена веб-интерфейсом на Django
(ПР5), шаблонами (ПР6), SQLite (ПР7), Django ORM (ПР9)
и административной панелью (ПР10).

## Используемые технологии

- Python 3, Django 5.2, Django ORM, SQLite;
- HTML5 / CSS3 / JavaScript / шаблоны Django;
- Unidecode (slug из кириллицы), django-debug-toolbar;
- pytest + pytest-django, flake8.

## Структура приложений

| Приложение | Модель | Назначение |
|---|---|---|
| `homepage` | — | главная страница, страница 404 |
| `products` | `Product` | продукты, slug, контекстный процессор |
| `developers` | `Developer` | участники команды |
| `releases` | `Release` | релизы, менеджер `ReleaseQuerySet` |
| `tasks` | `Task` | задачи разработчиков |

Классы ПР3 (`models/`) сохранены: правила публикации
`can_publish_release`, `get_release_status`, `classify_version`
используются свойствами модели `Release`.

## Модели и связи (ПР9–ПР10)

- `Product`: `name`, `slug` (уникальный, создаётся из названия через
  Unidecode, не меняется при переименовании).
- `Developer`: `name`, `role`.
- `Release`: `product` → `Product` (`PROTECT`, `related_name="releases"`),
  `version`, `environment` (TextChoices test/staging/production),
  `tests_passed`, `is_hotfix`, `approvals_count`, `required_approvals`,
  `release_date`, `status` (TextChoices `ACTIVE` / `CANCELLED` /
  `COMPLETED`), `is_approved` — `GeneratedField`
  (`approvals_count >= required_approvals`, хранится в БД).
  Уникальная пара `product + version`.
- `Task`: `developer` → `Developer`, `product` → `Product`,
  `release` → `Release` (`SET_NULL`, необязательно), `status`.

Менеджер `Release.objects` (`Manager.from_queryset(ReleaseQuerySet)`):
`active()`, `cancelled()`, `completed()`, `for_date(date)`,
`with_product()`, `ready_to_publish()`.

Занятость продукта на дату определяет только активный релиз:
отменённые и опубликованные релизы продукт не блокируют.

## Миграции

```text
products   0001_initial → 0002 slug (blank) → 0003 заполнение slug
           (RunPython) → 0004 slug unique
developers 0001_initial → 0002 verbose_name
releases   0001_initial → 0002 перевод статусов (RunPython:
           planned→active, published→completed) → 0003 TextChoices,
           GeneratedField is_approved, verbose_name
tasks      0001_initial → 0002 verbose_name
```

Миграции хранятся в репозитории. Проверка, что модели и миграции
совпадают: `python manage.py makemigrations --check --dry-run`.

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
- `/products/<slug>/` — карточка продукта по slug (`get_absolute_url`);
- `/products/available/?date=` — продукты без активного релиза на дату;
- `/releases/` — активные релизы: фильтры `date`, `product`, `developer`,
  `environment`, сортировка `sort` (белый список), пагинация по 5
  (`Paginator`, `{% querystring %}`);
- `/releases/<id>/` — карточка релиза и его задачи;
- `/releases/ready/` — `Release.objects.ready_to_publish()`;
- `/releases/statistics/` — статистика по статусам (`aggregate`) и по
  продуктам (`annotate`, порог `?min=`).

Поля выводятся HTML-элементами по типу поля модели (подпись
`data-field-type`): `DateField` → `<time>` / `input type="date"`,
`BooleanField` и `GeneratedField` → чекбокс, счётчики согласований →
`<meter>`, `ForeignKey` и choices → `<select>`, идентификаторы → `<data>`.

Контекстный процессор `products.context_processors.release_context`
передаёт во все шаблоны `site_name`, `products_total`,
`active_releases_total` (выводятся в шапке и навигации).

## Административная панель (ПР10)

Адрес: http://127.0.0.1:8000/admin/

```bash
python manage.py createsuperuser
```

- `ProductAdmin`: `list_display` (число релизов, ссылка «на сайте»
  через `format_html`), поиск, `readonly_fields=("slug",)`,
  inline релизов, `view_on_site`;
- `ReleaseAdmin`: `list_display_links`, `list_editable=("status",)`,
  `list_filter`, `search_fields` (в т. ч. `tasks__developer__name`),
  `date_hierarchy`, `list_select_related`, `autocomplete_fields`,
  `fieldsets`, inline задач, действия «опубликовать / отменить /
  вернуть в запланированные»;
- `DeveloperAdmin`: `list_editable=("role",)`, inline задач;
- `TaskAdmin`: фильтры, поиск, `autocomplete_fields`.

Названия приложений, моделей и полей локализованы
(`AppConfig.verbose_name`, `verbose_name`, `help_text`).

Поиск в SQLite не учитывает регистр только для латиницы:
«Плат» находит «Платёжный шлюз», «плат» — нет.

## Django Debug Toolbar

Подключается при `DEBUG = True` (кроме запуска тестов):
приложение `debug_toolbar`, middleware сразу после
`SecurityMiddleware`, `INTERNAL_IPS = ["127.0.0.1"]`, маршрут
`__debug__/`. Панель SQL показывает, что список релизов выполняется
одним запросом с `INNER JOIN products_product` без N+1.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python -m db.import_json
python db/import_sqlite_to_orm.py
python manage.py createsuperuser
python manage.py runserver
```

Открыть: http://127.0.0.1:8000/

Консоль (ПР3): `python main.py`

## Проверки

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations
pytest -v
flake8 . --extend-exclude=venv
```

Тесты Django: `releases/tests.py` (ORM-представления, фильтры,
сортировка, 404), `products/tests.py` (менеджер, `GeneratedField`, slug,
доступность по статусам, статистика, контекстный процессор, админка).

## План развития

- формы создания и редактирования релизов на сайте;
- аутентификация и права пользователей;
- REST API и CI/CD.
