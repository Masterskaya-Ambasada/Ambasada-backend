"""Маршруты API приложения."""

from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from projects.views import (
    ProjectDetailView,
    ProjectListView,
    ProjectTagListView,
    ProjectTypeListView,
)

app_name = 'api'

doc_urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]

project_urlpatterns = [
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

urlpatterns = doc_urlpatterns + project_urlpatterns
