from django.urls import path
from backend.api.about.views import AboutAPIView

urlpatterns = [
    path('about/', AboutAPIView.as_view(), name='about'),
]