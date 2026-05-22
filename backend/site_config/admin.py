from contacts.models import ContactSocialLink
from core.base_admin import BaseAdmin
from django import forms
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


class SiteConfigAdminForm(forms.ModelForm):
    """Кастомная форма админки для подстановки языковых HTML-шаблонов."""

    class Meta:
        model = SiteConfig
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Инициализация формы с предзаполнением полей для новых объектов."""
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            # ==================================================================
            # 1. РУССКИЙ ЯЗЫК (RU)
            # ==================================================================
            if 'privacy_policy_ru' in self.fields:
                self.fields['privacy_policy_ru'].initial = (
                    '<p>Нажимая кнопку «Отправить», вы соглашаетесь с '
                    '<a href="/policy">Политикой конфиденциальности</a> '
                    'и даёте согласие на обработку персональных данных.</p>'
                )
            if 'cookie_message_ru' in self.fields:
                self.fields[
                    'cookie_message_ru'
                ].initial = '<p>Мы используем технические cookie для корректной работы сайта.</p>'
            if 'cookie_button_text_ru' in self.fields:
                self.fields['cookie_button_text_ru'].initial = 'Принять'

            # ==================================================================
            # 2. АНГЛИЙСКИЙ ЯЗЫК (EN)
            # ==================================================================
            if 'privacy_policy_en' in self.fields:
                self.fields['privacy_policy_en'].initial = (
                    '<p>By clicking "Submit", you agree to our '
                    '<a href="/policy">Privacy Policy</a> and consent to '
                    'the processing of your personal data.</p>'
                )
            if 'cookie_message_en' in self.fields:
                self.fields[
                    'cookie_message_en'
                ].initial = '<p>We use technical cookies for the correct operation of the website.</p>'
            if 'cookie_button_text_en' in self.fields:
                self.fields['cookie_button_text_en'].initial = 'Accept'

            # ==================================================================
            # 3. СЕРБСКИЙ ЯЗЫК (ЛАТИНИЦА - SR_LATN)
            # ==================================================================
            if 'privacy_policy_sr_latn' in self.fields:
                self.fields['privacy_policy_sr_latn'].initial = (
                    '<p>Klikom na dugme "Pošalji", prihvatate '
                    '<a href="/policy">Politiku privatnosti</a> '
                    'i dajete saglasnost za obradu podataka o ličnosti.</p>'
                )
            if 'cookie_message_sr_latn' in self.fields:
                self.fields[
                    'cookie_message_sr_latn'
                ].initial = '<p>Koristimo tehničke kolačiće za ispravan rad veb sajta.</p>'
            if 'cookie_button_text_sr_latn' in self.fields:
                self.fields['cookie_button_text_sr_latn'].initial = 'Prihvati'

            # ==================================================================
            # 4. СЕРБСКИЙ ЯЗЫК (КИРИЛЛИЦА - SR_CYRL)
            # ==================================================================
            if 'privacy_policy_sr_cyrl' in self.fields:
                self.fields['privacy_policy_sr_cyrl'].initial = (
                    '<p>Кликом на дугме "Пошаљи", прихватате '
                    '<a href="/policy">Политику приватности</a> '
                    'и дајете сагласност за обраду података о личности.</p>'
                )
            if 'cookie_message_sr_cyrl' in self.fields:
                self.fields[
                    'cookie_message_sr_cyrl'
                ].initial = '<p>Користимо техничке колачиће за исправан рад веб сајта.</p>'
            if 'cookie_button_text_sr_cyrl' in self.fields:
                self.fields['cookie_button_text_sr_cyrl'].initial = 'Прихвати'


@admin.register(SiteConfig)
class ConfigAdmin(BaseAdmin):
    """Администрирование глобальных настроек сайта (Singleton)."""

    form = SiteConfigAdminForm
    ordering = ('id',)
    inlines = [ContactSocialLinkInline]

    list_display = [
        'site_name_sr_latn',
        'site_name_sr_cyrl',
        'seo_description_sr_latn',
        'copyright_sr_latn',
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
        'cookie_message_ru',
        'cookie_message_en',
        'cookie_message_sr_latn',
        'cookie_message_sr_cyrl',
    ]

    fieldsets = (
        (_('Название сайта'), {'fields': ('site_name_sr_latn', 'site_name_sr_cyrl')}),
        (
            _('Переводы (Русский)'),
            {
                'fields': (
                    'seo_description_ru',
                    'copyright_ru',
                    'privacy_policy_ru',
                    'cookie_message_ru',
                    'cookie_button_text_ru',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            _('Переводы (Английский)'),
            {
                'fields': (
                    'seo_description_en',
                    'copyright_en',
                    'privacy_policy_en',
                    'cookie_message_en',
                    'cookie_button_text_en',
                ),
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
                    'cookie_button_text_sr_latn',
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
                    'cookie_button_text_sr_cyrl',
                ),
                'classes': ('collapse',),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Исключает ненужные локализации для названия сайта."""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields.pop('site_name_ru', None)
        form.base_fields.pop('site_name_en', None)
        return form

    def has_add_permission(self, request):
        """Разрешает добавление только если конфигурация еще не создана."""
        if SiteConfig.objects.exists():
            return False
        return super().has_add_permission(request)

    def add_view(self, request, form_url='', extra_context=None):
        """Редиректит на редактирование, если конфиг уже существует."""
        existing_config = SiteConfig.objects.only('pk').first()
        if existing_config:
            return redirect(
                reverse(
                    'admin:site_config_siteconfig_change',
                    args=[existing_config.pk],
                )
            )
        return super().add_view(request, form_url, extra_context)

    def has_delete_permission(self, request, obj=None):
        """Скрывает кнопку 'Удалить' и запрещает доступ к delete_view."""
        return False

    def get_actions(self, request):
        """Удаляет возможность массового удаления из списка объектов."""
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions
