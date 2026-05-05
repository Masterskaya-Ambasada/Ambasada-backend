from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.models import SiteConfig

from api.schemas.init_schemas import INIT_VIEW_SCHEMA
from api.site_config.serializers import ErrorSerializer, SiteConfigSerializer

from .constants import CACHE_KEY_INIT, CACHE_TIMEOUT_NOT_FOUND, CACHE_TIMEOUT_SUCCESS


@INIT_VIEW_SCHEMA
class InitView(APIView):
    """API-представление для получения конфигурации сайта."""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Возвращает кэшированные или свежие настройки сайта."""
        cached = cache.get(CACHE_KEY_INIT)

        if cached == 'NOT_FOUND':
            error_data = {'status': 404, 'code': 'NOT_FOUND', 'message': _('Конфигурация сайта не найдена')}
            return Response(ErrorSerializer(error_data).data, status=status.HTTP_404_NOT_FOUND)

        if cached:
            return Response(cached)

        config = SiteConfig.objects.prefetch_related('languages', 'socials').first()

        if not config:
            cache.set(CACHE_KEY_INIT, 'NOT_FOUND', timeout=CACHE_TIMEOUT_NOT_FOUND)
            error_data = {'status': 404, 'code': 'NOT_FOUND', 'message': _('Конфигурация сайта не найдена')}
            return Response(ErrorSerializer(error_data).data, status=status.HTTP_404_NOT_FOUND)

        serializer = SiteConfigSerializer(config)
        data = serializer.data

        cache.set(CACHE_KEY_INIT, data, timeout=CACHE_TIMEOUT_SUCCESS)

        return Response(data, status=status.HTTP_200_OK)
