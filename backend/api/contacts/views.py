from contacts.models import ContactPageContent
from django.utils import translation
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.contacts.serializers import (
    ContactPageContentSerializer,
    ContactRequestSerializer,
)
from api.schemas.contact_schemas import contact_view_schemas


@contact_view_schemas
class ContactView(APIView):
    """API для формы обратной связи и получения контактного блока."""

    permission_classes = [AllowAny]
    throttle_scope = 'contact'
    serializer_class = ContactRequestSerializer

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        """Создаёт запрос обратной связи со встроенной валидацией антиспама."""
        raw_lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        lang = raw_lang.lower()

        with translation.override(lang):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            # Если фронтенд ОЖИДАЕТ поля созданного объекта (id, name, email...), пишем:
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
            # Если фронтенд ОЖИДАЕТ строго только текст "Получено", оставляем так:
            # Подкорректируем под фронт позже, если потребуется
            return Response({'detail': _('Получено')}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Возвращает текст пожертвований."""
        raw_lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        lang = raw_lang.lower()

        with translation.override(lang):
            content = ContactPageContent.objects.filter(is_active=True).first()

            return Response(
                {
                    'donation_text': (ContactPageContentSerializer(content).data['donation_text'] if content else ''),
                }
            )
