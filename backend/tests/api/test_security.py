import pytest
from django.core.exceptions import FieldError
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPrivacyPolicyAPI:
    """Тестирование эндпоинта API Политики конфиденциальности и локализации."""

    @pytest.fixture(autouse=True)
    def setup_url(self):
        self.url = reverse('api:politics')

    def test_get_policy_default_language_ru(self, api_client, sample_policy, privacy_policy_data):
        """Без заголовка Accept-Language API должен отдавать текст на русском языке."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == privacy_policy_data['text_ru']

    def test_get_policy_in_english(self, api_client, sample_policy, privacy_policy_data):
        """При передаче заголовка Accept-Language: en возвращается английский контент."""
        response = api_client.get(self.url, HTTP_ACCEPT_LANGUAGE='en')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == privacy_policy_data['text_en']

    def test_get_policy_in_serbian_latin(self, api_client, sample_policy, privacy_policy_data):
        """При передаче заголовка Accept-Language: sr-latn возвращается сербская латиница."""
        response = api_client.get(self.url, HTTP_ACCEPT_LANGUAGE='sr-latn')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == privacy_policy_data['text_sr_latn']

    def test_get_policy_when_not_found(self, api_client):
        """Если записи в базе нет, метод load() создает дефолтную и отдает ее."""
        from security.models import SecurityPolicy
        SecurityPolicy.objects.all().delete()
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == 'Текст политики...'