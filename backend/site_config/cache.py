from django.conf import settings
from django.core.cache import cache
from django.utils import translation
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from home.constants import HOME_PAGE_SINGLETON_PK
from home.models import HomePageContent

from site_config.models import SiteConfig

from .constants import (
    CACHE_KEY_FULL_CONFIG,
    CACHE_KEY_SITE_CONFIG,
    SITE_CONFIG_SINGLETON_PK,
    TIMEOUT_CACHE,
)


def format_locale_code_for_frontend(code: str) -> str:
    """Возвращает код локали в формате, который ожидает фронтенд."""
    language, separator, script = code.partition('-')
    if not separator:
        return language
    return f'{language}-{script.capitalize()}'


def get_config_cache_key(language=None) -> str:
    """Генерирует ключ кэша для Init запроса с учетом языка."""
    lang = language or get_language() or settings.LANGUAGE_CODE
    return f'{CACHE_KEY_SITE_CONFIG}:{lang.lower()}'


def get_site_config_cached(language=None) -> dict | None:
    """Получает настройки сайта для Init запроса. Использует встроенные фолбеки modeltranslation."""
    lang = language or get_language() or settings.LANGUAGE_CODE
    cache_key = f'{CACHE_KEY_SITE_CONFIG}:{lang.lower()}'

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    with translation.override(lang):
        config = SiteConfig.objects.prefetch_related('socials').filter(pk=SITE_CONFIG_SINGLETON_PK).first()
        if not config:
            return None
        data = {
            'site_name': config.site_name or '',
            'seo_description': config.seo_description or '',
            'privacy_policy': config.privacy_policy or '',
            'cookie_message': config.cookie_message or '',
            'cookie_button_text': config.cookie_button_text or '',
            'copyright': config.copyright or '',
            'team_title': config.team_title or _('Команда'),
            'main_team_button_label': config.main_team_button_label or '',
            'about_team_button_label': config.about_team_button_label or '',
            'legal_links': {},
            'socials': [
                {
                    'social_type': s.get_social_type_display(),
                    'url': s.url,
                }
                for s in config.socials.all()
                if getattr(s, 'is_active', True)
            ],
            'languages': [
                {'code': format_locale_code_for_frontend(code), 'label': label} for code, label in settings.LANGUAGES
            ],
        }

    cache.set(cache_key, data, timeout=TIMEOUT_CACHE)
    return data


def get_full_config_cached(language=None) -> dict:
    """Возвращает полный локализованный словарь полей для Главной страницы."""
    lang = language or get_language() or settings.LANGUAGE_CODE
    cache_key = f'{CACHE_KEY_FULL_CONFIG}:{lang.lower()}'

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    with translation.override(lang):
        site_config = SiteConfig.objects.filter(pk=SITE_CONFIG_SINGLETON_PK).first()
        home_content = HomePageContent.objects.filter(pk=HOME_PAGE_SINGLETON_PK).first()

        if not home_content and not site_config:
            return {}

        data = {
            'site_name': (site_config.site_name if site_config else '') or _('Ambasada'),
            # --- HERO BLOCK (из HomePageContent) ---
            'title': home_content.title if home_content else '',
            'subtitle': home_content.subtitle if home_content else '',
            'image_left': (home_content.image_left.url if home_content and home_content.image_left else None),
            'image_right': (home_content.image_right.url if home_content and home_content.image_right else None),
            'hero_button_label': home_content.hero_button_label if home_content else '',
            'hero_button_link': ((home_content.hero_button_link if home_content else '') or '/projects'),
            # --- ABOUT PREVIEW (из HomePageContent) ---
            'about_title': home_content.about_title if home_content else '',
            'about_text': home_content.about_text if home_content else '',
            'about_image': (home_content.about_image.url if home_content and home_content.about_image else None),
            # --- TEAM PREVIEW (Из SiteConfig) ---
            'team_title': (site_config.team_title if site_config else '') or _('Команда'),
            'main_team_button_label': (
                (site_config.main_team_button_label if site_config else '') or _('Присоединиться к команде')
            ),
            'about_team_button_label': (
                (site_config.about_team_button_label if site_config else '') or _('Присоединиться')
            ),
            'team_button_link': ((site_config.team_button_link if site_config else '') or '/contacts'),
            # --- PROJECTS PREVIEW (из HomePageContent) ---
            'projects_title': home_content.projects_title if home_content else '',
            'projects_button_label': (home_content.projects_button_label if home_content else ''),
            'projects_button_link': ((home_content.projects_button_link if home_content else '') or '/projects'),
        }

    cache.set(cache_key, data, timeout=TIMEOUT_CACHE)
    return data


def clear_config_cache():
    """Сброс кэша конфигурации (как базовой, так и полной) для всех языков."""
    for lang_code, label in settings.LANGUAGES:
        lang_lower = lang_code.lower()
        cache.delete(f'{CACHE_KEY_SITE_CONFIG}:{lang_lower}')
        cache.delete(f'{CACHE_KEY_FULL_CONFIG}:{lang_lower}')
