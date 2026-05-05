from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema

from api.site_config.serializers import ErrorSerializer, SiteConfigSerializer

INIT_VIEW_SCHEMA = extend_schema(
    summary=_('Инициализация сайта'),
    description=_('Возвращает глобальные настройки: название, SEO, языки и соцсети.'),
    responses={
        200: OpenApiResponse(
            response=SiteConfigSerializer,
            description=_('Успешный ответ'),
            examples=[
                OpenApiExample(
                    'Успешный ответ',
                    value={
                        'site_name': 'My Site',
                        'seo_description': 'Best site',
                        'languages': [
                            {'code': 'ru', 'label': 'Russian'},
                            {'code': 'sr-latn', 'label': 'Serbian (Latin)'},
                        ],
                        'socials': [
                            {'social_type': 'Telegram', 'url': 'https://t.me/test'},
                            {'social_type': 'Instagram', 'url': 'https://inst.com/test'},
                        ],
                        'copyright': '© 2026',
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorSerializer,
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
