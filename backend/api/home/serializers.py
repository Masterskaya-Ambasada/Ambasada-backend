from __future__ import annotations

from django.utils import translation
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from projects.models import Project
from rest_framework import serializers

from api.users.serializers import TeamMemberSerializer


def get_home_lang_suffix(context: dict) -> str:
    """Определяет языковой суффикс на основе контекста запроса или активного потока."""
    request = context.get('request')
    if request:
        lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        return lang.lower().replace('-', '_')

    current_lang = translation.get_language() or 'ru'
    return current_lang.lower().replace('-', '_')


class ActionButtonSerializer(serializers.Serializer):
    """Компонент интерактивной кнопки."""

    label = serializers.CharField(max_length=50, help_text=_('Текст на кнопке'))
    link = serializers.CharField(help_text=_('Ссылка перехода'))


class HomeProjectItemSerializer(serializers.ModelSerializer):
    """Сериализатор для превью-карточки проекта на главной странице с поддержкой динамической локализации."""

    id = serializers.CharField(source='slug', help_text=_('Уникальный строковый идентификатор проекта'))
    year = serializers.CharField()
    image = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    project_type = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

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

    def get_title(self, obj) -> str:
        """Возвращает локализованное название проекта с фолбэком на русский язык."""
        suffix = self.context.get('lang_suffix') or get_home_lang_suffix(self.context)
        return getattr(obj, f'title_{suffix}', None) or getattr(obj, 'title_ru', obj.title)

    def get_description(self, obj) -> str:
        """Возвращает локализованное краткое описание проекта с фолбэком на русский язык."""
        suffix = self.context.get('lang_suffix') or get_home_lang_suffix(self.context)
        return getattr(obj, f'description_{suffix}', None) or getattr(obj, 'description_ru', obj.description)

    @extend_schema_field(serializers.CharField(default=''))
    def get_project_type(self, obj) -> str:
        """Возвращает локализованный тип проекта."""
        if not getattr(obj, 'project_type', None):
            return ''
        suffix = self.context.get('lang_suffix') or get_home_lang_suffix(self.context)
        pt = obj.project_type
        return getattr(pt, f'label_{suffix}', None) or getattr(pt, 'label_ru', getattr(pt, 'label', ''))

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_tags(self, obj) -> list[str]:
        """Возвращает список локализованных тегов проекта."""
        suffix = self.context.get('lang_suffix') or get_home_lang_suffix(self.context)
        field_name = f'label_{suffix}'

        return [
            getattr(tag, field_name, None) or getattr(tag, 'label_ru', getattr(tag, 'label', ''))
            for tag in obj.tags.all()
        ]

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
        """Кнопка перехода к детальной странице проекта с гарантированным переводом."""
        slug = getattr(obj, 'slug', '')
        suffix = get_home_lang_suffix(self.context)
        lang_code = suffix.replace('_', '-')

        with translation.override(lang_code):
            translated_label = translation.gettext('Перейти к проекту')

        return {'label': translated_label, 'link': f'/projects/{slug}'}


class BaseHomeSectionSerializer(serializers.Serializer):
    """Базовый класс секций с хелперами для путей."""

    def _get_absolute_url(self, url_path: str | None) -> str | None:
        """Преобразует относительный путь медиа-файла в абсолютный URL."""
        if not url_path:
            return None
        request = self.context.get('request')
        if request and not url_path.startswith('http'):
            return request.build_absolute_uri(url_path)
        return url_path


class HomeHeroSectionSerializer(BaseHomeSectionSerializer):
    """Промо-блок (Hero) главной страницы."""

    title = serializers.CharField(default='')
    subtitle = serializers.CharField(default='')
    image_left = serializers.SerializerMethodField()
    image_right = serializers.SerializerMethodField()
    action_button = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image_left(self, obj) -> str | None:
        """Абсолютный URL левого изображения промо-блока."""
        return self._get_absolute_url(obj.get('image_left'))

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image_right(self, obj) -> str | None:
        """Абсолютный URL правого изображения промо-блока."""
        return self._get_absolute_url(obj.get('image_right'))

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        """Данные интерактивной кнопки промо-блока."""
        return {
            'label': obj.get('hero_button_label') or '',
            'link': obj.get('hero_button_link') or '/projects',
        }


