from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContactsConfig(AppConfig):
    name = 'home'
    verbose_name = _('Главная страница')

    def ready(self):
        import home.signals  # noqa
