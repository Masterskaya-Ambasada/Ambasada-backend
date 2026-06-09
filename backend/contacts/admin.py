from core.base_admin import BaseAdmin
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseModelFormSet
from django.utils.translation import gettext_lazy as _

from contacts import constants
from contacts.models import ContactRequest, ContactSocialLink, get_default_site_config


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
        match self.value():
            case 'yes':
                return queryset.filter(is_active=True)
            case 'no':
                return queryset.filter(is_active=False)
            case _:
                return queryset


@admin.register(ContactRequest)
class ContactRequestAdmin(BaseAdmin):
    """Админка для обработки входящих заявок с формы контактов."""

    list_display = ('name', 'email', 'created_at', 'is_processed')
    list_filter = ('created_at', 'is_processed')
    list_editable = ('is_processed',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    ordering = ('is_processed', '-created_at')

    def has_add_permission(self, request):
        return False


class ContactSocialLinkFormSet(BaseModelFormSet):
    """Перехватчик ошибок для списка социальных сетей."""

    def clean(self):
        super().clean()

        for form in self.forms:
            if '__all__' in form._errors:
                error_msg = ' '.join(form._errors['__all__'])
                form._errors.pop('__all__')
                raise ValidationError(error_msg)


class ContactSocialLinkAdminForm(forms.ModelForm):
    """Форма админки с проверкой уникальности до сохранения в БД."""

    class Meta:
        model = ContactSocialLink
        fields = '__all__'

    def clean(self):
        """Проверяет дубли типа и порядка с учетом скрытого site_config."""
        cleaned_data = super().clean()
        site_config = self.instance.site_config if self.instance.site_config_id else get_default_site_config()
        if not site_config:
            return cleaned_data
        same_site_links = ContactSocialLink.objects.filter(site_config=site_config)
        if self.instance.pk:
            same_site_links = same_site_links.exclude(pk=self.instance.pk)
        social_type = cleaned_data.get('social_type')
        if social_type and same_site_links.filter(social_type=social_type).exists():
            self.add_error('social_type', constants.ERROR_DUPLICATE_SOCIAL_TYPE)
        order = cleaned_data.get('order')
        if order is not None and same_site_links.filter(order=order).exists():
            self.add_error('order', constants.ERROR_DUPLICATE_SOCIAL_ORDER)
        return cleaned_data


@admin.register(ContactSocialLink)
class ContactSocialLinkAdmin(BaseAdmin):
    """Админка для управления ссылками на соцсети и мессенджеры."""

    form = ContactSocialLinkAdminForm
    exclude = ('site_config',)
    list_display = ('id', 'social_type', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('social_type', IsActiveOnSiteFilter)
    search_fields = ('url',)
    ordering = ('order',)

    def get_changelist_formset(self, request, **kwargs):
        """Инжектим перехватчик для списка соцсетей."""
        kwargs['formset'] = ContactSocialLinkFormSet
        return super().get_changelist_formset(request, **kwargs)
