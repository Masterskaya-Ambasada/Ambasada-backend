from modeltranslation.translator import TranslationOptions, register

from .models import ContactPageContent


@register(ContactPageContent)
class ContactPageContentTranslationOptions(TranslationOptions):
    """Настройки перевода контента контактной страницы."""

    fields = ('address',)
