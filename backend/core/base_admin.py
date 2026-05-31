from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
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

    image_preview_input_class = 'admin-image-preview-input'
    empty_value_display = '-empty-'
    import_error_display = ('message',)
    ordering = ('id',)
    tinymce_fields = []

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Добавляет общие настройки виджетов для полей админки."""
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        return self.add_image_preview_widget_class(db_field, formfield)

    def add_image_preview_widget_class(self, db_field, formfield):
        """Помечает ImageField для live-preview выбранного файла в админке."""
        if formfield and isinstance(db_field, models.ImageField):
            attrs = formfield.widget.attrs.copy()
            widget_classes = attrs.get('class', '').split()
            if self.image_preview_input_class not in widget_classes:
                widget_classes.append(self.image_preview_input_class)
            attrs['class'] = ' '.join(widget_classes)
            formfield.widget.attrs = attrs
        return formfield

    def get_form(self, request, obj=None, **kwargs):
        """Подменяет виджеты для полей, указанных в tinymce_fields."""
        form = super().get_form(request, obj, **kwargs)
        for field_name in self.tinymce_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].widget = TinyMCE()
        return form

    def get_formset(self, request, obj=None, **kwargs):
        """Переопределение формы для поддержки TinyMCE во inline-моделях."""
        formset = super().get_formset(request, obj, **kwargs)
        if hasattr(formset, 'form') and hasattr(formset.form, 'base_fields'):
            for field_name in self.tinymce_fields:
                if field_name in formset.form.base_fields:
                    formset.form.base_fields[field_name].widget = TinyMCE()
        return formset

    def get_image_thumbnail(self, obj, field_name):
        """Универсальный безопасный метод для создания миниатюры из поля ImageField."""
        image_field = getattr(obj, field_name, None)
        if image_field and hasattr(image_field, 'url') and image_field.name:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 4px;" />',
                image_field.url,
            )
        return self.empty_value_display

    def get_admin_image_preview(self, obj, field_name, width=240, height=160):
        """Выводит ограниченное по размеру превью изображения в форме админки."""
        image_field = getattr(obj, field_name, None)
        if image_field and hasattr(image_field, 'url') and image_field.name:
            image_width, image_height = self.get_image_preview_size(image_field, width, height)
            return format_html(
                (
                    '<div class="admin-image-preview admin-image-preview--saved" '
                    'style="--admin-image-preview-width: {}px; --admin-image-preview-height: {}px; '
                    'box-sizing: border-box; display: inline-flex; align-items: center; justify-content: center; '
                    'width: {}px; height: {}px; max-width: 100%; max-height: {}px; '
                    'margin-top: 8px; padding: 6px; overflow: hidden; '
                    'background: #f8fafc; border: 1px solid #cfd8dc; border-radius: 6px;">'
                    '<a href="{}" target="_blank" rel="noopener noreferrer" style="display: block; line-height: 0;">'
                    '<img src="{}" alt="" loading="lazy" width="{}" height="{}" '
                    'style="display: block; width: {}px !important; height: {}px !important; '
                    'max-width: {}px !important; max-height: {}px !important;">'
                    '</a>'
                    '</div>'
                ),
                width,
                height,
                width,
                height,
                height,
                image_field.url,
                image_field.url,
                image_width,
                image_height,
                image_width,
                image_height,
                width,
                height,
            )
        return format_html('<span class="admin-image-preview-empty">{}</span>', _('Нет файла'))

    def get_image_preview_size(self, image_field, max_width, max_height):
        """Рассчитывает размер превью без искажения пропорций."""
        try:
            source_width = image_field.width
            source_height = image_field.height
        except Exception:
            return max_width, max_height

        if not source_width or not source_height:
            return max_width, max_height

        scale = min(max_width / source_width, max_height / source_height)
        return max(round(source_width * scale), 1), max(round(source_height * scale), 1)


class BaseAdmin(BaseAdminMixin, admin.ModelAdmin):
    """Базовый админ-класс для обычных моделей."""


class BaseTranslatedAdmin(BaseAdminMixin, TranslationAdmin):
    """Базовый админ-класс для моделей с поддержкой перевода."""
