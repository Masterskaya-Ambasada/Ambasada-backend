from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer

from api.projects.serializers import ProjectCardSerializer, ProjectDetailSerializer, ProjectTypeSerializer

PROJECT_LIST_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Список проектов'),
        description=_(
            'Возвращает список опубликованных проектов с пагинацией, поиском по названию '
            'и фильтрацией по типу проекта и тегам.'
        ),
        parameters=[
            OpenApiParameter(
                name='project_type',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_('Идентификатор типа проекта для фильтрации.'),
            ),
            OpenApiParameter(
                name='tag',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_(
                    'Тег для фильтрации. Поддерживаются повторяющиеся query params '
                    '(`?tag=urban&tag=belgrade`) и CSV-формат (`?tag=urban,belgrade`).'
                ),
            ),
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=_('Строка поиска по названию проекта.'),
            ),
        ],
        responses={200: ProjectCardSerializer(many=True)},
    )
)

PROJECT_DETAIL_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Детальная страница проекта'),
        description=_('Возвращает основную информацию о проекте и список контентных блоков.'),
        responses={200: ProjectDetailSerializer},
    )
)

PROJECT_TAGS_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Список тегов проектов'),
        description=_('Возвращает теги, доступные для фильтрации опубликованных проектов.'),
    )
)

PROJECT_TYPES_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Список типов проектов'),
        description=_('Возвращает типы проектов для фильтрации и поиска на фронтенде.'),
        responses={
            200: inline_serializer(
                name='ProjectTypesResponse',
                fields={
                    'types': ProjectTypeSerializer(many=True),
                },
            )
        },
    )
)
