from site_config.cache import format_locale_code_for_frontend, format_social_url_for_frontend, get_config_cache_key


def test_format_locale_code_for_frontend_uses_script_title_case():
    """Проверяет формат кодов локалей, который ожидает фронтенд."""
    assert format_locale_code_for_frontend('ru') == 'ru'
    assert format_locale_code_for_frontend('en') == 'en'
    assert format_locale_code_for_frontend('sr-latn') == 'sr-Latn'
    assert format_locale_code_for_frontend('sr-cyrl') == 'sr-Cyrl'


def test_get_config_cache_key_normalizes_language_code():
    """Проверяет, что ключ кэша остается в формате внутренних кодов Django."""
    assert get_config_cache_key('sr-Latn') == 'site_config:v1.1:sr-latn'


def test_format_social_url_for_frontend_returns_plain_email_for_email_social_type():
    """Проверяет, что Init API отдает email без mailto-префикса."""
    assert format_social_url_for_frontend('email', 'hello@example.com') == 'hello@example.com'
    assert format_social_url_for_frontend('email', 'mailto:hello@example.com') == 'hello@example.com'
