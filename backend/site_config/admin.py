from contacts.models import ContactSocialLink
from core.base_admin import BaseAdmin
from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import SiteConfig


class ContactSocialLinkInline(admin.TabularInline):
    """Отображение ссылок на соцсети из модуля contacts внутри настроек сайта."""

    model = ContactSocialLink
    extra = 0
    fields = ('social_type', 'url', 'order', 'is_active')


class SiteConfigAdminForm(forms.ModelForm):
    """Кастомная форма админки для подстановки языковых HTML-шаблонов."""

    class Meta:
        model = SiteConfig
        fields = '__all__'
        exclude = ('site_name_ru', 'site_name_en')

    def __init__(self, *args, **kwargs):
        """Инициализация формы с предзаполнением начальных значений (initial)."""
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            # --- РУССКИЙ ---
            if 'privacy_policy_ru' in self.fields:
                self.fields['privacy_policy_ru'].initial = (
                    '<p>Нажимая кнопку «Отправить», вы соглашаетесь с '
                    '<a href="/policy">Политикой конфиденциальности</a> '
                    'и даёте согласие на обработку персональных данных.</p>'
                )
            if 'cookie_message_ru' in self.fields:
                self.fields[
                    'cookie_message_ru'
                ].initial = 'Мы используем технические cookie для корректной работы сайта.'
            if 'cookie_button_text_ru' in self.fields:
                self.fields['cookie_button_text_ru'].initial = 'Принять'
            if 'team_title_ru' in self.fields:
                self.fields['team_title_ru'].initial = 'Команда'
            if 'main_team_button_label_ru' in self.fields:
                self.fields['main_team_button_label_ru'].initial = 'Присоединиться к команде'
            if 'about_team_button_label_ru' in self.fields:
                self.fields['about_team_button_label_ru'].initial = 'Присоединиться'

            # --- АНГЛИЙСКИЙ ---
            if 'privacy_policy_en' in self.fields:
                self.fields['privacy_policy_en'].initial = (
                    '<p>By clicking "Submit", you agree to our '
                    '<a href="/policy">Privacy Policy</a> and consent to '
                    'the processing of your personal data.</p>'
                )
            if 'cookie_message_en' in self.fields:
                self.fields[
                    'cookie_message_en'
                ].initial = 'We use technical cookies for the correct operation of the website.'
            if 'cookie_button_text_en' in self.fields:
                self.fields['cookie_button_text_en'].initial = 'Accept'
            if 'team_title_en' in self.fields:
                self.fields['team_title_en'].initial = 'Team'
            if 'main_team_button_label_en' in self.fields:
                self.fields['main_team_button_label_en'].initial = 'Join the team'
            if 'about_team_button_label_en' in self.fields:
                self.fields['about_team_button_label_en'].initial = 'Join'

            # --- СЕРБСКИЙ (ЛАТИНИЦА) ---
            if 'privacy_policy_sr_latn' in self.fields:
                self.fields['privacy_policy_sr_latn'].initial = (
                    '<p>Klikom na dugme "Pošalji", prihvatate '
                    '<a href="/policy">Politiku privatnosti</a> '
                    'i dajete saglasnost za obradu podataka o ličnosti.</p>'
                )
            if 'cookie_message_sr_latn' in self.fields:
                self.fields['cookie_message_sr_latn'].initial = 'Koristimo tehničke kolačiće za ispravan rad veb sajta.'
            if 'cookie_button_text_sr_latn' in self.fields:
                self.fields['cookie_button_text_sr_latn'].initial = 'Prihvati'
            if 'team_title_sr_latn' in self.fields:
                self.fields['team_title_sr_latn'].initial = 'Tim'
            if 'main_team_button_label_sr_latn' in self.fields:
                self.fields['main_team_button_label_sr_latn'].initial = 'Pridruži se timu'
            if 'about_team_button_label_sr_latn' in self.fields:
                self.fields['about_team_button_label_sr_latn'].initial = 'Pridruži se'

            # --- СЕРБСКИЙ (КИРИЛЛИЦА) ---
            if 'privacy_policy_sr_cyrl' in self.fields:
                self.fields['privacy_policy_sr_cyrl'].initial = (
                    '<p>Кликом на дугме "Пошаљи", прихватате '
                    '<a href="/policy">Политику приватности</a> '
                    'и дајете сагласност за обраду података о личности.</p>'
                )
            if 'cookie_message_sr_cyrl' in self.fields:
                self.fields[
                    'cookie_message_sr_cyrl'
                ].initial = 'Користимо техничке колачиће за један исправни рад веб сајта.'
            if 'cookie_button_text_sr_cyrl' in self.fields:
                self.fields['cookie_button_text_sr_cyrl'].initial = 'Прихвати'
            if 'team_title_sr_cyrl' in self.fields:
                self.fields['team_title_sr_cyrl'].initial = 'Тим'
            if 'main_team_button_label_sr_cyrl' in self.fields:
                self.fields['main_team_button_label_sr_cyrl'].initial = 'Придружи се тиму'
            if 'about_team_button_label_sr_cyrl' in self.fields:
                self.fields['about_team_button_label_sr_cyrl'].initial = 'Придружи се'


