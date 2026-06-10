from django.utils.translation import get_language, get_language_from_request, override
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from projects.models import Project
from rest_framework import serializers

from api.users.serializers import TeamMemberSerializer


class ActionButtonSerializer(serializers.Serializer):
    """Компонент интерактивной кнопки."""

    label = serializers.CharField(max_length=50, help_text=_('Текст на кнопке'))
    link = serializers.CharField(help_text=_('Ссылка перехода'))


class HomeProjectItemSerializer(serializers.ModelSerializer):
    """Карточка проекта для главной страницы."""

    id = serializers.CharField(source='slug', help_text=_('Уникальный строковый идентификатор проекта'))
    year = serializers.CharField()
    image = serializers.SerializerMethodField()
    project_type = serializers.CharField(source='project_type.label', default='')
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='label')
    isFirst = serializers.SerializerMethodField()
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
            'isFirst',
            'action_button',
        )

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image(self, obj) -> str | None:
        """Абсолютный URL обложки проекта."""
        if not getattr(obj, 'cover_image', None):
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.cover_image.url)
        return obj.cover_image.url

    @extend_schema_field(serializers.BooleanField)
    def get_isFirst(self, obj) -> bool:
        """Проверка, является ли проект первым в списке."""
        first_id = self.context.get('first_project_id')
        obj_id = getattr(obj, 'id', None)
        return obj_id == first_id if (obj_id and first_id) else False

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        slug = getattr(obj, 'slug', '')
        request = self.context.get('request')

        lang = 'ru'
        if request:
            lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'

        with override(lang.lower()):
            print('ACTIVE INSIDE:', get_language())

            translated_label = _('Перейти к проекту')

            print('TRANSLATED:', repr(translated_label))

        result = {
            'label': translated_label,
            'link': f'/projects/{slug}',
        }
        return result


class BaseHomeSectionSerializer(serializers.Serializer):
    """Базовый класс секций с хелперами для мультиязычного кэша и путей."""

    def _get_lang_value(self, obj, base_key, default='') -> str:
        if not obj:
            return default
        request = self.context.get('request')
        lang = 'ru'
        if request:
            lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        lang = lang.lower()

        return obj.get(f'{base_key}_{lang}') or obj.get(base_key) or default

    def _get_absolute_url(self, url_path: str | None) -> str | None:
        if not url_path:
            return None
        request = self.context.get('request')
        if request and not url_path.startswith('http'):
            return request.build_absolute_uri(url_path)
        return url_path


class HomeHeroSectionSerializer(BaseHomeSectionSerializer):
    """Промо-блок (Hero) главной страницы."""

    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    image_left = serializers.SerializerMethodField()
    image_right = serializers.SerializerMethodField()
    action_button = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_title(self, obj) -> str:
        return self._get_lang_value(obj, 'title')

    @extend_schema_field(serializers.CharField())
    def get_subtitle(self, obj) -> str:
        return self._get_lang_value(obj, 'subtitle')

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image_left(self, obj) -> str | None:
        return self._get_absolute_url(obj.get('image_left'))

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image_right(self, obj) -> str | None:
        return self._get_absolute_url(obj.get('image_right'))

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        return {
            'label': (self._get_lang_value(obj, 'hero_button_label') or ''),
            'link': obj.get('hero_button_link') or '/projects',
        }


class HomeAboutPreviewSectionSerializer(BaseHomeSectionSerializer):
    """Блок краткой информации о сообществе."""

    title = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    action_button = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_title(self, obj) -> str:
        return self._get_lang_value(obj, 'about_title')

    @extend_schema_field(serializers.CharField())
    def get_text(self, obj) -> str:
        return self._get_lang_value(obj, 'about_text')

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image(self, obj) -> str | None:
        return self._get_absolute_url(obj.get('about_image'))

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        label_text = self._get_lang_value(obj, 'about_team_button_label') or 'Узнать больше'
        return {'label': label_text, 'link': '/about'}


class HomeTeamPreviewSectionSerializer(BaseHomeSectionSerializer):
    """Блок превью участников команды."""

    title = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    action_button = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_title(self, obj) -> str:
        config = obj.get('config') or {}
        return self._get_lang_value(config, 'team_title') or ''

    @extend_schema_field(TeamMemberSerializer(many=True))
    def get_members(self, obj) -> list:
        members_queryset = obj.get('members', [])
        serializer = TeamMemberSerializer(members_queryset, many=True, context=self.context)
        if 'id' in serializer.child.fields:
            serializer.child.fields.pop('id', None)
        return serializer.data

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        config = obj.get('config') or {}
        return {
            'label': (self._get_lang_value(config, 'main_team_button_label') or ''),
            'link': config.get('team_button_link') or '/contacts',
        }


class HomeProjectsPreviewSectionSerializer(BaseHomeSectionSerializer):
    """Блок со списком свежих проектов."""

    title = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    action_button = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_title(self, obj) -> str:
        config = obj.get('config') or {}
        return self._get_lang_value(config, 'projects_title') or ''

    @extend_schema_field(HomeProjectItemSerializer(many=True))
    def get_items(self, obj) -> list:
        projects = obj.get('projects', [])
        return HomeProjectItemSerializer(projects, many=True, context=self.context).data

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        config = obj.get('config') or {}
        return {
            'label': (self._get_lang_value(config, 'projects_button_label') or ''),
            'link': config.get('projects_button_link') or '/projects',
        }


class HomePageRootSerializer(serializers.Serializer):
    """Агрегатор структуры главной страницы."""

    hero = serializers.SerializerMethodField()
    about_preview = serializers.SerializerMethodField()
    team_preview = serializers.SerializerMethodField()
    projects_preview = serializers.SerializerMethodField()

    @extend_schema_field(HomeHeroSectionSerializer)
    def get_hero(self, obj) -> dict:
        return HomeHeroSectionSerializer(obj.get('config'), context=self.context).data

    @extend_schema_field(HomeAboutPreviewSectionSerializer)
    def get_about_preview(self, obj) -> dict:
        return HomeAboutPreviewSectionSerializer(obj.get('config'), context=self.context).data

    @extend_schema_field(HomeTeamPreviewSectionSerializer)
    def get_team_preview(self, obj) -> dict:
        return HomeTeamPreviewSectionSerializer(
            {
                'config': obj.get('config'),
                'members': obj.get('team_members'),
            },
            context=self.context,
        ).data

    @extend_schema_field(HomeProjectsPreviewSectionSerializer)
    def get_projects_preview(self, obj) -> dict:
        return HomeProjectsPreviewSectionSerializer(
            {'config': obj.get('config'), 'projects': obj.get('projects')},
            context=self.context,
        ).data
