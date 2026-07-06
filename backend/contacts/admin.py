from core.base_admin import BaseAdmin, BaseTranslatedAdmin
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import Textarea, TextInput
from django.forms.models import BaseModelFormSet
from django.utils.translation import gettext_lazy as _

from contacts.models import ContactPageContent, ContactRequest, ContactSocialLink

FIELD_OVERRIDES = {
    models.CharField: {'widget': TextInput(attrs={'style': 'width: 100%; max-width: 400px; border-radius: 4px;'})},
    models.TextField: {
        'widget': Textarea(
            attrs={
                'rows': 4,
                'style': ('width: 100%; max-width: 400px; ' 'border-radius: 4px; resize: vertical;'),
            }
        )
    },
    models.URLField: {'widget': TextInput(attrs={'style': 'width: 100%; max-width: 400px; border-radius: 4px;'})},
}


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
        'created_at',
        'notification_status',
        'notification_sent_at',
    )
    ordering = ('is_processed', '-created_at')

    def has_add_permission(self, request):
        return False


class ContactSocialLinkForm(forms.ModelForm):
    """Форма с валидацией уникальности social_type и order для добавления/редактирования."""

    class Meta:
        model = ContactSocialLink
        exclude = ('site_config', 'created_at')

    def clean(self):
        """Проверяет уникальность social_type и order для текущего SiteConfig."""
        cleaned_data = super().clean()
        social_type = cleaned_data.get('social_type')
        order = cleaned_data.get('order')
        if not social_type or order is None:
            return cleaned_data

        from contacts.models import get_default_site_config

        site_config = get_default_site_config()
        if not site_config:
            raise ValidationError(_('Сначала создайте настройки сайта'))

        qs = ContactSocialLink.objects.filter(site_config=site_config)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.filter(social_type=social_type).exists():
            raise ValidationError(
                {
                    'social_type': _('Ссылка на «{}» уже существует').format(
                        dict(ContactSocialLink.SocialType.choices).get(social_type, social_type)
                    ),
                }
            )

        if qs.filter(order=order).exists():
            raise ValidationError(
                {
                    'order': _('Порядок отображения «{}» уже занят другой записью').format(order),
                }
            )

        return cleaned_data


class ContactSocialLinkFormSet(BaseModelFormSet):
    """Перехватчик ошибок для списка социальных сетей."""

    def clean(self):
        """Проверяет уникальность порядка отображения среди всех записей в списке и в БД."""
        super().clean()

        for form in self.forms:
            if '__all__' in form._errors:
                error_msg = ' '.join(form._errors['__all__'])
                form._errors.pop('__all__')
                raise ValidationError(error_msg)

        for form in self.forms:
            if form.is_valid() and form.has_changed() and 'order' in form.changed_data:
                new_order = form.cleaned_data['order']
                conflict = (
                    ContactSocialLink.objects.filter(
                        order=new_order,
                        site_config=form.instance.site_config,
                    )
                    .exclude(pk=form.instance.pk)
                    .first()
                )
                if conflict:
                    raise ValidationError(
                        _('Порядок отображения «{}» уже занят записью «{}». ' 'Выберите другой порядок.').format(
                            new_order, conflict.get_social_type_display()
                        )
                    )


@admin.register(ContactSocialLink)
class ContactSocialLinkAdmin(BaseAdmin):
    """Админка для управления ссылками на соцсети и мессенджеры."""

    form = ContactSocialLinkForm
    exclude = ('site_config',)
    list_display = ('social_type', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('social_type', IsActiveOnSiteFilter)
    search_fields = ('url',)
    ordering = ('order',)

    def get_changelist_formset(self, request, **kwargs):
        """Инжектим перехватчик для списка соцсетей."""
        kwargs['formset'] = ContactSocialLinkFormSet
        return super().get_changelist_formset(request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Привязывает site_config по умолчанию при создании новой записи."""
        if not obj.site_config_id:
            from contacts.models import get_default_site_config

            obj.site_config = get_default_site_config()
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Привязывает site_config по умолчанию для новых записей в inline-формсете."""
        if formset.model == ContactSocialLink:
            for f in formset.forms:
                if not f.instance.site_config_id:
                    from contacts.models import get_default_site_config

                    f.instance.site_config = get_default_site_config()
        super().save_formset(request, form, formset, change)


@admin.register(ContactPageContent)
class ContactPageContentAdmin(BaseTranslatedAdmin):
    """Контактные данные организации."""

    formfield_overrides = FIELD_OVERRIDES
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    list_display = ('phone', 'address_ru', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('phone', 'address_ru', 'address_en', 'address_sr_cyrl', 'address_sr_latn')

    fieldsets = (
        (
            _('Основная информация'),
            {'fields': ('phone', 'is_active', 'created_at', 'updated_at')},
        ),
        (
            _('Переводы (Русский)'),
            {'fields': ('address_ru',), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Английский)'),
            {'fields': ('address_en',), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Сербский - Латиница)'),
            {'fields': ('address_sr_latn',), 'classes': ('collapse',)},
        ),
        (
            _('Переводы (Сербский - Кириллица)'),
            {'fields': ('address_sr_cyrl',), 'classes': ('collapse',)},
        ),
    )
