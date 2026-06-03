from about.models import AboutPage
from api.schemas.about_schemas import about_page_schema_decorator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AboutPageSerializer

User = get_user_model()


@about_page_schema_decorator
class AboutAPIView(APIView):
    """Возвращает структуру страницы 'О сообществе' согласно ТЗ."""

    permission_classes = [AllowAny]

    def get(self, request):
        # Делаем один чистый запрос со всеми связями
        about = AboutPage.objects.prefetch_related('paragraphs', 'values', 'gallery_images').first()

        if not about:
            return Response(
                {
                    'status': status.HTTP_404_NOT_FOUND,
                    'code': 'NOT_FOUND',
                    'message': _('Информация о сообществе не найдена'),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        members = User.objects.public()
        serializer = AboutPageSerializer(
            about,
            context={
                'request': request,
                'members': members,
            },
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
