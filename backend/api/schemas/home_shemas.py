from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers

HOME_VIEW_SCHEMA = extend_schema(
    summary=_('Данные главной страницы'),
    description=_('Возвращает структурированный контент для всех блоков главной страницы.'),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name='HomeResponse',
                fields={
                    'hero': inline_serializer(
                        name='HomeHero',
                        fields={
                            'title': serializers.CharField(),
                            'subtitle': serializers.CharField(),
                            'image_left': serializers.CharField(allow_null=True),
                            'image_right': serializers.CharField(allow_null=True),
                            'action_button': inline_serializer(
                                name='HeroButton',
                                fields={
                                    'label': serializers.CharField(),
                                    'link': serializers.CharField(),
                                },
                            ),
                        },
                    ),
                    'about_preview': inline_serializer(
                        name='HomeAboutPreview',
                        fields={
                            'title': serializers.CharField(),
                            'text': serializers.CharField(),
                            'image': serializers.CharField(allow_null=True),
                            'action_button': inline_serializer(
                                name='AboutPreviewButton',
                                fields={
                                    'label': serializers.CharField(),
                                    'link': serializers.CharField(),
                                },
                            ),
                        },
                    ),
                    'team_preview': inline_serializer(
                        name='HomeTeamPreview',
                        fields={
                            'title': serializers.CharField(),
                            'members': serializers.ListField(
                                child=inline_serializer(
                                    name='TeamMemberPreview',
                                    fields={
                                        'name': serializers.CharField(),
                                        'role': serializers.CharField(),
                                        'photo': serializers.CharField(allow_null=True),
                                    },
                                )
                            ),
                            'action_button': inline_serializer(
                                name='TeamPreviewButton',
                                fields={
                                    'label': serializers.CharField(),
                                    'link': serializers.CharField(),
                                },
                            ),
                        },
                    ),
                    'projects_preview': inline_serializer(
                        name='HomeProjectsPreview',
                        fields={
                            'title': serializers.CharField(),
                            'items': serializers.ListField(
                                child=inline_serializer(
                                    name='ProjectPreviewItem',
                                    fields={
                                        'id': serializers.CharField(),
                                        'title': serializers.CharField(),
                                        'description': serializers.CharField(),
                                        'project_type': serializers.CharField(),
                                        'tags': serializers.ListField(child=serializers.CharField()),
                                        'year': serializers.CharField(),
                                        'image': serializers.CharField(allow_null=True),
                                        'isFirst': serializers.BooleanField(),
                                        'action_button': inline_serializer(
                                            name='ProjectItemButton',
                                            fields={
                                                'label': serializers.CharField(),
                                                'link': serializers.CharField(),
                                            },
                                        ),
                                    },
                                )
                            ),
                            'action_button': inline_serializer(
                                name='ProjectsPreviewButton',
                                fields={
                                    'label': serializers.CharField(),
                                    'link': serializers.CharField(),
                                },
                            ),
                        },
                    ),
                },
            ),
            description=_('Успешный ответ'),
            examples=[
                OpenApiExample(
                    'Пример ответа Главной страницы',
                    value={
                        'hero': {
                            'title': 'Амбасада за урбанизам',
                            'subtitle': ('Исследуем, проектируем и меняем городскую среду Белграда'),
                            'image_left': 'https://cdn.example.com/hero1.webp',
                            'image_right': 'https://cdn.example.com/hero2.webp',
                            'action_button': {
                                'label': 'Смотреть проекты',
                                'link': '/projects',
                            },
                        },
                        'about_preview': {
                            'title': 'О сообществе',
                            'text': (
                                'Мы объединяем урбанистов, архитекторов и жителей для ' 'создания комфортного города.'
                            ),
                            'image': 'https://cdn.example.com/about.webp',
                            'action_button': {
                                'label': 'Узнать больше',
                                'link': '/about',
                            },
                        },
                        'team_preview': {
                            'title': 'Команда',
                            'members': [
                                {
                                    'name': 'Петр Петрович',
                                    'role': 'Архитектор',
                                    'photo': 'https://cdn.example.com/p1.jpg',
                                },
                                {
                                    'name': 'Николай Николаевич',
                                    'role': 'Дизайнер',
                                    'photo': None,
                                },
                            ],
                            'action_button': {
                                'label': 'Присоединиться к команде',
                                'link': '/contacts',
                            },
                        },
                        'projects_preview': {
                            'title': 'Наши проекты',
                            'items': [
                                {
                                    'id': 'zvezdarska-suma',
                                    'title': 'Звездарский лес',
                                    'description': ('Звездарский лес — одна из крупнейших зеленых зон...'),
                                    'project_type': 'Навигация',
                                    'tags': ['Урбанистика', 'Белград'],
                                    'year': '2023',
                                    'image': 'https://cdn.example.com/z1.webp',
                                    'isFirst': True,
                                    'action_button': {
                                        'label': 'Перейти к проекту',
                                        'link': '/projects/zvezdarska-suma',
                                    },
                                }
                            ],
                            'action_button': {
                                'label': 'Все проекты',
                                'link': '/projects',
                            },
                        },
                    },
                )
            ],
        )
    },
)
