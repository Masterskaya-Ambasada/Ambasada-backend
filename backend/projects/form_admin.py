from django import forms
from django.utils.translation import gettext_lazy as _
from import_export.forms import ConfirmImportForm, ImportForm

from .models import Project, ProjectContentBlock, ProjectType


class ProjectTypeImportForm(ImportForm):
    """Форма выбора типа проекта на первом этапе импорта Project."""

    project_type = forms.ModelChoiceField(
        queryset=ProjectType.objects.all(),
        required=True,
        label=_('Тип проекта'),
        help_text=_(' будет применен ко всем импортируемым проектам'),
    )


class ProjectTypeConfirmImportForm(ConfirmImportForm):
    """Форма выбора типа проекта на этапе подтверждения импорта Project."""

    project_type = forms.ModelChoiceField(
        queryset=ProjectType.objects.all(),
        required=True,
        label=_('Тип проекта'),
        help_text=_(' будет применен ко всем импортируемым проектам'),
    )


class ProjectImportForm(ImportForm):
    """Форма выбора проекта на первом этапе импорта ProjectContentBlock."""

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True,
        label=_('Проект в блоке'),
        help_text=_(' будет применен ко всем импортируемым блокам'),
    )
    variant = forms.ChoiceField(
        choices=ProjectContentBlock.Variant.choices,
        required=True,
        label=_('Вариант разметки'),
        help_text=_(' будет применен ко всем импортируемым блокам'),
        initial=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
    )


class ProjectConfirmImportForm(ConfirmImportForm):
    """Форма выбора проекта на этапе подтверждения импорта ProjectContentBlock."""

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True,
        label=_('Проект в блоке'),
        help_text=_(' будет применен ко всем импортируемым блокам'),
    )
    variant = forms.ChoiceField(
        choices=ProjectContentBlock.Variant.choices,
        required=True,
        label=_('Вариант разметки'),
        help_text=_(' будет применен ко всем импортируемым блокам'),
    )
