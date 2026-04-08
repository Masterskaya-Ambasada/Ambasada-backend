"""Маршруты API приложения."""

from django.urls import path
from projects.views import (
    ProjectDetailView,
    ProjectListView,
    ProjectTagListView,
    ProjectTypeListView,
)

app_name = 'api'

urlpatterns = [
    path('v1/projects', ProjectListView.as_view(), name='projects-list'),
    path('v1/projects/tags', ProjectTagListView.as_view(), name='projects-tags'),
    path(
        'v1/projects/types',
        ProjectTypeListView.as_view(),
        name='projects-types',
    ),
    path(
        'v1/projects/<slug:project_id>',
        ProjectDetailView.as_view(),
        name='projects-detail',
    ),
]