class HomeAboutPreviewSectionSerializer(BaseHomeSectionSerializer):
    """Блок краткой информации о сообществе."""

    title = serializers.CharField(source='about_title', default='')
    text = serializers.CharField(source='about_text', default='')
    image = serializers.SerializerMethodField()
    action_button = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image(self, obj) -> str | None:
        """Абсолютный URL изображения блока о сообществе."""
        return self._get_absolute_url(obj.get('about_image'))

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        """Данные интерактивной кнопки блока о сообществе."""
        suffix = get_home_lang_suffix(self.context)
        lang_code = suffix.replace('_', '-')

        with translation.override(lang_code):
            fallback_label = translation.gettext('Подробнее')

        return {
            'label': obj.get('about_team_button_label') or obj.get('about_button_label') or fallback_label,
            'link': '/about',
        }


class HomeTeamPreviewSectionSerializer(BaseHomeSectionSerializer):
    """Блок превью участников команды."""

    title = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    action_button = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_title(self, obj) -> str:
        """Возвращает заголовок секции команды с учетом фолбэка локализации."""
        config = obj.get('config') or {}
        suffix = get_home_lang_suffix(self.context)
        lang_code = suffix.replace('_', '-')

        with translation.override(lang_code):
            fallback_title = translation.gettext('Наша команда')

        return config.get('team_title') or fallback_title

    @extend_schema_field(TeamMemberSerializer(many=True))
    def get_members(self, obj) -> list:
        """Возвращает список сериализованных участников команды."""
        members_queryset = obj.get('members', [])
        serializer = TeamMemberSerializer(members_queryset, many=True, context=self.context)
        if 'id' in serializer.child.fields:
            serializer.child.fields.pop('id', None)
        return serializer.data

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        """Данные кнопки перехода к списку контактов и команды."""
        config = obj.get('config') or {}
        suffix = get_home_lang_suffix(self.context)
        lang_code = suffix.replace('_', '-')

        with translation.override(lang_code):
            fallback_label = translation.gettext('Присоединиться к команде')

        return {
            'label': config.get('main_team_button_label') or config.get('team_button_label') or fallback_label,
            'link': config.get('team_button_link') or '/contacts',
        }


class HomeProjectsPreviewSectionSerializer(BaseHomeSectionSerializer):
    """Блок со списком свежих проектов."""

    title = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    action_button = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_title(self, obj) -> str:
        """Возвращает заголовок секции свежих проектов."""
        config = obj.get('config') or {}
        suffix = get_home_lang_suffix(self.context)
        lang_code = suffix.replace('_', '-')

        with translation.override(lang_code):
            fallback_title = translation.gettext('Наши проекты')

        return config.get('projects_title') or fallback_title

    @extend_schema_field(HomeProjectItemSerializer(many=True))
    def get_items(self, obj) -> list:
        """Возвращает список локализованных карточек проектов для главной."""
        projects = obj.get('projects', [])
        return HomeProjectItemSerializer(projects, many=True, context=self.context).data

    @extend_schema_field(ActionButtonSerializer)
    def get_action_button(self, obj) -> dict:
        """Данные кнопки перехода ко всем проектам."""
        config = obj.get('config') or {}
        suffix = get_home_lang_suffix(self.context)
        lang_code = suffix.replace('_', '-')

        with translation.override(lang_code):
            fallback_label = translation.gettext('Все проекты')

        return {
            'label': config.get('projects_button_label') or fallback_label,
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
        """Формирует данные промо-блока главной страницы."""
        return HomeHeroSectionSerializer(obj.get('config'), context=self.context).data

    @extend_schema_field(HomeAboutPreviewSectionSerializer)
    def get_about_preview(self, obj) -> dict:
        """Формирует данные превью-блока информации о сообществе."""
        return HomeAboutPreviewSectionSerializer(obj.get('config'), context=self.context).data

    @extend_schema_field(HomeTeamPreviewSectionSerializer)
    def get_team_preview(self, obj) -> dict:
        """Формирует данные блока участников команды."""
        return HomeTeamPreviewSectionSerializer(
            {
                'config': obj.get('config'),
                'members': obj.get('team_members'),
            },
            context=self.context,
        ).data

    @extend_schema_field(HomeProjectsPreviewSectionSerializer)
    def get_projects_preview(self, obj) -> dict:
        """Формирует блок со списком свежих проектов."""
        return HomeProjectsPreviewSectionSerializer(
            {'config': obj.get('config'), 'projects': obj.get('projects')},
            context=self.context,
        ).data
