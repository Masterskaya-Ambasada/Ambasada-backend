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

ABOUT_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Получение страницы "О сообществе"'),
        description=_('Возвращает данные страницы "О нас" со всеми секциями.'),
        responses={
            200: OpenApiResponse(
                description=_('Успешный ответ'),
                response=inline_serializer(
                    name='AboutPageResponse',
                    fields={
                        'hero': inline_serializer(
                            name='AboutHero',
                            fields={
                                'title': serializers.CharField(),
                                'description': serializers.CharField(),
                                'image_left': serializers.URLField(allow_null=True),
                                'image_right': serializers.URLField(allow_null=True),
                            },
                        ),
                        'about_section': inline_serializer(
                            name='AboutSection',
                            fields={
                                'title': serializers.CharField(),
                                'paragraphs': inline_serializer(
                                    name='AboutParagraph',
                                    fields={
                                        'first_sentence': serializers.CharField(),
                                        'main_text': serializers.CharField(),
                                    },
                                    many=True,
                                ),
                                'action_button': inline_serializer(
                                    name='AboutActionButton',
                                    fields={
                                        'text': serializers.CharField(),
                                        'link': serializers.CharField(),
                                    },
                                ),
                            },
                        ),
                        'values': inline_serializer(
                            name='AboutValues',
                            fields={
                                'title': serializers.CharField(),
                                'items': inline_serializer(
                                    name='AboutValueItem',
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
                            name='AboutTeam',
                            fields={
                                'title': serializers.CharField(),
                                'members': inline_serializer(
                                    name='AboutTeamMember',
                                    fields={
                                        'id': serializers.IntegerField(),
                                        'name': serializers.CharField(),
                                        'position': serializers.CharField(allow_blank=True),
                                        'photo': serializers.URLField(allow_null=True),
                                    },
                                    many=True,
                                ),
                                'action_button': inline_serializer(
                                    name='TeamActionButton',
                                    fields={
                                        'label': serializers.CharField(),
                                        'link': serializers.CharField(),
                                    },
                                ),
                            },
                        ),
                        'gallery_carousel': inline_serializer(
                            name='AboutGallery',
                            fields={
                                'title': serializers.CharField(),
                                'images': inline_serializer(
                                    name='AboutGalleryImage',
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
    )
)
