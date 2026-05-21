from core.base_admin import BaseTranslatedAdmin
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import AboutPage, AboutParagraph, GalleryImage, Value

User = get_user_model()


class AboutParagraphInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        orders = []
        for form in self.forms:
            if not form.is_valid() or form.cleaned_data.get('DELETE'):
                continue
            order = form.cleaned_data.get('order')
            if order is not None:
                if order in orders:
                    form.add_error('order', _('Параграф с таким порядковым номером уже добавлен.'))
                else:
                    orders.append(order)


class AboutParagraphInline(admin.StackedInline):
    model = AboutParagraph
    formset = AboutParagraphInlineFormSet
    extra = 1
    fieldsets = (
        (_('Порядок отображения'), {'fields': ('order',)}),
        (_('Параграф (Русский)'), {'fields': ('first_sentence_ru', 'main_text_ru'), 'classes': ('collapse',)}),
        (_('Параграф (Английский)'), {'fields': ('first_sentence_en', 'main_text_en'), 'classes': ('collapse',)}),
        (
            _('Параграф (Сербский - Латиница)'),
            {'fields': ('first_sentence_sr_latn', 'main_text_sr_latn'), 'classes': ('collapse',)},
        ),
        (
            _('Параграф (Сербский - Кириллица)'),
            {'fields': ('first_sentence_sr_cyrl', 'main_text_sr_cyrl'), 'classes': ('collapse',)},
        ),
    )


@admin.register(Value)
class ValueAdmin(BaseTranslatedAdmin):
    list_display = ('title', 'text_preview')
    search_fields = ('title',)
    ordering = ['title']
    tinymce_fields = ['text_ru', 'text_en', 'text_sr_latn', 'text_sr_cyrl']

    def text_preview(self, obj):
        text = obj.text or ''
        return f'{text[:50]}...' if len(text) > 50 else text

    text_preview.short_description = _('Предпросмотр текста')

    fieldsets = (
        (_('Ценность (Русский)'), {'fields': ('title_ru', 'text_ru'), 'classes': ('collapse',)}),
        (_('Ценность (Английский)'), {'fields': ('title_en', 'text_en'), 'classes': ('collapse',)}),
        (_('Ценность (Сербский - Латиница)'), {'fields': ('title_sr_latn', 'text_sr_latn'), 'classes': ('collapse',)}),
        (_('Ценность (Сербский - Кириллица)'), {'fields': ('title_sr_cyrl', 'text_sr_cyrl'), 'classes': ('collapse',)}),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(BaseTranslatedAdmin):
    list_display = ('alt', 'image_preview')
    search_fields = ('alt',)
    ordering = None

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="60" height="60" />')
        return _('Нет изображения')

    image_preview.short_description = _('Изображение')


@admin.register(AboutPage)
class AboutPageAdmin(BaseTranslatedAdmin):
    inlines = [AboutParagraphInline]
    readonly_fields = ('display_public_users',)
    list_display = ['id', 'email']
    ordering = None

    fieldsets = (
        (
            _('Основное (Общие настройки)'),
            {'fields': ('image_left', 'image_right', 'button_link', 'team_button_link', 'display_public_users')},
        ),
        (
            _('Заголовки (Русский)'),
            {
                'fields': (
                    'hero_title_ru',
                    'hero_description_ru',
                    'about_title_ru',
                    'button_label_ru',
                    'values_title_ru',
                    'team_title_ru',
                    'team_button_label_ru',
                    'gallery_title_ru',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            _('Заголовки (Английский)'),
            {
                'fields': (
                    'hero_title_en',
                    'hero_description_en',
                    'about_title_en',
                    'button_label_en',
                    'values_title_en',
                    'team_title_en',
                    'team_button_label_en',
                    'gallery_title_en',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            _('Заголовки (Сербский - Латиница)'),
            {
                'fields': (
                    'hero_title_sr_latn',
                    'hero_description_sr_latn',
                    'about_title_sr_latn',
                    'button_label_sr_latn',
                    'values_title_sr_latn',
                    'team_title_sr_latn',
                    'team_button_label_sr_latn',
                    'gallery_title_sr_latn',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            _('Заголовки (Сербский - Кириллица)'),
            {
                'fields': (
                    'hero_title_sr_cyrl',
                    'hero_description_sr_cyrl',
                    'about_title_sr_cyrl',
                    'button_label_sr_cyrl',
                    'values_title_sr_cyrl',
                    'team_title_sr_cyrl',
                    'team_button_label_sr_cyrl',
                    'gallery_title_sr_cyrl',
                ),
                'classes': ('collapse',),
            },
        ),
        (_('Контакты'), {'fields': ('email', 'contact_link'), 'classes': ('wide',)}),
    )

    def display_public_users(self, obj):
        if not obj or not obj.pk:
            return _('Сохраните страницу, чтобы увидеть список команды')

        public_users = User.objects.public()

        if not public_users or not public_users.exists():
            users_html = f'<div class="team-empty-warning">⚠️ {_("Публичные пользователи не найдены")}</div>'
        else:
            cards = []
            for user in public_users:
                full_name = getattr(user, 'full_name', '').strip()
                email = user.email
                display_name = full_name if (full_name and full_name != email) else email
                cards.append(
                    f'<div class="team-user-card">'
                    f'<div class="status-dot"></div>'
                    f'<span class="user-name">{display_name}</span>'
                    f'</div>'
                )
            users_html = f'<div class="team-cards-wrapper">{"".join(cards)}</div>'

        manage_link = (
            f'<a href="/admin/users/user/" class="team-manage-btn"><span>+</span> {_("Управление командой")}</a>'
        )
        help_text = _(
            'Если вы хотите добавить участника команды, перейдите в раздел '
            '"Пользователи и команда", создайте нового пользователя или '
            'отредактируйте существующего, обязательно установив галочку "Публичный".'
        )

        return mark_safe(
            f'<div class="team-widget-root">'
            f'<div class="team-widget-container">'
            f'<div class="team-left-column">{users_html}{manage_link}</div>'
            f'<div class="team-right-column team-help-text">{help_text}</div>'
            f'</div>'
            f'</div>'
        )

    display_public_users.short_description = _('Текущий состав команды на сайте')

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        css = {'all': ('about/css/custom_about_admin.css',)}
