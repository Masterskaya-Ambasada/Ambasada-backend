"""Регистрация модели User в админ-панели."""

import os
import shutil

from core.base_admin import BaseTranslatedAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseTranslatedAdmin):
    """Административный интерфейс для модели User, с поддержкой перевода."""

    date_hierarchy = 'date_joined'
    empty_value_display = '-empty-'
    ordering = (
        '-is_public',
        'email',
    )
    list_editable = (
        'order',
        'position',
        'is_active',
        'is_staff',
        'is_public',
    )

    list_display_links = ('get_full_name', 'email')
    list_display = [
        'get_full_name',
        'email',
        'position',
        'order',
        'role',
        'is_active',
        'is_staff',
        'is_public',
        'avatar_thumbnail',
    ]
    readonly_fields = (*BaseUserAdmin.readonly_fields, 'photo_preview')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'photo', 'photo_preview')}),
        (
            _('Персональная информация (Русский)'),
            {'fields': ('first_name_ru', 'last_name_ru', 'role_ru'), 'classes': ('collapse',)},
        ),
        (
            _('Персональная информация (Английский)'),
            {'fields': ('first_name_en', 'last_name_en', 'role_en'), 'classes': ('collapse',)},
        ),
        (
            _('Персональная информация (Сербский - Латиница)'),
            {
                'fields': ('first_name_sr_latn', 'last_name_sr_latn', 'role_sr_latn'),
                'classes': ('collapse',),
            },
        ),
        (
            _('Персональная информация (Сербский - Кирилица)'),
            {
                'fields': ('first_name_sr_cyrl', 'last_name_sr_cyrl', 'role_sr_cyrl'),
                'classes': ('collapse',),
            },
        ),
        (_('Разрешения'), {'fields': ('order', 'is_active', 'is_staff', 'is_superuser', 'is_public', 'position')}),
        (_('Активность'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'photo', 'order', 'is_public'),
            },
        ),
    )

    form = UserChangeForm
    add_form = UserCreationForm

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        return self.add_image_preview_widget_class(db_field, formfield)

    def delete_queryset(self, request, queryset):
        """Массовое удаление объектов User с удалением файлов фото."""
        for user in queryset:
            if user.photo:
                full_path = user.photo.path
                uuid_dir = os.path.dirname(full_path)
                if os.path.exists(uuid_dir):
                    shutil.rmtree(uuid_dir)
            user.delete()

    def get_full_name(self, obj):
        """Отображение заголовка динамического поля full_name."""
        return obj.full_name

    get_full_name.short_description = _('Полное имя')

    def avatar_thumbnail(self, obj):
        """Метод для отображения миниатюры изображения в списке."""
        return self.get_image_thumbnail(obj, 'photo')

    avatar_thumbnail.short_description = User._meta.get_field('photo').verbose_name

    @admin.display(description=_('Превью фото'))
    def photo_preview(self, obj):
        return self.get_admin_image_preview(obj, 'photo', width=220, height=220)

    class Media:
        js = ('core/js/admin_image_preview_inline.js',)
        css = {'all': ('core/css/admin_image_preview.css',)}
