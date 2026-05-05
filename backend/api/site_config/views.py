from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.models import SiteConfig

from api.schemas.init_schemas import INIT_VIEW_SCHEMA
from api.site_config.serializers import ErrorSerializer, SiteConfigSerializer

from .constants import (
    CACHE_KEY_INIT,
    CACHE_TIMEOUT_NOT_FOUND,
    CACHE_TIMEOUT_SUCCESS,
    CACHE_VALUE_NOT_FOUND,
    ERROR_CODE_NOT_FOUND,
    ERROR_MESSAGE_NOT_FOUND,
)


@INIT_VIEW_SCHEMA
class InitView(APIView):
    """API-представление для получения конфигурации сайта."""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cached = cache.get(CACHE_KEY_INIT)

        if cached == CACHE_VALUE_NOT_FOUND:
            return self._not_found_response()

        if cached is not None:
            return Response(cached, status=status.HTTP_200_OK)

        config = SiteConfig.objects.prefetch_related('languages', 'socials').first()

        if not config:
            cache.set(CACHE_KEY_INIT, CACHE_VALUE_NOT_FOUND, timeout=CACHE_TIMEOUT_NOT_FOUND)
            return self._not_found_response()

        serializer = SiteConfigSerializer(config)
        data = serializer.data

        cache.set(CACHE_KEY_INIT, data, timeout=CACHE_TIMEOUT_SUCCESS)
        return Response(data, status=status.HTTP_200_OK)

    def _not_found_response(self):
        """Вспомогательный метод для единообразного ответа 404."""
        error_data = {
            'status': status.HTTP_404_NOT_FOUND,
            'code': ERROR_CODE_NOT_FOUND,
            'message': ERROR_MESSAGE_NOT_FOUND,
        }
        return Response(ErrorSerializer(error_data).data, status=status.HTTP_404_NOT_FOUND)
