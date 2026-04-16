"""Маршруты API приложения."""

from csp.decorators import csp_update
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from api.contacts.views import ContactCreateView
from api.projects.views import (
    ProjectDetailView,
    ProjectListView,
    ProjectTagListView,
    ProjectTypeListView,
)

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

contact_urlpatterns = [
    path('v1/contacts/', ContactCreateView.as_view(), name='contact-create'),
]


urlpatterns = doc_urlpatterns + project_urlpatterns + contact_urlpatterns
