"""Tests for AdminLoginThrottleMiddleware."""

import pytest
from core.middleware import AdminLoginThrottleMiddleware
from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory


class TestAdminLoginThrottleMiddleware:
    """Test suite for admin login rate limiting middleware."""

    @pytest.fixture(autouse=True)
    def setup_cache(self):
        """Clear cache before each test."""
        cache.clear()
        yield
        cache.clear()

    @pytest.fixture
    def factory(self):
        """Request factory for creating test requests."""
        return RequestFactory()

    @pytest.fixture
    def middleware(self):
        """Middleware instance with mock response."""

        def get_response(request):
            return HttpResponse('OK', status=200)

        return AdminLoginThrottleMiddleware(get_response)

    @pytest.fixture
    def test_ip(self):
        """Test IP address."""
        return '192.168.1.100'

    @pytest.fixture
    def create_login_request(self, factory):
        """Helper fixture to create POST requests to admin login with IP."""
        def _create_login_request(ip, data=None):
            """Create a POST request to /admin/login/ with specified IP."""
            if data is None:
                data = {'username': 'admin', 'password': 'pass'}
            request = factory.post('/admin/login/', data)
            request.META['REMOTE_ADDR'] = ip
            return request
        return _create_login_request

    def test_normal_login_allowed(self, middleware, create_login_request, test_ip):
        """Test that normal login attempts are allowed under limit."""
        # Make 9 attempts (under the limit)
        for i in range(9):
            request = create_login_request(test_ip)
            response = middleware(request)
            assert response.status_code == 200
            assert response.content == b'OK'

        # Check cache state
        count_key = f'admin_login_count:{test_ip}'
        block_key = f'admin_login_block:{test_ip}'

        assert cache.get(count_key) == 9
        assert cache.get(block_key) is None

    def test_login_blocked_after_10_attempts(self, middleware, create_login_request, test_ip):
        """Test that login is blocked after 10 attempts."""
        # Make 10 attempts (at the limit) - all should return 200
        for i in range(10):
            request = create_login_request(test_ip)
            response = middleware(request)
            assert response.status_code == 200, f"Attempt {i+1} should return 200"

        # Next attempt (11th) should be blocked with 429
        request = create_login_request(test_ip)
        response = middleware(request)
        assert response.status_code == 429, "11th attempt should return 429 after block"
        assert b'Too many login attempts' in response.content

        # Check that block was set in cache
        block_key = f'admin_login_block:{test_ip}'
        assert cache.get(block_key) is True

    def test_blocked_ip_returns_429(self, middleware, create_login_request, test_ip):
        """Test that blocked IP returns 429 status."""
        # Simulate blocked state
        block_key = f'admin_login_block:{test_ip}'
        cache.set(block_key, True, 300)

        request = create_login_request(test_ip)
        response = middleware(request)

        assert response.status_code == 429
        assert b'Too many login attempts' in response.content

    def test_different_ips_independent_throttling(self, middleware, create_login_request):
        """Test that different IPs have independent throttling."""
        ip1 = '192.168.1.100'
        ip2 = '192.168.1.101'

        # Block first IP
        for _ in range(10):
            request = create_login_request(ip1, {})
            middleware(request)

        # First IP should be blocked
        block_key_1 = f'admin_login_block:{ip1}'
        assert cache.get(block_key_1) is True

        # Second IP should still be allowed
        request = create_login_request(ip2, {})
        response = middleware(request)
        assert response.status_code == 200

        block_key_2 = f'admin_login_block:{ip2}'
        assert cache.get(block_key_2) is None

    def test_non_post_requests_ignored(self, middleware, factory, test_ip):
        """Test that non-POST requests are not throttled."""
        request = factory.get('/admin/login/')
        request.META['REMOTE_ADDR'] = test_ip

        response = middleware(request)

        assert response.status_code == 200
        count_key = f'admin_login_count:{test_ip}'
        assert cache.get(count_key) is None

    def test_non_admin_paths_ignored(self, middleware, factory, test_ip):
        """Test that non-admin paths are not throttled."""
        request = factory.post('/some-other-path/', {})
        request.META['REMOTE_ADDR'] = test_ip

        response = middleware(request)

        assert response.status_code == 200
        count_key = f'admin_login_count:{test_ip}'
        assert cache.get(count_key) is None

    def test_forwarded_for_ip_extraction(self, middleware, factory):
        """Test that IP is correctly extracted from X-Forwarded-For header."""
        test_ip = '203.0.113.1'
        request = factory.post('/admin/login/', {})
        request.META['HTTP_X_FORWARDED_FOR'] = f'{test_ip}, 203.0.113.2'

        response = middleware(request)

        assert response.status_code == 200
        count_key = f'admin_login_count:{test_ip}'
        assert cache.get(count_key) == 1

    def test_count_key_expires_after_window(self, middleware, create_login_request, test_ip):
        """Test that count key expires after the window period."""
        # Make some attempts
        for _ in range(5):
            request = create_login_request(test_ip, {})
            middleware(request)

        count_key = f'admin_login_count:{test_ip}'
        assert cache.get(count_key) == 5

        # Manually expire the key (in real test you'd use time.sleep or mock)
        cache.set(count_key, None, 0)

        # Next attempt should start fresh count
        request = create_login_request(test_ip, {})
        response = middleware(request)
        assert response.status_code == 200
        assert cache.get(count_key) == 1

    def test_block_key_expires_after_block_period(self, middleware, create_login_request, test_ip):
        """Test that block key expires after the block period."""
        # Set up blocked state
        block_key = f'admin_login_block:{test_ip}'
        cache.set(block_key, True, 300)

        # Verify blocked
        request = create_login_request(test_ip, {})
        response = middleware(request)
        assert response.status_code == 429

        # Expire the block
        cache.set(block_key, None, 0)

        # Should be allowed now
        request = create_login_request(test_ip, {})
        response = middleware(request)
        assert response.status_code == 200

    def test_concurrent_attempts_handling(self, middleware, create_login_request, test_ip):
        """Test that concurrent attempts are properly counted."""
        # Simulate rapid attempts
        for _ in range(10):
            request = create_login_request(test_ip, {})
            middleware(request)

        block_key = f'admin_login_block:{test_ip}'
        count_key = f'admin_login_count:{test_ip}'

        # Should be blocked now
        assert cache.get(block_key) is True
        assert cache.get(count_key) == 10

        # Next attempt should be blocked
        request = create_login_request(test_ip, {})
        response = middleware(request)
        assert response.status_code == 429

    def test_get_ip_static_method(self):
        """Test the _get_ip static method directly."""
        factory = RequestFactory()

        # Test with X-Forwarded-For
        request = factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 203.0.113.2'
        ip = AdminLoginThrottleMiddleware._get_ip(request)
        assert ip == '203.0.113.1'

        # Test with REMOTE_ADDR
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        ip = AdminLoginThrottleMiddleware._get_ip(request)
        assert ip == '192.168.1.1'

        # Test fallback to default IP when no headers present
        request = factory.get('/')
        # Remove REMOTE_ADDR to test fallback (RequestFactory sets it by default)
        if 'REMOTE_ADDR' in request.META:
            del request.META['REMOTE_ADDR']
        ip = AdminLoginThrottleMiddleware._get_ip(request)
        assert ip == '0.0.0.0'

    def test_middleware_constants(self):
        """Test that middleware constants are properly set."""
        assert AdminLoginThrottleMiddleware.MAX_ATTEMPTS == 10
        assert AdminLoginThrottleMiddleware.WINDOW_SECONDS == 60
        assert AdminLoginThrottleMiddleware.BLOCK_SECONDS == 300

    def test_cache_keys_format(self, middleware, create_login_request, test_ip):
        """Test that cache keys are formatted correctly."""
        request = create_login_request(test_ip, {})
        middleware(request)

        count_key = f'admin_login_count:{test_ip}'
        block_key = f'admin_login_block:{test_ip}'

        # Verify keys exist and have correct values
        assert cache.get(count_key) is not None
        assert cache.get(block_key) is None  # Not blocked yet

        # Verify key format
        assert count_key.startswith('admin_login_count:')
        assert block_key.startswith('admin_login_block:')
        assert test_ip in count_key
        assert test_ip in block_key

    def test_reset_after_block_expires(self, middleware, create_login_request, test_ip):
        """Test that user can login again after block expires."""
        # Make 10 attempts to trigger block
        for _ in range(10):
            request = create_login_request(test_ip, {})
            middleware(request)

        # Verify blocked
        block_key = f'admin_login_block:{test_ip}'
        assert cache.get(block_key) is True

        # Simulate block expiration
        cache.set(block_key, None, 0)

        # Clear count as well (in real scenario count would also expire)
        count_key = f'admin_login_count:{test_ip}'
        cache.set(count_key, None, 0)

        # Should be able to login again
        request = create_login_request(test_ip, {})
        response = middleware(request)
        assert response.status_code == 200
        assert cache.get(count_key) == 1

    def test_x_forwarded_for_with_multiple_ips(self, middleware, factory):
        """Test X-Forwarded-For with multiple IPs extracts first one."""
        test_ip = '203.0.113.10'
        request = factory.post('/admin/login/', {})
        request.META['HTTP_X_FORWARDED_FOR'] = f'{test_ip}, 203.0.113.11, 203.0.113.12'

        response = middleware(request)

        assert response.status_code == 200
        count_key = f'admin_login_count:{test_ip}'
        assert cache.get(count_key) == 1

        # Verify other IPs are not counted
        other_ip_key = 'admin_login_count:203.0.113.11'
        assert cache.get(other_ip_key) is None
        count_key = f'admin_login_count:{test_ip}'
        assert cache.get(count_key) == 1

        # Verify other IPs are not counted
        other_ip_key = 'admin_login_count:203.0.113.11'
        assert cache.get(other_ip_key) is None
