from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProjectsConfig(AppConfig):
    """Настройки приложения для управления урбанистическими проектами."""

    name = 'projects'
    verbose_name = _('Урбанистические проекты')

    def ready(self):
        import site_config.signals  # noqa
