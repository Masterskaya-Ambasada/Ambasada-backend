"""Base settings."""

import sys
from datetime import timedelta
from pathlib import Path

from decouple import Config, RepositoryEnv
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    config = Config(RepositoryEnv(BASE_DIR.parent / '.env'))
except FileNotFoundError:
    print('Error: .env file not found!', file=sys.stderr)
    sys.exit(1)

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
APP_ENV = config('APP_ENV', default='development')


if APP_ENV == 'production':
    DEBUG = False

    CSRF_COOKIE_HTTPONLY = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Content Security Policy
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'",)
    CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
    CSP_IMG_SRC = ("'self'", 'data:')
    CSP_FONT_SRC = ("'self'",)
    CSP_CONNECT_SRC = ("'self'",)
    CSP_FRAME_ANCESTORS = ("'none'",)
    # SSL redirect is disabled because Caddy handles HTTPS termination
    SECURE_SSL_REDIRECT = False
    # HSTS is managed by Caddy — Django must not add its own header
    # SECURE_HSTS_SECONDS = 0 (default)

SESSION_COOKIE_NAME = 'ambasada_sessionid'
CSRF_COOKIE_NAME = 'ambasada_csrftoken'


ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    cast=lambda v: [s.strip() for s in v.split(',')],
    default='localhost,127.0.0.1',
)

# CORS
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    cast=lambda v: [s.strip() for s in v.split(',')],
    default='http://localhost:3000',
)

CORS_ALLOW_CREDENTIALS = False

# Allowed headers - adding Accept-Language for localization
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'accept-language',  # needed for i18n, the front transmits the language
    'content-type',
    'authorization',
    'x-csrftoken',
    'x-requested-with',
]

# Permitted methods are only those that are actually used.
CORS_ALLOW_METHODS = [
    'GET',
    'POST',  # for /contact
    'OPTIONS',  # preflight
]


# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_extensions',
    'drf_spectacular',
    # local
    'projects',
    'users',
    'about',
    'api',
    'site_config',
    'contacts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.AdminLoginThrottleMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

# Cache — Redis
CACHE_LOCATION = config('CACHE_LOCATION', default='')

if APP_ENV == 'production':
    # В продакшене только Redis. Если CACHE_LOCATION пуст — будет ошибка, и это ХОРОШО.
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('CACHE_LOCATION'),
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        }
    }
elif 'test' in sys.argv:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

if config('ENABLE_POSTGRES_DB', '').lower() == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB'),
            'USER': config('POSTGRES_USER'),
            'PASSWORD': config('POSTGRES_PASSWORD'),
            'HOST': config('POSTGRES_HOST'),
            'PORT': config('POSTGRES_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_data' / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'ru'

LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
    ('sr-latn', _('Serbian (Latin)')),
    ('sr-cyrl', _('Serbian (Cyrillic)')),
]

MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'sr-latn': ('sr-cyrl', 'en', 'ru'),
    'sr-cyrl': ('sr-latn', 'en', 'ru'),
    'default': ('ru',),
}

MODELTRANSLATION_FALLBACK_VALUES = None

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en'

LOCALE_PATHS = ['/var/www/django/locale' if APP_ENV == 'production' else str(BASE_DIR / 'locale')]

TIME_ZONE = 'Europe/Moscow'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

_COLLECTSTATIC_DRYRUN = config(
    'DJANGO_COLLECTSTATIC_DRYRUN',
    cast=bool,
    default=False,
)
STATIC_ROOT = '.static' if _COLLECTSTATIC_DRYRUN else '/var/www/django/static'

# Media files (User uploaded content)
MEDIA_URL = 'media/'
MEDIA_ROOT = '/var/www/django/media' if APP_ENV == 'production' else str(BASE_DIR / 'media')


# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': config('PAGE_SIZE', default=20, cast=int),
    'MAX_PAGE_SIZE': config('MAX_PAGE_SIZE', default=100, cast=int),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '120/hour',
        'user': '600/hour',
        'contact': '5/hour',  # форма обратной связи
        'auth': '10/minute',  # вход в Admin — защита от brute-force
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'COERCE_DECIMAL_TO_STRING': False,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'console': {
            'format': '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        },
    },
    'handlers': {
        # Always active — writes to stdout in both dev and production
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'level': 'DEBUG',
        },
        # Production only — writes WARNING+ to file
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'console',
            'filters': ['require_debug_false'],
            'level': 'WARNING',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        # Django internals
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # SQL queries — INFO to avoid flooding in dev, switch to DEBUG when needed
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Email sending — useful to trace in both dev and production
        'django.core.mail': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Security events: admin brute-force, honeypot, invalid form attempts
        'security': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Backend API',
    'DESCRIPTION': 'API documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
