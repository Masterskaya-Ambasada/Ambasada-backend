import logging

from django.utils.translation import get_language_from_request
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.cache import get_site_config_cached

from api.schemas.init_schemas import INIT_VIEW_SCHEMA

from .constants import ERROR_RESPONSE_NOT_FOUND

logger = logging.getLogger(__name__)


@INIT_VIEW_SCHEMA
class InitView(APIView):
    """API-представление для получения конфигурации сайта."""

    permission_classes = [AllowAny]

    def get(self, request):
        lang = request.query_params.get('lang') or get_language_from_request(request)

        data = get_site_config_cached(language=lang)

        if data is not None:
            return Response(data, status=status.HTTP_200_OK)
        logger.warning('Конфигурация сайта не найдена в кэше/БД.')
        return Response(ERROR_RESPONSE_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
