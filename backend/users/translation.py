from modeltranslation.translator import TranslationOptions, register

from .models import User


@register(User)
class UserTranslationOptions(TranslationOptions):
    """Настройки перевода для модели User."""

    fields = (
        'position',
        'bio',
    )
