"""Представления API для каталога и страницы проекта."""

from __future__ import annotations

from django.db.models import Prefetch
from projects.models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectType,
    Tag,
)
from api.projects.pagination import ProjectLimitOffsetPagination
from api.projects.serializers import (
    ProjectCardSerializer,
    ProjectDetailSerializer,
    ProjectTypeSerializer,
)
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class ProjectListView(ListAPIView):
    """Возвращает список опубликованных проектов с фильтрацией и пагинацией."""

    permission_classes = (AllowAny,)
    serializer_class = ProjectCardSerializer
    pagination_class = ProjectLimitOffsetPagination

    def get_queryset(self):
        tag_queryset = Tag.objects.order_by('label', 'pk')
        queryset = (
            Project.objects.filter(is_published=True)
            .select_related('project_type')
            .prefetch_related(Prefetch('tags', queryset=tag_queryset))
        )
        project_type = self.request.query_params.get('project_type')
        if project_type:
            queryset = queryset.filter(project_type__slug=project_type)
        tags = [tag for tag in self.request.query_params.getlist('tag') if tag]
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset.distinct()


class ProjectDetailView(RetrieveAPIView):
    """Возвращает детальную страницу опубликованного проекта по slug."""

    permission_classes = (AllowAny,)
    serializer_class = ProjectDetailSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'project_id'

    def get_queryset(self):
        tag_queryset = Tag.objects.order_by('label', 'pk')
        button_queryset = ProjectBlockButton.objects.order_by('order', 'pk')
        block_queryset = ProjectContentBlock.objects.prefetch_related(
            Prefetch('buttons', queryset=button_queryset)
        ).order_by('order', 'pk')
        return (
            Project.objects.filter(is_published=True)
            .select_related('project_type')
            .prefetch_related(
                Prefetch('tags', queryset=tag_queryset),
                Prefetch('content_blocks', queryset=block_queryset),
            )
        )


class ProjectTagListView(APIView):
    """Возвращает список тегов опубликованных проектов."""

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        queryset = Tag.objects.filter(projects__is_published=True).order_by('label', 'pk').distinct()
        tags = [tag.label for tag in queryset]
        return Response(tags)


class ProjectTypeListView(APIView):
    """Возвращает список типов проектов для фильтров фронтенда."""

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        queryset = ProjectType.objects.filter(projects__is_published=True).order_by('label', 'pk').distinct()
        serializer = ProjectTypeSerializer(queryset, many=True)
        return Response({'types': serializer.data})
