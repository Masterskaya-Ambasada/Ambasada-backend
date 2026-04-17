"""Регистрация моделей для Django admin."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import AboutPage, GalleryImage, TeamMember, Value


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    """Настройка отображения ценностей в админке."""

    list_display = ('title', 'text')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Настройка отображения членов команды в админке."""

    list_display = ('name', 'role')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """Настройка отображения изображений галереи в админке."""

    list_display = ('alt',)


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    """Настройка отображения страницы 'О нас' в админке."""

    fieldsets = (
        (_('Hero'), {'fields': ('hero_title', 'hero_description', 'image_left', 'image_right')}),
        (_('About'), {'fields': ('about_title', 'paragraph_1', 'paragraph_2', 'button_label', 'button_link')}),
        (_('Values'), {'fields': ('values_title',)}),
        (_('Team'), {'fields': ('team_title', 'team_button_label', 'team_button_link')}),
        (_('Gallery'), {'fields': ('gallery_title',)}),
    )
