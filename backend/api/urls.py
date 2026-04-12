from django.urls import path  # type: ignore

from .views import InitView

app_name = 'api'


urlpatterns = [
    path('init/', InitView.as_view(), name='init'),
]
