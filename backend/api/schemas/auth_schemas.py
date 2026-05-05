from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers

from api.users.serializers import AmbasadaTokenObtainPairSerializer

AUTH_TOKEN_SCHEMA = extend_schema_view(
    post=extend_schema(
        summary='Вход в систему (JWT + User info)',
        description='Принимает email и пароль, возвращает access/refresh токены и данные пользователя.',
        responses={
            200: inline_serializer(
                name='TokenResponse',
                fields={
                    'refresh': serializers.CharField(),
                    'access': serializers.CharField(),
                    'user': AmbasadaTokenObtainPairSerializer(),
                },
            )
        },
    )
)


TOKEN_REFRESH_SCHEMA = extend_schema_view(
    post=extend_schema(
        summary='Обновление access токена',
        description='Принимает валидный refresh токен и возвращает новый access токен.',
        request=inline_serializer(name='TokenRefreshRequest', fields={'refresh': serializers.CharField()}),
        responses={200: inline_serializer(name='TokenRefreshResponse', fields={'access': serializers.CharField()})},
    )
)
