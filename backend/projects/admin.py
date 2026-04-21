import os

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from import_export import resources
from .models import Project, ProjectType, Tag, ProjectContentBlock
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from import_export.admin import ImportExportModelAdmin

from modeltranslation.utils import build_localized_fieldname
from django.conf import settings
from deep_translator import GoogleTranslator, MyMemoryTranslator
# deep-translator
from google_trans_new import google_translator
import requests 
import re
from django.core.exceptions import ValidationError
from django.contrib import messages
from import_export.formats.base_formats import CSV
from .resources_admin import TagResource, ProjectContentBlockResource, ProjectTypeResource


class BaseAdmin(ImportExportModelAdmin, TranslationAdmin):
    """Базовый админ-класс."""

    empty_value_display = '-empty-'
    import_export_args = {
        'import_formats': ['csv'],
        'export_formats': ['csv'],
    }
    import_error_display = ("message",)

    def get_import_formats(self):
        """Ограничиваем форматы импорта только CSV"""
        return [CSV]
    
    def get_export_formats(self):
        """Ограничиваем форматы экспорта только CSV"""
        return [CSV]

    def get_exclude(self, request, obj=None):
        """Исключаем все поля, заканчивающиеся на _sr_cyrl."""
        exclude = super().get_exclude(request, obj) or []
        exclude = list(exclude)
        for field in self.model._meta.get_fields():
            if field.name.endswith('_sr_cyrl') and field.name not in exclude:
                exclude.append(field.name)
        return exclude


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    """Класс администрирования Тегов."""

    resource_classes = [TagResource]
    ordering = ('slug',)
    list_display = [
        'slug', 
        'label', 
        'label_ru', 
        'label_en', 
        'label_sr_latn'
    ]

    search_fields = ['slug']


@admin.register(ProjectType)
class ProjectTypeAdmin(BaseAdmin):
    """Класс администрирования типов проектов."""

    resource_classes = [ProjectTypeResource]
    ordering = ('slug',)
    list_display = [
        'slug', 
        'label', 
        'label_ru', 
        'label_en', 
        'label_sr_latn'
    ]
    search_fields = ['slug']


@admin.register(ProjectContentBlock)
class ProjectContentBlockAdmin(BaseAdmin):
    resources_classes = [ProjectContentBlockResource]
    # ordering = ('slug',)
    # list_display = [
    #     'slug', 
    #     'label', 
    #     'label_ru', 
    #     'label_en', 
    #     'label_sr_latn'
    # ]
 

@admin.register(Project)
class ProjectAdmin(BaseAdmin):
    """Класс администрирования проектов."""

    resources_classes = [ProjectContentBlockResource]
    list_display = [
        'title',
        'year',
        'get_project_type',
        'is_published',
        'get_view_on_site'
        ]
    list_filter = [
        'project_type',
        'year',
        ]
    ordering = ('-is_published', '-year')

    def get_project_type(self, obj):
        """Отображение типа проекта."""
        return obj.project_type.label if obj.project_type else '-'
    get_project_type.short_description = _('Тип проекта')  # добавить перевод
    get_project_type.admin_order_field = 'project_type__label'

    def get_view_on_site(self, obj):
        """Отображение ссылки на проект."""
        #return f"{frontend_url}/projects/{obj.slug}/"
        return 'В разработке'
    get_view_on_site.short_description = _('Ссылка') # добавить перевод