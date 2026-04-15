"""Сериализаторы для API проектов."""

from __future__ import annotations

from rest_framework import serializers

from projects.constants import CONTENT_BLOCK_INDEX_WIDTH
from projects.models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectType,
)


class ProjectTypeSerializer(serializers.ModelSerializer):
    """Сериализатор типа проекта для списка фильтров."""

    id = serializers.CharField(source='slug', read_only=True)

    class Meta:
        model = ProjectType
        fields = ('id', 'label')


class ProjectCardSerializer(serializers.ModelSerializer):
    """Сериализатор карточки проекта для списка и верхнего блока detail."""

    id = serializers.CharField(source='slug', read_only=True)
    project_type = serializers.CharField(source='project_type.label', read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='label')
    year = serializers.SerializerMethodField()
    image = serializers.URLField(source='cover_image', read_only=True)

    class Meta:
        model = Project
        fields = (
            'id',
            'title',
            'description',
            'project_type',
            'tags',
            'year',
            'image',
        )

    def get_year(self, obj: Project) -> str:
        """Возвращает год строкой в формате, ожидаемом фронтендом."""
        return str(obj.year)


class ProjectBlockButtonSerializer(serializers.ModelSerializer):
    """Сериализатор кнопки контентного блока проекта."""

    class Meta:
        model = ProjectBlockButton
        fields = ('label', 'type', 'url')


class ProjectContentBlockSerializer(serializers.ModelSerializer):
    """Сериализатор контентного блока детальной страницы проекта."""

    index = serializers.SerializerMethodField()
    string_list = serializers.ListField(child=serializers.CharField(), read_only=True)
    buttons = ProjectBlockButtonSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectContentBlock
        fields = (
            'variant',
            'index',
            'title',
            'image',
            'left_image',
            'string_list',
            'text',
            'accented_text',
            'buttons',
        )

    def get_index(self, obj: ProjectContentBlock) -> str:
        """Форматирует индекс секции в строку фиксированной ширины."""
        return f'{obj.order:0{CONTENT_BLOCK_INDEX_WIDTH}d}'

    def to_representation(self, instance: ProjectContentBlock) -> dict:
        """Удаляет поля, которые не относятся к выбранному варианту блока."""
        data = super().to_representation(instance)
        if instance.variant != ProjectContentBlock.Variant.IMAGE_WITH_LIST:
            data.pop('string_list', None)
        if instance.variant != ProjectContentBlock.Variant.TWO_IMAGES:
            data.pop('left_image', None)
        if instance.variant != ProjectContentBlock.Variant.IMAGE_WITH_BUTTONS:
            data.pop('buttons', None)
        return data


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Сериализатор детальной страницы проекта."""

    info = ProjectCardSerializer(source='*', read_only=True)
    content_blocks = ProjectContentBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('info', 'content_blocks')
