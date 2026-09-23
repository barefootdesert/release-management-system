"""Точка запуска системы управления релизами."""

from datetime import date

from developers import (
    add_developer,
    delete_developer,
    find_developer,
    get_developer,
    sort_developers,
)
from products import (
    add_product,
    delete_product,
    find_product,
    get_product,
    sort_products,
)
from releases import (
    ENVIRONMENTS,
    cancel_release,
    classify_version,
    collect_statistics,
    create_release,
    describe_release_deadline,
    filter_releases_by_environment,
    find_release,
    find_releases_by_version,
    get_release_status,
    is_release_publishable,
    publish_release,
    sort_releases,
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
from tasks import (
    TASK_STATUSES,
    add_task,
    find_tasks_by_title,
    set_task_status,
    sort_tasks,
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


def _product_name(products: dict[int, dict], product_id: int) -> str:
    """Вернуть название продукта или заглушку."""
    product = get_product(products, product_id)
    if product is None:
        return f"#{product_id}"
    return str(product["name"])


def _print_release(products: dict[int, dict], item: dict) -> None:
    """Вывести карточку одного релиза."""
    release_date = date.fromisoformat(item["release_date"])
    status = get_release_status(
        item["tests_passed"],
        item["approvals_count"],
        item["required_approvals"],
    )
    print(
        f"[{item['id']}] {_product_name(products, item['product_id'])} "
        f"{item['version']} ({classify_version(item['version'])})"
    )
    print(
        f"    окружение: {item['environment']}; "
        f"состояние: {item['status']}; "
        f"готовность: {status}"
    )
    print(
        f"    дата: {release_date}; "
        f"{describe_release_deadline(release_date, date.today())}"
    )


def show_products(products: dict[int, dict]) -> None:
    """Вывести список продуктов."""
    if not products:
        print("Продукты ещё не добавлены.")
        return
    print("Продукты:")
    for product in sort_products(products):
        print(f"  {product['id']}. {product['name']}")


def show_releases(
    products: dict[int, dict],
    releases: list[dict],
) -> None:
    """Вывести список релизов."""
    if not releases:
        print("Релизы ещё не добавлены.")
        return
    print("Релизы:")
    for item in sort_releases(releases):
        _print_release(products, item)


def action_add_product(products: dict[int, dict]) -> None:
    """Добавить продукт и сохранить данные."""
    name = input("Название продукта: ").strip()
    if not name:
        print("Название не может быть пустым.")
        return
    product_id = add_product(products, name)
    save_products(products)
    print(f"Добавлен продукт #{product_id}.")


def action_find_product(products: dict[int, dict]) -> None:
    """Найти продукты по подстроке названия."""
    query = input("Подстрока названия: ").strip()
    found = find_product(products, query)
    if not found:
        print("Ничего не найдено.")
        return
    show_products(found)


def action_delete_product(
    products: dict[int, dict],
    releases: list[dict],
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
    print(f"Продукт «{product['name']}» удалён.")


def action_add_release(
    products: dict[int, dict],
    releases: list[dict],
) -> None:
    """Добавить релиз для существующего продукта."""
    if not products:
        print("Сначала добавьте продукт.")
        return
    show_products(products)
    product_id = input_int("Id продукта: ")
    if get_product(products, product_id) is None:
        print("Продукт не найден.")
        return
    version = input("Версия (например, 2.1.0): ").strip()
    if version.count(".") != 2:
        print("Ожидается версия вида major.minor.patch.")
        return
    try:
        item = create_release(
            releases,
            product_id,
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
    print(f"Добавлен релиз #{item['id']}.")


def action_check_publish(
    products: dict[int, dict],
    releases: list[dict],
) -> None:
    """Проверить готовность релиза функцией из ПР1."""
    release_id = input_int("Id релиза: ")
    item = find_release(releases, release_id)
    if item is None:
        print("Релиз не найден.")
        return
    _print_release(products, item)
    if is_release_publishable(item):
        print("Решение: публикацию можно выполнить")
    else:
        print("Решение: публикацию выполнять нельзя")


def action_publish(releases: list[dict]) -> None:
    """Опубликовать готовый релиз."""
    release_id = input_int("Id релиза: ")
    try:
        item = publish_release(releases, release_id)
    except (KeyError, ValueError) as error:
        print(error)
        return
    save_releases(releases)
    print(f"Релиз #{item['id']} опубликован.")


def action_cancel(releases: list[dict]) -> None:
    """Отменить запланированный релиз."""
    release_id = input_int("Id релиза: ")
    try:
        item = cancel_release(releases, release_id)
    except (KeyError, ValueError) as error:
        print(error)
        return
    save_releases(releases)
    print(f"Релиз #{item['id']} отменён.")


def action_find_release(
    products: dict[int, dict],
    releases: list[dict],
) -> None:
    """Найти релизы по подстроке версии."""
    query = input("Подстрока версии: ").strip()
    found = find_releases_by_version(releases, query)
    if not found:
        print("Ничего не найдено.")
        return
    for item in found:
        _print_release(products, item)


def action_stats(releases: list[dict]) -> None:
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


def _developer_name(
    developers: dict[int, dict],
    developer_id: int,
) -> str:
    """Вернуть имя разработчика или заглушку."""
    developer = get_developer(developers, developer_id)
    if developer is None:
        return f"#{developer_id}"
    return str(developer["name"])


def show_developers(developers: dict[int, dict]) -> None:
    """Вывести список разработчиков."""
    if not developers:
        print("Разработчики ещё не добавлены.")
        return
    print("Разработчики:")
    for item in sort_developers(developers):
        print(f"  {item['id']}. {item['name']} ({item['role']})")


def action_add_developer(developers: dict[int, dict]) -> None:
    """Добавить разработчика."""
    name = input("Имя разработчика: ").strip()
    role = input("Роль (backend/frontend/qa): ").strip()
    if not name or not role:
        print("Имя и роль не могут быть пустыми.")
        return
    developer_id = add_developer(developers, name, role)
    save_developers(developers)
    print(f"Добавлен разработчик #{developer_id}.")


def action_find_developer(developers: dict[int, dict]) -> None:
    """Найти разработчиков по имени или роли."""
    query = input("Подстрока имени или роли: ").strip()
    found = find_developer(developers, query)
    if not found:
        print("Ничего не найдено.")
        return
    show_developers(found)


def action_delete_developer(
    developers: dict[int, dict],
    tasks: list[dict],
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
    print(f"Разработчик «{item['name']}» удалён.")


def _print_task(
    products: dict[int, dict],
    developers: dict[int, dict],
    item: dict,
) -> None:
    """Вывести одну задачу."""
    release_id = item.get("release_id")
    release_text = f"релиз #{release_id}" if release_id else "без релиза"
    print(
        f"[{item['id']}] {item['title']} — {item['status']}; "
        f"{_developer_name(developers, item['developer_id'])}; "
        f"{_product_name(products, item['product_id'])}; "
        f"{release_text}"
    )


def show_tasks(
    products: dict[int, dict],
    developers: dict[int, dict],
    tasks: list[dict],
) -> None:
    """Вывести список задач."""
    if not tasks:
        print("Задачи ещё не добавлены.")
        return
    print("Задачи:")
    for item in sort_tasks(tasks):
        _print_task(products, developers, item)


def action_add_task(
    products: dict[int, dict],
    developers: dict[int, dict],
    releases: list[dict],
    tasks: list[dict],
) -> None:
    """Добавить задачу разработчику."""
    if not products or not developers:
        print("Сначала добавьте продукт и разработчика.")
        return
    show_developers(developers)
    developer_id = input_int("Id разработчика: ")
    if get_developer(developers, developer_id) is None:
        print("Разработчик не найден.")
        return
    show_products(products)
    product_id = input_int("Id продукта: ")
    if get_product(products, product_id) is None:
        print("Продукт не найден.")
        return
    release_id = input_optional_int(
        "Id релиза (0, если задача пока без релиза): "
    )
    if release_id is not None and find_release(releases, release_id) is None:
        print("Релиз не найден.")
        return
    title = input("Название задачи: ").strip()
    try:
        item = add_task(
            tasks,
            title,
            developer_id,
            product_id,
            release_id,
        )
    except ValueError as error:
        print(error)
        return
    save_tasks(tasks)
    print(f"Добавлена задача #{item['id']}.")


def action_find_task(
    products: dict[int, dict],
    developers: dict[int, dict],
    tasks: list[dict],
) -> None:
    """Найти задачи по названию."""
    query = input("Подстрока названия задачи: ").strip()
    found = find_tasks_by_title(tasks, query)
    if not found:
        print("Ничего не найдено.")
        return
    for item in found:
        _print_task(products, developers, item)


def action_set_task_status(tasks: list[dict]) -> None:
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
    print(f"Задача #{item['id']}: статус {item['status']}.")


def main() -> None:
    """Точка запуска: цикл меню и вызов функций проекта."""
    products = load_products()
    releases = load_releases()
    developers = load_developers()
    tasks = load_tasks()

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
            show_releases(products, releases)
        elif choice == "6":
            action_add_release(products, releases)
        elif choice == "7":
            action_check_publish(products, releases)
        elif choice == "8":
            action_publish(releases)
        elif choice == "9":
            action_cancel(releases)
        elif choice == "10":
            action_find_release(products, releases)
        elif choice == "11":
            action_stats(releases)
        elif choice == "12":
            show_developers(developers)
        elif choice == "13":
            action_add_developer(developers)
        elif choice == "14":
            action_delete_developer(developers, tasks)
        elif choice == "15":
            show_tasks(products, developers, tasks)
        elif choice == "16":
            action_add_task(products, developers, releases, tasks)
        elif choice == "17":
            action_set_task_status(tasks)
        elif choice == "18":
            action_find_developer(developers)
        elif choice == "19":
            action_find_task(products, developers, tasks)
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Нужна цифра из меню, например 1. Не название.")
            continue
        input("Нажмите Enter, чтобы вернуться в меню...")


if __name__ == "__main__":
    main()
