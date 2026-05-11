from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language

from site_config.models import SiteConfig

from .constants import CACHE_KEY_SITE_CONFIG, SITE_CONFIG_SINGLETON_PK, TIMEOUT_CACHE


def get_config_cache_key(language=None):
    """Генерирует ключ кэша с учетом языка."""
    lang = language or get_language() or settings.LANGUAGE_CODE
    return f'{CACHE_KEY_SITE_CONFIG}:{lang}'


def get_site_config_cached(language=None):
    """Получает настройки сайта. Использует кэш для минимизации запросов к БД."""
    cache_key = get_config_cache_key(language)

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    config = SiteConfig.objects.prefetch_related('socials').filter(pk=SITE_CONFIG_SINGLETON_PK).first()

    if not config:
        return None

    data = {
        'site_name': config.site_name,
        'seo_description': config.seo_description,
        'privacy_policy': config.privacy_policy,
        'cookie_message': config.cookie_message,
        'cookie_button_text': config.cookie_button_text,
        'copyright': config.copyright,
        'socials': [
            {
                'social_type': s.get_social_type_display(),
                'url': s.url,
            }
            for s in config.socials.all()
            if getattr(s, 'is_active', True)
        ],
        'languages': [{'code': code, 'label': label} for code, label in settings.LANGUAGES],
    }

    cache.set(cache_key, data, timeout=TIMEOUT_CACHE)
    return data


def clear_config_cache():
    """Сброс кэша для всех языков."""
    keys = [f'{CACHE_KEY_SITE_CONFIG}:{lang}' for lang, _ in settings.LANGUAGES]
    cache.delete_many(keys)
