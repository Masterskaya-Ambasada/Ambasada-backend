from rest_framework.response import Response  # type: ignore
from rest_framework.views import APIView  # type: ignore

from .models import SiteConfig
from .serializers import SiteConfigSerializer


class InitView(APIView):
    def get(self, request):
        config = SiteConfig.objects.first()

        if not config:
            return Response({'detail': 'Config not found'}, status=404)

        serializer = SiteConfigSerializer(config)
        return Response(serializer.data)
