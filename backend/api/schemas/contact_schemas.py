from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers

from api.contacts.serializers import ContactRequestSerializer

contact_view_schemas = extend_schema_view(
    post=extend_schema(
        summary=_('Создание запроса обратной связи'),
        description=_(
            'Принимает данные формы и сохраняет их. '
            'Поле `contact_preference` — техническое антиспам-поле (honeypot). '
            'Если поле заполнено, запрос считается спамом и игнорируется.'
        ),
        request=ContactRequestSerializer,
        responses={
            201: inline_serializer(
                name='ContactCreateResponse',
                fields={'detail': serializers.CharField()},
            ),
            400: OpenApiResponse(description=_('Ошибка валидации формы')),
        },
    ),
    get=extend_schema(
        summary=_('Получение контента блока контактов'),
        description=_('Возвращает данные для страницы "Связаться с нами" и активный текстовый блок.'),
        responses={
            200: inline_serializer(
                name='ContactGetResponse',
                fields={
                    'phone': serializers.CharField(),
                    'address': serializers.CharField(),
                    'donation_text': serializers.CharField(),
                },
            ),
        },
    ),
)
