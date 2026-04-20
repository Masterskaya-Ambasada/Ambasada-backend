from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import AmbasadaTokenObtainPairSerializer, TeamMemberSerializer

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary='Вход в систему (JWT + User info)',
        description='Принимает email и пароль, возвращает пару токенов и краткую информацию о пользователе',
        responses={200: AmbasadaTokenObtainPairSerializer},
    )
)
class AmbasadaTokenObtainPairView(TokenObtainPairView):
    serializer_class = AmbasadaTokenObtainPairSerializer


class TeamListView(ListAPIView):
    """Список участников команды для фронтенда."""

    queryset = User.objects.public().order_by('id')
    serializer_class = TeamMemberSerializer
    permission_classes = [AllowAny]
