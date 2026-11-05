"""Модели приложения developers."""

from django.db import models


class Developer(models.Model):
    """Участник команды: разработчик, тестировщик и т. п."""

    name = models.CharField("имя", max_length=100)
    role = models.CharField(
        "роль",
        max_length=50,
        help_text="Специализация в команде: backend, frontend, qa и т. п.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "разработчик"
        verbose_name_plural = "разработчики"

    def __str__(self):
        return f"{self.name} ({self.role})"
