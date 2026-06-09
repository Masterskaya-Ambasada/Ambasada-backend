from django.conf import settings
from site_config.cache import format_locale_code_for_frontend


def get_languages():
    """Получение языков из настроек проекта."""
    return [{'code': format_locale_code_for_frontend(code), 'label': label} for code, label in settings.LANGUAGES]
