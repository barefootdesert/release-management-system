# Система управления релизами: начальный сценарий практической работы № 1.

from datetime import date


product_name = "Платёжный шлюз"
version = "2.1.0"
environment = "production"
tests_passed = True
approvals_count = 2
required_approvals = 2
is_hotfix = False
release_date = date(2026, 9, 20)


def get_release_status(tests_passed, approvals_count, required_approvals):
    # Вернуть текстовый статус релиза по тестам и согласованиям.
    if not tests_passed:
        return "заблокирован: тесты не пройдены"
    if approvals_count < required_approvals:
        return "ожидает согласования"
    return "готов к публикации"


def can_publish_release(
    environment,
    tests_passed,
    approvals_count,
    required_approvals,
    is_hotfix,
):
    """Проверить, допускается ли публикация релиза в указанное окружение."""
    if not tests_passed:
        return False

    if environment == "test":
        return True

    if environment == "staging":
        return approvals_count >= 1 or is_hotfix

    if environment == "production":
        return approvals_count >= required_approvals

    return False


def classify_version(version):
    # Определить тип версии по номерам major и patch без коллекций.
    first_dot_index = version.find(".")
    last_dot_index = version.rfind(".")
    major = int(version[:first_dot_index])
    patch = int(version[last_dot_index + 1 :])

    if major == 0:
        return "предрелизная версия"
    if patch == 0:
        return "minor-релиз"
    return "patch-релиз"


def describe_release_deadline(release_date, today):
    # Описать, сколько дней осталось до запланированной даты релиза.
    days_left = (release_date - today).days

    if days_left < 0:
        return "дата релиза уже прошла"
    if days_left == 0:
        return "релиз запланирован на сегодня"
    return f"до релиза осталось {days_left} дн."


today = date.today()
status = get_release_status(tests_passed, approvals_count, required_approvals)
allowed_to_publish = can_publish_release(
    environment,
    tests_passed,
    approvals_count,
    required_approvals,
    is_hotfix,
)
version_type = classify_version(version)
deadline_text = describe_release_deadline(release_date, today)

if allowed_to_publish:
    publish_decision = "публикацию можно выполнить"
else:
    publish_decision = "публикацию выполнять нельзя"

print(f"Продукт: {product_name}")
print(f"Версия: {version} ({version_type})")
print(f"Окружение: {environment}")
print(f"Дата релиза: {release_date}")
print(f"Срок: {deadline_text}")
print(f"Тесты пройдены: {tests_passed}")
print(f"Согласования: {approvals_count} из {required_approvals}")
print(f"Hotfix: {is_hotfix}")
print(f"Статус: {status}")
print(f"Решение: {publish_decision}")
