from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers

INIT_VIEW_SCHEMA = extend_schema(
    summary=_('Инициализация сайта'),
    description=_(
        'Возвращает глобальные настройки строго по интерфейсу InitResponse: '
        'название, SEO, языки, копирайт, юридические тексты и соцсети.'
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name='SiteConfigResponse',
                fields={
                    'site_name': serializers.CharField(),
                    'seo_description': serializers.CharField(),
                    'privacy_policy': serializers.CharField(),
                    'cookie_message': serializers.CharField(),
                    'cookie_button_text': serializers.CharField(),
                    'copyright': serializers.CharField(),
                    'team_title': serializers.CharField(),
                    'main_team_button_label': serializers.CharField(),
                    'about_team_button_label': serializers.CharField(),
                    'legal_links': serializers.DictField(
                        child=serializers.CharField(),
                        help_text=_('Дополнительные юридические ссылки (Record<string, string>)'),
                    ),
                    'languages': serializers.ListField(
                        child=serializers.DictField(), help_text=_('Список доступных языков')
                    ),
                    'socials': serializers.ListField(
                        child=inline_serializer(
                            name='SocialLink',
                            fields={
                                'social_type': serializers.CharField(),
                                'url': serializers.URLField(),
                            },
                        ),
                        help_text=_('Ссылки на социальные сети'),
                    ),
                },
            ),
            description=_('Успешный ответ'),
            examples=[
                OpenApiExample(
                    'Успешный ответ',
                    value={
                        'site_name': 'Ambasada',
                        'seo_description': 'Best site',
                        'privacy_policy': '<p>Политика конфиденциальности...</p>',
                        'cookie_message': '<p>Мы используем технические cookie...</p>',
                        'cookie_button_text': 'Принять',
                        'copyright': '© 2026 Ambasada za Urbanizam',
                        'team_title': 'Команда',
                        'main_team_button_label': 'Присоединиться к команде',
                        'about_team_button_label': 'Подробнее о сообществе',
                        'legal_links': {},
                        'languages': [
                            {'code': 'ru', 'label': 'Russian'},
                            {'code': 'en', 'label': 'English'},
                            {'code': 'sr-Latn', 'label': 'Serbian (Latin)'},
                            {'code': 'sr-Cyrl', 'label': 'Serbian (Cyrillic)'},
                        ],
                        'socials': [
                            {'social_type': 'Telegram', 'url': 'https://t.me/test'},
                            {'social_type': 'Instagram', 'url': 'https://inst.com/test'},
                        ],
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            response=inline_serializer(
                name='ConfigErrorResponse',
                fields={
                    'status': serializers.IntegerField(),
                    'code': serializers.CharField(),
                    'message': serializers.CharField(),
                },
            ),
            description=_('Конфигурация сайта не найдена'),
            examples=[
                OpenApiExample(
                    'Ошибка',
                    value={
                        'status': 404,
                        'code': 'NOT_FOUND',
                        'message': 'Конфигурация сайта не найдена',
                    },
                )
            ],
        ),
    },
)
