from contacts.models import ContactSocialLink
from core.base_admin import BaseAdmin
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import SiteConfig


class ContactSocialLinkInline(admin.TabularInline):
    """Настройка отображения ссылок на соцсети внутри конфигурации сайта."""

    model = ContactSocialLink
    extra = 0
    fields = ('social_type', 'url', 'order', 'is_active')
    can_delete = False


@admin.register(SiteConfig)
class ConfigAdmin(BaseAdmin):
    """Администрирование глобальных настроек сайта (Singleton)."""

    ordering = ('id',)

    inlines = [ContactSocialLinkInline]

    list_display = [
        'site_name_sr_latn',
        'site_name_sr_cyrl',
        'seo_description',
        'copyright',
    ]

    tinymce_fields = [
        'seo_description_ru',
        'seo_description_en',
        'seo_description_sr_latn',
        'seo_description_sr_cyrl',
        'copyright_ru',
        'copyright_en',
        'copyright_sr_latn',
        'copyright_sr_cyrl',
        'privacy_policy_ru',
        'privacy_policy_en',
        'privacy_policy_sr_latn',
        'privacy_policy_sr_cyrl',
    ]

    fieldsets = (
        (_('Название сайта'), {'fields': ('site_name_sr_latn', 'site_name_sr_cyrl')}),
        (_('Cookie'), {'fields': ('cookie_button_text',)}),
        (
            _('Переводы (Русский)'),
            {
                'fields': ('seo_description_ru', 'copyright_ru', 'privacy_policy_ru', 'cookie_message_ru'),
                'classes': ('collapse',),
            },
        ),
        (
            _('Переводы (Английский)'),
            {
                'fields': ('seo_description_en', 'copyright_en', 'privacy_policy_en', 'cookie_message_en'),
                'classes': ('collapse',),
            },
        ),
        (
            _('Переводы (Сербский - Латиница)'),
            {
                'fields': (
                    'seo_description_sr_latn',
                    'copyright_sr_latn',
                    'privacy_policy_sr_latn',
                    'cookie_message_sr_latn',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            _('Преводи (Сербский - Кириллица)'),
            {
                'fields': (
                    'seo_description_sr_cyrl',
                    'copyright_sr_cyrl',
                    'privacy_policy_sr_cyrl',
                    'cookie_message_sr_cyrl',
                ),
                'classes': ('collapse',),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'site_name_ru' in form.base_fields:
            del form.base_fields['site_name_ru']
        if 'site_name_en' in form.base_fields:
            del form.base_fields['site_name_en']
        return form

    def has_add_permission(self, request):
        if SiteConfig.objects.exists():
            return False
        return super().has_add_permission(request)

    def add_view(self, request, form_url='', extra_context=None):
        if SiteConfig.objects.exists():
            existing_config = SiteConfig.objects.first()
            return redirect(reverse('admin:site_config_siteconfig_change', args=[existing_config.pk]))
        return super().add_view(request, form_url, extra_context)

    def has_delete_permission(self, request, obj=None):
        """Скрывает кнопку 'Удалить' и запрещает доступ к delete_view."""
        return False

    def get_actions(self, request):
        """Удаляет возможность массового удаления из списка объектов."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
