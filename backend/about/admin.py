"""Регистрация моделей для Django admin."""

from core.base_admin import BaseTranslatedAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import AboutPage, AboutParagraph, GalleryImage, Value
from users.models import User
from django.utils.safestring import mark_safe


class AboutParagraphInline(admin.TabularInline):
    """Inline-редактирование параграфов страницы 'О нас' в админке."""

    model = AboutParagraph
    extra = 1


@admin.register(Value)
class ValueAdmin(BaseTranslatedAdmin):
    """Настройка отображения ценностей в админке."""

    list_display = ('title', 'text')
    ordering = ['title']
    tinymce_fields = ['text_ru', 'text_en', 'text_sr_latn', 'text_sr_cyrl']
    fieldsets = (
        (_('Ценность (Русский)'), {'fields': ('title_ru', 'text_ru'), 'classes': ('collapse',)}),
        (_('Ценность (Английский)'), {'fields': ('title_en', 'text_en'), 'classes': ('collapse',)}),
        (_('Ценность (Сербский - Латиница)'), {'fields': ('title_sr_latn', 'text_sr_latn'), 'classes': ('collapse',)}),
        (_('Ценность (Сербский - Кирилица)'), {'fields': ('title_sr_cyrl', 'text_sr_cyrl'), 'classes': ('collapse',)}),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(BaseTranslatedAdmin):
    """Настройка отображения изображений галереи в админке."""

    list_display = ('alt',)
    ordering = None


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    """Настройка отображения страницы 'О нас' в админке."""

    inlines = [AboutParagraphInline]
    readonly_fields = ('display_public_users',)
    list_display = ['id']

    # fieldsets = (
    #     (_('Main'), {'fields': ('image_left', 'image_right', 'display_public_users')}),

    #     (_('Hero====================='), {'fields': (),
    #                                       'classes': ('wide',)}),

    #     (_('Hero (Русский)'), {'fields': ('hero_title_ru', 'hero_description_ru'),
    #                            'classes': ('collapse',)}),
    #     (_('Hero (Английский)'), {'fields': ('hero_title_en', 'hero_description_en'),
    #                               'classes': ('collapse',)}),
    #     (_('Hero (Сербский - Латиница)'), {'fields': ('hero_title_sr_latn', 'hero_description_sr_latn'),
    #                                        'classes': ('collapse',)}),
    #     (_('Hero (Сербский - Кириллица)'), {'fields': ('hero_title_sr_cyrl', 'hero_description_sr_cyrl'),
    #                                         'classes': ('collapse',)}),

    #     (_('About====================='), {'fields': ('button_link',),
    #                                        'classes': ('wide',)}),
    #     (_('About (Русский)'), {'fields': ('about_title_ru', 'button_label_ru', 'values_title_ru'),
    #                             'classes': ('collapse',)}),
    #     (_('About (Английский)'), {'fields': ('about_title_en', 'button_label_en', 'values_title_en'),
    #                                'classes': ('collapse',)}),
    #     (_('About (Сербский - Латиница)'), {'fields': ('about_title_sr_latn', 'button_label_sr_latn', 'values_title_sr_latn'),
    #                                         'classes': ('collapse',)}),
    #     (_('About (Сербский - Кириллица)'), {'fields': ('about_title_sr_cyrl', 'button_label_sr_cyrl', 'values_title_sr_cyrl'),
    #                                          'classes': ('collapse',)}),

    #     # (),
    # )




    fieldsets = (
        (_('Hero'), {'fields': ('hero_title', 'hero_description', 'image_left', 'image_right', 'display_public_users')}),
        (_('About'), {'fields': ('about_title', 'button_label', 'button_link')}),
        (_('Values'), {'fields': ('values_title',)}),
        (
            _('Team'),
            {
                'fields': (
                    'team_title',
                    'team_members',
                    'team_button_label',
                    'team_button_link',
                )
            },
        ),
        (_('Gallery'), {'fields': ('gallery_title',)}),
        (
            _('Contacts'),
            {
                'fields': (
                    'email',
                    'contact_link',
                )
            },
        ),
    )

    def display_public_users(self, obj):
        public_users = AboutPage().get_public_team()
        if not public_users.exists():
            return _("Публичные пользователи не найдены")
        items = [f"<li><b>{user.full_name} ({user.email})</b></li>" for user in public_users]
        return mark_safe(f"<ul style='margin: 0;'>{''.join(items)}</ul>")
    display_public_users.short_description = _("Текущий состав команды на сайте")
