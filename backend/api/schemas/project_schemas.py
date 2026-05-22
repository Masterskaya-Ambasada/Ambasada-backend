from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)

from api.projects.constants import (
    ACCEPT_LANGUAGE_HEADER,
    PATH_PARAM_PROJECT_SLUG,
    PROJECT_TYPES_RESPONSE_KEY,
    QUERY_PARAM_PROJECT_TYPE,
    QUERY_PARAM_SEARCH,
    QUERY_PARAM_TAG,
    SUPPORTED_LANGUAGE_CODES,
)
from api.projects.serializers import ProjectCardSerializer, ProjectDetailSerializer, ProjectTypeSerializer

PROJECT_LANGUAGE_PARAMETER = OpenApiParameter(
    name=ACCEPT_LANGUAGE_HEADER,
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=False,
    enum=list(SUPPORTED_LANGUAGE_CODES),
    description=_('Код языка ответа. Поддерживаются ru, en, sr-latn и sr-cyrl.'),
)

PROJECT_DETAIL_PATH_PARAMETER = OpenApiParameter(
    name=PATH_PARAM_PROJECT_SLUG,
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    required=True,
    description=_('Slug проекта. Например: belgrade-navigation.'),
)

PROJECT_TAG_LIST_RESPONSE_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'string',
    },
}

PROJECT_TYPES_RESPONSE_SERIALIZER = inline_serializer(
    name='ProjectTypesResponse',
    fields={
        PROJECT_TYPES_RESPONSE_KEY: ProjectTypeSerializer(many=True),
    },
)

PROJECT_LIST_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Список проектов'),
        description=_(
            'Возвращает список опубликованных проектов с пагинацией, поиском по названию '
            'и фильтрацией по типу проекта и тегам.'
        ),
        parameters=[
            PROJECT_LANGUAGE_PARAMETER,
            OpenApiParameter(
                name=QUERY_PARAM_PROJECT_TYPE,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_('Идентификатор типа проекта для фильтрации.'),
            ),
            OpenApiParameter(
                name=QUERY_PARAM_TAG,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_(
                    'Тег для фильтрации. Поддерживаются повторяющиеся query params '
                    '(`?tag=urban&tag=belgrade`) и CSV-формат (`?tag=urban,belgrade`).'
                ),
            ),
            OpenApiParameter(
                name=QUERY_PARAM_SEARCH,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_('Строка поиска по названию проекта.'),
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=ProjectCardSerializer(many=True),
                description=_('Список опубликованных проектов с пагинацией.'),
                examples=[
                    OpenApiExample(
                        'Список проектов',
                        value={
                            'items': [
                                {
                                    'id': 'belgrade-navigation',
                                    'title': 'Белградская навигация',
                                    'description': 'Исследование городской навигации в Белграде.',
                                    'project_type': 'Исследование',
                                    'tags': ['Белград', 'Урбанистика'],
                                    'year': '2024',
                                    'image': 'http://localhost:8000/media/projects/belgrade-navigation/cover/cover.webp',
                                    'action_button': {
                                        'label': 'Перейти к проекту',
                                        'link': '/projects/belgrade-navigation',
                                    },
                                }
                            ],
                            'pagination': {
                                'totalItems': 1,
                                'offset': 0,
                                'limit': 20,
                                'isNext': False,
                            },
                        },
                    )
                ],
            )
        },
    )
)

PROJECT_DETAIL_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Детальная страница проекта'),
        description=_('Возвращает основную информацию о проекте и список контентных блоков.'),
        parameters=[
            PROJECT_LANGUAGE_PARAMETER,
            PROJECT_DETAIL_PATH_PARAMETER,
        ],
        responses={
            200: OpenApiResponse(
                response=ProjectDetailSerializer,
                description=_('Детальная страница опубликованного проекта.'),
                examples=[
                    OpenApiExample(
                        'Детальная страница проекта',
                        value={
                            'info': {
                                'id': 'belgrade-navigation',
                                'title': 'Белградская навигация',
                                'description': 'Исследование городской навигации в Белграде.',
                                'project_type': 'Исследование',
                                'tags': ['Белград', 'Урбанистика'],
                                'year': '2024',
                                'image': [
                                    'http://localhost:8000/media/projects/belgrade-navigation/gallery/01.webp',
                                ],
                            },
                            'content_blocks': [
                                {
                                    'variant': 3,
                                    'index': '001',
                                    'title': 'Исследование',
                                    'image': None,
                                    'text': '<p>Основной текст блока</p>',
                                    'accented_text': '<p>Акцентный текст блока</p>',
                                    'buttons': [
                                        {
                                            'label': 'Скачать материалы проекта',
                                            'type': 'download',
                                            'url': 'https://cdn.example.com/project.pdf',
                                        }
                                    ],
                                }
                            ],
                        },
                    )
                ],
            ),
            404: OpenApiResponse(description=_('Проект не найден или не опубликован.')),
        },
    )
)

PROJECT_TAGS_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Список тегов проектов'),
        description=_('Возвращает теги, доступные для фильтрации опубликованных проектов.'),
        parameters=[PROJECT_LANGUAGE_PARAMETER],
        responses={
            200: OpenApiResponse(
                response=PROJECT_TAG_LIST_RESPONSE_SCHEMA,
                description=_('Список тегов опубликованных проектов.'),
                examples=[
                    OpenApiExample(
                        'Список тегов',
                        value=['Урбанистика', 'Белград'],
                    )
                ],
            )
        },
    )
)

PROJECT_TYPES_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Список типов проектов'),
        description=_('Возвращает типы проектов для фильтрации и поиска на фронтенде.'),
        parameters=[PROJECT_LANGUAGE_PARAMETER],
        responses={
            200: OpenApiResponse(
                response=PROJECT_TYPES_RESPONSE_SERIALIZER,
                description=_('Список типов опубликованных проектов.'),
                examples=[
                    OpenApiExample(
                        'Список типов проектов',
                        value={
                            PROJECT_TYPES_RESPONSE_KEY: [
                                {
                                    'id': 'research',
                                    'label': 'Исследование',
                                }
                            ]
                        },
                    )
                ],
            )
        },
    )
)
