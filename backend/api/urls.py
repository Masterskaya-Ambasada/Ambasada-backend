from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from api.projects.views import (
    ProjectDetailView,
    ProjectListView,
    ProjectTagListView,
    ProjectTypeListView,
)
from api.users.views import AmbasadaTokenObtainPairView

app_name = 'api'

# Эндпоинты документации
doc_urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:v1:schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:v1:schema'), name='redoc'),
]

# Эндпоинты авторизации
auth_urlpatterns = [
    path('login/', AmbasadaTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Эндпоинты проектов
project_urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='projects-list'),
    path('projects/tags/', ProjectTagListView.as_view(), name='projects-tags'),
    path('projects/types/', ProjectTypeListView.as_view(), name='projects-types'),
    path('projects/<slug:project_id>/', ProjectDetailView.as_view(), name='projects-detail'),
]

# Объединение всех эндпоинтов версии v1
v1_urlpatterns = (
    [
        path('auth/', include(auth_urlpatterns)),
    ]
    + doc_urlpatterns
    + project_urlpatterns
)

# Главный список путей
urlpatterns = [
    path('v1/', include((v1_urlpatterns, 'v1'))),
]
