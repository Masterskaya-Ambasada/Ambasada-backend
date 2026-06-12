from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SecurityConfig(AppConfig):
    """Приложение политики конфиденциальности."""

    name = 'security'
    verbose_name = _('Полтика конфиденциальности')
