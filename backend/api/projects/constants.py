from django.utils.translation import gettext_lazy as _

ACCEPT_LANGUAGE_HEADER = 'Accept-Language'
SUPPORTED_LANGUAGE_CODES = ('ru', 'en', 'sr-latn', 'sr-cyrl')

QUERY_PARAM_PROJECT_TYPE = 'project_type'
QUERY_PARAM_TAG = 'tag'
QUERY_PARAM_SEARCH = 'search'
TAG_QUERY_VALUE_SEPARATOR = ','
PATH_PARAM_PROJECT_ID = 'project_id'

PROJECT_TYPES_RESPONSE_KEY = 'types'
PROJECT_LIST_RESPONSE_ITEMS_KEY = 'items'
PROJECT_LIST_RESPONSE_PAGINATION_KEY = 'pagination'
PAGINATION_TOTAL_ITEMS_KEY = 'totalItems'
PAGINATION_OFFSET_KEY = 'offset'
PAGINATION_LIMIT_KEY = 'limit'
PAGINATION_IS_NEXT_KEY = 'isNext'
PROJECT_ACTION_BUTTON_LABEL = _('Перейти к проекту')
PROJECT_ACTION_BUTTON_LINK_TEMPLATE = '/projects/{slug}'
