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
                            'title': 'Ambasada za urbanizam',
                            'subtitle': 'Istražujemo, projektujemo i menjamo urbanu sredinu',
                            'image_left': 'https://cdn.example.com/hero1.webp',
                            'image_right': 'https://cdn.example.com/hero2.webp',
                            'action_button': {'label': 'Saznajte više', 'link': '/projects'},
                        },
                        'about_preview': {
                            'title': 'O zajednici',
                            'text': 'Mi smo udruženje arhitekata i urbanista...',
                            'action_button': {'label': 'Saznajte više', 'link': '/about'},
                        },
                        'team_preview': {
                            'title': 'Tim',
                            'members': [
                                {
                                    'name': 'Petar Petrović',
                                    'role': 'Arhitekta',
                                    'photo': 'https://cdn.example.com/p1.jpg',
                                },
                                {'name': 'Nikola Nikolić', 'role': 'Dizajner', 'photo': None},
                            ],
                            'action_button': {'label': 'Pridruži se timu', 'link': '/contacts'},
                        },
                        'projects_preview': {
                            'title': 'Projekti',
                            'items': [
                                {
                                    'id': 'zvezdarska-suma',
                                    'title': 'Zvezdarska šuma',
                                    'description': 'Zvezdarska šuma je jedna od najvećih zelenih zona...',
                                    'project_type': 'Navigacija',
                                    'tags': ['Urbanizam', 'Beograd'],
                                    'year': '2023',
                                    'image': 'https://cdn.example.com/z1.webp',
                                    'isFirst': True,
                                    'action_button': {
                                        'label': 'Pregledaj projekat',
                                        'link': '/projects/zvezdarska-suma',
                                    },
                                }
                            ],
                            'action_button': {'label': 'Svi projekti', 'link': '/projects'},
                        },
                    },
                )
            ],
        )
    },
)
