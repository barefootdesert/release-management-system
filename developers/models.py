"""Модели приложения developers."""

from django.db import models


class Developer(models.Model):
    """Участник команды: разработчик, тестировщик и т. п."""

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.role})"
