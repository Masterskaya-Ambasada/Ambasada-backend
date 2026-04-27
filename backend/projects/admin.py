import os
import shutil

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin, ImportMixin
from import_export.formats.base_formats import CSV
from modeltranslation.admin import TranslationAdmin

from .form_admin import ProjectTypeConfirmImportForm, ProjectTypeImportForm, ProjectImportForm, ProjectConfirmImportForm
from .models import Project, ProjectContentBlock, ProjectType, Tag
from .resources_admin import ProjectContentBlockResource, ProjectResource, ProjectTypeResource, TagResource
from tinymce.widgets import TinyMCE


class BaseAdmin(ImportExportModelAdmin, TranslationAdmin):
    """Базовый админ-класс."""

    empty_value_display = '-empty-'
    import_export_args = {
        'import_formats': ['csv'],
        'export_formats': ['csv'],
    }
    import_error_display = ('message',)
    ordering = ('slug',)
    tinymce_fields = []
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name in self.tinymce_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].widget = TinyMCE()
        return form
   
    def get_import_formats(self):
        """Ограничение формата импорта только CSV."""
        return [CSV]

    def get_export_formats(self):
        """Ограничение формата экспорта только CSV."""
        return [CSV]

    def get_image_thumbnail(self, obj, field_name):
        """Универсальный метод для создания миниатюры из поля ImageField."""
        image_field = getattr(obj, field_name, None)
        if image_field:
            photo_url = f'{settings.MEDIA_URL}{image_field}'
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 4px;" />', 
                photo_url)
        return '-empty-'


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    """Класс администрирования Тегов."""

    resource_classes = [TagResource]
    list_display = [
        'slug',
        'label_ru',
        'label_en',
        'label_sr_latn',
        'label_sr_cyrl'
        ]

    search_fields = ['slug']
    ordering = ['slug']


@admin.register(ProjectType)
class ProjectTypeAdmin(TagAdmin):
    """Класс администрирования типов проектов."""

    resource_classes = [ProjectTypeResource]


@admin.register(Project)
class ProjectAdmin(BaseAdmin, ImportMixin):
    """Класс администрирования проектов."""

    resource_classes = [ProjectResource]
    import_form_class = ProjectTypeImportForm
    confirm_form_class = ProjectTypeConfirmImportForm
    list_display = [
        'title',
        'slug',
        'year',
        'get_project_type',
        'is_published',
        'cover_image_thumbnail',
        'get_view_on_site'
        ]
    list_filter = [
        'project_type',
        'year',
        'is_published'
    ]
    ordering = ('-is_published', '-year')    
    fieldsets = (
        ('Основная информация', {
            'fields': ('slug', 'year', 'project_type', 'tags', 'cover_image', 'is_published')
        }),
        ('Переводы (Русский)', {
            'fields': ('title_ru', 'description_ru'),
            'classes': ('collapse',),
        }),
        ('Переводы (English)', {
            'fields': ('title_en', 'description_en'),
            'classes': ('collapse',),
        }),
        ('Prevodi (Srpski - Latinica)', {
            'fields': ('title_sr_latn', 'description_sr_latn'),
            'classes': ('collapse',),
        }),
        ('Преводи (Српски - Ћирилица)', {
            'fields': ('title_sr_cyrl', 'description_sr_cyrl'),
            'classes': ('collapse',),
        }),
    )

    def get_project_type(self, obj):
        """Отображение типа проекта."""
        return obj.project_type.label if obj.project_type else '-empty-'

    get_project_type.short_description = _('Тип проекта')
    get_project_type.admin_order_field = 'project_type__label'

    def get_view_on_site(self, obj):
        """Отображение ссылки на проект."""
        if obj.slug:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            absolute_url = f'{frontend_url}/projects/{obj.slug}/'
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">{} {}</a>',
                absolute_url, '🔗', _('Просмотр на сайте'))
        return '-empty-'
    get_view_on_site.short_description = _('Ссылка')

    def delete_queryset(self, request, queryset):
        """Массовое удаление объектов Project с удалением файлов фото."""
        for project in queryset:
            if project.cover_image:
                full_path = project.cover_image.path
                cover_dir = os.path.dirname(full_path)
                project_dir = os.path.dirname(cover_dir)
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
            project.delete()

    def cover_image_thumbnail(self, obj):
        """Метод для отображения миниатюры изображения в списке."""
        return self.get_image_thumbnail(obj, 'cover_image')
    cover_image_thumbnail.short_description = Project._meta.get_field('cover_image').verbose_name

    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)
        if import_form:
            initial['project_type'] = import_form.cleaned_data['project_type'].id
        return initial

    def get_import_data_kwargs(self, request, *args, **kwargs):
        form = kwargs.get('form', None)
        if form and hasattr(form, 'cleaned_data'):
            kwargs.update({'project_type': form.cleaned_data.get('project_type', None)})
        return kwargs


