"""Константы модуля About."""

from django.utils.translation import gettext_lazy as _

# --- Ограничения длины полей ---
TITLE_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 600
TEXT_MAX_LENGTH = 600


# --- Пути для загрузки медиафайлов ---
UPLOAD_GALLERY = 'about/gallery/'
UPLOAD_ABOUT = 'about/'

# --- Настройки по умолчанию ---
PARAGRAPH_DEFAULT_ORDER = 0

# --- Значения по умолчанию для полей страницы ---
DEFAULT_HERO_TITLE = _('О сообществе')
DEFAULT_HERO_DESCRIPTION = ''
DEFAULT_ABOUT_TITLE = _('О нас')
DEFAULT_BUTTON_LABEL = _('Перейти к проектам')
DEFAULT_BUTTON_LINK = 'https://'
DEFAULT_VALUES_TITLE = _('Наши ценности')
DEFAULT_GALLERY_TITLE = _('Наша галерея')

# --- Подсказки для Контент-Менеджера ---
HELP_LIMIT_100 = _('Максимум 100 символов.')
HELP_LIMIT_600 = _('Максимум 600 символов.')

FIELD_HERO_TITLE_HELP = _('Крупный заголовок главного вводного блока страницы. ') + HELP_LIMIT_100
FIELD_HERO_DESC_HELP = _('Краткий вводный текст, подзаголовок или слоган. ') + HELP_LIMIT_600
FIELD_ABOUT_TITLE_HELP = _('Главный заголовок текстового раздела с описанием проекта. ') + HELP_LIMIT_100
FIELD_BUTTON_LABEL_HELP = _('Надпись на кнопке (например: "Узнать больше"). ') + HELP_LIMIT_100
FIELD_BUTTON_LINK_HELP = (
    _('Ссылка, на которую перенаправит кнопка (например: /projects/ или ' 'https://external-site.com). ')
    + HELP_LIMIT_600
)
FIELD_VALUES_TITLE_HELP = _('Заголовок для секции с ценностями сообщества. ') + HELP_LIMIT_100
FIELD_GALLERY_TITLE_HELP = _('Главный заголовок для блока фотогалереи. ') + HELP_LIMIT_100

FIELD_FIRST_SENTENCE_HELP = _('Первое предложение. Фронтенд выделит его жирным шрифтом или цветом. ') + HELP_LIMIT_600
FIELD_MAIN_TEXT_HELP = _('Продолжение абзаца обычным (не выделенным) шрифтом.')
FIELD_ORDER_HELP = _('Индекс для сортировки. Чем меньше число, тем выше абзац на сайте.')

FIELD_VALUE_TITLE_HELP = _('Короткое название (например: "Развитие"). ') + HELP_LIMIT_100
FIELD_VALUE_TEXT_HELP = _('Детальное описание сути этой ценности. ') + HELP_LIMIT_600

FIELD_IMAGE_HELP = _('Фото для карусели. Рекомендуется современный формат WebP или JPG.')
FIELD_ALT_HELP = _('Описание фото для поисковых роботов (SEO) и экранных дикторов.')
