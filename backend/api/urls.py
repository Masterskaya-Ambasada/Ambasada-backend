from django.urls import path
from .views import InitView


app_name = 'api'


urlpatterns = [
    path("init/", InitView.as_view(), name="init"),
]

