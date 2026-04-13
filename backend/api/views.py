"""APIView для получения данных страницы 'О нас'."""

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import AboutPage
from .serializers import AboutPageSerializer


class AboutAPIView(APIView):
    """Возвращает структуру страницы 'О сообществе' согласно ТЗ."""

    permission_classes = [AllowAny]

    def get(self, request):
        about = AboutPage.objects.first()
        if not about:
            return Response({"detail": "About page not found."}, status=404)
        serializer = AboutPageSerializer(about).data
        return Response(serializer.data)