from django.contrib.auth import get_user_model
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.cache import get_full_config_cached

from api.schemas.home_shemas import HOME_VIEW_SCHEMA

from .serializers import HomePageRootSerializer

User = get_user_model()


@HOME_VIEW_SCHEMA
class HomeAPIView(APIView):
    """Эндпоинт для генерации структуры главной страницы сообщества."""

    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        raw_lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        lang = raw_lang.lower()

        config_data = get_full_config_cached(language=lang)

        if not config_data:
            return Response(
                {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': _('Контент главной страницы не сконфигурирован.'),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        team_members = User.objects.public()[:6]

        projects = (
            Project.objects.filter(is_published=True)
            .select_related('project_type')
            .prefetch_related('tags')
            .order_by('-year', '-id')[:4]
        )

        first_project_id = projects[0].id if projects.exists() else None

        page_data = {
            'config': config_data,
            'team_members': team_members,
            'projects': projects,
        }

        lang_suffix = lang.replace('-', '_')
        context = {'request': request, 'first_project_id': first_project_id, 'lang_suffix': lang_suffix}

        serializer = HomePageRootSerializer(page_data, context=context)

        return Response(serializer.data, status=status.HTTP_200_OK)
