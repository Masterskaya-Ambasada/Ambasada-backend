"""Регистрация моделей для Django admin."""

from django.contrib import admin

from .models import AboutPage, GalleryImage, TeamMember, Value

admin.site.register(Value)
admin.site.register(TeamMember)
admin.site.register(GalleryImage)
admin.site.register(AboutPage)
