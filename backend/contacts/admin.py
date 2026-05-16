from core.base_admin import BaseAdmin, BaseTranslatedAdmin
from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from contacts.models import ContactPageContent, ContactRequest, ContactSocialLink


class IsActiveOnSiteFilter(admin.SimpleListFilter):
    """Кастомный фильтр для отображения ссылок по статусу показа на сайте."""

    title = _('Отображение на сайте')
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Показываются на сайте')),
            ('no', _('Скрыты с сайта')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_active=True)
        if self.value() == 'no':
            return queryset.filter(is_active=False)
        return queryset


@admin.register(ContactRequest)
class ContactRequestAdmin(BaseAdmin):
    list_display = (
        'reason',
        'name',
        'email',
        'created_at',
        'is_processed',
    )
    list_filter = (
        'created_at',
        'is_processed',
    )
    list_editable = ('is_processed',)
    search_fields = (
        'name',
        'email',
        'message',
        'reason',
    )
    readonly_fields = (
        'name',
        'email',
        'message',
        'reason',
        'created_at',
    )
    ordering = (
        'is_processed',
        '-created_at',
    )

    def has_add_permission(self, request):
        return False


class ContactPageContentAdminForm(forms.ModelForm):
    """Форма админки для блока пожертвований."""

    class Meta:
        model = ContactPageContent
        fields = '__all__'

    def clean(self):
        """Гарантирует, что активной может быть только одна запись."""
        cleaned_data = super().clean()
        is_active = cleaned_data.get('is_active')

        if is_active:
            qs = ContactPageContent.objects.filter(is_active=True)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    _('Доступной может быть только одна ссылка! Оставьте галочку только на одной из них')
                )
        return cleaned_data


@admin.register(ContactPageContent)
class ContactPageContentAdmin(BaseTranslatedAdmin):
    """Админка для управления текстовым блоком пожертвований."""

    form = ContactPageContentAdminForm
    list_display = ('id', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('donation_text',)
    ordering = ['created_at']
    tinymce_fields = ['donation_text_ru', 'donation_text_en', 'donation_text_sr_latn', 'donation_text_sr_cyrl']

    fieldsets = (
        (_('Текстовый блок для пожертвований (Русский)'), {'fields': ('donation_text_ru',), 'classes': ('collapse',)}),
        (
            _('Текстовый блок для пожертвований (Английский)'),
            {'fields': ('donation_text_en',), 'classes': ('collapse',)},
        ),
        (
            _('Текстовый блок для пожертвований (Сербский - Латиница)'),
            {'fields': ('donation_text_sr_latn',), 'classes': ('collapse',)},
        ),
        (
            _('Текстовый блок для пожертвований (Сербский - Кириллица)'),
            {'fields': ('donation_text_sr_cyrl',), 'classes': ('collapse',)},
        ),
    )


@admin.register(ContactSocialLink)
class ContactSocialLinkAdmin(BaseAdmin):
    """Админка для управления ссылками на соцсети и мессенджеры."""

    exclude = ('site_config',)

    list_display = ('id', 'social_type', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('social_type', IsActiveOnSiteFilter)
    search_fields = ('url',)
    ordering = ('order',)

    def save_model(self, request, obj, form, change):
        """Автоматически подтягиваем единственный SiteConfig при сохранении."""
        if not hasattr(obj, 'site_config') or obj.site_config is None:
            from site_config.models import SiteConfig

            config = SiteConfig.objects.first()
            if config:
                obj.site_config = config
        super().save_model(request, obj, form, change)
