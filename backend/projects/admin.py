import os
import shutil

from core.base_admin import BaseAdminMixin, BaseTranslatedAdmin, ImportExportMixin
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from .constants import (
    ADMIN_EMPTY_VALUE,
    DEFAULT_FRONTEND_URL,
    FRONTEND_PROJECT_PATH_TEMPLATE,
)
from .models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectGalleryImage,
    ProjectType,
    Tag,
)
from .resources_admin import (
    ProjectTypeResource,
    TagResource,
)


@admin.register(Tag)
class TagAdmin(BaseTranslatedAdmin, ImportExportMixin):
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
class ProjectTypeAdmin(BaseTranslatedAdmin, ImportExportMixin):
    """Класс администрирования типов проектов."""

    resource_classes = [ProjectTypeResource]
    list_display = [
        'slug',
        'label_ru',
        'label_en',
        'label_sr_latn',
        'label_sr_cyrl',
    ]
    search_fields = ['slug']


class ProjectGalleryImageInline(NestedTabularInline):
    """Инлайн для картинок верхней карусели проекта."""

    model = ProjectGalleryImage
    extra = 0
    fk_name = 'project'
    fields = ('order', 'image')


class ProjectBlockButtonInline(NestedTabularInline):
    """Инлайн для кнопок внутри контентного блока (самый нижний уровень)."""

    model = ProjectBlockButton
    extra = 0
    fk_name = 'block'
    fields = ('order', 'label', 'type', 'url')


class ProjectContentBlockInline(BaseAdminMixin, NestedStackedInline):
    """Инлайн для контентных блоков внутри проекта (средний уровень)."""

    model = ProjectContentBlock
    extra = 0
    fk_name = 'project'
    inlines = [ProjectBlockButtonInline]
    ordering = ('order',)

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
        (_('Основная информация'), {'fields': ('variant', 'order', 'image', 'left_image')}),
        (
            _('Переводы (Русский)'),
            {'fields': ('title_ru', 'text_ru', 'accented_text_ru', 'string_list_ru'), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Английский)'),
            {'fields': ('title_en', 'text_en', 'accented_text_en', 'string_list_en'), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Сербский - Латиница)'),
            {
                'fields': ('title_sr_latn', 'text_sr_latn', 'accented_text_sr_latn', 'string_list_sr_latn'),
                'classes': ('collapse',),
            },
        ),
        (
            _('Переводы (Сербский - Кириллица)'),
            {
                'fields': ('title_sr_cyrl', 'text_sr_cyrl', 'accented_text_sr_cyrl', 'string_list_sr_cyrl'),
                'classes': ('collapse',),
            },
        ),
    )


@admin.register(Project)
class ProjectAdmin(BaseTranslatedAdmin, NestedModelAdmin):
    """Класс администрирования проектов с вложенными blocks и кнопками."""

    list_display = [
        'title',
        'slug',
        'year',
        'get_project_type',
        'is_published',
        'cover_image_thumbnail',
        'get_view_on_site',
    ]
    list_editable = ('is_published',)
    list_filter = ['project_type', 'year', 'is_published']
    ordering = ('-is_published', '-year')

    inlines = [ProjectGalleryImageInline, ProjectContentBlockInline]

    fieldsets = (
        (_('Основная информация'), {'fields': ('slug', 'year', 'project_type', 'tags', 'cover_image', 'is_published')}),
        (_('Переводы (Русский)'), {'fields': ('title_ru', 'description_ru'), 'classes': ('collapse',)}),
        (_('Переводы (Английский)'), {'fields': ('title_en', 'description_en'), 'classes': ('collapse',)}),
        (
            _('Переводы (Сербский - Латиница)'),
            {'fields': ('title_sr_latn', 'description_sr_latn'), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Сербский - Кириллица)'),
            {'fields': ('title_sr_cyrl', 'description_sr_cyrl'), 'classes': ('collapse',)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project_type')

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + ['slug'] if obj else self.readonly_fields

    def get_project_type(self, obj):
        return obj.project_type.label if obj.project_type else ADMIN_EMPTY_VALUE

    get_project_type.short_description = _('Тип проекта')
    get_project_type.admin_order_field = 'project_type__label'

    def get_view_on_site(self, obj):
        if obj.slug:
            frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FRONTEND_URL)
            absolute_url = FRONTEND_PROJECT_PATH_TEMPLATE.format(frontend_url=frontend_url, slug=obj.slug)
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">🔗 {}</a>',
                absolute_url,
                _('Просмотр на сайте'),
            )
        return ADMIN_EMPTY_VALUE

    get_view_on_site.short_description = _('Ссылка')

    def delete_queryset(self, request, queryset):
        """Безопасное удаление объектов с защитой файловой системы."""
        base_path = os.path.join(settings.MEDIA_ROOT, 'projects')
        for project in queryset:
            if project.slug and len(project.slug) > 2:
                project_dir = os.path.join(base_path, project.slug)
                if project_dir.startswith(base_path) and os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
        queryset.delete()

    def cover_image_thumbnail(self, obj):
        return self.get_image_thumbnail(obj, 'cover_image')

    cover_image_thumbnail.short_description = Project._meta.get_field('cover_image').verbose_name

    class Media:
        js = ('projects/js/admin_variant_toggle.js',)
        css = {'all': ('projects/css/admin_custom.css',)}
