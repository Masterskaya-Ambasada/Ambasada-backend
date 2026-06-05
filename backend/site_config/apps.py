from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteConfigConfig(AppConfig):
    """Конфигурация приложения настроек сайта."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'site_config'
    verbose_name = _('Конфигурация настроек сайта')

    def ready(self):
        import site_config.signals  # noqa
