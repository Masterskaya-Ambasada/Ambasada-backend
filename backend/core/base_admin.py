"""Базовый функционал Админ-моделей."""

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import CSV
from modeltranslation.admin import TranslationAdmin
from tinymce.widgets import TinyMCE


class ImportExportMixin(ImportExportModelAdmin):
    """Миксин функционала импорта/экспорта csv."""

    import_export_args = {
        'import_formats': ['csv'],
        'export_formats': ['csv'],
    }

    def get_import_formats(self):
        """Ограничение формата импорта только CSV."""
        return [CSV]

    def get_export_formats(self):
        """Ограничение формата экспорта только CSV."""
        return [CSV]


class BaseAdminMixin:
    """Базовый миксин с общей логикой для админ-классов."""

    empty_value_display = '-empty-'
    import_error_display = ('message',)
    ordering = ('slug',)
    tinymce_fields = []

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name in self.tinymce_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].widget = TinyMCE()
        return form

    def get_image_thumbnail(self, obj, field_name):
        """Универсальный метод для создания миниатюры из поля ImageField."""
        image_field = getattr(obj, field_name, None)
        if image_field:
            photo_url = f'{settings.MEDIA_URL}{image_field}'
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 4px;" />', photo_url
            )
        return '-empty-'


class BaseAdmin(BaseAdminMixin, admin.ModelAdmin):
    """Базовый админ-класс для обычных моделей."""


class BaseTranslatedAdmin(BaseAdminMixin, TranslationAdmin):
    """Базовый админ-класс для моделей с поддержкой перевода."""
