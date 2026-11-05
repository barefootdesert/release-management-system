"""Модели приложения releases."""

from django.db import models

from models.releases import (
    can_publish_release,
    classify_version,
    get_release_status,
)


class Release(models.Model):
    """Релиз продукта в одном из окружений."""

    class Environment(models.TextChoices):
        TEST = "test", "test"
        STAGING = "staging", "staging"
        PRODUCTION = "production", "production"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="releases",
    )
    version = models.CharField(max_length=20)
    environment = models.CharField(
        max_length=20,
        choices=Environment.choices,
        default=Environment.TEST,
    )
    tests_passed = models.BooleanField(default=False)
    approvals_count = models.PositiveSmallIntegerField(default=0)
    required_approvals = models.PositiveSmallIntegerField(default=1)
    is_hotfix = models.BooleanField(default=False)
    release_date = models.DateField()
    status = models.CharField(max_length=20, default="planned")

    class Meta:
        ordering = ["release_date", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "version"],
                name="unique_product_version",
            ),
        ]

    def __str__(self):
        return f"{self.product} {self.version}"

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
