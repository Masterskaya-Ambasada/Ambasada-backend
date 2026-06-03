from core.base_admin import BaseAdminMixin, BaseTranslatedAdmin
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.forms import Textarea, TextInput
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import AboutPage, AboutParagraph, GalleryImage, Value

User = get_user_model()

FIELD_OVERRIDES = {
    models.CharField: {'widget': TextInput(attrs={'style': 'width: 100%; max-width: 400px; border-radius: 4px;'})},
    models.TextField: {
        'widget': Textarea(
            attrs={
                'rows': 4,
                'style': ('width: 100%; max-width: 400px; ' 'border-radius: 4px; resize: vertical;'),
            }
        )
    },
    models.URLField: {'widget': TextInput(attrs={'style': 'width: 100%; max-width: 400px; border-radius: 4px;'})},
}


class AboutParagraphInlineFormSet(BaseInlineFormSet):
    """Формсет для валидации уникальности порядка параграфов."""

    def clean(self):
        super().clean()
        orders = []
        for form in self.forms:
            if not form.is_valid() or form.cleaned_data.get('DELETE'):
                continue
            order = form.cleaned_data.get('order')
            if order is not None:
                if order in orders:
                    form.add_error(
                        'order',
                        _('Параграф с таким порядковым номером уже добавлен.'),
                    )
                else:
                    orders.append(order)


class AboutParagraphInline(admin.StackedInline):
    """Инлайн для параграфов секции 'О нас'."""

    model = AboutParagraph
    formset = AboutParagraphInlineFormSet
    extra = 0
    ordering = ('order',)
    verbose_name = _('Параграф секции "О нас"')
    verbose_name_plural = _('📋 Параграфы секции "О нас"')
    classes = ['collapse']
    formfield_overrides = FIELD_OVERRIDES

    fieldsets = (
        (_('Основная информация'), {'fields': ('order',)}),
        (
            _('Переводы (Русский)'),
            {'fields': ('first_sentence_ru', 'main_text_ru'), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Английский)'),
            {'fields': ('first_sentence_en', 'main_text_en'), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Сербский - Латиница)'),
            {
                'fields': ('first_sentence_sr_latn', 'main_text_sr_latn'),
                'classes': ('collapse',),
            },
        ),
        (
            _('Переводы (Сербский - Кириллица)'),
            {
                'fields': ('first_sentence_sr_cyrl', 'main_text_sr_cyrl'),
                'classes': ('collapse',),
            },
        ),
    )


class ValueInline(admin.StackedInline):
    """Инлайн для ценностей сообщества."""

    model = Value
    extra = 0
    verbose_name = _('Ценность')
    verbose_name_plural = _('💎 Ценности сообщества')
    classes = ['collapse']
    formfield_overrides = FIELD_OVERRIDES

    fieldsets = (
        (
            _('Переводы (Русский)'),
            {'fields': ('title_ru', 'text_ru'), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Английский)'),
            {'fields': ('title_en', 'text_en'), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Сербский - Латиница)'),
            {
                'fields': ('title_sr_latn', 'text_sr_latn'),
                'classes': ('collapse',),
            },
        ),
        (
            _('Переводы (Сербский - Кириллица)'),
            {
                'fields': ('title_sr_cyrl', 'text_sr_cyrl'),
                'classes': ('collapse',),
            },
        ),
    )


class GalleryImageInline(BaseAdminMixin, admin.StackedInline):
    """Инлайн для фотогалереи."""

    model = GalleryImage
    extra = 0
    readonly_fields = ('image_preview_field',)
    verbose_name = _('Изображение')
    verbose_name_plural = _('🖼️ Фотогалерея')
    classes = ['collapse']
    formfield_overrides = FIELD_OVERRIDES

    fieldsets = (
        (_('Основная информация'), {'fields': ('image', 'image_preview_field')}),
        (_('Переводы (Русский)'), {'fields': ('alt_ru',), 'classes': ('collapse',)}),
        (_('Переводы (Английский)'), {'fields': ('alt_en',), 'classes': ('collapse',)}),
        (
            _('Переводы (Сербский - Латиница)'),
            {'fields': ('alt_sr_latn',), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Сербский - Кириллица)'),
            {'fields': ('alt_sr_cyrl',), 'classes': ('collapse',)},
        ),
    )

    @admin.display(description=_('Превью'))
    def image_preview_field(self, obj):
        return self.get_admin_image_preview(obj, 'image', width=240, height=160)


