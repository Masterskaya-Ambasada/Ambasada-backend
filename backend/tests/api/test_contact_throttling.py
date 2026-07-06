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
        """POST запросы должны быть throttled после превышения лимита."""
        # conftest отключает ScopedRateThrottle глобально — возвращаем реальный лимит.
        monkeypatch.undo()
        factory = APIRequestFactory()
        view = ContactView.as_view()

        success_count = 0
        throttled_count = 0

        # Лимит из settings: THROTTLE_RATE_CONTACT=30/hour
        # Отправляем 35 запросов, чтобы гарантированно превысить лимит
        for i in range(35):
            request = factory.post(
                '/api/v1/contacts/',
                {
                    'name': 'Test User',
                    'email': f'test{i}@example.com',
                    'message': 'This is a test message that is long enough to pass validation',
                },
            )
            request.META['REMOTE_ADDR'] = '127.0.0.1'
            response = view(request)

            if response.status_code == 429:
                throttled_count += 1
            elif response.status_code in [201, 400]:
                success_count += 1

        assert throttled_count > 0, 'POST requests should be throttled after limit (30/hour)'
        assert success_count > 0, 'At least some POST requests should pass before throttling'

    def test_get_works_after_post_throttle_exceeded(self, monkeypatch):
        """GET контактного блока доступен даже после превышения лимита на POST."""
        monkeypatch.undo()
        factory = APIRequestFactory()
        view = ContactView.as_view()

        payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'This is a test message that is long enough to pass validation',
        }

        # Исчерпываем POST-лимит (30/hour).
        for i in range(35):
            request = factory.post('/api/v1/contacts/', {
                'name': 'Test User',
                'email': f'test{i}@example.com',
                'message': 'This is a test message that is long enough to pass validation',
            })
            request.META['REMOTE_ADDR'] = '127.0.0.1'
            view(request)

        # GET с того же IP должен работать — он не подпадает под лимит формы.
        request = factory.get('/api/v1/contacts/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        response = view(request)
        assert (
            response.status_code == 200
        ), f'GET after POST throttle exceeded should return 200, got {response.status_code}'