@admin.register(ProjectContentBlock)
class ProjectContentBlockAdmin(BaseAdmin, ImportMixin):
    resource_classes = [ProjectContentBlockResource]
    import_form_class = ProjectImportForm
    confirm_form_class = ProjectConfirmImportForm
    ordering = ('order', 'title',)
    list_display = [
        'order',
        'title',
        'accented_text',
        'text',
        'project__title',
        'main_image_thumbnail',
        'left_image_thumbnail',
    ]

    tinymce_fields = [
        'text_ru',
        'text_en',
        'text_sr_latn',
        'text_sr_cyrl',
        'accented_text_ru',
        'accented_text_en',
        'accented_text_sr_latn',
        'accented_text_sr_cyrl',
        ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'variant', 'order', 'image', 'left_image')
        }),
        ('Переводы (Русский)', {
            'fields': ('title_ru', 'text_ru', 'accented_text_ru', 'string_list_ru'),
            'classes': ('collapse',),
        }),
        ('Переводы (English)', {
            'fields': ('title_en', 'text_en', 'accented_text_en', 'string_list_en'),
            'classes': ('collapse',),
        }),
        ('Prevodi (Srpski - Latinica)', {
            'fields': ('title_sr_latn', 'text_sr_latn', 'accented_text_sr_latn', 'string_list_sr_latn'),
            'classes': ('collapse',),
        }),
        ('Преводи (Српски - Ћирилица)', {
            'fields': ('title_sr_cyrl', 'text_sr_cyrl', 'accented_text_sr_cyrl', 'string_list_sr_cyrl'),
            'classes': ('collapse',),
        }),
    )

    def delete_queryset(self, request, queryset):
        """Массовое удаление объектов ProjectContentBlock с удалением связанных файлов."""
        for project_block in queryset:
            if project_block.image and os.path.exists(project_block.image.path):
                os.remove(project_block.image.path)
            if project_block.left_image and os.path.exists(project_block.left_image.path):
                os.remove(project_block.left_image.path)
            project_block.delete()

    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)
        if import_form:
            initial['project'] = import_form.cleaned_data['project'].id
            initial['variant'] = import_form.cleaned_data['variant']
        return initial

    def get_import_data_kwargs(self, request, *args, **kwargs):
        form = kwargs.get("form", None)
        if form and hasattr(form, "cleaned_data"):
            kwargs.update({"project": form.cleaned_data.get("project", None),
                           "variant": form.cleaned_data.get("variant", None),})
        return kwargs

    def main_image_thumbnail(self, obj):
        """Метод для отображения миниатюры изображения в списке."""
        return self.get_image_thumbnail(obj, 'image')
    main_image_thumbnail.short_description = ProjectContentBlock._meta.get_field('image').verbose_name
    
    def left_image_thumbnail(self, obj):
        """Метод для отображения миниатюры левого изображения в списке."""
        return self.get_image_thumbnail(obj, 'left_image')
    main_image_thumbnail.short_description = ProjectContentBlock._meta.get_field('left_image').verbose_name
