"""APIView для получения данных страницы 'О нас'."""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AboutPage, GalleryImage, TeamMember, Value
from .serializers import AboutPageSerializer


class AboutAPIView(APIView):
    """Возвращает структуру страницы 'О сообществе' согласно ТЗ."""

    permission_classes = [AllowAny]

    def get(self, request):
        about = AboutPage.objects.first()
        if not about:
            return Response({'detail': 'About page not found.'}, status=404)

        values = Value.objects.all()
        members = TeamMember.objects.all()
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
