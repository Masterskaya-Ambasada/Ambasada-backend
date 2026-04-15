from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import AmbasadaTokenObtainPairSerializer

User = get_user_model()


class AmbasadaTokenObtainPairView(TokenObtainPairView):
    """Представление для получения токена с расширенными данными профиля."""
    serializer_class = AmbasadaTokenObtainPairSerializer
