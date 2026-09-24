"""Точка запуска системы управления релизами."""

from models import Developer, Product, Release, Task
from models.developers import (
    add_developer,
    delete_developer,
    find_developer,
    get_developer,
    show_developers,
)
from models.products import (
    add_product,
    delete_product,
    find_product,
    get_product,
    show_products,
)
from models.releases import (
    ENVIRONMENTS,
    cancel_release,
    collect_statistics,
    create_release,
    filter_releases_by_environment,
    find_release,
    find_releases_by_version,
    publish_release,
    show_releases,
)
from models.tasks import (
    TASK_STATUSES,
    add_task,
    find_tasks_by_title,
    set_task_status,
    show_tasks,
)
from storage import (
    load_developers,
    load_products,
    load_releases,
    load_tasks,
    save_developers,
    save_products,
    save_releases,
    save_tasks,
)
from utils import (
    input_bool,
    input_date,
    input_environment,
    input_int,
    input_optional_int,
)

MENU = """
=== Система управления релизами ===
1. Показать продукты
2. Найти продукт
3. Добавить продукт
4. Удалить продукт
5. Показать релизы
6. Добавить релиз
7. Проверить готовность к публикации
8. Опубликовать релиз
9. Отменить релиз
10. Найти релиз по версии
11. Статистика
12. Показать разработчиков
13. Добавить разработчика
14. Удалить разработчика
15. Показать задачи
16. Добавить задачу
17. Изменить статус задачи
18. Найти разработчика
19. Найти задачу
0. Выход
"""


def action_add_product(products: list[Product]) -> None:
    """Добавить продукт и сохранить данные."""
    name = input("Название продукта: ").strip()
    try:
        product = add_product(products, name)
    except ValueError as error:
        print(error)
        return
    save_products(products)
    print(f"Добавлен продукт #{product.id}.")


def action_find_product(products: list[Product]) -> None:
    """Найти продукты по подстроке названия."""
    query = input("Подстрока названия: ").strip()
    found = find_product(products, query)
    if not found:
        print("Ничего не найдено.")
        return
    show_products(found)


def action_delete_product(
    products: list[Product],
    releases: list[Release],
) -> None:
    """Удалить продукт, если нет активных релизов."""
    if not products:
        print("Продукты ещё не добавлены.")
        return
    show_products(products)
    product_id = input_int("Id продукта для удаления: ")
    try:
        product = delete_product(products, product_id, releases)
    except (KeyError, ValueError) as error:
        print(error)
        return
    save_products(products)
    print(f"Продукт «{product.name}» удалён.")


def create_new_release(
    products: list[Product],
    releases: list[Release],
) -> None:
    """Создать релиз: найти Product и связать его с новым Release."""
    if not products:
        print("Сначала добавьте продукт.")
        return
    show_products(products)
    product = get_product(products, input_int("Id продукта: "))
    if product is None:
        print("Продукт не найден.")
        return
    version = input("Версия (например, 2.1.0): ").strip()
    if version.count(".") != 2:
        print("Ожидается версия вида major.minor.patch.")
        return
    try:
        item = create_release(
            releases,
            product,
            version,
            input_environment("Окружение"),
            input_bool("Тесты пройдены"),
            input_int("Число согласований: "),
            input_int("Нужно согласований: "),
            input_bool("Это hotfix"),
            input_date("Дата релиза: "),
        )
    except ValueError as error:
        print(error)
        return
    save_releases(releases)
    print(f"Добавлен релиз #{item.id}.")


def action_check_publish(
    releases: list[Release],
) -> None:
    """Проверить готовность релиза методами объекта."""
    item = find_release(releases, input_int("Id релиза: "))
    if item is None:
        print("Релиз не найден.")
        return
    print(item)
    if item.can_publish():
        print("Решение: публикацию можно выполнить")
    else:
        print("Решение: публикацию выполнять нельзя")


def action_publish(releases: list[Release]) -> None:
    """Опубликовать готовый релиз."""
    release_id = input_int("Id релиза: ")
    try:
        item = publish_release(releases, release_id)
    except (KeyError, ValueError) as error:
        print(error)
        return
    save_releases(releases)
    print(f"Релиз #{item.id} опубликован.")


def action_cancel(releases: list[Release]) -> None:
    """Отменить запланированный релиз."""
    release_id = input_int("Id релиза: ")
    try:
        item = cancel_release(releases, release_id)
    except (KeyError, ValueError) as error:
        print(error)
        return
    save_releases(releases)
    print(f"Релиз #{item.id} отменён.")


def action_find_release(releases: list[Release]) -> None:
    """Найти релизы по подстроке версии."""
    query = input("Подстрока версии: ").strip()
    found = find_releases_by_version(releases, query)
    if not found:
        print("Ничего не найдено.")
        return
    show_releases(found)


