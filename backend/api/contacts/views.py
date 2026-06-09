import logging

from contacts.models import ContactPageContent
from django.utils import translation
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.contacts.serializers import ContactPageContentSerializer, ContactRequestSerializer
from api.schemas.contact_schemas import contact_view_schemas

logger = logging.getLogger(__name__)


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
        try:
            lang = request.query_params.get('lang') or get_language_from_request(request)
            with translation.override(lang):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                logger.info('Пользователь успешно отправил запрос обратной связи.')

                return Response({'detail': _('Получено')}, status=status.HTTP_201_CREATED)
        except Exception as exc:
            error_messages = []
            for errors in exc.detail.values():
                for error in errors:
                    error_messages.append(str(error))
            error_text = ', '.join(error_messages)
            logger.error(f'Ошибка: {exc.__class__.__name__} ({error_text})')
            raise

    def get(self, request, *args, **kwargs):
        """Возвращает текст пожертвований."""
        lang = request.query_params.get('lang') or get_language_from_request(request)

        with translation.override(lang):
            content = ContactPageContent.objects.filter(is_active=True).first()
            if not content:
                logger.warning('Объект ContactPageContent не найден.')
                return Response({'donation_text': ''})

            return Response(
                {
                    'donation_text': (ContactPageContentSerializer(content).data['donation_text']),
                }
            )
