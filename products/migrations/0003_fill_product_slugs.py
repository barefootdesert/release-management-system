from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def fill_slugs(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    used = set()
    for product in Product.objects.order_by("id"):
        base = slugify(unidecode(product.name))[:100] or "product"
        slug = base
        suffix = 2
        while slug in used:
            slug = f"{base}-{suffix}"
            suffix += 1
        used.add(slug)
        product.slug = slug
        product.save(update_fields=["slug"])


def clear_slugs(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    Product.objects.update(slug="")


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_product_slug_and_verbose_names"),
    ]

    operations = [
        migrations.RunPython(fill_slugs, clear_slugs),
    ]
