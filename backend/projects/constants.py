"""Константы модели projects."""

REFERENCE_SLUG_MAX_LENGTH = 64
PROJECT_SLUG_MAX_LENGTH = 150
TITLE_MAX_LENGTH = 150
LABEL_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 500
URL_MAX_LENGTH = 500
CONTENT_BLOCK_TITLE_MAX_LENGTH = 50
BUTTON_TYPE_MAX_LENGTH = 16

DEFAULT_ORDER = 0
ORDER_STEP = 1
JSONFORM_TEXTAREA_ROWS = 5
REFERENCE_TRANSLATED_FIELDS = ('slug', 'label_ru', 'label_en', 'label_sr_latn', 'label_sr_cyrl')

BLOCK_VARIANT_IMAGE_WITH_LIST = 1
BLOCK_VARIANT_TWO_IMAGES = 2
BLOCK_VARIANT_IMAGE_WITH_BUTTONS = 3
CONTENT_BLOCK_INDEX_WIDTH = 3
STRING_LIST_MAX_ITEMS = 20
STRING_LIST_ITEM_MAX_LENGTH = 200
BUTTON_TYPE_DOWNLOAD = 'download'
BUTTON_TYPE_REDIRECT = 'redirect'
STRING_LIST_HELP = 'Добавляйте тезисы отдельными пунктами через Add item.'

PROJECT_COVER_IMAGE_HELP = 'Загрузите обложку проекта. Формат: JPG, PNG или WEBP, размер до 20 МБ.'
PROJECT_GALLERY_IMAGE_HELP = 'Загрузите изображение карусели проекта. Формат: JPG, PNG или WEBP, размер до 20 МБ.'
PROJECT_BLOCK_IMAGE_HELP = (
    'Загрузите основное изображение контентного блока. Формат: JPG, PNG или WEBP, размер до 20 МБ.'
)
PROJECT_BLOCK_LEFT_IMAGE_HELP = (
    'Загрузите дополнительное изображение контентного блока. Формат: JPG, PNG или WEBP, размер до 20 МБ.'
)

PROJECT_MEDIA_DIRECTORY = 'projects'
PROJECT_COVER_DIRECTORY = 'cover'
PROJECT_GALLERY_DIRECTORY = 'gallery'
PROJECT_BLOCKS_DIRECTORY = 'blocks'
PROJECT_BLOCK_FALLBACK_SLUG = 'project'

ADMIN_EMPTY_VALUE = '-empty-'
DEFAULT_FRONTEND_URL = 'http://localhost:3000'
FRONTEND_PROJECT_PATH_TEMPLATE = '{frontend_url}/projects/{slug}/'
