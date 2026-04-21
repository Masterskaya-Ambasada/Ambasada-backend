import os

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from modeltranslation.admin import TranslationAdmin
from django.utils.html import format_html
from django.conf import settings
from .models import User
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class UserAdmin(BaseUserAdmin, TranslationAdmin):
    """Административный интерфейс для модели User, с поддержкой перевода."""

    date_hierarchy = 'date_joined'
    empty_value_display = '-empty-'
    ordering = ('email',)
    list_display = [
        'get_full_name',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'is_staff',
        'is_public',
        'image_thumbnail'
    ]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('photo', 'is_public')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'photo', 'is_public'),
        }),
    )

    form = UserChangeForm
    add_form = UserCreationForm


    def delete_queryset(self, request, queryset):
        """Массовое удаление объектов User с удалением файлов фото."""
        for user in queryset:
            if (
                user.photo
            ):  # если в модели User будет переопределен метод delete с удалением фото, заменить на user.delete()
                full_path = user.photo.path
                if os.path.isfile(full_path):
                    os.remove(full_path)
            user.delete()

    def get_full_name(self, obj):
        """Отображение заголовка динамического поля full_name."""
        return obj.full_name
    get_full_name.short_description = _('Полное имя')

    def image_thumbnail(self, obj):
        """Метод для отображения миниатюры изображения в списке."""
        if obj.photo:
            photo_url = f"{settings.MEDIA_URL}{obj.photo}"
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 4px;" />',
                photo_url)
        return "-empty-"
    image_thumbnail.short_description = _('Фото') # добавить в переводы Фото
