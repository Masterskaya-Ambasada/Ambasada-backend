from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

from api.security.serializers import SecurityPolicySerializer

security_view_schemas = extend_schema_view(
    get=extend_schema(
        summary=_('Получение текста политики конфиденциальности'),
        description=_(
            'Возвращает локализованный текст политики конфиденциальности в формате HTML. '
            'Локализация зависит от переданного заголовка `Accept-Language`.'
        ),
        responses={
            200: SecurityPolicySerializer,
            404: OpenApiResponse(description=_('Политика конфиденциальности не найдена')),
        },
    ),
)
