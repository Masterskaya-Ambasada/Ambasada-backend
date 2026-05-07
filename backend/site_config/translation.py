from modeltranslation.translator import TranslationOptions, register

from .models import SiteConfig


@register(SiteConfig)
class SiteConfigTranslationOptions(TranslationOptions):
    fields = (
        'site_name',
        'seo_description',
        'copyright',
        'privacy_policy',
        'cookie_message',
        'cookie_button_text',
    )
