"""Регистрация переводимых полей моделей приложения projects."""

from modeltranslation.translator import TranslationOptions, register

from projects.models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectType,
    Tag,
)


@register(ProjectType)
class ProjectTypeTranslationOptions(TranslationOptions):
    """Настройки перевода справочника типов проектов."""

    fields = ('label',)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    """Настройки перевода справочника тегов."""

    fields = ('label',)


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    """Настройки перевода проекта."""

    fields = ('title', 'description')


@register(ProjectContentBlock)
class ProjectContentBlockTranslationOptions(TranslationOptions):
    """Настройки перевода контентного блока проекта."""

    fields = ('title', 'string_list', 'text', 'accented_text')


@register(ProjectBlockButton)
class ProjectBlockButtonTranslationOptions(TranslationOptions):
    """Настройки перевода кнопки контентного блока проекта."""

    fields = ('label',)
