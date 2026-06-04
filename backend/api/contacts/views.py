from contacts.models import ContactPageContent
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.contacts.serializers import (
    ContactPageContentSerializer,
    ContactRequestSerializer,
)
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from api.schemas.contact_schemas import contact_view_schemas
import logging


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
        try:
            serializer.save()
            logger.info("Запрос обратной связи успешно сохранён")
        except ValidationError as exc:
            logger.error(f"Ошибка валидации при сохранении запроса: {exc}", exc_info=True)
            raise
        except DatabaseError as exc:
            logger.error(f"Ошибка базы данных при сохранении запроса: {exc}", exc_info=True)
            raise
        except Exception as exc:
            logger.error(f"Непредвиденная ошибка при сохранении запроса: {exc}", exc_info=True)
            raise

    def post(self, request, *args, **kwargs):
        """Создаёт запрос обратной связи со встроенной валидацией антиспама."""       
        try:
            if not request.data.get('contact_preference'):
                logger.debug("Валидация данных запроса обратной связи")
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                logger.info("Обращение успешно создано")
            else:
                logger.warning("Запрос содержит поле contact_preference, возможно, это бот")
            return Response({'detail': _('Получено')}, status=status.HTTP_201_CREATED)

        except ValidationError as exc:
            logger.error(f"Ошибка валидации в POST запросе: {exc}", exc_info=True)
            return Response(
                {'detail': _('Ошибка валидации данных'), 'errors': exc.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as exc:
            logger.error(f"Ошибка базы данных в POST запросе: {exc}", exc_info=True)
            return Response(
                {'detail': _('Ошибка сервера базы данных. Попробуйте позже.')},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as exc:
            logger.error(f"Непредвиденная ошибка в POST запросе: {exc}", exc_info=True)
            return Response(
                {'detail': _('Внутренняя ошибка сервера. Администратор уже уведомлён.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, *args, **kwargs):
        """Возвращает текст пожертвований."""
        try:
            logger.debug("Поиск активного контента контактной страницы")
            content = ContactPageContent.objects.filter(is_active=True).first()
            if content:
                logger.debug(f"Найден контент с ID: {content.id}")
                donation_text = ContactPageContentSerializer(content).data.get('donation_text', '')
            else:
                logger.warning("Активный контент контактной страницы не найден")
                donation_text = ''
            logger.info("Контактная информация успешно возвращена")
            return Response({
                'donation_text': donation_text,
            })

        except DatabaseError as exc:
            logger.error(f"Ошибка базы данных при получении контента: {exc}", exc_info=True)
            return Response(
                {'detail': _('Ошибка сервера базы данных. Попробуйте позже.')},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as exc:
            logger.error(f"Непредвиденная ошибка в GET запросе: {exc}", exc_info=True)
            return Response(
                {'detail': _('Внутренняя ошибка сервера')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
