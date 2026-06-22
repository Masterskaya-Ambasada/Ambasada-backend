from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

custom_url_validator = RegexValidator(
    regex=r'^(https?://|mailto:|tel:)\S+$', message=_('Введите правильный URL-адрес, mailto: или tel:')
)
phone_validator = RegexValidator(
    regex=r'^[+]?[0-9()\-\s]{5,20}$',
    message=_('Введите корректный номер телефона'),
)
