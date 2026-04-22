from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.models import SiteConfig
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema
from django.utils.translation import gettext_lazy as _

from .serializers import SiteConfigSerializer


@extend_schema(
    summary=_('Инициализация сайта'),
    description=_('Возвращает глобальные настройки: название, SEO, языки и соцсети.'),
    responses={200: SiteConfigSerializer},
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
