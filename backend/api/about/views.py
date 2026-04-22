"""APIView для получения данных страницы 'О нас'."""

from about.models import AboutPage, GalleryImage, Value
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User

from .serializers import AboutPageSerializer


class AboutAPIView(APIView):
    """Возвращает структуру страницы 'О сообществе' согласно ТЗ."""

    permission_classes = [AllowAny]

    def get(self, request):
        about = AboutPage.objects.first()
        if not about:
            return Response({'detail': _('Страница "О нас" не найдена.')}, status=404)

        values = Value.objects.all()
        members = User.objects.public()
        images = GalleryImage.objects.all()

        serializer = AboutPageSerializer(
            about,
            context={
                'values': values,
                'members': members,
                'images': images,
            },
        )
        return Response(serializer.data)
