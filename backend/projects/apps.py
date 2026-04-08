from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProjectsConfig(AppConfig):
    """App configuration for the urban projects module."""

    name = 'projects'
    verbose_name = _('Урбанистические проекты')
