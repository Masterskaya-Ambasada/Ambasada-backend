from django.urls import path  # type: ignore
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import InitView

app_name = 'api'

doc_urlpatterns = [
    path('init/', InitView.as_view(), name='init'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]

urlpatterns = [] + doc_urlpatterns
