from rest_framework import status  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.views import APIView  # type: ignore

from .models import SiteConfig
from .serializers import SiteConfigSerializer


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

    def get(self, request):
        config = SiteConfig.objects.prefetch_related('languages', 'socials').first()

        if not config:
            return Response(
                {'status': 404, 'code': 'NOT_FOUND', 'message': 'Site config not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SiteConfigSerializer(config)
        return Response(serializer.data)
