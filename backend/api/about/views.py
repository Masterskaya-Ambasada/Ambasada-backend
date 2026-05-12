"""APIView для получения данных страницы 'О нас'."""

from about.models import AboutPage, GalleryImage, Value
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AboutPageSerializer


class AboutNotFoundSerializer(serializers.Serializer):
    """Простой контракт для 404 (Swagger schema helper)."""

    detail = serializers.CharField()


@extend_schema(
    summary=_('Получение страницы "О сообществе"'),
    description=_('Возвращает данные страницы "О нас" со всеми секциями'),
    responses={
        200: AboutPageSerializer,
        404: AboutNotFoundSerializer,
    },
)
class AboutAPIView(APIView):
    """Возвращает структуру страницы 'О сообществе' согласно ТЗ."""

    permission_classes = [AllowAny]

    def get(self, request):
        about = AboutPage.objects.prefetch_related(
            'paragraphs',
            'team_members',
        ).first()
        if not about:
            return Response({'detail': _('Страница "О нас" не найдена.')}, status=404)

        values = Value.objects.all()
        members = about.team_members.all() # User.objects.get_public_team()
        images = GalleryImage.objects.all()

        serializer = AboutPageSerializer(
            about,
            context={
                'request': request,
                'values': values,
                'members': members,
                'images': images,
            },
        )
        return Response(serializer.data)
