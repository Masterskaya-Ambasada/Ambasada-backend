from django.contrib.auth import get_user_model
from django.utils import translation
from django.utils.translation import get_language_from_request
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

    def initial(self, request, *args, **kwargs):
        """Переключает локаль для всего цикла запроса-ответа DRF (включая рендеринг JSON)."""
        raw_lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        lang = raw_lang.lower()
        translation.activate(lang)

        super().initial(request, *args, **kwargs)
