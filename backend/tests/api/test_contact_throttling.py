"""Тесты throttling для контактной формы."""

import pytest
from api.contacts.views import ContactView
from rest_framework.test import APIRequestFactory

pytestmark = pytest.mark.django_db


class TestContactThrottling:
    """Тесты throttling GET и POST запросов."""

    def test_get_requests_without_throttling(self):
        """GET запросы не должны иметь throttling."""
        factory = APIRequestFactory()
        view = ContactView.as_view()

        # 10 GET запросов подряд - все должны пройти
        for i in range(10):
            request = factory.get('/api/v1/contacts/')
            response = view(request)
            assert response.status_code == 200, f'GET request {i+1} failed with {response.status_code}'

    def test_post_requests_with_throttling(self, monkeypatch):
        """POST запросы должны быть throttled."""
        # Глобальный autouse-фикстур disable_scoped_throttling (conftest) подменяет
        # ScopedRateThrottle.allow_request на no-op для всех тестов. Этот тест
        # намеренно проверяет реальный лимит — откатываем обезличивание.
        monkeypatch.undo()
        factory = APIRequestFactory()
        view = ContactView.as_view()

        success_count = 0
        throttled_count = 0

        # Делаем 10 POST запросов
        for i in range(10):
            request = factory.post(
                '/api/v1/contacts/',
                {
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'message': 'This is a test message that is long enough to pass validation',
                },
            )
            request.META['REMOTE_ADDR'] = '127.0.0.1'
            response = view(request)

            if response.status_code == 429:
                throttled_count += 1
            elif response.status_code in [201, 400]:
                success_count += 1

        # Лимит из .env: THROTTLE_RATE_CONTACT=5/hour
        # Хотя бы один запрос должен быть throttled
        assert throttled_count > 0, 'POST requests should be throttled after limit (5/hour)'
        # И хотя бы несколько должны пройти до throttling
        assert success_count > 0, 'At least some POST requests should pass before throttling'
