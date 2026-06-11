from modeltranslation.translator import TranslationOptions, register

from .models import SecurityPolicy


@register(SecurityPolicy)
class SecurityPolicyTranslationOptions(TranslationOptions):
    """Регистрируем поля модели SecurityPolicy для перевода."""

    fields = ('text',)
