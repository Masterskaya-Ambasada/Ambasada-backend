import logging
from django.contrib.auth import get_user_model
from django.utils.translation import get_language
from projects.models import Project
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from site_config.cache import get_full_config_cached

from api.schemas.home_shemas import HOME_VIEW_SCHEMA

from .serializers import HomePageRootSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


@HOME_VIEW_SCHEMA
class HomeAPIView(APIView):
    """Эндпоинт для генерации структуры главной страницы сообщества."""

    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        logger.info(f'Получен запрос к HomeAPIView от {request.META.get("REMOTE_ADDR", "unknown")}')
        lang = request.query_params.get('lang') or get_language()
        try:
            config_data = get_full_config_cached(language=lang)
            logger.info(f'!!! Конфигурации из кэша: {config_data}')
        except Exception:
            logger.error(f'Не удалось получить конфигурацию из кеша для языка {lang}', exc_info=True)
            raise
        if not config_data:
            logger.warning(f'Данные конфигурации отсутствуют для языка {lang}')
            return Response(
                {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': 'Контент главной страницы не сконфигурирован.',
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            team_members = User.objects.public()[:6]
            logger.info(f'Получено {team_members.count() if team_members else 0} членов команды')
        except Exception:
            logger.error('Ошибка получения членов команды из базы данных', exc_info=True)
            raise
        try:
            projects = (
                Project.objects.filter(is_published=True)
                .select_related('project_type')
                .prefetch_related('tags')
                .order_by('-year', '-id')[:4]
            )
            logger.info(f'Получено {projects.count() if projects else 0} опубликованных проектов')
        except Exception:
            logger.error('Ошибка получения проектов из базы данных', exc_info=True)
            raise

        first_project_id = projects[0].id if projects.exists() else None

        page_data = {
            'config': config_data,
            'team_members': team_members,
            'projects': projects,
        }

        context = {'request': request, 'first_project_id': first_project_id}
        try:
            serializer = HomePageRootSerializer(page_data, context=context)
        except Exception:
            logger.error('Ошибка сериализации данных для главной страницы', exc_info=True)
            raise
        return Response(serializer.data, status=status.HTTP_200_OK)
