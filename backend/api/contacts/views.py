from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.contacts.serializers import ContactRequestSerializer


@extend_schema(
    summary=_('Создание запроса обратной связи'),
    description=_(
        'Принимает данные формы и сохраняет их.'
        'Поле `contact_preference` — техническое антиспам-поле (honeypot). '
        'Фронтенд должен передавать его пустым. '
        'Если поле заполнено, запрос считается спамом и игнорируется.'
    ),
    responses={
        201: inline_serializer(
            name='ContactCreateResponse',
            fields={
                'detail': serializers.CharField(),
            },
        ),
    },
)
class ContactCreateView(generics.CreateAPIView):
    """Представление для создания запроса обратной связи со встроенным антиспамом."""

    serializer_class = ContactRequestSerializer
    permission_classes = [AllowAny]
    throttle_scope = 'contact'

    def create(self, request, *args, **kwargs):
        if not request.data.get('contact_preference'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        return Response({'detail': _('Получено')}, status=status.HTTP_201_CREATED)
