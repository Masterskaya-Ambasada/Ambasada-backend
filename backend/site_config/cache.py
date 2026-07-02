from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language
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


def format_social_url_for_frontend(social_type: str, url: str) -> str:
    """Возвращает URL соцсети в формате, который ожидает фронтенд."""
    normalized_url = url.strip()
    if social_type == 'email':
        return normalized_url.removeprefix('mailto:')
    return normalized_url


def get_config_cache_key(language=None) -> str:
    """Генерирует ключ кэша для Init запроса с учетом языка."""
    lang = (language or get_language() or settings.LANGUAGE_CODE).lower()
    return f'{CACHE_KEY_SITE_CONFIG}:{lang}'


def get_site_config_cached(language=None) -> dict | None:
    """Получает настройки сайта для Init запроса."""
    lang = (language or get_language() or settings.LANGUAGE_CODE).lower()
    cache_key = f'{CACHE_KEY_SITE_CONFIG}:{lang}'

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Формируем суффикс поля для базы данных (например, 'sr-latn' -> 'sr_latn')
    lang_suffix = lang.replace('-', '_')

    config = SiteConfig.objects.prefetch_related('socials').filter(pk=SITE_CONFIG_SINGLETON_PK).first()
    if not config:
        return None

    data = {
        'site_name': getattr(config, f'site_name_{lang_suffix}', '') or config.site_name or '',
        'seo_description': getattr(config, f'seo_description_{lang_suffix}', '') or config.seo_description or '',
        'privacy_policy': getattr(config, f'privacy_policy_{lang_suffix}', '') or config.privacy_policy or '',
        'cookie_message': getattr(config, f'cookie_message_{lang_suffix}', '') or config.cookie_message or '',
        'cookie_button_text': getattr(config, f'cookie_button_text_{lang_suffix}', '')
        or config.cookie_button_text
        or '',
        'copyright': getattr(config, f'copyright_{lang_suffix}', '') or config.copyright or '',
        'team_title': getattr(config, f'team_title_{lang_suffix}', '') or config.team_title or '',
        'main_team_button_label': getattr(config, f'main_team_button_label_{lang_suffix}', '')
        or config.main_team_button_label
        or '',
        'about_team_button_label': getattr(config, f'about_team_button_label_{lang_suffix}', '')
        or config.about_team_button_label
        or '',
        'legal_links': {},
        'socials': [
            {
                'social_type': s.get_social_type_display(),
                'url': format_social_url_for_frontend(s.social_type, s.url),
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
    lang = (language or get_language() or settings.LANGUAGE_CODE).lower()
    cache_key = f'{CACHE_KEY_FULL_CONFIG}:{lang}'

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Формируем точный суффикс поля для базы данных (например, 'sr_latn' или 'sr_cyrl')
    lang_suffix = lang.replace('-', '_')

    site_config = SiteConfig.objects.filter(pk=SITE_CONFIG_SINGLETON_PK).first()
    home_content = HomePageContent.objects.filter(pk=HOME_PAGE_SINGLETON_PK).first()

    if not home_content and not site_config:
        return {}

    data = {
        'site_name': (
            getattr(site_config, f'site_name_{lang_suffix}', '') or (site_config.site_name if site_config else '')
        )
        or 'Ambasada',
        # --- HERO BLOCK ---
        'title': getattr(home_content, f'title_{lang_suffix}', '') if home_content else '',
        'subtitle': getattr(home_content, f'subtitle_{lang_suffix}', '') if home_content else '',
        'image_left': (home_content.image_left.url if home_content and home_content.image_left else None),
        'image_right': (home_content.image_right.url if home_content and home_content.image_right else None),
        'hero_button_label': getattr(home_content, f'hero_button_label_{lang_suffix}', '') if home_content else '',
        'hero_button_link': ((home_content.hero_button_link if home_content else '') or '/projects'),
        # --- ABOUT PREVIEW ---
        'about_title': getattr(home_content, f'about_title_{lang_suffix}', '') if home_content else '',
        'about_text': getattr(home_content, f'about_text_{lang_suffix}', '') if home_content else '',
        'about_image': (home_content.about_image.url if home_content and home_content.about_image else None),
        # --- TEAM PREVIEW ---
        'team_title': (
            getattr(site_config, f'team_title_{lang_suffix}', '') or (site_config.team_title if site_config else '')
        )
        or '',
        'main_team_button_label': (
            getattr(site_config, f'main_team_button_label_{lang_suffix}', '')
            or (site_config.main_team_button_label if site_config else '')
        )
        or '',
        'about_team_button_label': (
            getattr(site_config, f'about_team_button_label_{lang_suffix}', '')
            or (site_config.about_team_button_label if site_config else '')
        )
        or '',
        'team_button_link': ((site_config.team_button_link if site_config else '') or '/contacts'),
        # --- PROJECTS PREVIEW ---
        'projects_title': getattr(home_content, f'projects_title_{lang_suffix}', '') if home_content else '',
        'projects_button_label': getattr(home_content, f'projects_button_label_{lang_suffix}', '')
        if home_content
        else '',
        'projects_button_link': ((home_content.projects_button_link if home_content else '') or '/projects'),
    }

    cache.set(cache_key, data, timeout=TIMEOUT_CACHE)
    return data


def clear_config_cache():
    """Сброс кэша конфигурации для всех активных языков."""
    languages_to_clear = [lang_code.lower() for lang_code, _ in settings.LANGUAGES]

    guaranteed_langs = ['sr-latn', 'sr-cyrl', 'en', 'ru']
    for lang in guaranteed_langs:
        if lang not in languages_to_clear:
            languages_to_clear.append(lang)

    for lang_lower in languages_to_clear:
        cache.delete(f'{CACHE_KEY_SITE_CONFIG}:{lang_lower}')
        cache.delete(f'{CACHE_KEY_FULL_CONFIG}:{lang_lower}')
