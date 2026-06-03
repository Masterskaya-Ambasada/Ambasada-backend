from modeltranslation.translator import TranslationOptions, register

from .models import HomePageContent


@register(HomePageContent)
class HomePageContentTranslationOptions(TranslationOptions):
    """Настройки перевода контента главной страницы."""

    fields = (
        'title',
        'subtitle',
        'hero_button_label',
        'about_title',
        'about_text',
        'projects_title',
        'projects_button_label',
    )
