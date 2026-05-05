from django import forms
from django.conf import settings
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
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'reason',
        'created_at',
    )
    list_filter = (
        'reason',
        'created_at',
    )
    search_fields = (
        'name',
        'email',
        'message',
        'reason',
    )
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


try:
    from tinymce.widgets import TinyMCE

    TINYMCE_AVAILABLE = True
except ImportError:
    TinyMCE = None
    TINYMCE_AVAILABLE = False


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

    if TINYMCE_AVAILABLE:
        donation_text = forms.CharField(
            required=False,
            label='Текстовый блок для пожертвований',
            widget=TinyMCE(
                attrs={'cols': 100, 'rows': 12},
                mce_attrs=settings.TINYMCE_DEFAULT_CONFIG,
            ),
        )


@admin.register(ContactPageContent)
class ContactPageContentAdmin(admin.ModelAdmin):
    """Админка для управления текстовым блоком пожертвований."""

    form = ContactPageContentAdminForm
    list_display = ('id', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('donation_text',)


@admin.register(ContactSocialLink)
class ContactSocialLinkAdmin(admin.ModelAdmin):
    """Админка для управления ссылками на соцсети и мессенджеры."""

    list_display = ('id', 'social_type', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('social_type', IsActiveOnSiteFilter)
    search_fields = ('url',)