def action_stats(releases: list[Release]) -> None:
    """Показать статистику по релизам."""
    stats = collect_statistics(releases)
    print("Статистика:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("По окружениям:")
    for environment in ENVIRONMENTS:
        count = sum(
            1
            for _ in filter_releases_by_environment(
                releases,
                environment,
            )
        )
        print(f"  {environment}: {count}")


def action_add_developer(developers: list[Developer]) -> None:
    """Добавить разработчика."""
    name = input("Имя разработчика: ").strip()
    role = input("Роль (backend/frontend/qa): ").strip()
    try:
        developer = add_developer(developers, name, role)
    except ValueError as error:
        print(error)
        return
    save_developers(developers)
    print(f"Добавлен разработчик #{developer.id}.")


def action_find_developer(developers: list[Developer]) -> None:
    """Найти разработчиков по имени или роли."""
    query = input("Подстрока имени или роли: ").strip()
    found = find_developer(developers, query)
    if not found:
        print("Ничего не найдено.")
        return
    show_developers(found)


def action_delete_developer(
    developers: list[Developer],
    tasks: list[Task],
) -> None:
    """Удалить разработчика без открытых задач."""
    if not developers:
        print("Разработчики ещё не добавлены.")
        return
    show_developers(developers)
    developer_id = input_int("Id разработчика для удаления: ")
    try:
        item = delete_developer(developers, developer_id, tasks)
    except (KeyError, ValueError) as error:
        print(error)
        return
    save_developers(developers)
    print(f"Разработчик «{item.name}» удалён.")


def action_add_task(
    products: list[Product],
    developers: list[Developer],
    releases: list[Release],
    tasks: list[Task],
) -> None:
    """Добавить задачу: связать Developer, Product и необязательный Release."""
    if not products or not developers:
        print("Сначала добавьте продукт и разработчика.")
        return
    show_developers(developers)
    developer = get_developer(developers, input_int("Id разработчика: "))
    if developer is None:
        print("Разработчик не найден.")
        return
    show_products(products)
    product = get_product(products, input_int("Id продукта: "))
    if product is None:
        print("Продукт не найден.")
        return
    release_id = input_optional_int(
        "Id релиза (0, если задача пока без релиза): "
    )
    release = None
    if release_id is not None:
        release = find_release(releases, release_id)
        if release is None:
            print("Релиз не найден.")
            return
    title = input("Название задачи: ").strip()
    try:
        item = add_task(tasks, title, developer, product, release)
    except ValueError as error:
        print(error)
        return
    save_tasks(tasks)
    print(f"Добавлена задача #{item.id}.")


def action_find_task(tasks: list[Task]) -> None:
    """Найти задачи по названию."""
    query = input("Подстрока названия задачи: ").strip()
    found = find_tasks_by_title(tasks, query)
    if not found:
        print("Ничего не найдено.")
        return
    show_tasks(found)


def action_set_task_status(tasks: list[Task]) -> None:
    """Изменить статус задачи."""
    task_id = input_int("Id задачи: ")
    allowed = "/".join(TASK_STATUSES)
    status = input(f"Новый статус ({allowed}): ").strip().lower()
    try:
        item = set_task_status(tasks, task_id, status)
    except (KeyError, ValueError) as error:
        print(error)
        return
    save_tasks(tasks)
    print(f"Задача #{item.id}: статус {item.status}.")


def main() -> None:
    """Загрузить объекты, запустить меню и сохранить данные при выходе."""
    products = load_products()
    developers = load_developers()
    releases = load_releases(products)
    tasks = load_tasks(products, developers, releases)

    while True:
        print(MENU)
        choice = input("Введите номер пункта и нажмите Enter: ").strip()
        if choice == "1":
            show_products(products)
        elif choice == "2":
            action_find_product(products)
        elif choice == "3":
            action_add_product(products)
        elif choice == "4":
            action_delete_product(products, releases)
        elif choice == "5":
            show_releases(releases)
        elif choice == "6":
            create_new_release(products, releases)
        elif choice == "7":
            action_check_publish(releases)
        elif choice == "8":
            action_publish(releases)
        elif choice == "9":
            action_cancel(releases)
        elif choice == "10":
            action_find_release(releases)
        elif choice == "11":
            action_stats(releases)
        elif choice == "12":
            show_developers(developers)
        elif choice == "13":
            action_add_developer(developers)
        elif choice == "14":
            action_delete_developer(developers, tasks)
        elif choice == "15":
            show_tasks(tasks)
        elif choice == "16":
            action_add_task(products, developers, releases, tasks)
        elif choice == "17":
            action_set_task_status(tasks)
        elif choice == "18":
            action_find_developer(developers)
        elif choice == "19":
            action_find_task(tasks)
        elif choice == "0":
            save_products(products)
            save_developers(developers)
            save_releases(releases)
            save_tasks(tasks)
            print("Выход.")
            break
        else:
            print("Нужна цифра из меню, например 1. Не название.")
            continue
        input("Нажмите Enter, чтобы вернуться в меню...")


if __name__ == "__main__":
    main()
