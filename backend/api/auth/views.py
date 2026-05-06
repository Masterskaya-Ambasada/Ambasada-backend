from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from api.schemas.auth_schemas import AUTH_TOKEN_SCHEMA

from .serializers import AmbasadaTokenObtainPairSerializer

User = get_user_model()


@AUTH_TOKEN_SCHEMA
class AmbasadaTokenObtainPairView(TokenObtainPairView):
    """Представление для получения JWT-токенов с расширенными данными пользователя."""

    serializer_class = AmbasadaTokenObtainPairSerializer
