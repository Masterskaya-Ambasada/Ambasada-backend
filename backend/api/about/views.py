"""APIView для получения данных страницы 'О нас'."""

from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from about.models import AboutPage, GalleryImage, Value

from .serializers import AboutPageSerializer


@extend_schema(
    summary=_('Получение страницы "О сообществе"'),
    description=_('Возвращает данные страницы "О нас" со всеми секциями'),
    responses=inline_serializer(
        name='AboutResponse',
        fields={
            'hero': serializers.DictField(),
            'about_section': serializers.DictField(),
            'values': serializers.DictField(),
            'team': serializers.DictField(),
            'gallery_carousel': serializers.DictField(),
        },
    ),
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
        members = about.team_members.all()
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
