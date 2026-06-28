import time
from unittest.mock import patch

import pytest
from core.middleware import AdminLoginThrottleMiddleware
from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory


class TestAdminLoginThrottleMiddleware:
    """Тесты ограничения частоты попыток входа в админку."""

    @pytest.fixture(autouse=True)
    def setup_cache(self):
        """Очистка кеша до и после каждого теста."""
        cache.clear()
        yield
        cache.clear()

    @pytest.fixture
    def factory(self):
        """Фабрика для создания HTTP-запросов."""
        return RequestFactory()

    @pytest.fixture
    def middleware(self):
        """Экземпляр middleware с заглушкой get_response."""

        def get_response(request):
            return HttpResponse('OK', status=200)

        return AdminLoginThrottleMiddleware(get_response)

    @pytest.fixture
    def test_ip(self):
        """Тестовый IP-адрес."""
        return '192.168.1.100'

    @pytest.fixture
    def create_request(self, factory):
        """Хелпер для создания POST-запросов к админке с заданным IP."""

        def _create(ip, data=None):
            if data is None:
                data = {'username': 'admin', 'password': 'pass'}

            request = factory.post('/admin/login/', data)
            request.META['REMOTE_ADDR'] = ip
            return request

        return _create

    def test_allows_requests_under_limit(self, middleware, create_request, test_ip):
        """Запросы ниже лимита должны проходить без блокировки."""
        for _ in range(9):
            response = middleware(create_request(test_ip))
            assert response.status_code == 200

        assert cache.get(f'admin_login_count:{test_ip}') == 9
        assert cache.get(f'admin_login_block:{test_ip}') is None

    def test_blocks_after_max_attempts(self, middleware, create_request, test_ip):
        """Блокировка срабатывает после достижения лимита попыток."""

        for _ in range(AdminLoginThrottleMiddleware.MAX_ATTEMPTS):
            response = middleware(create_request(test_ip))
            assert response.status_code == 200

        response = middleware(create_request(test_ip))

        assert response.status_code == 429
        assert cache.get(f'admin_login_block:{test_ip}') is True

    def test_blocked_ip_is_rejected(self, middleware, create_request, test_ip):
        """Заблокированный IP должен получать 429."""

        cache.set(f'admin_login_block:{test_ip}', True, 300)

        response = middleware(create_request(test_ip))

        assert response.status_code == 429

    def test_independent_ip_throttling(self, middleware, create_request):
        """Разные IP должны иметь независимые лимиты."""

        ip1 = '192.168.1.100'
        ip2 = '192.168.1.101'

        for _ in range(10):
            middleware(create_request(ip1))

        assert cache.get(f'admin_login_block:{ip1}') is True
        assert cache.get(f'admin_login_block:{ip2}') is None

        response = middleware(create_request(ip2))
        assert response.status_code == 200

    def test_non_post_requests_are_ignored(self, middleware, factory, test_ip):
        """GET-запросы не должны учитываться в лимите."""

        request = factory.get('/admin/login/')
        request.META['REMOTE_ADDR'] = test_ip

        middleware(request)

        assert cache.get(f'admin_login_count:{test_ip}') is None

    def test_non_admin_path_is_ignored(self, middleware, factory, test_ip):
        """Запросы вне админки не должны учитываться."""

        request = factory.post('/other/', {})
        request.META['REMOTE_ADDR'] = test_ip

        middleware(request)

        assert cache.get(f'admin_login_count:{test_ip}') is None

    def test_x_forwarded_for_priority(self, middleware, factory):
        """X-Forwarded-For имеет приоритет над REMOTE_ADDR."""

        request = factory.post('/admin/login/', {})
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 203.0.113.2'

        middleware(request)

        assert cache.get('admin_login_count:203.0.113.1') == 1

    def test_window_reset(self, middleware, create_request, test_ip):
        """Счётчик должен сбрасываться после окна времени."""

        with patch.object(AdminLoginThrottleMiddleware, 'WINDOW_SECONDS', 1):
            for _ in range(5):
                middleware(create_request(test_ip))

            assert cache.get(f'admin_login_count:{test_ip}') == 5

            time.sleep(1.1)

            middleware(create_request(test_ip))

            assert cache.get(f'admin_login_count:{test_ip}') == 1

    def test_block_expires(self, middleware, create_request, test_ip):
        """Блокировка должна истекать после BLOCK_SECONDS."""

        with patch.object(AdminLoginThrottleMiddleware, 'BLOCK_SECONDS', 1):
            for _ in range(10):
                middleware(create_request(test_ip))

            assert cache.get(f'admin_login_block:{test_ip}') is True

            time.sleep(1.1)

            response = middleware(create_request(test_ip))
            assert response.status_code == 200

    def test_ip_extraction_static_method(self):
        """Проверка логики извлечения IP из заголовков."""

        factory = RequestFactory()

        req = factory.get('/')
        req.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1, 2.2.2.2'
        assert AdminLoginThrottleMiddleware._get_ip(req) == '1.1.1.1'

        req = factory.get('/')
        req.META['REMOTE_ADDR'] = '3.3.3.3'
        assert AdminLoginThrottleMiddleware._get_ip(req) == '3.3.3.3'

        req = factory.get('/')
        req.META.pop('REMOTE_ADDR', None)
        assert AdminLoginThrottleMiddleware._get_ip(req) == '0.0.0.0'

    @pytest.mark.skip(reason="Тест отключён на время тестирования проекта")
    def test_constants(self):
        """Проверка неизменности констант middleware."""
        assert AdminLoginThrottleMiddleware.MAX_ATTEMPTS == 10
        assert AdminLoginThrottleMiddleware.WINDOW_SECONDS == 60
        assert AdminLoginThrottleMiddleware.BLOCK_SECONDS == 300