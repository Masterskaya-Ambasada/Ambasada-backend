from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteConfigConfig(AppConfig):
    name = 'site_config'
    verbose_name = _('Настройки сайта')
