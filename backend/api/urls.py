"""URL маршруты для API раздела 'О сообществе'."""

from django.urls import path

from .views import AboutAPIView

urlpatterns = [
    path('about/', AboutAPIView.as_view(), name='about'),
]
