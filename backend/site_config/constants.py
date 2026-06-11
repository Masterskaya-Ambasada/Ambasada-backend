from django.utils.translation import gettext_lazy as _

# --- СИСТЕМНЫЕ НАСТРОЙКИ И КЭШИРОВАНИЕ ---
SITE_CONFIG_SINGLETON_PK = 1
CACHE_KEY_SITE_CONFIG = 'site_config:v1.1'
CACHE_KEY_FULL_CONFIG = 'site_config:v1.1_full'
TIMEOUT_CACHE = 86400

# --- МАКСИМАЛЬНЫЕ ДЛИНЫ ПОЛЕЙ ---
SITE_NAME_MAX_LENGTH = 100
SEO_DESCRIPTION_MAX_LENGTH = 250
COOKIE_BUTTON_TEXT_MAX_LENGTH = 20
COPYRIGHT_MAX_LENGTH = 150
SOCIAL_TYPE_MAX_LENGTH = 20
CONTACT_BUTTON_LABEL_MAX_LENGTH = 50
CONTACT_LINK_MAX_LENGTH = 255
TEAM_TITLE_MAX_LENGTH = 100

# --- ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ (ДЕФОЛТЫ) ---
DEFAULT_COOKIE_BUTTON_TEXT = 'OK'
DEFAULT_COOKIE_MESSAGE = _('Мы используем технические cookie для корректной работы сайта.')

DEFAULT_COPYRIGHT_TEXT = '@2026'

DEFAULT_TEAM_TITLE = _('Команда')
DEFAULT_MAIN_TEAM_BUTTON_LABEL = _('Присоединиться к команде')
DEFAULT_ABOUT_TEAM_BUTTON_LABEL = _('Присоединиться')
DEFAULT_TEAM_BUTTON_LINK = '/contacts'

# --- ПОДСКАЗКИ ДЛЯ АДМИН-ПАНЕЛИ (HELP TEXT) ---
VALIDATION_SITE_DELETE_ERROR = _('Удаление системных настроек сайта запрещено.')

HELP_SITE_NAME = _('Выводится во вкладке браузера и заголовках писем. До 100 симв.')
HELP_SEO_DESCRIPTION = _('Описание сайта в поисковых системах Google и Яндекс. До 250 симв. Важно для SEO!')
HELP_PRIVACY_POLICY = help_text = (
    _(
        'Краткий текст для форм обратной связи (рядом с кнопкой отправки). '
        'Обязательно выделите слова "Политикой конфиденциальности" и вставьте '
        'на них ссылку на саму страницу политики через редактор TinyMCE.'
    ),
)
HELP_COOKIE_MESSAGE = _('Текст всплывающего уведомления об использовании файлов Cookie.')
HELP_COOKIE_BUTTON_TEXT = _('Текст на кнопке согласия Cookie (например: "OK" или "Принять").')
HELP_COPYRIGHT = _('Текст в самом низу страницы (футере). До 150 симв.')
HELP_TEAM_TITLE = _('Заголовок блока со списком команды на странице "О нас".')
HELP_MAIN_TEAM_BUTTON = _('Надпись на кнопке в блоке команды на Главной странице.')
HELP_ABOUT_TEAM_BUTTON = _('Надпись на кнопке в блоке команды на странице "О нас".')
HELP_TEAM_BUTTON_LINK = _('Ссылка для обеих кнопок команды. Например: /contacts или ссылка на якорный блок.')
