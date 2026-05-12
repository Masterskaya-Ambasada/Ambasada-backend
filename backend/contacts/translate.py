from modeltranslation.translator import TranslationOptions, register

from .models import ContactPageContent


@register(ContactPageContent)
class ContactPageContentTranslationOptions(TranslationOptions):
    """Настройки перевода полей конфигурации сайта."""

    fields = ('donation_text',)
