"""Маршруты API приложения Ambasada."""

from csp.decorators import csp_update
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from api.about.views import AboutAPIView
from api.contacts.views import ContactView
from api.projects.views import (
    ProjectDetailView,
    ProjectListView,
    ProjectTagListView,
    ProjectTypeListView,
)
from api.site_config.views import InitView
from api.users.views import AmbasadaTokenObtainPairView, TeamListView

app_name = 'api'

# Эндпоинты документации
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

# Эндпоинты авторизации
auth_urlpatterns = [
    path('login/', AmbasadaTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Эндпоинты пользователей и команды
user_urlpatterns = [
    path('team/', TeamListView.as_view(), name='team_list'),
]

# Эндпоинты проектов
project_urlpatterns = [
    path('', ProjectListView.as_view(), name='projects-list'),
    path('tags/', ProjectTagListView.as_view(), name='projects-tags'),
    path('types/', ProjectTypeListView.as_view(), name='projects-types'),
    path('<slug:project_id>/', ProjectDetailView.as_view(), name='projects-detail'),
]

# Эндпоинты страницы "О нас"
about_urlpatterns = [
    path('about/', AboutAPIView.as_view(), name='about'),
]

# Эндпоинты контактов
contact_urlpatterns = [
    path('', ContactView.as_view(), name='contact-create'),
]

# Объединение всех эндпоинтов версии v1
v1_urlpatterns = [
    path('init/', InitView.as_view(), name='init'),
    path('auth/', include(auth_urlpatterns)),
    path('users/', include(user_urlpatterns)),
    path('projects/', include(project_urlpatterns)),
    path('contact/', include(contact_urlpatterns)),
    path('', include(about_urlpatterns)),
    path('', include(doc_urlpatterns)),
]

# Главный список путей
urlpatterns = [path('v1/', include(v1_urlpatterns))]
