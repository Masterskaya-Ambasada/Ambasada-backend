from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view

from api.users.serializers import TeamMemberSerializer

TEAM_LIST_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary=_('Список участников команды'),
        description=_('Возвращает список публичных профилей пользователей для отображения на фронтенде.'),
        responses={200: TeamMemberSerializer(many=True)},
    )
)
