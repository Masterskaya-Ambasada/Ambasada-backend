from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import AmbasadaTokenObtainPairView

app_name = 'api'

doc_urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:v1:schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:v1:schema'), name='redoc'),
]

auth_urlpatterns = [
    path('login/', AmbasadaTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

v1_urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
] + doc_urlpatterns

urlpatterns = [
    path('v1/', include((v1_urlpatterns, 'v1'))),
]
