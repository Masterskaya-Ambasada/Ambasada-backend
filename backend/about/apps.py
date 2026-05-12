from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContactsConfig(AppConfig):
    name = 'about'
    verbose_name = _('Страница "О нас"')

    def ready(self):
        pass
