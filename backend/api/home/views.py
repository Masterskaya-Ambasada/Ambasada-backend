import logging

from django.contrib.auth import get_user_model
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _
from home.constants import HOME_PAGE_SINGLETON_PK, HOME_PROJECTS_PREVIEW_LIMIT
from home.models import HomePageProject
from projects.models import Project
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.cache import get_full_config_cached

from api.schemas.home_shemas import HOME_VIEW_SCHEMA

from .serializers import HomePageRootSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


def get_home_preview_projects() -> list[Project]:
    """Возвращает проекты для главной страницы в порядке, заданном менеджером."""
    configured_projects = HomePageProject.objects.filter(home_page_id=HOME_PAGE_SINGLETON_PK)
    if configured_projects.exists():
        project_items = (
            configured_projects.filter(project__is_published=True)
            .select_related('project', 'project__project_type')
            .prefetch_related('project__tags')
            .order_by('order', 'pk')[:HOME_PROJECTS_PREVIEW_LIMIT]
        )
        return [item.project for item in project_items]

    return list(
        Project.objects.filter(is_published=True)
        .select_related('project_type')
        .prefetch_related('tags')
        .order_by('-year', '-id')[:HOME_PROJECTS_PREVIEW_LIMIT]
    )


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
            logger.warning(f'Данные конфигурации отсутствуют для языка {lang}')
            return Response(
                {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': _('Контент главной страницы не сконфигурирован.'),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        team_members = User.objects.public()[:6]
        logger.info(f'Получено {team_members.count() if team_members else 0} членов команды')

        projects = get_home_preview_projects()
        logger.info(f'Получено {len(projects)} опубликованных проектов')
        first_project_id = projects[0].id if projects else None

        page_data = {
            'config': config_data,
            'team_members': team_members,
            'projects': projects,
        }

        lang_suffix = lang.replace('-', '_')
        context = {'request': request, 'first_project_id': first_project_id, 'lang_suffix': lang_suffix}

        serializer = HomePageRootSerializer(page_data, context=context)

        return Response(serializer.data, status=status.HTTP_200_OK)
