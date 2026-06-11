from django.utils.translation import get_language_from_request
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from security.models import SecurityPolicy

from api.schemas.security_schemas import security_view_schemas

from .serializers import SecurityPolicySerializer


@security_view_schemas
class SecurityPolicyView(APIView):
    """Эндпоинт для получения политики конфиденциальности."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        lang = lang.lower()

        lang_suffix = lang.replace('-', '_')

        instance = SecurityPolicy.load()

        context = {'request': request, 'lang_suffix': lang_suffix}

        serializer = SecurityPolicySerializer(instance, context=context)
        return Response(serializer.data)
