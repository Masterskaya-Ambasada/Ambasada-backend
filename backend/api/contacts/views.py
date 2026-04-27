from contacts.models import ContactPageContent, ContactSocialLink
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.contacts.serializers import (
    ContactPageContentSerializer,
    ContactRequestSerializer,
    ContactSocialLinkSerializer,
)


class ContactView(APIView):
    '''API для формы обратной связи и получения контактного блока.'''

    permission_classes = [AllowAny]
    throttle_scope = 'contact'
    serializer_class = ContactRequestSerializer

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(
        summary=_('Создание запроса обратной связи'),
        description=_(
            'Принимает данные формы и сохраняет их. '
            'Поле `contact_preference` — техническое антиспам-поле (honeypot). '
            'Если поле заполнено, запрос считается спамом и игнорируется.'
        ),
        responses={
            201: inline_serializer(
                name='ContactCreateResponse',
                fields={'detail': serializers.CharField()},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        '''Создаёт запрос обратной связи.'''
        if not request.data.get('contact_preference'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        return Response({'detail': _('Получено')}, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary=_('Получение контента блока контактов'),
        description=_(
            'Возвращает текстовый блок для пожертвований и список ' 'активных ссылок на соцсети и мессенджеры.'
        ),
        responses={200: None},
    )
    def get(self, request, *args, **kwargs):
        '''Возвращает текст пожертвований и список активных соцсетей.'''
        content = ContactPageContent.objects.filter(is_active=True).first()
        links = ContactSocialLink.objects.filter(is_active=True)

        return Response(
            {
                'donation_text': (ContactPageContentSerializer(content).data['donation_text'] if content else ''),
                'social_links': ContactSocialLinkSerializer(links, many=True).data,
            }
        )
