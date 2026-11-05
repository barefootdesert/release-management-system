"""Модели приложения products."""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


class Product(models.Model):
    """Продукт, для которого выпускаются релизы."""

    name = models.CharField(
        "название",
        max_length=100,
        help_text="Название продукта, как его видят пользователи.",
    )
    slug = models.SlugField(
        "адрес (slug)",
        max_length=120,
        unique=True,
        blank=True,
        editable=False,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "продукт"
        verbose_name_plural = "продукты"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    def _unique_slug(self):
        base = slugify(unidecode(self.name))[:100] or "product"
        slug = base
        suffix = 2
        others = Product.objects.exclude(pk=self.pk)
        while others.filter(slug=slug).exists():
            slug = f"{base}-{suffix}"
            suffix += 1
        return slug

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"slug": self.slug})
