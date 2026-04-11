from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SiteConfig
from .serializers import SiteConfigSerializer


class InitView(APIView):
    def get(self, request):
        config = SiteConfig.objects.first()

        if not config:
            return Response({"detail": "Config not found"}, status=404)

        serializer = SiteConfigSerializer(config)
        return Response(serializer.data)
