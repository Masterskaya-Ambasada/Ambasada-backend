"""Настройка мультиязычности моделей через django-modeltranslation."""

from modeltranslation.translator import TranslationOptions, register

from .models import AboutPage, AboutParagraph, GalleryImage, Value


@register(AboutPage)
class AboutPageTranslationOptions(TranslationOptions):
    """Переводимые поля страницы 'О нас'."""

    fields = (
        'hero_title',
        'hero_description',
        'about_title',
        'button_label',
        'values_title',
        'team_title',
        'team_button_label',
        'gallery_title',
    )
    required_languages = ('ru', 'en')


@register(AboutParagraph)
class AboutParagraphTranslationOptions(TranslationOptions):
    """Переводимые поля параграфов."""

    fields = ('first_sentence', 'main_text')
    required_languages = ('ru', 'en')


@register(Value)
class ValueTranslationOptions(TranslationOptions):
    """Переводимые поля ценностей."""

    fields = ('title', 'text')
    required_languages = ('ru', 'en')


@register(GalleryImage)
class GalleryImageTranslationOptions(TranslationOptions):
    """Переводимые поля изображений галереи."""

    fields = ('alt',)
    required_languages = ('ru', 'en')
