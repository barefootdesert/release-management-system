"""Модели приложения products."""

from django.db import models


class Product(models.Model):
    """Продукт, для которого выпускаются релизы."""

    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
