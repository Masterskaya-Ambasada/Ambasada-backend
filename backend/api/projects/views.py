from __future__ import annotations

from django.db.models import Prefetch, Q
from django.utils import translation
from django.utils.translation import get_language_from_request
from projects.models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectGalleryImage,
    ProjectType,
    Tag,
)
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.projects.constants import (
    PATH_PARAM_PROJECT_SLUG,
    PROJECT_TYPES_RESPONSE_KEY,
    QUERY_PARAM_PROJECT_TYPE,
    QUERY_PARAM_SEARCH,
    QUERY_PARAM_TAG,
    TAG_QUERY_VALUE_SEPARATOR,
)
from api.projects.pagination import ProjectLimitOffsetPagination
from api.projects.serializers import (
    ProjectCardSerializer,
    ProjectDetailSerializer,
    ProjectTypeSerializer,
)
from api.schemas.project_schemas import (
    PROJECT_DETAIL_SCHEMA,
    PROJECT_LIST_SCHEMA,
    PROJECT_TAGS_SCHEMA,
    PROJECT_TYPES_SCHEMA,
)


@PROJECT_LIST_SCHEMA
class ProjectListView(ListAPIView):
    """Возвращает список опубликованных проектов с фильтрацией и пагинацией."""

    permission_classes = (AllowAny,)
    serializer_class = ProjectCardSerializer
    pagination_class = ProjectLimitOffsetPagination

    def initial(self, request, *args, **kwargs):
        """Переключает локаль для всего цикла запроса-ответа DRF."""
        lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        translation.activate(lang.lower())
        super().initial(request, *args, **kwargs)

    def _normalize_tag_filters(self) -> list[str]:
        tags: list[str] = []
        for raw_tag in self.request.query_params.getlist(QUERY_PARAM_TAG):
            for tag in raw_tag.split(TAG_QUERY_VALUE_SEPARATOR):
                normalized_tag = tag.strip()
                if normalized_tag:
                    tags.append(normalized_tag)
        return tags

    def get_queryset(self):
        tag_queryset = Tag.objects.order_by('label', 'pk')
        queryset = (
            Project.objects.filter(is_published=True)
            .select_related('project_type')
            .prefetch_related(Prefetch('tags', queryset=tag_queryset))
        )

        project_type = (self.request.query_params.get(QUERY_PARAM_PROJECT_TYPE) or '').strip()
        if project_type:
            queryset = queryset.filter(Q(project_type__slug=project_type) | Q(project_type__label__iexact=project_type))

        tags = self._normalize_tag_filters()
        if tags:
            tag_filter = Q()
            for tag in tags:
                tag_filter |= Q(tags__slug=tag) | Q(tags__label__iexact=tag)
            queryset = queryset.filter(tag_filter)

        search = (self.request.query_params.get(QUERY_PARAM_SEARCH) or '').strip()
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset.distinct()


@PROJECT_DETAIL_SCHEMA
class ProjectDetailView(RetrieveAPIView):
    """Возвращает детальную страницу опубликованного проекта по slug."""

    permission_classes = (AllowAny,)
    serializer_class = ProjectDetailSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = PATH_PARAM_PROJECT_SLUG

    def initial(self, request, *args, **kwargs):
        """Переключает локаль для всего цикла запроса-ответа DRF."""
        lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        translation.activate(lang.lower())
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        tag_queryset = Tag.objects.order_by('label', 'pk')
        button_queryset = ProjectBlockButton.objects.order_by('order', 'pk')
        gallery_queryset = ProjectGalleryImage.objects.order_by('order', 'pk')
        block_queryset = ProjectContentBlock.objects.prefetch_related(
            Prefetch('buttons', queryset=button_queryset)
        ).order_by('order', 'pk')

        return (
            Project.objects.filter(is_published=True)
            .select_related('project_type')
            .prefetch_related(
                Prefetch('tags', queryset=tag_queryset),
                Prefetch('gallery_images', queryset=gallery_queryset),
                Prefetch('content_blocks', queryset=block_queryset),
            )
        )


@PROJECT_TAGS_SCHEMA
class ProjectTagListView(APIView):
    """Возвращает список тегов опубликованных проектов."""

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'

        with translation.override(lang.lower()):
            queryset = Tag.objects.filter(projects__is_published=True).order_by('label', 'pk').distinct()
            tags = [tag.label for tag in queryset]
            return Response(tags)


@PROJECT_TYPES_SCHEMA
class ProjectTypeListView(APIView):
    """Возвращает список типов проектов для фильтров фронтенда."""

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'

        with translation.override(lang.lower()):
            queryset = ProjectType.objects.filter(projects__is_published=True).order_by('label', 'pk').distinct()
            serializer = ProjectTypeSerializer(queryset, many=True)
            return Response({PROJECT_TYPES_RESPONSE_KEY: serializer.data})
