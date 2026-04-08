"""Регистрация моделей для Django admin."""

from django.contrib import admin
from .models import Value, TeamMember, GalleryImage, AboutPage

admin.site.register(Value)
admin.site.register(TeamMember)
admin.site.register(GalleryImage)
admin.site.register(AboutPage)
