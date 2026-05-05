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
        cached = cache.get(CACHE_KEY_INIT)

        # 1. Проверяем кэшированный 404
        if cached == 'NOT_FOUND':
            return self._not_found_response()

        # 2. Проверяем успешный кэш
        if cached is not None:
            return Response(cached, status=status.HTTP_200_OK)

        # 3. Идем в базу, если в кэше пусто
        config = SiteConfig.objects.prefetch_related('languages', 'socials').first()

        if not config:
            cache.set(CACHE_KEY_INIT, 'NOT_FOUND', timeout=CACHE_TIMEOUT_NOT_FOUND)
            return self._not_found_response()

        serializer = SiteConfigSerializer(config)
        data = serializer.data

        cache.set(CACHE_KEY_INIT, data, timeout=CACHE_TIMEOUT_SUCCESS)
        return Response(data, status=status.HTTP_200_OK)

    def _not_found_response(self):
        """Вспомогательный метод для единообразного ответа 404."""
        error_data = {'status': 404, 'code': 'NOT_FOUND', 'message': _('Конфигурация сайта не найдена')}
        return Response(ErrorSerializer(error_data).data, status=status.HTTP_404_NOT_FOUND)
