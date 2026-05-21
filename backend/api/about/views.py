"""APIView для получения данных страницы 'О нас'."""

from about.models import AboutPage, GalleryImage, Value
from api.schemas.about_schemas import ABOUT_SCHEMA
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AboutPageSerializer

User = get_user_model()


@ABOUT_SCHEMA
class AboutAPIView(APIView):
    """Возвращает структуру страницы 'О сообществе' согласно ТЗ."""

    permission_classes = [AllowAny]

    def get(self, request):
        about = AboutPage.objects.prefetch_related(
            'paragraphs',
        ).first()

        if not about:
            return Response(
                {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': _('Информация о сообществе не найдена'),
                },
                status=404,
            )

        values = Value.objects.all()
        images = GalleryImage.objects.all()
        members = User.objects.public()

        serializer = AboutPageSerializer(
            about,
            context={
                'request': request,
                'values': values,
                'images': images,
                'members': members,
            },
        )
        return Response(serializer.data)
