"""Конфигурация приложения проектов."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProjectsConfig(AppConfig):
    """Конфигурация приложения с проектами."""

    name = 'projects'
    verbose_name = _('Проекты Амбасада за урбанизм.')
