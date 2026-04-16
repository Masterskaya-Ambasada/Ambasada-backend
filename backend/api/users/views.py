from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import AmbasadaTokenObtainPairSerializer, TeamMemberSerializer

User = get_user_model()


class AmbasadaTokenObtainPairView(TokenObtainPairView):
    """Вьюха для входа (login)."""

    serializer_class = AmbasadaTokenObtainPairSerializer


class TeamListView(ListAPIView):
    """Список участников команды для фронтенда."""

    queryset = User.objects.public().order_by('id')
    serializer_class = TeamMemberSerializer
    permission_classes = [AllowAny]
