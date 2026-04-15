"""Настройка мультиязычности моделей через django-modeltranslation."""

from modeltranslation.translator import TranslationOptions, register

from .models import AboutPage, GalleryImage, TeamMember, Value


@register(AboutPage)
class AboutPageTranslationOptions(TranslationOptions):
    """Переводимые поля страницы 'О нас'."""

    fields = (
        'hero_title',
        'hero_description',
        'about_title',
        'paragraph_1',
        'paragraph_2',
        'button_label',
        'values_title',
        'team_title',
        'team_button_label',
        'gallery_title',
    )
    required_languages = ('ru', 'en')


@register(Value)
class ValueTranslationOptions(TranslationOptions):
    """Переводимые поля ценностей."""

    fields = ('title', 'text')
    required_languages = ('ru', 'en')


@register(TeamMember)
class TeamMemberTranslationOptions(TranslationOptions):
    """Переводимые поля членов команды."""

    fields = ('name', 'role')
    required_languages = ('ru', 'en')


@register(GalleryImage)
class GalleryImageTranslationOptions(TranslationOptions):
    """Переводимые поля изображений галереи."""

    fields = ('alt',)
    required_languages = ('ru', 'en')
