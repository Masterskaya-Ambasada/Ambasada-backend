"""Сериализаторы для API раздела 'О сообществе'."""

from rest_framework import serializers
from .models import AboutPage, Value, TeamMember, GalleryImage


class ValueSerializer(serializers.ModelSerializer):
    """Сериализация ценностей."""
    class Meta:
        model = Value
        fields = ['id', 'title', 'text']


class TeamMemberSerializer(serializers.ModelSerializer):
    """Сериализация членов команды."""
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'photo']


class GalleryImageSerializer(serializers.ModelSerializer):
    """Сериализация изображений галереи."""
    class Meta:
        model = GalleryImage
        fields = ['id', 'url', 'alt']


class AboutPageSerializer(serializers.ModelSerializer):
    """Сериализация основной страницы 'О нас'."""
    class Meta:
        model = AboutPage
        fields = [
            'hero_title', 'hero_description',
            'about_title', 'paragraph_1', 'paragraph_2',
            'button_text', 'button_link'
        ]
