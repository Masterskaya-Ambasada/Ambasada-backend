from __future__ import annotations

from django.utils.encoding import force_str
from django.utils.translation import get_language_from_request
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


def get_lang_suffix(context: dict) -> str:
    """Определяет языковой суффикс на основе контекста запроса."""
    suffix = context.get('lang_suffix')
    if suffix:
        return suffix.lower().replace('-', '_')

    request = context.get('request')
    if request:
        lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        return lang.lower().replace('-', '_')
    return 'ru'


class ProjectTypeSerializer(serializers.ModelSerializer):
    """Сериализатор типа проекта для списка фильтров."""

    id = serializers.CharField(source='slug', read_only=True)

    class Meta:
        """Метаданные сериализатора типа проекта."""

        model = ProjectType
        fields = ('id', 'label')

    def __init__(self, *args, **kwargs):
        """Динамически переключает источник поля label под текущую локаль."""
        super().__init__(*args, **kwargs)
        suffix = get_lang_suffix(self.context)
        if f'label_{suffix}' in self.fields:
            self.fields['label'].source = f'label_{suffix}'


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
        """Метаданные сериализатора карточки проекта."""

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

    def __init__(self, *args, **kwargs):
        """Динамически переключает локализованные поля проекта и связанных сущностей."""
        super().__init__(*args, **kwargs)
        suffix = get_lang_suffix(self.context)

        if f'title_{suffix}' in self.fields:
            self.fields['title'].source = f'title_{suffix}'
        if f'description_{suffix}' in self.fields:
            self.fields['description'].source = f'description_{suffix}'

        self.fields['project_type'].source = f'project_type.label_{suffix}'
        self.fields['tags'].slug_field = f'label_{suffix}'

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
        """Метаданные сериализатора верхнего блока детальной страницы."""

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
        """Преобразует ImageFieldFile в абсолютный или относительный URL."""
        if not image:
            return None

        image_url = image.url
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(image_url)
        return image_url

    def get_image(self, obj: Project) -> list[str]:
        """Возвращает массив изображений для карусели детальной страницы."""
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
        """Метаданные сериализатора кнопки блока."""

        model = ProjectBlockButton
        fields = ('label', 'type', 'url')

    def __init__(self, *args, **kwargs):
        """Динамически переключает источник поля label кнопки под текущую локаль."""
        super().__init__(*args, **kwargs)
        suffix = get_lang_suffix(self.context)
        if f'label_{suffix}' in self.fields:
            self.fields['label'].source = f'label_{suffix}'


class ProjectContentBlockSerializer(serializers.ModelSerializer):
    """Сериализатор контентного блока детальной страницы проекта."""

    index = serializers.SerializerMethodField()
    string_list = serializers.ListField(child=serializers.CharField(), read_only=True)
    buttons = ProjectBlockButtonSerializer(many=True, read_only=True)

    class Meta:
        """Метаданные сериализатора контентного блока."""

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

    def __init__(self, *args, **kwargs):
        """Динамически переключает источники текстовых полей контент-блока под локаль запроса."""
        super().__init__(*args, **kwargs)
        suffix = get_lang_suffix(self.context)

        if f'title_{suffix}' in self.fields:
            self.fields['title'].source = f'title_{suffix}'
        if f'text_{suffix}' in self.fields:
            self.fields['text'].source = f'text_{suffix}'
        if f'accented_text_{suffix}' in self.fields:
            self.fields['accented_text'].source = f'accented_text_{suffix}'
        if f'string_list_{suffix}' in self.fields:
            self.fields['string_list'].source = f'string_list_{suffix}'

    def get_index(self, obj: ProjectContentBlock) -> str:
        """Форматирует индекс секции в строку фиксированной ширины."""
        return f'{obj.order:0{CONTENT_BLOCK_INDEX_WIDTH}d}'

    def to_representation(self, instance: ProjectContentBlock) -> dict:
        """Удаляет из ответа поля, не относящиеся к выбранному варианту контент-блока."""
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
        """Метаданные сериализатора детальной страницы проекта."""

        model = Project
        fields = ('info', 'content_blocks')
