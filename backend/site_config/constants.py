from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

CACHE_KEY_INIT = 'site_config_init'

COOKIE_BUTTON_TEXT_MAX_LENGTH = 20
SITE_NAME_MAX_LENGTH = 100
LANGUAGE_CODE_MAX_LENGTH = 10
SOCIAL_TYPE_MAX_LENGTH = 20
SEO_DESCRIPTION_MAX_LENGTH = 250
COPYRIGHT_MAX_LENGTH = 150

DEFAULT_COOKIE_BUTTON_TEXT = 'OK'
DEFAULT_COOKIE_MESSAGE = _('Мы используем технические cookie для корректной работы сайта.')
SITE_CONFIG_SINGLETON_PK = 1


def get_config_cache_key(language=None):
    """Возвращает cache key с учетом активного языка."""
    lang = language or get_language() or settings.LANGUAGE_CODE
    return f'{CACHE_KEY_INIT}:{lang}'


def clear_config_cache():
    """Очищает cache конфигурации сайта для всех языков."""
    cache_keys = [get_config_cache_key(language_code) for language_code, _ in settings.LANGUAGES]

    cache.delete_many(cache_keys)
