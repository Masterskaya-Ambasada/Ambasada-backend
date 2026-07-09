from __future__ import annotations

import os
import shutil

from core.base_admin import BaseAdminMixin, BaseTranslatedAdmin, ImportExportMixin
from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from .admin_forms import ProjectContentBlockInlineFormSet
from .constants import (
    ADMIN_EMPTY_VALUE,
    BLOCK_BUTTON_ADMIN_HELP_TEXTS,
    CONTENT_BLOCK_ADMIN_HELP_TEXTS,
    CYRILLIC_TO_LATIN,
    DEFAULT_FRONTEND_URL,
    FRONTEND_PROJECT_PATH_TEMPLATE,
    GALLERY_IMAGE_ADMIN_HELP_TEXTS,
    PROJECT_ADMIN_HELP_TEXTS,
    REFERENCE_ADMIN_HELP_TEXTS,
    REFERENCE_TRANSLATED_FIELDS,
    TRANSLATED_FIELD_SUFFIXES,
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


def get_admin_help_text(field_name: str, help_texts: dict[str, str]) -> str | None:
    """Возвращает подсказку для обычного или переведенного поля modeltranslation."""
    if field_name in help_texts:
        return help_texts[field_name]
    for suffix in TRANSLATED_FIELD_SUFFIXES:
        if field_name.endswith(suffix):
            return help_texts.get(field_name[: -len(suffix)])
    return None


def apply_admin_help_text(formfield, db_field_name: str, help_texts: dict[str, str]):
    """Подставляет проектные подсказки в поля админки без изменения модели и миграций."""
    if formfield is not None:
        help_text = get_admin_help_text(db_field_name, help_texts)
        if help_text is not None:
            formfield.help_text = help_text
    return formfield


def make_slug_from_russian_title(title: str) -> str:
    """Создаёт URL-safe slug из русского названия проекта."""
    return slugify(title.lower().translate(CYRILLIC_TO_LATIN))


class ProjectHelpTextMixin:
    """Добавляет подробные подсказки к полям проектной админки."""

    admin_help_texts = {}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        return apply_admin_help_text(formfield, db_field.name, self.admin_help_texts)


class ProjectAdminForm(forms.ModelForm):
    """Форма проекта с серверной генерацией slug из русского названия."""

    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Инициализирует форму, снимая обязательность со slug и очищая help_text у тегов."""
        super().__init__(*args, **kwargs)
        if 'slug' in self.fields:
            self.fields['slug'].required = False

    def clean(self):
        """Валидирует данные формы и автоматически генерирует slug, если он не заполнен."""
        cleaned_data = super().clean()
        if not cleaned_data.get('slug'):
            cleaned_data['slug'] = make_slug_from_russian_title(cleaned_data.get('title_ru', ''))
        return cleaned_data


@admin.register(Tag)
class TagAdmin(ProjectHelpTextMixin, BaseTranslatedAdmin, ImportExportMixin):
    """Класс администрирования Тегов."""

    admin_help_texts = REFERENCE_ADMIN_HELP_TEXTS
    resource_classes = [TagResource]
    fields = REFERENCE_TRANSLATED_FIELDS
    list_display = REFERENCE_TRANSLATED_FIELDS
    search_fields = ['slug']


@admin.register(ProjectType)
class ProjectTypeAdmin(ProjectHelpTextMixin, BaseTranslatedAdmin, ImportExportMixin):
    """Класс администрирования типов проектов."""

    admin_help_texts = REFERENCE_ADMIN_HELP_TEXTS
    resource_classes = [ProjectTypeResource]
    fields = REFERENCE_TRANSLATED_FIELDS
    list_display = REFERENCE_TRANSLATED_FIELDS
    search_fields = ['slug']


class ProjectGalleryImageInline(ProjectHelpTextMixin, BaseAdminMixin, NestedTabularInline):
    """Инлайн для картинок верхней карусели проекта."""

    admin_help_texts = GALLERY_IMAGE_ADMIN_HELP_TEXTS
    model = ProjectGalleryImage
    extra = 0
    fk_name = 'project'
    ordering = ('order',)
    readonly_fields = ('image_preview',)
    fields = ('order', 'image', 'image_preview')

    @admin.display(description=_('Превью'))
    def image_preview(self, obj):
        """Возвращает HTML-тег предпросмотра изображения для галереи проекта."""
        return self.get_admin_image_preview(obj, 'image', width=220, height=140)


class ProjectBlockButtonInline(ProjectHelpTextMixin, NestedStackedInline):
    """Инлайн для кнопок внутри контентного блока (самый нижний уровень)."""

    admin_help_texts = BLOCK_BUTTON_ADMIN_HELP_TEXTS
    model = ProjectBlockButton
    extra = 0
    fk_name = 'block'
    fields = ('order', 'label_ru', 'label_en', 'label_sr_latn', 'label_sr_cyrl', 'type', 'url')


class ProjectContentBlockInline(ProjectHelpTextMixin, BaseAdminMixin, NestedStackedInline):
    """Инлайн для контентных блоков внутри проекта (средний уровень)."""

    admin_help_texts = CONTENT_BLOCK_ADMIN_HELP_TEXTS
    model = ProjectContentBlock
    extra = 0
    fk_name = 'project'
    inlines = [ProjectBlockButtonInline]
    formset = ProjectContentBlockInlineFormSet
    readonly_fields = ('image_preview', 'left_image_preview')
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
        (
            _('Основная информация'),
            {'fields': ('variant', 'order', 'image', 'image_preview', 'left_image', 'left_image_preview')},
        ),
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

    @admin.display(description=_('Превью изображения'))
    def image_preview(self, obj):
        """Возвращает HTML-тег предпросмотра основного изображения контентного блока."""
        return self.get_admin_image_preview(obj, 'image', width=240, height=160)

    @admin.display(description=_('Превью левого изображения'))
    def left_image_preview(self, obj):
        """Возвращает HTML-тег предпросмотра дополнительного (левого) изображения блока."""
        return self.get_admin_image_preview(obj, 'left_image', width=240, height=160)


@admin.register(Project)
class ProjectAdmin(ProjectHelpTextMixin, BaseTranslatedAdmin, NestedModelAdmin):
    """Класс администрирования проектов с вложенными blocks и кнопками."""

    admin_help_texts = PROJECT_ADMIN_HELP_TEXTS
    form = ProjectAdminForm
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
    readonly_fields = ('cover_image_preview',)
    filter_horizontal = ('tags',)

    inlines = [ProjectGalleryImageInline, ProjectContentBlockInline]

    fieldsets = (
        (
            _('Основная информация'),
            {
                'fields': (
                    'title_ru',
                    'slug',
                    'year',
                    'project_type',
                    'tags',
                    'cover_image',
                    'cover_image_preview',
                    'is_published',
                )
            },
        ),
        (_('Переводы (Русский)'), {'fields': ('description_ru',), 'classes': ('collapse',)}),
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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Кастомизирует отображение текстовых полей описания, задавая им высоту и стили."""
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name.startswith('description'):
            attrs = formfield.widget.attrs.copy()
            widget_classes = attrs.get('class', '').split()
            for class_name in ('vLargeTextField', 'project-description-textarea'):
                if class_name not in widget_classes:
                    widget_classes.append(class_name)
            attrs['class'] = ' '.join(widget_classes)
            attrs['rows'] = 3
            attrs['style'] = f"{attrs.get('style', '')} resize: vertical; min-height: 72px;".strip()
            if db_field.max_length:
                attrs['maxlength'] = db_field.max_length
            formfield.widget = forms.Textarea(attrs=attrs)
        return formfield

    def get_queryset(self, request):
        """Оптимизирует запрос к БД, подтягивая связанные типы проектов через select_related."""
        return super().get_queryset(request).select_related('project_type')

    def get_readonly_fields(self, request, obj=None):
        """Делает поле slug доступным только для чтения при редактировании существующего проекта."""
        return list(self.readonly_fields) + ['slug'] if obj else self.readonly_fields

    def get_prepopulated_fields(self, request, obj=None):
        """Включает автоматическое заполнение slug на основе title_ru только для новых проектов."""
        return {} if obj else {'slug': ('title_ru',)}

    def get_project_type(self, obj):
        """Безопасно извлекает название типа проекта с учётом текущего языка админки."""
        if not obj.project_type:
            return ADMIN_EMPTY_VALUE

        lang = (get_language() or 'ru').lower().replace('-', '_')
        return getattr(obj.project_type, f'label_{lang}', '') or obj.project_type.label or ADMIN_EMPTY_VALUE

    get_project_type.short_description = _('Тип проекта')
    get_project_type.admin_order_field = 'project_type__label_ru'

    def get_view_on_site(self, obj):
        """Генерирует HTML-ссылку для быстрого перехода из админки на страницу проекта на фронтенде."""
        if obj.slug:
            frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FRONTEND_URL).rstrip('/')
            absolute_url = FRONTEND_PROJECT_PATH_TEMPLATE.format(frontend_url=frontend_url, slug=obj.slug)
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">🔗 {}</a>',
                absolute_url,
                _('Просмотр на сайте'),
            )
        return ADMIN_EMPTY_VALUE

    get_view_on_site.short_description = _('Ссылка')

    def delete_queryset(self, request, queryset):
        """Безопасное массовое удаление проектов с защитой и очисткой соответствующих папок в MEDIA_ROOT."""
        base_path = os.path.join(settings.MEDIA_ROOT, 'projects')
        for project in queryset:
            if project.slug and len(project.slug) > 2:
                project_dir = os.path.join(base_path, project.slug)
                if project_dir.startswith(base_path) and os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
        queryset.delete()

    def cover_image_thumbnail(self, obj):
        """Возвращает миниатюру обложки проекта для списка объектов (list_display)."""
        return self.get_image_thumbnail(obj, 'cover_image')

    cover_image_thumbnail.short_description = Project._meta.get_field('cover_image').verbose_name

    @admin.display(description=_('Превью обложки'))
    def cover_image_preview(self, obj):
        """Возвращает HTML-тег полноценного превью обложки проекта для формы редактирования."""
        return self.get_admin_image_preview(obj, 'cover_image', width=260, height=170)

    class Media:
        js = ('core/js/admin_image_preview_inline.js', 'projects/js/admin_variant_toggle.js')
        css = {'all': ('core/css/admin_image_preview.css', 'projects/css/admin_custom.css')}
