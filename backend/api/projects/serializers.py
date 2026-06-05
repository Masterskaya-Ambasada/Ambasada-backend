from __future__ import annotations

from django.utils.encoding import force_str
from drf_spectacular.utils import extend_schema_field
from projects.constants import CONTENT_BLOCK_INDEX_WIDTH
from projects.models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectType,
)
from rest_framework import serializers

from api.projects.constants import (
    PROJECT_ACTION_BUTTON_LABEL,
    PROJECT_ACTION_BUTTON_LINK_TEMPLATE,
)


class ProjectTypeSerializer(serializers.ModelSerializer):
    """Сериализатор типа проекта для списка фильтров."""

    id = serializers.CharField(source='slug', read_only=True)

    class Meta:
        model = ProjectType
        fields = ('id', 'label')


class ProjectActionButtonSerializer(serializers.Serializer):
    """Схема кнопки перехода к проекту для OpenAPI и ответов API."""

    label = serializers.CharField()
    link = serializers.CharField()


class ProjectCardSerializer(serializers.ModelSerializer):
    """Сериализатор карточки проекта для списка проектов."""

    id = serializers.CharField(source='slug', read_only=True)
    project_type = serializers.CharField(source='project_type.label', read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='label')
    year = serializers.SerializerMethodField()
    image = serializers.ImageField(source='cover_image', read_only=True)
    action_button = serializers.SerializerMethodField()

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
            'action_button',
        )

    def get_year(self, obj: Project) -> str:
        """Возвращает год строкой в формате, ожидаемом фронтендом."""
        return str(obj.year)

    @extend_schema_field(ProjectActionButtonSerializer)
    def get_action_button(self, obj: Project) -> dict[str, str]:
        """Возвращает кнопку перехода к детальной странице проекта."""
        return {
            'label': force_str(PROJECT_ACTION_BUTTON_LABEL),
            'link': PROJECT_ACTION_BUTTON_LINK_TEMPLATE.format(slug=obj.slug),
        }


class ProjectDetailInfoSerializer(ProjectCardSerializer):
    """Сериализатор верхнего блока детальной страницы проекта."""

    image = serializers.SerializerMethodField()

    class Meta(ProjectCardSerializer.Meta):
        fields = (
            'id',
            'title',
            'description',
            'project_type',
            'tags',
            'year',
            'image',
        )

    def _build_image_url(self, image) -> str | None:
        """Преобразует ImageFieldFile в URL в формате DRF."""
        if not image:
            return None

        image_url = image.url
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(image_url)
        return image_url

    def get_image(self, obj: Project) -> list[str]:
        """
        Возвращает массив изображений для карусели детальной страницы.

        Приоритет отдается изображениям из связанной галереи.
        Если галерея пуста, используется cover_image как fallback.
        """
        image_urls: list[str] = []
        for gallery_image in obj.gallery_images.all():
            image_url = self._build_image_url(gallery_image.image)
            if image_url:
                image_urls.append(image_url)

        if image_urls:
            return image_urls

        cover_image_url = self._build_image_url(obj.cover_image)
        return [cover_image_url] if cover_image_url else []


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

    info = ProjectDetailInfoSerializer(source='*', read_only=True)
    content_blocks = ProjectContentBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('info', 'content_blocks')
