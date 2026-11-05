from django.db import migrations

FORWARD = {
    "planned": "active",
    "published": "completed",
    "cancelled": "cancelled",
}
BACKWARD = {new: old for old, new in FORWARD.items()}


def to_status_codes(apps, schema_editor):
    Release = apps.get_model("releases", "Release")
    for old, new in FORWARD.items():
        Release.objects.filter(status=old).update(status=new)


def to_legacy_statuses(apps, schema_editor):
    Release = apps.get_model("releases", "Release")
    for new, old in BACKWARD.items():
        Release.objects.filter(status=new).update(status=old)


class Migration(migrations.Migration):

    dependencies = [
        ("releases", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(to_status_codes, to_legacy_statuses),
    ]
