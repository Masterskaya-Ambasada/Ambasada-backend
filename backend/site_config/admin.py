"""Регистрация моделей SiteConfig, Social, Language в админ-панели."""

from core.base_admin import BaseAdmin
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import Language, SiteConfig, Social


@admin.register(SiteConfig)
class ConfigAdmin(BaseAdmin):
    ordering = ('id',)
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
        ('Социальные сети', {'fields': ('socials',), 'classes': ('wide',)}),
        ('Языки', {'fields': ('languages',), 'classes': ('wide',)}),
        (
            'Переводы (Русский)',
            {
                'fields': ('seo_description_ru', 'copyright_ru', 'privacy_policy_ru'),
                'classes': ('collapse',),
            },
        ),
        (
            'Переводы (English)',
            {
                'fields': ('seo_description_en', 'copyright_en', 'privacy_policy_en'),
                'classes': ('collapse',),
            },
        ),
        (
            'Prevodi (Srpski - Latinica)',
            {
                'fields': ('seo_description_sr_latn', 'copyright_sr_latn', 'privacy_policy_sr_latn'),
                'classes': ('collapse',),
            },
        ),
        (
            'Преводи (Српски - Ћирилица)',
            {
                'fields': ('seo_description_sr_cyrl', 'copyright_sr_cyrl', 'privacy_policy_sr_cyrl'),
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
        """Скрывает кнопку add на странице списка если объект SiteConfig же существует."""
        if SiteConfig.objects.exists():
            return False
        return super().has_add_permission(request)

    def add_view(self, request, form_url='', extra_context=None):
        """Редирект на страницу update."""
        if SiteConfig.objects.exists():
            existing_config = SiteConfig.objects.first()
            return redirect(reverse('admin:site_config_siteconfig_change', args=[existing_config.pk]))
        return super().add_view(request, form_url, extra_context)


@admin.register(Social)
class SocialAdmin(admin.ModelAdmin):
    list_display = ['social_type', 'url']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'label']
