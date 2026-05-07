"""Регистрация моделей Project, ProjectContentBlock, Tag, ProjectType в админ-панели."""

import os
import shutil

from core.base_admin import BaseAdmin, ImportExportMixin
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .constants import (
    ADMIN_EMPTY_VALUE,
    DEFAULT_FRONTEND_URL,
    FRONTEND_PROJECT_PATH_TEMPLATE,
)
from .models import Project, ProjectContentBlock, ProjectType, Tag
from .resources_admin import (
    ProjectTypeResource,
    TagResource,
)


@admin.register(Tag)
class TagAdmin(BaseAdmin, ImportExportMixin):
    """Класс администрирования Тегов."""

    resource_classes = [TagResource]
    list_display = [
        'slug',
        'label_ru',
        'label_en',
        'label_sr_latn',
        'label_sr_cyrl',
    ]

    search_fields = ['slug']


@admin.register(ProjectType)
class ProjectTypeAdmin(TagAdmin):
    """Класс администрирования типов проектов."""

    resource_classes = [ProjectTypeResource]


@admin.register(Project)
class ProjectAdmin(BaseAdmin):
    """Класс администрирования проектов."""

    list_display = [
        'title',
        'slug',
        'year',
        'get_project_type',
        'is_published',
        'cover_image_thumbnail',
        'get_view_on_site',
    ]
    list_filter = ['project_type', 'year', 'is_published']
    ordering = ('-is_published', '-year')
    fieldsets = (
        ('Основная информация', {'fields': ('slug', 'year', 'project_type', 'tags', 'cover_image', 'is_published')}),
        (
            'Переводы (Русский)',
            {
                'fields': ('title_ru', 'description_ru'),
                'classes': ('collapse',),
            },
        ),
        (
            'Переводы (English)',
            {
                'fields': ('title_en', 'description_en'),
                'classes': ('collapse',),
            },
        ),
        (
            'Prevodi (Srpski - Latinica)',
            {
                'fields': ('title_sr_latn', 'description_sr_latn'),
                'classes': ('collapse',),
            },
        ),
        (
            'Преводи (Српски - Ћирилица)',
            {
                'fields': ('title_sr_cyrl', 'description_sr_cyrl'),
                'classes': ('collapse',),
            },
        ),
    )

    def get_project_type(self, obj):
        """Отображение типа проекта."""
        return obj.project_type.label if obj.project_type else ADMIN_EMPTY_VALUE

    get_project_type.short_description = _('Тип проекта')
    get_project_type.admin_order_field = 'project_type__label'

    def get_view_on_site(self, obj):
        """Отображение ссылки на проект."""
        if obj.slug:
            frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FRONTEND_URL)
            absolute_url = FRONTEND_PROJECT_PATH_TEMPLATE.format(frontend_url=frontend_url, slug=obj.slug)
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">{} {}</a>',
                absolute_url,
                '🔗',
                _('Просмотр на сайте'),
            )
        return ADMIN_EMPTY_VALUE

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


@admin.register(ProjectContentBlock)
class ProjectContentBlockAdmin(BaseAdmin):
    """Класс администрирования детальной страницы проектов."""

    ordering = (
        'project__slug',
        'order',
    )
    list_display = [
        'order',
        'project__title',
        'title',
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
        ('Основная информация', {'fields': ('project', 'variant', 'order', 'image', 'left_image')}),
        (
            'Переводы (Русский)',
            {
                'fields': ('title_ru', 'text_ru', 'accented_text_ru', 'string_list_ru'),
                'classes': ('collapse',),
            },
        ),
        (
            'Переводы (English)',
            {
                'fields': ('title_en', 'text_en', 'accented_text_en', 'string_list_en'),
                'classes': ('collapse',),
            },
        ),
        (
            'Prevodi (Srpski - Latinica)',
            {
                'fields': ('title_sr_latn', 'text_sr_latn', 'accented_text_sr_latn', 'string_list_sr_latn'),
                'classes': ('collapse',),
            },
        ),
        (
            'Преводи (Српски - Ћирилица)',
            {
                'fields': ('title_sr_cyrl', 'text_sr_cyrl', 'accented_text_sr_cyrl', 'string_list_sr_cyrl'),
                'classes': ('collapse',),
            },
        ),
    )

    def delete_queryset(self, request, queryset):
        """Массовое удаление объектов ProjectContentBlock с удалением связанных файлов."""
        for project_block in queryset:
            if project_block.image and os.path.exists(project_block.image.path):
                os.remove(project_block.image.path)
            if project_block.left_image and os.path.exists(project_block.left_image.path):
                os.remove(project_block.left_image.path)
            project_block.delete()

    def main_image_thumbnail(self, obj):
        """Метод для отображения миниатюры изображения в списке."""
        return self.get_image_thumbnail(obj, 'image')

    main_image_thumbnail.short_description = ProjectContentBlock._meta.get_field('image').verbose_name

    def left_image_thumbnail(self, obj):
        """Метод для отображения миниатюры левого изображения в списке."""
        return self.get_image_thumbnail(obj, 'left_image')

    left_image_thumbnail.short_description = ProjectContentBlock._meta.get_field('left_image').verbose_name
