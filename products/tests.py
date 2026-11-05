"""Тесты ПР10: менеджер, GeneratedField, slug, контекст и админка."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from developers.models import Developer
from products.models import Product
from releases.models import Release
from tasks.models import Task

DAY = date(2026, 9, 20)


class ReleaseManagerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(name="Платёжный шлюз")
        cls.active = Release.objects.create(
            product=cls.product, version="1.0.0", release_date=DAY
        )
        cls.cancelled = Release.objects.create(
            product=cls.product,
            version="1.0.1",
            release_date=DAY,
            status=Release.Status.CANCELLED,
        )
        cls.completed = Release.objects.create(
            product=cls.product,
            version="0.9.0",
            release_date=date(2026, 8, 1),
            status=Release.Status.COMPLETED,
        )

    def test_status_methods(self):
        self.assertEqual(list(Release.objects.active()), [self.active])
        self.assertEqual(
            list(Release.objects.cancelled()), [self.cancelled]
        )
        self.assertEqual(
            list(Release.objects.completed()), [self.completed]
        )

    def test_for_date_chains_with_status(self):
        self.assertEqual(
            list(Release.objects.active().for_date(DAY)), [self.active]
        )

    def test_generated_is_approved(self):
        release = Release.objects.create(
            product=self.product,
            version="2.0.0",
            release_date=DAY,
            approvals_count=2,
            required_approvals=2,
        )
        release.refresh_from_db()
        self.assertTrue(release.is_approved)
        Release.objects.filter(pk=release.pk).update(required_approvals=3)
        release.refresh_from_db()
        self.assertFalse(release.is_approved)

    def test_ready_to_publish_production_needs_approvals(self):
        ready = Release.objects.create(
            product=self.product,
            version="3.0.0",
            environment=Release.Environment.PRODUCTION,
            tests_passed=True,
            approvals_count=1,
            required_approvals=1,
            release_date=DAY,
        )
        Release.objects.create(
            product=self.product,
            version="3.0.1",
            environment=Release.Environment.PRODUCTION,
            tests_passed=True,
            approvals_count=0,
            required_approvals=1,
            release_date=DAY,
        )
        self.assertEqual(list(Release.objects.ready_to_publish()), [ready])


class AvailabilityAndStatisticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.busy = Product.objects.create(name="Занятый")
        cls.cancelled = Product.objects.create(name="С отменённым")
        cls.completed = Product.objects.create(name="С опубликованным")
        Release.objects.create(
            product=cls.busy, version="1.0.0", release_date=DAY
        )
        Release.objects.create(
            product=cls.cancelled,
            version="1.0.0",
            release_date=DAY,
            status=Release.Status.CANCELLED,
        )
        Release.objects.create(
            product=cls.completed,
            version="1.0.0",
            release_date=DAY,
            status=Release.Status.COMPLETED,
        )

    def test_only_active_release_blocks_product(self):
        response = self.client.get(
            reverse("products:available"), {"date": DAY.isoformat()}
        )
        names = {p.name for p in response.context["products"]}
        self.assertEqual(names, {"С отменённым", "С опубликованным"})

    def test_statistics_by_status(self):
        response = self.client.get(reverse("releases:statistics"))
        self.assertEqual(
            response.context["by_status"],
            {"total": 3, "active": 1, "cancelled": 1, "completed": 1},
        )


class SlugAndContextTests(TestCase):
    def test_slug_is_transliterated_and_unique(self):
        first = Product.objects.create(name="Личный кабинет")
        second = Product.objects.create(name="Личный кабинет")
        self.assertEqual(first.slug, "lichnyi-kabinet")
        self.assertEqual(second.slug, "lichnyi-kabinet-2")

    def test_slug_kept_after_rename(self):
        product = Product.objects.create(name="Админ-панель")
        product.name = "Панель администратора"
        product.save()
        self.assertEqual(product.slug, "admin-panel")

    def test_detail_by_slug(self):
        product = Product.objects.create(name="Сервис уведомлений")
        self.assertEqual(
            product.get_absolute_url(), "/products/servis-uvedomlenii/"
        )
        response = self.client.get(product.get_absolute_url())
        self.assertContains(response, "Сервис уведомлений")
        missing = self.client.get("/products/net-takogo/")
        self.assertEqual(missing.status_code, 404)

    def test_context_processor_on_every_page(self):
        product = Product.objects.create(name="Шлюз")
        Release.objects.create(
            product=product, version="1.0.0", release_date=DAY
        )
        for url in ("/", "/products/", "/releases/statistics/"):
            response = self.client.get(url)
            self.assertEqual(response.context["products_total"], 1)
            self.assertEqual(response.context["active_releases_total"], 1)
            self.assertEqual(
                response.context["site_name"], "Система управления релизами"
            )


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            "admin", "admin@example.com", "admin12345"
        )
        cls.product = Product.objects.create(name="Платёжный шлюз")
        cls.developer = Developer.objects.create(name="Анна", role="qa")
        cls.release = Release.objects.create(
            product=cls.product, version="1.0.0", release_date=DAY
        )
        Task.objects.create(
            title="Регресс",
            developer=cls.developer,
            product=cls.product,
            release=cls.release,
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_changelists_and_change_pages_open(self):
        pages = [
            ("products", "product", self.product.pk),
            ("developers", "developer", self.developer.pk),
            ("releases", "release", self.release.pk),
            ("tasks", "task", Task.objects.get().pk),
        ]
        for app, model, pk in pages:
            changelist = reverse(f"admin:{app}_{model}_changelist")
            self.assertEqual(self.client.get(changelist).status_code, 200)
            self.assertEqual(
                self.client.get(changelist, {"q": "1"}).status_code, 200
            )
            change = reverse(f"admin:{app}_{model}_change", args=[pk])
            self.assertEqual(self.client.get(change).status_code, 200)

    def test_release_inline_on_product_page(self):
        response = self.client.get(
            reverse("admin:products_product_change", args=[self.product.pk])
        )
        self.assertContains(response, "1.0.0")

    def test_mark_cancelled_action(self):
        self.client.post(
            reverse("admin:releases_release_changelist"),
            {
                "action": "mark_cancelled",
                "_selected_action": [self.release.pk],
            },
        )
        self.release.refresh_from_db()
        self.assertEqual(self.release.status, Release.Status.CANCELLED)
