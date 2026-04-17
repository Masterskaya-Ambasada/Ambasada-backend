"""Маршруты API приложения Ambasada."""

from csp.decorators import csp_update
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from api.projects.views import (
    ProjectDetailView,
    ProjectListView,
    ProjectTagListView,
    ProjectTypeListView,
)

from api.about.views import AboutAPIView

app_name = 'api'

doc_urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'docs/',
        csp_update(
            SCRIPT_SRC=("'unsafe-inline'", 'cdn.jsdelivr.net'),
            STYLE_SRC=("'unsafe-inline'", 'cdn.jsdelivr.net'),
            IMG_SRC=('data:', 'cdn.jsdelivr.net'),
        )(SpectacularSwaggerView.as_view(url_name='api:schema')),
        name='swagger',
    ),
    path(
        'redoc/',
        csp_update(
            SCRIPT_SRC=('cdn.jsdelivr.net',),
            STYLE_SRC=("'unsafe-inline'", 'fonts.googleapis.com'),
            FONT_SRC=('fonts.gstatic.com',),
            IMG_SRC=('data:',),
        )(SpectacularRedocView.as_view(url_name='api:schema')),
        name='redoc',
    ),
]

project_urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='projects-list'),
    path('projects/tags/', ProjectTagListView.as_view(), name='projects-tags'),
    path('projects/types/', ProjectTypeListView.as_view(), name='projects-types'),
    path('projects/<slug:project_id>/', ProjectDetailView.as_view(), name='projects-detail'),
]

about_urlpatterns = [
    path('about/', AboutAPIView.as_view(), name='about'),
]

v1_urlpatterns = [
    path('', include(project_urlpatterns)),
    path('', include(about_urlpatterns)),
]

urlpatterns = [
    path('v1/', include(v1_urlpatterns)),
] + doc_urlpatterns