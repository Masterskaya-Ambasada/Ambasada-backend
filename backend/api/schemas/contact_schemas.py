from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers

contact_view_schemas = extend_schema_view(
    post=extend_schema(
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
    ),
    get=extend_schema(
        summary=_('Получение контента блока контактов'),
        description=_('Возвращает активный текстовый блок для пожертвований.'),
        responses={
            200: inline_serializer(
                name='ContactGetResponse',
                fields={
                    'donation_text': serializers.CharField(),
                },
            ),
        },
    ),
)
