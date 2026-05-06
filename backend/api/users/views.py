from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from api.schemas.users_schemas import TEAM_LIST_SCHEMA

from .serializers import TeamMemberSerializer

User = get_user_model()


@TEAM_LIST_SCHEMA
class TeamListView(ListAPIView):
    """Список участников команды для фронтенда."""

    queryset = User.objects.public().order_by('id')
    serializer_class = TeamMemberSerializer
    permission_classes = [AllowAny]
