from modeltranslation.translator import TranslationOptions, register

from .models import SiteConfig


@register(SiteConfig)
class SiteConfigTranslationOptions(TranslationOptions):
    """Настройки перевода полей конфигурации сайта."""

    fields = (
        'site_name',
        'seo_description',
        'copyright',
        'privacy_policy',
        'cookie_message',
        'cookie_button_text',
    )
