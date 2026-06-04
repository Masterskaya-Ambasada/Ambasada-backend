from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers

# Импортируем твой готовый сериализатор данных пользователя
from api.users.serializers import UserLoginResponseSerializer

AUTH_TOKEN_SCHEMA = extend_schema_view(
    post=extend_schema(
        summary=_('Вход в систему (JWT + User info)'),
        description=_('Принимает email и пароль, возвращает access/refresh токены и данные пользователя.'),
        responses={
            200: inline_serializer(
                name='TokenResponse',
                fields={
                    'refresh': serializers.CharField(),
                    'access': serializers.CharField(),
                    'user': UserLoginResponseSerializer(),
                },
            )
        },
    )
)


TOKEN_REFRESH_SCHEMA = extend_schema_view(
    post=extend_schema(
        summary=_('Обновление access токена'),
        description=_('Принимает валидный refresh токен и возвращает новый access токен.'),
        request=inline_serializer(name='TokenRefreshRequest', fields={'refresh': serializers.CharField()}),
        responses={200: inline_serializer(name='TokenRefreshResponse', fields={'access': serializers.CharField()})},
    )
)
