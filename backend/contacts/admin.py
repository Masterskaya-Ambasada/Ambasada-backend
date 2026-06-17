from core.base_admin import BaseAdmin
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseModelFormSet
from django.utils.translation import gettext_lazy as _

from contacts.models import ContactRequest, ContactSocialLink


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

    list_display = ('name', 'email', 'created_at', 'notification_status', 'is_processed')
    list_filter = ('created_at', 'notification_status', 'is_processed')
    list_editable = ('is_processed',)
    search_fields = ('name', 'email', 'message')
    exclude = ('notification_attempts', 'notification_error')
    readonly_fields = (
        'name',
        'email',
        'message',
        'reason',
        'created_at',
        'notification_status',
        'notification_sent_at',
    )
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


@admin.register(ContactSocialLink)
class ContactSocialLinkAdmin(BaseAdmin):
    """Админка для управления ссылками на соцсети и мессенджеры."""

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
