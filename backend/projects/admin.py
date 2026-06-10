import os
import shutil

from core.base_admin import BaseAdminMixin, BaseTranslatedAdmin, ImportExportMixin
from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from .admin_forms import ProjectContentBlockInlineFormSet
from .constants import (
    ADMIN_EMPTY_VALUE,
    DEFAULT_FRONTEND_URL,
    FRONTEND_PROJECT_PATH_TEMPLATE,
    REFERENCE_TRANSLATED_FIELDS,
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

CYRILLIC_TO_LATIN = str.maketrans(
    {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'e',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'y',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'kh',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'sch',
        'ъ': '',
        'ы': 'y',
        'ь': '',
        'э': 'e',
        'ю': 'yu',
        'я': 'ya',
    }
)


def make_slug_from_russian_title(title: str) -> str:
    """Создаёт URL-safe slug из русского названия проекта."""
    return slugify(title.lower().translate(CYRILLIC_TO_LATIN))


class ProjectAdminForm(forms.ModelForm):
    """Форма проекта с серверной генерацией slug из русского названия."""

    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Разрешает оставить slug пустым, чтобы форма сгенерировала его из title_ru."""
        super().__init__(*args, **kwargs)
        if 'slug' in self.fields:
            self.fields['slug'].required = False
        if 'tags' in self.fields:
            self.fields['tags'].help_text = ''

    def clean(self):
        """Заполняет пустой slug после валидации всех полей формы."""
        cleaned_data = super().clean()
        if not cleaned_data.get('slug'):
            cleaned_data['slug'] = make_slug_from_russian_title(cleaned_data.get('title_ru', ''))
        return cleaned_data


@admin.register(Tag)
class TagAdmin(BaseTranslatedAdmin, ImportExportMixin):
    """Класс администрирования Тегов."""

    resource_classes = [TagResource]
    fields = REFERENCE_TRANSLATED_FIELDS
    list_display = REFERENCE_TRANSLATED_FIELDS
    search_fields = ['slug']


@admin.register(ProjectType)
class ProjectTypeAdmin(BaseTranslatedAdmin, ImportExportMixin):
    """Класс администрирования типов проектов."""

    resource_classes = [ProjectTypeResource]
    fields = REFERENCE_TRANSLATED_FIELDS
    list_display = REFERENCE_TRANSLATED_FIELDS
    search_fields = ['slug']


class ProjectGalleryImageInline(BaseAdminMixin, NestedTabularInline):
    """Инлайн для картинок верхней карусели проекта."""

    model = ProjectGalleryImage
    extra = 0
    fk_name = 'project'
    ordering = ('order',)
    readonly_fields = ('image_preview',)
    fields = ('order', 'image', 'image_preview')

    @admin.display(description=_('Превью'))
    def image_preview(self, obj):
        return self.get_admin_image_preview(obj, 'image', width=220, height=140)


class ProjectBlockButtonInline(NestedTabularInline):
    """Инлайн для кнопок внутри контентного блока (самый нижний уровень)."""

    model = ProjectBlockButton
    extra = 0
    fk_name = 'block'
    fields = ('order', 'label_ru', 'label_en', 'label_sr_latn', 'label_sr_cyrl', 'type', 'url')


class ProjectContentBlockInline(BaseAdminMixin, NestedStackedInline):
    """Инлайн для контентных блоков внутри проекта (средний уровень)."""

    model = ProjectContentBlock
    extra = 0
    fk_name = 'project'
    inlines = [ProjectBlockButtonInline]
    formset = ProjectContentBlockInlineFormSet
    readonly_fields = ('image_preview', 'left_image_preview')

    # Перебиваем дефолтный ordering='slug' из BaseAdminMixin, чтобы не было ошибок
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
        return self.get_admin_image_preview(obj, 'image', width=240, height=160)

    @admin.display(description=_('Превью левого изображения'))
    def left_image_preview(self, obj):
        return self.get_admin_image_preview(obj, 'left_image', width=240, height=160)


@admin.register(Project)
class ProjectAdmin(BaseTranslatedAdmin, NestedModelAdmin):
    """Класс администрирования проектов с вложенными blocks и кнопками."""

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
            formfield.widget = forms.Textarea(attrs=attrs)
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project_type')

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + ['slug'] if obj else self.readonly_fields

    def get_prepopulated_fields(self, request, obj=None):
        return {} if obj else {'slug': ('title_ru',)}

    def get_project_type(self, obj):
        return obj.project_type.label if obj.project_type else ADMIN_EMPTY_VALUE

    get_project_type.short_description = _('Тип проекта')
    get_project_type.admin_order_field = 'project_type__label'

    def get_view_on_site(self, obj):
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

    @admin.display(description=_('Превью обложки'))
    def cover_image_preview(self, obj):
        return self.get_admin_image_preview(obj, 'cover_image', width=260, height=170)

    class Media:
        js = ('core/js/admin_image_preview_inline.js', 'projects/js/admin_variant_toggle.js')
        css = {'all': ('core/css/admin_image_preview.css', 'projects/css/admin_custom.css')}
