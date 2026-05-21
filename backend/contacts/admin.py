from core.base_admin import BaseAdmin, BaseTranslatedAdmin
from django import forms
from django.contrib import admin, messages
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
    """Админка для обработки входящих заявок с формы контактов."""

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
    """Форма админки для текстового блока пожертвований."""

    class Meta:
        model = ContactPageContent
        fields = '__all__'


@admin.register(ContactPageContent)
class ContactPageContentAdmin(BaseTranslatedAdmin):
    """Админка для управления текстовым блоком пожертвований."""

    form = ContactPageContentAdminForm
    list_display = ('updated_at', 'is_active')
    list_editable = ('is_active',)

    search_fields = ('donation_text_ru', 'donation_text_en')
    ordering = ['created_at']
    tinymce_fields = ['donation_text_ru', 'donation_text_en', 'donation_text_sr_latn', 'donation_text_sr_cyrl']

    fieldsets = (
        (
            None,
            {
                'fields': ('is_active',),
            },
        ),
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

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            ContactPageContent.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if instance.is_active:
                ContactPageContent.objects.filter(is_active=True).exclude(pk=instance.pk).update(is_active=False)
            instance.save()
        formset.save_m2m()


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
            else:
                messages.error(
                    request,
                    _('Ошибка сохранения: Сначала необходимо создать хотя бы одну конфигурацию сайта (SiteConfig).'),
                )
                return

        super().save_model(request, obj, form, change)
