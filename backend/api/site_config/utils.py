from django.conf import settings


def get_languages():
    """Получение языков из настроек проекта."""
    return [{'code': code, 'label': label} for code, label in settings.LANGUAGES]
