"""Модели приложения releases."""

from django.db import models
from django.db.models import Case, F, Q, Value, When
from django.urls import reverse

from models.releases import (
    can_publish_release,
    classify_version,
    get_release_status,
)


class ReleaseQuerySet(models.QuerySet):
    """Типовые выборки релизов."""

    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, release_date):
        return self.filter(release_date=release_date)

    def with_product(self):
        return self.select_related("product")

    def ready_to_publish(self):
        """Активные релизы, которые можно публиковать (правило ПР1)."""
        env = self.model.Environment
        rules = (
            Q(environment=env.TEST)
            | Q(environment=env.STAGING)
            & (Q(approvals_count__gte=1) | Q(is_hotfix=True))
            | Q(environment=env.PRODUCTION, is_approved=True)
        )
        return self.active().filter(tests_passed=True).filter(rules)


ReleaseManager = models.Manager.from_queryset(ReleaseQuerySet)


class Release(models.Model):
    """Релиз продукта в одном из окружений."""

    class Environment(models.TextChoices):
        TEST = "test", "Тестовое (test)"
        STAGING = "staging", "Предрелизное (staging)"
        PRODUCTION = "production", "Рабочее (production)"

    class Status(models.TextChoices):
        ACTIVE = "active", "Запланирован"
        CANCELLED = "cancelled", "Отменён"
        COMPLETED = "completed", "Опубликован"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="releases",
        verbose_name="продукт",
    )
    version = models.CharField(
        "версия",
        max_length=20,
        help_text="Номер версии в формате major.minor.patch, например 2.1.0.",
    )
    environment = models.CharField(
        "окружение",
        max_length=20,
        choices=Environment.choices,
        default=Environment.TEST,
    )
    tests_passed = models.BooleanField("тесты пройдены", default=False)
    approvals_count = models.PositiveSmallIntegerField(
        "получено согласований",
        default=0,
    )
    required_approvals = models.PositiveSmallIntegerField(
        "требуется согласований",
        default=1,
        help_text="Сколько согласований нужно для публикации в production.",
    )
    is_hotfix = models.BooleanField(
        "hotfix",
        default=False,
        help_text="Срочное исправление: в staging допускается без "
        "согласований.",
    )
    release_date = models.DateField("дата релиза")
    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    is_approved = models.GeneratedField(
        expression=Case(
            When(
                approvals_count__gte=F("required_approvals"),
                then=Value(True),
            ),
            default=Value(False),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="согласован",
    )

    objects = ReleaseManager()

    class Meta:
        ordering = ["release_date", "id"]
        verbose_name = "релиз"
        verbose_name_plural = "релизы"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "version"],
                name="unique_product_version",
            ),
        ]

    def __str__(self):
        return f"{self.product} {self.version}"

    def get_absolute_url(self):
        return reverse("releases:release_detail", args=[self.pk])

    @property
    def can_publish(self):
        """Правило публикации из ПР1–ПР3."""
        return can_publish_release(
            self.environment,
            self.tests_passed,
            self.approvals_count,
            self.required_approvals,
            self.is_hotfix,
        )

    @property
    def readiness(self):
        return get_release_status(
            self.tests_passed,
            self.approvals_count,
            self.required_approvals,
        )

    @property
    def version_kind(self):
        return classify_version(self.version)