@admin.register(AboutPage)
class AboutPageAdmin(BaseTranslatedAdmin):
    """Класс администрирования страницы 'О нас'."""

    formfield_overrides = FIELD_OVERRIDES
    inlines = [AboutParagraphInline, ValueInline, GalleryImageInline]
    readonly_fields = ('display_public_users',)
    list_display = ['id', 'about_title']
    list_display_links = ['id', 'about_title']
    ordering = None

    fieldsets = (
        (
            _('⚙️ Навигация и Ссылки главного экрана (Hero)'),
            {
                'fields': (
                    'hero_title_ru',
                    'button_label_ru',
                    'button_link',
                ),
                'description': _('Управление контентом главного приветственного блока ' 'и кнопкой действия.'),
            },
        ),
        (
            _('👥 Состав команды'),
            {
                'fields': ('display_public_users',),
                'description': _('Просмотр текущего состава команды и переход к управление.'),
            },
        ),
        (
            _('Переводы (Русский)'),
            {
                'classes': ('collapse',),
                'fields': (
                    'hero_description_ru',
                    'about_title_ru',
                    'values_title_ru',
                    'gallery_title_ru',
                ),
            },
        ),
        (
            _('Переводы (Английский)'),
            {
                'classes': ('collapse',),
                'fields': (
                    'hero_title_en',
                    'hero_description_en',
                    'about_title_en',
                    'button_label_en',
                    'values_title_en',
                    'gallery_title_en',
                ),
            },
        ),
        (
            _('Переводы (Сербский - Латиница)'),
            {
                'classes': ('collapse',),
                'fields': (
                    'hero_title_sr_latn',
                    'hero_description_sr_latn',
                    'about_title_sr_latn',
                    'button_label_sr_latn',
                    'values_title_sr_latn',
                    'gallery_title_sr_latn',
                ),
            },
        ),
        (
            _('Переводы (Сербский - Кириллица)'),
            {
                'classes': ('collapse',),
                'fields': (
                    'hero_title_sr_cyrl',
                    'hero_description_sr_cyrl',
                    'about_title_sr_cyrl',
                    'button_label_sr_cyrl',
                    'values_title_sr_cyrl',
                    'gallery_title_sr_cyrl',
                ),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'hero_title_ru' in form.base_fields:
            form.base_fields['hero_title_ru'].label = _('Главный заголовок (Экран Hero)')
        if 'button_label_ru' in form.base_fields:
            form.base_fields['button_label_ru'].label = _('Текст целевой кнопки')
        if 'button_link' in form.base_fields:
            form.base_fields['button_link'].label = _('Ссылка целевой кнопки')
        return form

    @admin.display(description=_('Текущий состав команды'))
    def display_public_users(self, obj):
        if not obj or not obj.pk:
            return _('Сохраните страницу, чтобы увидеть список команды')

        public_users = User.objects.public()
        if not public_users or not public_users.exists():
            users_html = f'<div class="team-empty-warning">' f'⚠️ {_("Публичные пользователи не найдены")}</div>'
        else:
            cards = [
                f'<div class="team-user-card"><div class="status-dot"></div>'
                f'<span class="user-name">{u.full_name or u.email}</span></div>'
                for u in public_users
            ]
            users_html = f'<div class="team-cards-wrapper">{"".join(cards)}</div>'

        manage_link = (
            f'<a href="/admin/users/user/" class="team-manage-btn">' f'<span>+</span> {_("Управление командой")}</a>'
        )
        return mark_safe(
            f'<div class="team-widget-root">'
            f'  <div class="team-widget-container">'
            f'    <div class="team-left-column">{users_html}{manage_link}</div>'
            f'  </div>'
            f'</div>'
        )

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        js = ('core/js/admin_image_preview_inline.js',)
        css = {
            'all': (
                'core/css/admin_image_preview.css',
                'about/css/custom_about_admin.css',
            )
        }
