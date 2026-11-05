"""Модели приложения tasks."""

from django.db import models


class Task(models.Model):
    """Задача разработчика по продукту, при необходимости — по релизу."""

    class Status(models.TextChoices):
        TODO = "todo", "К выполнению"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Готово"

    title = models.CharField("название", max_length=200)
    developer = models.ForeignKey(
        "developers.Developer",
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="исполнитель",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="продукт",
    )
    release = models.ForeignKey(
        "releases.Release",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="релиз",
        help_text="Можно оставить пустым, если задача не привязана "
        "к релизу.",
    )
    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "задача"
        verbose_name_plural = "задачи"

    def __str__(self):
        return self.title
