from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

custom_url_validator = RegexValidator(
    regex=r'^(https?://|mailto:|tel:)\S+$', message=_('Введите правильный URL-адрес, mailto: или tel:')
)
