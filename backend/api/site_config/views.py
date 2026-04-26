from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.models import SiteConfig

from .serializers import SiteConfigSerializer, ErrorSerializer


@extend_schema(
    summary=_('Инициализация сайта'),
    description=_('Возвращает глобальные настройки: название, SEO, языки и соцсети.'),
    responses={
        200: SiteConfigSerializer,
        404: OpenApiResponse(
            response=ErrorSerializer,
            description="Конфигурация сайта не найдена"
        ),
    },
    examples=[
        OpenApiExample(
            'Успешный ответ',
            value={
                "site_name": "My Site",
                "seo_description": "Best site",
                "languages": [
                    {"code": "en", "label": "English"}
                ],
                "socials": [
                    {"social_type": "Telegram", "url": "https://t.me/test"}
                ],
                "copyright": "© 2026"
            },
            response_only=True
        )
    ]
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
        config = SiteConfig.objects.prefetch_related('languages', 'socials').first()

        if not config:
            return Response(
                {'status': 404, 'code': 'NOT_FOUND', 'message': 'Site config not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SiteConfigSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)