@admin.register(SiteConfig)
class ConfigAdmin(BaseAdmin):
    """Администрирование глобальных настроек сайта (Singleton)."""

    form = SiteConfigAdminForm
    ordering = ('id',)
    inlines = [ContactSocialLinkInline]

    list_display = [
        'site_name_sr_latn',
        'site_name_sr_cyrl',
        'copyright_sr_latn',
    ]

    tinymce_fields = [
        'privacy_policy_ru',
        'privacy_policy_en',
        'privacy_policy_sr_latn',
        'privacy_policy_sr_cyrl',
    ]

    fieldsets = (
        (
            _('1. Основные и общие настройки'),
            {
                'fields': ('site_name_sr_latn', 'site_name_sr_cyrl', 'team_button_link', 'contact_notification_email'),
                'description': _(
                    'Глобальные названия проекта, сквозные ссылки и почта получателя заявок с формы контактов.'
                ),
            },
        ),
        (
            _('2. Локализация: Русский (RU)'),
            {
                'fields': (
                    'copyright_ru',
                    'seo_description_ru',
                    'cookie_message_ru',
                    'cookie_button_text_ru',
                    'privacy_policy_ru',
                    'team_title_ru',
                    'main_team_button_label_ru',
                    'about_team_button_label_ru',
                ),
                'classes': ('collapse',),
                'description': _('Переводы интерфейса, SEO-теги и тексты на русском.'),
            },
        ),
        (
            _('3. Локализация: Английский (EN)'),
            {
                'fields': (
                    'copyright_en',
                    'seo_description_en',
                    'cookie_message_en',
                    'cookie_button_text_en',
                    'privacy_policy_en',
                    'team_title_en',
                    'main_team_button_label_en',
                    'about_team_button_label_en',
                ),
                'classes': ('collapse',),
                'description': _('Переводы интерфейса, SEO-теги и тексты на английском.'),
            },
        ),
        (
            _('4. Локализация: Сербский Латиница (SR-Latn)'),
            {
                'fields': (
                    'copyright_sr_latn',
                    'seo_description_sr_latn',
                    'cookie_message_sr_latn',
                    'cookie_button_text_sr_latn',
                    'privacy_policy_sr_latn',
                    'team_title_sr_latn',
                    'main_team_button_label_sr_latn',
                    'about_team_button_label_sr_latn',
                ),
                'classes': ('collapse',),
                'description': _('Переводы интерфейса и тексты на сербской латинице.'),
            },
        ),
        (
            _('5. Локализация: Сербский Кириллица (SR-Cyrl)'),
            {
                'fields': (
                    'copyright_sr_cyrl',
                    'seo_description_sr_cyrl',
                    'cookie_message_sr_cyrl',
                    'cookie_button_text_sr_cyrl',
                    'privacy_policy_sr_cyrl',
                    'team_title_sr_cyrl',
                    'main_team_button_label_sr_cyrl',
                    'about_team_button_label_sr_cyrl',
                ),
                'classes': ('collapse',),
                'description': _('Переводы интерфейса и тексты на сербской кириллице.'),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Гарантирует строгую валидацию полей названия сайта, перебивая сброс из fieldsets."""
        form = super().get_form(request, obj, **kwargs)
        if 'site_name_sr_latn' in form.base_fields:
            form.base_fields['site_name_sr_latn'].required = True
        if 'site_name_sr_cyrl' in form.base_fields:
            form.base_fields['site_name_sr_cyrl'].required = True
        return form

    def has_add_permission(self, request):
        """Разрешение добавления записи только при её отсутствии."""
        if SiteConfig.objects.exists():
            return False
        return super().has_add_permission(request)

    def add_view(self, request, form_url='', extra_context=None):
        """Перенаправление на редактирование существующего конфига."""
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
        """Запрет удаления глобальной конфигурации."""
        return False

    def get_actions(self, request):
        """Удаление экшена массового удаления объектов."""
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions
