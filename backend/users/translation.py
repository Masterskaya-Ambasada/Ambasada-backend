from modeltranslation.translator import TranslationOptions, register

from .models import User


@register(User)
class UserTranslationOptions(TranslationOptions):
    """Модель перевода для модели User, с указанием переводимых полей."""
