from core.base_admin import BaseTranslatedAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE

from .models import SecurityPolicy


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(BaseTranslatedAdmin):
    """Настройка админки для политики конфиденциальности."""

    list_display = ('short_text', 'updated_at')

    def get_form(self, request, obj=None, **kwargs):
        """Локально подменяем виджеты для всех языковых версий поля text."""
        form = super().get_form(request, obj, **kwargs)

        locales = ['ru', 'en', 'sr_latn', 'sr_cyrl']

        for lang in locales:
            field_name = f'text_{lang}'
            if field_name in form.base_fields:
                form.base_fields[field_name].widget = TinyMCE()

        return form

    def short_text(self, obj):
        """Отображает первые 10 слов текста в списке, чтобы не раздувать таблицу."""
        return 'Текст политики'

    short_text.short_description = _('Текст политики')

    def has_add_permission(self, request):
        if SecurityPolicy.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
