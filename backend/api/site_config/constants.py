from django.utils.translation import gettext_lazy as _

CACHE_TIMEOUT_SUCCESS = 3600
CACHE_TIMEOUT_NOT_FOUND = 300
CACHE_KEY_INIT = 'site_config_init'
CACHE_VALUE_NOT_FOUND = 'NOT_FOUND'
ERROR_CODE_NOT_FOUND = 'NOT_FOUND'
ERROR_MESSAGE_NOT_FOUND = _('Конфигурация сайта не найдена')
