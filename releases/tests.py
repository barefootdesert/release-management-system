"""Тесты ORM-представлений релизов и продуктов (ПР9)."""

from datetime import date

from django.test import TestCase
from django.urls import reverse

from developers.models import Developer
from products.models import Product
from releases.models import Release
from tasks.models import Task


class ReleaseViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gateway = Product.objects.create(name="Платёжный шлюз")
        cls.cabinet = Product.objects.create(name="Личный кабинет")
        cls.anna = Developer.objects.create(name="Анна", role="backend")
        cls.prod = Release.objects.create(
            product=cls.gateway,
            version="2.1.0",
            environment="production",
            tests_passed=True,
            approvals_count=2,
            required_approvals=2,
            release_date=date(2026, 9, 20),
        )
        cls.staging = Release.objects.create(
            product=cls.cabinet,
            version="1.4.3",
            environment="staging",
            tests_passed=True,
            approvals_count=0,
            required_approvals=2,
            release_date=date(2026, 9, 18),
        )
        cls.cancelled = Release.objects.create(
            product=cls.cabinet,
            version="1.4.2",
            release_date=date(2026, 9, 20),
            status="cancelled",
        )
        Task.objects.create(
            title="Таймаут оплаты",
            developer=cls.anna,
            product=cls.gateway,
            release=cls.prod,
        )

    def test_list_excludes_cancelled(self):
        response = self.client.get(reverse("releases:releases"))
        ids = [item["id"] for item in response.context["releases"]]
        self.assertEqual(ids, [self.staging.id, self.prod.id])

    def test_filter_by_product_and_developer(self):
        url = reverse("releases:releases")
        by_product = self.client.get(url, {"product": self.cabinet.id})
        self.assertEqual(
            [r["id"] for r in by_product.context["releases"]],
            [self.staging.id],
        )
        by_developer = self.client.get(url, {"developer": self.anna.id})
        self.assertEqual(
            [r["id"] for r in by_developer.context["releases"]],
            [self.prod.id],
        )

    def test_bad_date_shows_error(self):
        response = self.client.get(
            reverse("releases:releases"), {"date": "2026-99-99"}
        )
        self.assertEqual(response.context["error"], "Укажите корректную дату.")

    def test_unknown_sort_falls_back_to_date(self):
        response = self.client.get(
            reverse("releases:releases"), {"sort": "drop table"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["releases"][0]["id"], self.staging.id
        )

    def test_detail_and_404(self):
        ok = self.client.get(
            reverse("releases:release_detail", args=[self.prod.id])
        )
        self.assertContains(ok, "Таймаут оплаты")
        missing = self.client.get(
            reverse("releases:release_detail", args=[9999])
        )
        self.assertEqual(missing.status_code, 404)

    def test_ready_uses_publish_rules(self):
        response = self.client.get(reverse("releases:ready"))
        ids = [item["id"] for item in response.context["releases"]]
        self.assertEqual(ids, [self.prod.id])

    def test_statistics_min_filter(self):
        response = self.client.get(
            reverse("releases:statistics"), {"min": 2}
        )
        stats = list(response.context["statistics"])
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]["name"], "Личный кабинет")
        self.assertEqual(stats[0]["active_count"], 1)

    def test_available_products_on_date(self):
        response = self.client.get(
            reverse("products:available"), {"date": "2026-09-20"}
        )
        names = [p.name for p in response.context["products"]]
        self.assertEqual(names, ["Личный кабинет"])
