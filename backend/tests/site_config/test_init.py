from django.core.cache import cache

from django.urls import reverse
from rest_framework.test import APITestCase
from django.db import IntegrityError, transaction

from site_config.models import SiteConfig



class InitViewTests(APITestCase):
    """Тесты для API инициализации настроек сайта."""

    def setUp(self):
        """Очистка кеша и подготовка URL перед каждым тестом."""
        cache.clear()
        self.url = reverse('api:init')
        SiteConfig.objects.all().delete()

    def test_init_success(self):
        """Проверка успешного получения существующего конфига."""
        SiteConfig.objects.create(
            site_name='Test Site', 
            seo_description='SEO text', 
            copyright='2026'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['site_name'], 'Test Site')
        self.assertEqual(response.data['seo_description'], 'SEO text')

    def test_init_not_found(self):
        """Проверка возврата 404 при отсутствии конфигурации."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'NOT_FOUND')

    def test_response_structure(self):
        """Проверка наличия всех обязательных полей в JSON-ответе."""
        SiteConfig.objects.create(site_name='Test')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('site_name', response.data)
        self.assertIn('seo_description', response.data)
        self.assertIn('languages', response.data)
        self.assertIn('socials', response.data)
        self.assertIn('copyright', response.data)

    def test_empty_relations(self):
        """Проверка корректного возврата пустых списков для связей."""
        SiteConfig.objects.create(site_name='Test')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['languages'], [])
        self.assertEqual(response.data['socials'], [])


    def test_only_one_site_config_allowed(self):
        """Проверка валидации на создание единственного экземпляра настроек."""
        SiteConfig.objects.create(site_name='First')
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SiteConfig.objects.create(site_name='Second')