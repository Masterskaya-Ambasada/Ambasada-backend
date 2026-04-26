from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase

from site_config.models import Language, SiteConfig, Social


class InitViewTests(APITestCase):
    def setUp(self):
        self.url = '/api/v1/init/'
        SiteConfig.objects.all().delete()

    # Успешный сценарий
    def test_init_success(self):
        SiteConfig.objects.create(
            site_name='Test Site',
            seo_description='SEO text',
            copyright='2026'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['site_name'], 'Test Site')
        self.assertEqual(response.data['seo_description'], 'SEO text')

    # Нет конфига → 404
    def test_init_not_found(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'NOT_FOUND')
        self.assertEqual(response.data['status'], 404)

    # Проверка структуры ответа
    def test_response_structure(self):
        SiteConfig.objects.create(site_name='Test')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertIn('site_name', response.data)
        self.assertIn('seo_description', response.data)
        self.assertIn('languages', response.data)
        self.assertIn('socials', response.data)
        self.assertIn('copyright', response.data)

    # Пустые связи
    def test_empty_relations(self):
        SiteConfig.objects.create(site_name='Test')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['languages'], [])
        self.assertEqual(response.data['socials'], [])

    # Связанные данные (languages + socials)
    def test_with_relations(self):
        config = SiteConfig.objects.create(site_name='Test', seo_description='SEO', copyright='©')

        lang_en = Language.objects.create(code='en', label='English')
        lang_ru = Language.objects.create(code='ru', label='Русский')

        social_tg = Social.objects.create(social_type=1, url='https://t.me/test')
        social_fb = Social.objects.create(social_type=2, url='https://fb.com/test')

        config.languages.add(lang_en, lang_ru)
        config.socials.add(social_tg, social_fb)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['languages']), 2)
        self.assertEqual(len(response.data['socials']), 2)

    def test_only_one_site_config_allowed(self):
        SiteConfig.objects.create(site_name='First')

        with self.assertRaises(ValidationError):
            SiteConfig.objects.create(site_name='Second')
