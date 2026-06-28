"""Константы приложения projects."""

from django.utils.translation import gettext_lazy as _

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
TRANSLATED_FIELD_SUFFIXES = ('_sr_latn', '_sr_cyrl', '_ru', '_en')

REFERENCE_ADMIN_HELP_TEXTS = {
    'slug': _(
        'Системный код для API и фильтров: только латинские буквы, цифры, дефис или подчеркивание, до 64 символов. '
        'Например: research или belgrade-navigation.'
    ),
    'label': _(
        'Название, которое видит пользователь в карточках и фильтрах. До 100 символов. Заполните все языковые версии; '
        'если перевод пустой, API отдаст fallback на другой язык.'
    ),
}

PROJECT_ADMIN_HELP_TEXTS = {
    'slug': _(
        'URL-идентификатор проекта. Можно оставить пустым при создании: он сгенерируется из русского названия. '
        'После сохранения slug лучше не менять.'
    ),
    'title': _('Название проекта для карточки, каталога и детальной страницы. До 150 символов.'),
    'description': _(
        'Краткое описание используется и в карточке проекта в каталоге, и в верхнем блоке страницы проекта. '
        'В карточке длинный текст может обрезаться многоточием. До 500 символов, без длинных абзацев.'
    ),
    'year': _('Год реализации или публикации. Введите только число, например 2025.'),
    'project_type': _('Выберите один тип проекта. Названия типов редактируются отдельно в разделе "Типы проектов".'),
    'tags': _(
        'Можно выбрать несколько тегов через виджет выбора. Названия тегов редактируются отдельно в разделе "Теги".'
    ),
    'cover_image': _('Обязательная обложка проекта. Формат: JPG, PNG или WEBP, размер до 20 МБ.'),
    'is_published': _('Если выключено, проект не попадет в публичный API и не будет виден на сайте.'),
}

GALLERY_IMAGE_ADMIN_HELP_TEXTS = {
    'image': _('Изображение для верхней карусели проекта. Формат: JPG, PNG или WEBP, размер до 20 МБ.'),
    'order': _('Порядок изображения в карусели. Меньшее число показывается раньше.'),
}

CONTENT_BLOCK_ADMIN_HELP_TEXTS = {
    'variant': _(
        'Выберите макет блока. "Изображение и список" использует список тезисов; "Два изображения" использует '
        'основное и левое изображение; "Изображение и кнопки" показывает вложенные кнопки. Изображения можно не '
        'загружать, если по макету они не нужны.'
    ),
    'order': _('Порядок блока внутри проекта. Значение должно быть уникальным в рамках проекта; меньшее число выше.'),
    'title': _('Заголовок секции проекта. До 50 символов. Заполните нужные языковые версии.'),
    'image': _('Необязательное основное изображение блока. Формат: JPG, PNG или WEBP, размер до 20 МБ.'),
    'left_image': _(
        'Необязательное дополнительное изображение. Используется только для варианта "Два изображения". '
        'Формат: JPG, PNG или WEBP, размер до 20 МБ.'
    ),
    'text': _('Обязательный основной текст блока. Заполняется через редактор, HTML формируется автоматически.'),
    'accented_text': _('Необязательный выделенный текст, подпись или акцентный абзац. Оставьте пустым, если не нужен.'),
    'string_list': _(
        'Только для варианта "Изображение и список". Добавляйте тезисы через "Add item": до 20 пунктов, '
        'каждый до 200 символов.'
    ),
}

BLOCK_BUTTON_ADMIN_HELP_TEXTS = {
    'order': _('Порядок кнопки внутри блока. Меньшее число показывается раньше.'),
    'label': _('Текст на кнопке. До 100 символов. Заполните нужные языковые версии.'),
    'type': _(
        '"Скачать файл" используйте для материалов проекта; "Перейти по ссылке" — для обычной внешней '
        'или внутренней ссылки.'
    ),
    'url': _('Полная ссылка с http:// или https://. Для Google Drive проверьте, что доступ открыт по ссылке.'),
}

CYRILLIC_TO_LATIN = str.maketrans(
    {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'e',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'y',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'kh',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'sch',
        'ъ': '',
        'ы': 'y',
        'ь': '',
        'э': 'e',
        'ю': 'yu',
        'я': 'ya',
    }
)

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
