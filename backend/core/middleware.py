import logging

from django.core.cache import cache
from django.http import HttpResponse

security_logger = logging.getLogger('security')


class AdminLoginThrottleMiddleware:
    """
    Limits the number of login attempts to Django Admin.

    10 attempts per minute from a single IP address, then a 5-minute lockout.
    """

    MAX_ATTEMPTS = 10
    WINDOW_SECONDS = 60  # attempt counting window
    BLOCK_SECONDS = 300  # blocking time after exceeding

    def __init__(self, get_response):
        """Initialize middleware with the next handler in the chain."""
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/admin/login/' and request.method == 'POST':
            ip = self._get_ip(request)
            block_key = f'admin_login_block:{ip}'
            count_key = f'admin_login_count:{ip}'

            # Checking the blocking
            if cache.get(block_key):
                security_logger.warning('Admin login blocked: IP=%s', ip)
                return HttpResponse(
                    'Too many login attempts. Try again later.',
                    status=429,
                )

            # Count attempts
            attempts = cache.get(count_key, 0) + 1
            cache.set(count_key, attempts, self.WINDOW_SECONDS)

            if attempts >= self.MAX_ATTEMPTS:
                cache.set(block_key, True, self.BLOCK_SECONDS)
                security_logger.warning('Admin login throttled: IP=%s, attempts=%d', ip, attempts)

        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
