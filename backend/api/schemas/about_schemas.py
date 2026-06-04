from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers


def about_page_schema_decorator(cls):
    """Декоратор для AboutAPIView."""
    return extend_schema(
        summary=_('Получение страницы "О сообществе"'),
        description=_('Возвращает данные страницы "О нас" со всеми секциями.'),
        responses={
            200: OpenApiResponse(
                description=_('Успешный ответ'),
                response=inline_serializer(
                    name='AboutPageResponse',
                    fields={
                        'about_section': inline_serializer(
                            name='AboutSectionSchema',
                            fields={
                                'title': serializers.CharField(),
                                'paragraphs': inline_serializer(
                                    name='AboutParagraphSchema',
                                    fields={
                                        'first_sentence': serializers.CharField(),
                                        'main_text': serializers.CharField(),
                                    },
                                    many=True,
                                ),
                                'action_button': inline_serializer(
                                    name='AboutActionButtonSchema',
                                    fields={
                                        'text': serializers.CharField(),
                                        'link': serializers.CharField(),
                                    },
                                ),
                            },
                        ),
                        'values': inline_serializer(
                            name='AboutValuesSchema',
                            fields={
                                'title': serializers.CharField(),
                                'items': inline_serializer(
                                    name='AboutValueItemSchema',
                                    fields={
                                        'id': serializers.IntegerField(),
                                        'title': serializers.CharField(),
                                        'text': serializers.CharField(),
                                    },
                                    many=True,
                                ),
                            },
                        ),
                        'team': inline_serializer(
                            name='AboutTeamSchema',
                            fields={
                                'title': serializers.CharField(),
                                'members': inline_serializer(
                                    name='AboutTeamMemberSchema',
                                    fields={
                                        'id': serializers.IntegerField(),
                                        'name': serializers.CharField(),
                                        'role': serializers.CharField(allow_blank=True),
                                        'photo': serializers.URLField(allow_null=True),
                                    },
                                    many=True,
                                ),
                                'action_button': inline_serializer(
                                    name='AboutTeamActionButtonSchema',
                                    fields={
                                        'label': serializers.CharField(),
                                        'link': serializers.CharField(),
                                    },
                                ),
                            },
                        ),
                        'gallery_carousel': inline_serializer(
                            name='AboutGallerySchema',
                            fields={
                                'title': serializers.CharField(),
                                'images': inline_serializer(
                                    name='AboutGalleryImageSchema',
                                    fields={
                                        'id': serializers.IntegerField(),
                                        'url': serializers.URLField(),
                                        'alt': serializers.CharField(),
                                    },
                                    many=True,
                                ),
                            },
                        ),
                    },
                ),
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
                            'message': 'Информация о сообществе не найдена',
                        },
                    )
                ],
            ),
        },
    )(cls)
