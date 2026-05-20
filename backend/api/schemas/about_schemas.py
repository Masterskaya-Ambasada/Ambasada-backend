"""OpenAPI схемы для About API."""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers

from api.about.serializers import AboutPageSerializer

ABOUT_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Получение страницы "О сообществе"'),
        description=_('Возвращает данные страницы "О нас" со всеми секциями.'),
        responses={
            200: OpenApiResponse(
                response=AboutPageSerializer,
                description=_('Успешный ответ'),
            ),
            404: OpenApiResponse(
                response=inline_serializer(
                    name='AboutNotFoundResponse',
                    fields={
                        'status': serializers.IntegerField(),
                        'code': serializers.CharField(),
                        'message': serializers.CharField(),
                    },
                ),
                description=_('Страница не найдена'),
                examples=[
                    OpenApiExample(
                        'Ошибка',
                        value={
                            'status': 404,
                            'code': 'NOT_FOUND',
                            'message': 'Проект не найден',
                        },
                    )
                ],
            ),
        },
    )
)
