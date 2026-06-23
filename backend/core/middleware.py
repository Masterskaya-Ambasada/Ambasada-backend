import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _

security_logger = logging.getLogger('security')


class AdminLoginThrottleMiddleware:
    """
    Middleware для ограничения количества попыток входа в админку.

    Блокирует IP на 5 минут после 10 неудачных попыток в минуту.
    """

    MAX_ATTEMPTS = int(getattr(settings, 'ADMIN_LOGIN_MAX_ATTEMPTS', 10))
    WINDOW_SECONDS = int(getattr(settings, 'ADMIN_LOGIN_WINDOW_SECONDS', 5))  # ВЕРНУТЬ ЗНАЧЕНИЕ 60 ПОСЛЕ ТЕСТИРОВАНИЯ
    BLOCK_SECONDS = int(getattr(settings, 'ADMIN_LOGIN_BLOCK_SECONDS', 5))  # ВЕРНУТЬ ЗНАЧЕНИЕ 200 ПОСЛЕ ТЕСТИРОВАНИЯ

    def __init__(self, get_response):
        """Инициализация middleware."""
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/admin/login/' and request.method == 'POST':
            ip = self._get_ip(request)
            block_key = f'admin_login_block:{ip}'
            count_key = f'admin_login_count:{ip}'

            if cache.get(block_key):
                security_logger.warning('Admin login blocked: IP=%s', ip)
                return HttpResponse(
                    _('Слишком много попыток входа. Попробуйте позже.'),
                    status=429,
                )

            attempts = cache.get(count_key, 0) + 1
            cache.set(count_key, attempts, self.WINDOW_SECONDS)

            if attempts >= self.MAX_ATTEMPTS:
                cache.set(block_key, True, self.BLOCK_SECONDS)
                security_logger.warning('Admin login throttled: IP=%s, attempts=%d', ip, attempts)

        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        """Получение реального IP адреса клиента."""
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class FrontendLocaleNormalizeMiddleware(MiddlewareMixin):
    """Мидлварь для нормализации CamelCase кодов сербского языка в Accept-Language."""

    def process_request(self, request):
        accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE')

        if accept_lang:
            normalized = accept_lang.replace('sr-Latn', 'sr-latn').replace('sr-Cyrl', 'sr-cyrl')
            normalized = normalized.replace('sr_latn', 'sr-latn').replace('sr_cyrl', 'sr-cyrl')

            request.META['HTTP_ACCEPT_LANGUAGE'] = normalized
