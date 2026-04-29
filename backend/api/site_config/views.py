from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.models import SiteConfig

from .serializers import ErrorSerializer, SiteConfigSerializer


@extend_schema(
    summary=_('Инициализация сайта'),
    description=_('Возвращает глобальные настройки: название, SEO, языки и соцсети.'),
    responses={
        200: OpenApiResponse(
            response=SiteConfigSerializer,
            description='Успешный ответ',
            examples=[
                OpenApiExample(
                    'Успешный ответ',
                    value={
                        'site_name': 'My Site',
                        'seo_description': 'Best site',
                        'languages': [
                            {'code': 'en', 'label': 'English'},
                            {'code': 'ru', 'label': 'Русский'},
                        ],
                        'socials': [
                            {'social_type': 'Telegram', 'url': 'https://t.me/test'},
                            {'social_type': 'Facebook', 'url': 'https://fb.com/test'},
                        ],
                        'copyright': '© 2026',
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorSerializer,
            description='Конфигурация сайта не найдена',
            examples=[
                OpenApiExample(
                    'Ошибка',
                    value={
                        'status': 404,
                        'code': 'NOT_FOUND',
                        'message': 'Site config not found',
                    },
                )
            ],
        ),
    },
)
class InitView(APIView):
    """
    Возвращает константы сайта.

    Содержит:
    - название сайта
    - SEO-описание
    - список языков
    - ссылки на соцсети
    - копирайт
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cached = cache.get('site_config_init')

        if cached == 'NOT_FOUND':
            return Response(
                {'status': 404, 'code': 'NOT_FOUND', 'message': 'Site config not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if cached:
            return Response(cached)

        config = SiteConfig.objects.prefetch_related('languages', 'socials').first()

        if not config:
            cache.set('site_config_init', 'NOT_FOUND', timeout=300)
            return Response(
                {'status': 404, 'code': 'NOT_FOUND', 'message': 'Site config not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SiteConfigSerializer(config)
        data = serializer.data

        cache.set('site_config_init', data, timeout=3600)

        return Response(data, status=status.HTTP_200_OK)
