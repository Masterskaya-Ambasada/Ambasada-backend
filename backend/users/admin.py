from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import User


@admin.register(User)
class UserAdmin(TranslationAdmin):
    """Административный интерфейс для модели User, с поддержкой перевода."""
