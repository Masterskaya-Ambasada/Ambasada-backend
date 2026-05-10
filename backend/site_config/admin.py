from contacts.models import ContactSocialLink
from core.base_admin import BaseAdmin
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import SiteConfig


class ContactSocialLinkInline(admin.TabularInline):
    """Настройка отображения ссылок на соцсети внутри конфигурации сайта."""

    model = ContactSocialLink
    extra = 1
    fields = ('social_type', 'url', 'order', 'is_active')


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
        ('Название сайта', {'fields': ('site_name_sr_latn', 'site_name_sr_cyrl')}),
        (
            'Cookie',
            {
                'fields': ('cookie_button_text',),
            },
        ),
        (
            'Переводы (Русский)',
            {
                'fields': ('seo_description_ru', 'copyright_ru', 'privacy_policy_ru', 'cookie_message_ru'),
                'classes': ('collapse',),
            },
        ),
        (
            'Переводы (English)',
            {
                'fields': ('seo_description_en', 'copyright_en', 'privacy_policy_en', 'cookie_message_en'),
                'classes': ('collapse',),
            },
        ),
        (
            'Prevodi (Srpski - Latinica)',
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
            'Преводи (Српски - Ћирилица)',
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
