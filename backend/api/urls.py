"""Маршруты API приложения."""

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from api.projects.urls import urlpatterns as project_urls
from api.about.urls import urlpatterns as about_urls

app_name = 'api'

doc_urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]

v1_urlpatterns = [
    path('', include(project_urls)),
    path('', include(about_urls)),
]

urlpatterns = [
    path('v1/', include(v1_urlpatterns)),
] + doc_urlpatterns