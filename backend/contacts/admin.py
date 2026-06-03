from core.base_admin import BaseAdmin, BaseTranslatedAdmin
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseModelFormSet
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


class ContactPageContentFormSet(BaseModelFormSet):
    """Перехватчик ошибок валидации для вывода их наверх."""

    def clean(self):
        super().clean()

        active_count = 0
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            cleaned_data = getattr(form, 'cleaned_data', {})
            if cleaned_data and cleaned_data.get('is_active'):
                active_count += 1

        if active_count > 1:
            self._clear_form_errors()
            raise ValidationError(
                _('Вы не можете активировать несколько блоков одновременно через список. Выберите только один.')
            )
        self._clear_form_errors()

    def _clear_form_errors(self):
        """Вспомогательный метод для полной очистки строк от системных ошибок constraints."""
        for form in self.forms:
            if '__all__' in form._errors:
                form._errors.pop('__all__')
            if 'is_active' in form._errors:
                form._errors.pop('is_active')


@admin.register(ContactPageContent)
class ContactPageContentAdmin(BaseTranslatedAdmin):
    """Админка для управления текстовым блоком пожертвований."""

    list_display = ('updated_at', 'is_active')
    list_editable = ('is_active',)

    search_fields = ('donation_text_ru', 'donation_text_en')
    ordering = ['created_at']
    tinymce_fields = ['donation_text_ru', 'donation_text_en', 'donation_text_sr_latn', 'donation_text_sr_cyrl']

    fieldsets = (
        (None, {'fields': ('is_active',)}),
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

    def get_changelist_formset(self, request, **kwargs):
        """Подменяем стандартный FormSet на наш перехватчик."""
        kwargs['formset'] = ContactPageContentFormSet
        return super().get_changelist_formset(request, **kwargs)


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
