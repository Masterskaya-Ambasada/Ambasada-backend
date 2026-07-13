# Ambasada za urbanizam — Backend API

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![CI](https://github.com/Masterskaya-Ambasada/Ambasada-backend/actions/workflows/codecheck.yaml/badge.svg)
![License](https://img.shields.io/badge/License-Private-red)

**Backend система на Django REST Framework для веб-сайта Ambasada za urbanizam — комплексной платформы для управления проектами в сфере урбанистики**

## 📋 Общее описание

Backend обеспечивает REST API для работы с проектами, командой, контактами и контентом сайта. Система поддерживает 3 языка (русский, английский, сербский; у сербского два начертания — латиница и кириллица), реализует кэширование через Redis, фоновые задачи через Celery и обеспечивает безопасность через JWT авторизацию, rate limiting и CSP защиту.

### 🎯 Ключевые возможности

- **Управление проектами**: Полный CRUD для проектов с категоризациями, тегами и публикацией
- **Мультиязычность**: Поддержка 4 языков (русский, английский, сербский латиница/кириллица)
- **API документация**: Явно прописанные OpenAPI схемы для всех эндпоинтов
- **Кэширование**: Redis-кэширование для высоконагруженных эндпоинтов с автоматической инвалидацией
- **Безопасность**: JWT авторизация, rate limiting, CSP защита
- **Контент-менеджмент**: Динамические страницы с админ-панелью
- **Медиа-ресурсы**: Управление изображениями и файлами с валидацией
- **Логирование**: Сквозное логирование бизнес-логики с выводом в терминал/файл

---

## 🏗️ Архитектура

```
┌─────────────┐
│  Frontend   │
│   (React)   │
└──────┬──────┘
       │
       ↓
┌─────────────┐     ┌──────────────┐
│    Caddy    │────→│   Django     │
│  (Reverse   │     │   (Gunicorn) │
│   Proxy)    │     └──────┬───────┘
└──────┬──────┘            │
       │                   │
       ↓                   ↓
┌─────────────┐     ┌────────────┐
│  Media/CDN  │     │  PostgreSQL│
└─────────────┘     └──────┬──────┘
                           │
                  ┌────────┴────────┐
                  ↓                 ↓
            ┌──────────┐      ┌──────────┐
            │  Redis   │      │   Files  │
            │  Cache   │      │  Static  │
            └──────────┘      └──────────┘
```

### Компоненты системы
- **Caddy**: Reverse proxy, HTTPS termination, rate limiting, static files serving
- **Django/Gunicorn**: Application server, business logic
- **PostgreSQL**: Primary database storage
- **Redis**: Кэширование данных эндпоинтов init/home с автоматической инвалидацией через сигналы; брокер для Celery
- **Celery**: Фоновые задачи (отправка уведомлений о заявках из формы контактов)
- **Media/CDN**: Static files and user uploaded content

---

## 🛠️ Стек технологий

<details>
<summary><b>🔧 Подробный стек технологий</b></summary>

### Backend Core
- **Django 6.0** — основной веб-фреймворк
- **Django REST Framework 3.16** — API слой
- **Python 3.12** — язык программирования
- **Gunicorn** — production сервер
- **PostgreSQL 17** — основная БД (опционально SQLite для разработки)

### API & Документация
- **drf-spectacular** — OpenAPI 3.0 схема с явными описаниями
- **явные OpenAPI схемы** — явно прописанные схемы в `backend/api/schemas/`
- **django-filter** — фильтрация и поиск
- **django-cors-headers** — CORS поддержка
- **django-csp** — Content Security Policy

### Безопасность & Авторизация
- **SimpleJWT** — JWT токены авторизации
- **django-modeltranslation** — мультиязычность данных
- **python-decouple** — управление конфигурацией через ENV

### Разработка & Тестирование
- **Poetry** — менеджер зависимостей
- **pytest** + **pytest-django** — тесты
- **pytest-cov** — coverage отчёты
- **ruff** — линтер и форматтер
- **mypy** — type checking

### Инфраструктура
- **Docker & Docker Compose** — контейнеризация
- **Caddy** — reverse proxy + HTTPS
- **Redis** — кэширование и сессии

</details>

---

## 🌿 Git Workflow

```
main     → production (ручной деплой)
develop  → dev-сервер (авто-деплой через CI/CD)
feature/* → PR в develop
```

### CI/CD процесс
1. **PR в `main` или `develop`** → lint, tests, checks
2. **Merge в `develop`** → автоматический деплой на dev-сервер
3. **Merge в `main`** → production деплой (вручную)

---

## 🚀 Быстрый старт

### Требования
- Docker 20.10+ и Docker Compose 2.0+
- Git для клонирования репозитория
- **Development**: порт 8000 должен быть свободен
- **Production**: порты 80 и 443 должны быть свободны (для Caddy reverse proxy)

### Установка и запуск

```bash
# 1. Клонирование репозитория
git clone https://github.com/Masterskaya-Ambasada/Ambasada-backend.git
cd Ambasada-backend

# 2. Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env согласно вашим требованиям

# 3. Запуск контейнеров
docker compose up -d

# 4. Инициализация проекта
docker compose exec -it web python backend/manage.py migrate
docker compose exec -it web python backend/manage.py createsuperuser

# 5. Проверка работы
docker compose logs web
# API документация: http://localhost:8000/api/docs/
# Админ-панель:    http://localhost:8000/admin/
```

### Полная документация по установке

<details>
<summary><b>📖 Подробная инструкция по установке и деплою</b></summary>

#### Используемые порты

**Development:**
- **8000** - Django development server (пробрасывается на хост)

**Production:**
- **80** - HTTP (через Caddy reverse proxy)
- **443** - HTTPS (через Caddy reverse proxy с автоматическим SSL)
- **8000** - Django внутри Docker сети (не пробрасывается наружу, доступ через Caddy)
- **8080** - Dozzle (Docker container viewer, доступ внутри сети на `/dozzle/*`)

#### Разработка (Development)

**Pre-requisites для production деплоя:**
- SSH доступ к production серверу
- Настроенные secrets в GitHub Actions (SSH_KEY, etc.)
- Доменное имя и SSL сертификаты (через Caddy)
- Production database credentials

**Деплой через скрипт:**
```bash
# На сервере
cd ~/backend
bash docker/deploy_dev_server.sh
```

**Деплой вручную:**
```bash
# Сборка production образа
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml build web

# Запуск production контейнеров
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

# Применение миграций
docker compose exec web python backend/manage.py migrate

# Создание суперпользователя
docker compose exec web python backend/manage.py createsuperuser

# Сборка статических файлов
docker compose exec web python backend/manage.py collectstatic --no-input
```

**Мониторинг деплоя:**
```bash
# Проверка статуса контейнеров
docker compose ps

# Просмотр логов
docker compose logs -f web

# Проверка здоровья сервиса
curl https://yourdomain.com/api/v1/init/
```

</details>

---

## 📁 Структура проекта

```
ambasada-backend/
├── backend/                    # Основной Django код
│   ├── about/                  # Приложение "О нас"
│   │   ├── models.py          # Модели: AboutPage, GalleryImage
│   │   ├── admin.py           # Админ-панель
│   │   └── migrations/        # Миграции БД
│   ├── api/                   # REST API приложение
│   │   ├── about/             # Эндпоинты страницы "О нас"
│   │   ├── auth/              # JWT авторизация
│   │   ├── contacts/          # Форма обратной связи
│   │   ├── home/              # Эндпоинты главной страницы
│   │   ├── projects/          # CRUD проектов
│   │   ├── schemas/           # OpenAPI схемы
│   │   ├── security/          # Эндпоинт политики конфиденциальности
│   │   ├── site_config/       # Инициализация API
│   │   ├── users/             # Команда проекта
│   │   ├── urls.py            # Маршруты API v1
│   │   ├── serializers.py     # DRF сериализаторы
│   │   └── views.py           # API представления
│   ├── backend/               # Основные настройки Django
│   │   ├── settings.py        # Конфигурация (ENV переменные)
│   │   ├── urls.py            # Главный routes файл
│   │   ├── wsgi.py            # WSGI приложение
│   │   ├── asgi.py            # ASGI приложение
│   │   └── celery.py          # Конфигурация Celery
│   ├── contacts/              # Приложение контактов
│   │   ├── models.py          # Модели: Contact, ContactSocialLink
│   │   ├── tasks.py           # Celery задачи (уведомления о заявках)
│   │   └── admin.py           # Кастомная админка
│   ├── core/                  # Общие утилиты проекта
│   │   ├── middleware.py      # Кастомный middleware (throttle)
│   │   ├── validators.py      # Валидаторы файлов, текста
│   │   └── base_admin.py      # Базовый админ-класс (BaseTranslatedAdmin)
│   ├── home/                  # Приложение главной страницы
│   │   ├── models.py          # Модели: HomePageContent
│   │   ├── admin.py           # Админ-панель
│   │   └── signals.py         # Сигналы для инвалидации кэша
│   ├── locale/                # Файлы переводов (i18n)
│   │   ├── ru/LC_MESSAGES/    # Русский
│   │   ├── en/LC_MESSAGES/    # Английский
│   │   ├── sr_Latn/LC_MESSAGES/  # Сербский (латиница)
│   │   └── sr_Cyrl/LC_MESSAGES/  # Сербский (кириллица)
│   ├── projects/              # Приложение проектов
│   │   ├── models.py          # Модели: Project, ProjectTag, ProjectType
│   │   ├── validators.py      # Валидаторы slug, полей
│   │   ├── admin_forms.py     # Формы админки проектов
│   │   ├── resources_admin.py # Админ-ресурсы проектов
│   │   └── admin.py           # Кастомная админка
│   ├── security/              # Политика конфиденциальности
│   │   ├── models.py          # Модель: SecurityPolicy
│   │   ├── admin.py           # Админ-панель
│   │   └── migrations/        # Миграции БД
│   ├── site_config/           # Конфигурация сайта
│   │   ├── models.py          # Модели: SiteConfig
│   │   ├── cache.py           # Функции кэширования init/home
│   │   ├── middleware.py      # Middleware
│   │   └── signals.py         # Сигналы для инвалидации кэша
│   ├── tests/                 # Тесты проекта
│   │   ├── api/               # API тесты
│   │   ├── about/             # Тесты about
│   │   ├── contacts/          # Тесты контактов
│   │   ├── home/              # Тесты home
│   │   ├── projects/          # Тесты проектов
│   │   ├── security/          # Тесты политики конфиденциальности
│   │   ├── site_config/       # Тесты кэширования/инициализации
│   │   ├── users/             # Тесты пользователей
│   │   ├── test_admin_login_throttle.py  # Тесты throttle админки
│   │   └── conftest.py        # Pytest конфигурация
│   └── users/                 # Приложение пользователей
│       ├── models.py          # Кастомный User (extends AbstractUser)
│       └── admin.py           # Админ-панель пользователей
├── docker/                     # Docker конфигурации
│   ├── caddy/                 # Caddy reverse proxy
│   │   ├── Caddyfile          # HTTPS + rate limiting конфиг
│   │   └── Dockerfile         # Caddy контейнер
│   ├── django/                # Django/gunicorn контейнер
│   │   ├── Dockerfile         # Multi-stage build (dev/prod)
│   │   ├── entrypoint.sh      # Startup скрипт
│   │   ├── gunicorn_config.py # Gunicorn конфигурация
│   │   ├── gunicorn.sh        # Gunicorn startup
│   │   └── ci.sh              # CI pipeline скрипт
│   ├── deploy_dev_server.sh   # Скрипт деплоя на dev сервер
│   └── docker-compose.prod.yml # Production compose конфиг
├── .env.example               # Пример переменных окружения
├── .github/                   # GitHub Actions
│   └── workflows/
│       ├── codecheck.yaml     # CI проверка кода
│       └── deploy_develop.yaml # Деплой develop ветки
├── docker-compose.yml         # Основной compose файл (dev)
├── docker-compose.override.yml # Локальные override
├── Dockerfile                 # Alias для docker/django/Dockerfile
├── pyproject.toml             # Poetry зависимости и конфигурация
├── poetry.lock                # Зафиксированные версии зависимостей
├── pytest.ini                 # Конфигурация pytest
├── CLAUDE.md                  # Инструкции для Claude Code
└── README.md                  # Этот файл
```

### Описание модулей

| Модуль | Назначение | Ключевые функции |
|--------|------------|-----------------|
| **about** | Страница "О нас" | Галерея, контент, SEO |
| **api** | REST API слой | Эндпоинты, сериализаторы, явные OpenAPI схемы |
| **contacts** | Обратная связь | Форма контактов, социальные ссылки |
| **home** | Главная страница | Контент, кэширование, сигналы |
| **projects** | Управление проектами | CRUD, категории, публикация |
| **users** | Пользователи | Профили, команда проекта |
| **security** | Политика конфиденциальности | Текст политики, эндпоинт `/politics/` |
| **site_config** | Настройки сайта | Init endpoint, Redis-кэширование |
| **core** | Общие утилиты | Middleware, валидаторы |
| **backend** | Django конфигурация | Settings, URLs, WSGI |

---

## 🌍 Переменные окружения

Все переменные с комментариями и значениями по умолчанию собраны в `.env.example`. Скопируйте его и отредактируйте:

```bash
cp .env.example .env
```

### Основные (development)

```env
# Django core
DEBUG=True
APP_ENV=development
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=backend.settings
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
FRONTEND_URL=https://azu.rassokha.pro      # URL фронтенда (CORS, ссылки в письмах)
CORS_ALLOWED_ORIGINS=http://localhost:3000  # домен фронтенда

# База данных
ENABLE_POSTGRES_DB=True                      # False → SQLite
POSTGRES_DB=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Дополнительные группы переменных

| Группа | Переменные | Назначение |
|--------|------------|------------|
| **Redis & Кэш** | `REDIS_URL`, `CACHE_LOCATION` | Кэш эндпоинтов `init`/`home` |
| **Celery** | `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CELERY_TIMEZONE` | Брокер фоновых задач (уведомления о заявках) |
| **Email** | `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `ADMIN_EMAIL` | SMTP и уведомления о новых заявках |
| **Caddy** | `CADDY_DOMAIN_NAME`, `CADDY_LETSENCRYPT_EMAIL` | Домен и сертификаты Let's Encrypt |
| **JWT / Безопасность** | `JWT_ACCESS_TOKEN_MINUTES`, `JWT_REFRESH_TOKEN_DAYS` | Время жизни токенов авторизации |
| **Throttling** | `THROTTLE_RATE_ANON`, `THROTTLE_RATE_USER`, `THROTTLE_RATE_CONTACT`, `THROTTLE_RATE_AUTH` | Rate limits API |
| **Логирование** | `LOG_FILE_PATH` | Путь к файлу логов |
| **Суперпользователь** | `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_FIRST_NAME`, `DJANGO_SUPERUSER_LAST_NAME` | Автосоздание admin в production |
| **Gunicorn** | `GUNICORN_MAX_REQUESTS`, `GUNICORN_MAX_REQUESTS_JITTER` | Параметры production-сервера |
| **Защита админки** | `ADMIN_LOGIN_MAX_ATTEMPTS`, `ADMIN_LOGIN_WINDOW_SECONDS`, `ADMIN_LOGIN_BLOCK_SECONDS` | Brute-force защита входа в admin |
| **Caddy rate limit** | `CADDY_RATE_STATIC_EVENTS/WINDOW`, `CADDY_RATE_DYNAMIC_EVENTS/WINDOW` | Лимиты reverse proxy |
| **Cookies** | `SESSION_COOKIE_NAME`, `CSRF_COOKIE_NAME` | Имена security-cookies |
| **Пагинация** | `PAGE_SIZE`, `MAX_PAGE_SIZE` | Размер страницы API (дефолты в `settings.py`) |
| **Production paths** | `PRODUCTION_MEDIA_ROOT` | Путь к медиа в production |

📖 **Полный список с комментариями — в `.env.example`.** Переменные без явного значения используют разумные дефолты из `settings.py`.

<details>
<summary><b>📋 Переменные для production</b></summary>

Для production обязательно меняются:

```env
# Режим production
DEBUG=False
APP_ENV=production
SECRET_KEY=<сгенерированный сложный ключ>

# Хосты и CORS (замените на свой домен)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Логирование в файл
LOG_FILE_PATH=/code/logs/django.log

# Redis/кэш (пример)
REDIS_URL=redis://redis:6379/0
CACHE_LOCATION=redis://redis:6379/1
```

</details>

---

## 💾 Работа с базой данных

<details>
<summary><b>🗄️ Миграции и резервное копирование</b></summary>

### Миграции

```bash
# Создание новых миграций (после изменений моделей)
docker compose exec -it web python backend/manage.py makemigrations

# Применение миграций
docker compose exec -it web python backend/manage.py migrate

# Проверка статуса миграций
docker compose exec -it web python backend/manage.py showmigrations
```

### Резервное копирование

```bash
# PostgreSQL backup
docker compose exec db pg_dump -U postgres db > backup.sql

# PostgreSQL restore
docker compose exec -T db psql -U postgres db < backup.sql

# Django shell для работы с данными
docker compose exec -it web python backend/manage.py shell
```

</details>

---

## 📡 Работа с API

### Доступ к документации

| Документация | URL | Описание             |
|--------------|-----|----------------------|
| **Swagger UI** | `http://localhost:8000/api/docs/` | Swagger документация |
| **ReDoc** | `http://localhost:8000/api/redoc/` | ReDoc документация   |
| **OpenAPI Schema** | `http://localhost:8000/api/schema/` | RAW JSON схема       |

### Основные эндпоинты API

<details>
<summary><b>🔗 Список доступных эндпоинтов</b></summary>

#### Инициализация и главные страницы
- `GET /api/v1/init/` — Инициализация фронтенда (кэшируется в Redis)
- `GET /api/v1/home/` — Главная страница (кэшируется в Redis)

#### Контент
- `GET /api/v1/about/` — Страница "О нас"
- `POST /api/v1/contacts/` — Форма обратной связи (anti-spam защита)
- `GET /api/v1/politics/` — Политика конфиденциальности

#### Проекты
- `GET /api/v1/projects/` — Список проектов
- `GET /api/v1/projects/{slug}/` — Детали проекта
- `GET /api/v1/projects/tags/` — Теги проектов
- `GET /api/v1/projects/categories/` — Категории проектов

#### Пользователи
- `GET /api/v1/users/team/` — Список команды

#### Авторизация (JWT)
- `POST /api/v1/auth/login/` — Получение токенов
- `POST /api/v1/auth/token/refresh/` — Обновление access токена

### Явные OpenAPI схемы

Для всех эндпоинтов явно прописаны схемы в `backend/api/schemas/`:
- `init_schemas.py`, `home_shemas.py` (опечатка в имени файла - legacy), `about_schemas.py`
- `contact_schemas.py`, `project_schemas.py`
- `auth_schemas.py`, `users_schemas.py`, `security_schemas.py`

### Кэширование API

**Redis-кэширование** реализовано для высоконагруженных эндпоинтов:
- **`/api/v1/init/`** — все данные для инициализации фронтенда
- **`/api/v1/home/`** — данные главной страницы

**Инвалидация кэша** происходит автоматически через Django signals при изменении данных в админ-панели.

</details>

---

## 🌐 Локализация

### Поддерживаемые языки

- 🇷🇺 **Русский** (`ru`) — основной язык
- 🇬🇧 **Английский** (`en`) — международный
- 🇷🇸 **Сербский (латиница)** (`sr-latn` backend → `sr-Latn` frontend) — для Сербии
- 🇷🇸 **Сербский (кириллица)** (`sr-cyrl` backend → `sr-Cyrl` frontend) — альтернативная форма

**Важно**: Бэкенд использует коды `sr-latn` и `sr-cyrl`, а фронтенд получает `sr-Latn` и `sr-Cyrl`.

### Fallback цепочка

```
sr-latn → sr-cyrl → ru → en
```

### Использование в API

Язык ответа определяется заголовком `Accept-Language`:

```bash
GET /api/v1/projects/
Accept-Language: en

# Ответ будет на английском
```

<details>
<summary><b>🔧 Работа с переводами (для разработчиков)</b></summary>

#### Переводы интерфейса (gettext)

```python
from django.utils.translation import gettext_lazy as _

class Project(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название'),
    )
```

#### Переводы данных в БД (modeltranslation)

```python
# translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Project

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = ('ru', 'en', 'sr-latn')
```

#### Обновление переводов

```bash
# Сбор новых строк
docker compose exec web python backend/manage.py makemessages -a

# Компиляция
docker compose exec web python backend/manage.py compilemessages
```

</details>

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
docker compose exec web pytest

# С coverage отчётом
docker compose exec web pytest --cov=backend --cov-report=html

# По модулям
docker compose exec web pytest backend/tests/projects/
docker compose exec web pytest backend/tests/api/

# Отдельный тест
docker compose exec web pytest backend/tests/projects/test_models.py::test_project_slug_generation
```

### Покрытие тестами

<details>
<summary><b>📊 Структура и покрытие тестов</b></summary>

```
backend/tests/
├── api/              # Тесты эндпоинтов
├── about/            # Тесты админки about
├── contacts/         # Тесты админки contacts
├── home/             # Тесты моделей home
├── projects/         # Тесты проектов и админки
├── users/            # Тесты пользователей
├── site_config/      # Тесты кэширования и инициализации
└── conftest.py       # Pytest конфигурация
```

Основные модули, покрытые тестами: projects, users, api, site_config, about, contacts, home.

Для получения актуальных показателей coverage:
```bash
docker compose exec web pytest --cov=backend --cov-report=term
```

</details>

---

## 🚨 Troubleshooting

<details>
<summary><b>🔧 Решение частых проблем</b></summary>

### Docker проблемы

**Cannot connect to the Docker daemon**:
```bash
docker info
sudo systemctl start docker  # Linux
```

### Порт занят

**port is already allocated**:
```bash
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac
```

### Проблемы с БД

**FATAL: database "db" does not exist**:
```bash
docker compose down -v
docker compose up -d
docker compose exec web python backend/manage.py migrate
```

### Проблемы с миграциями

**AttributeError: module has no attribute**:
```bash
docker compose exec web python backend/manage.py showmigrations
docker compose exec web python backend/manage.py migrate <app_name> <previous_migration>
```

### Проблемы с переводами

**Переводы не применяются**:
```bash
grep "#, fuzzy" backend/locale/*/LC_MESSAGES/django.po
# Удалить "#, fuzzy" вручную
docker compose exec web python backend/manage.py compilemessages
```

### CORS/CSRF проблемы

**CSRF token missing или CORS blocked**:
```bash
# Проверка .env
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

</details>

---

## 🚀 Деплой на Production сервер

#### 1. Подготовка сервера

```bash
# Установка Docker и Docker Compose на сервер
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Клонирование репозитория
git clone https://github.com/Masterskaya-Ambasada/Ambasada-backend.git ~/backend
cd ~/backend
```

#### 2. Настройка ENV переменных

```bash
# Копирование и редактирование .env
cp .env.example .env
nano .env

# Обязательные изменения для production:
# DEBUG=False
# APP_ENV=production
# SECRET_KEY=<сгенерированный сложный ключ>
# CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

#### 3. Деплой через скрипт

```bash
# Запуск деплоя (автоматизирует весь процесс)
bash docker/deploy_dev_server.sh
```

**Скрипт выполняет**:
1. Сборку нового Docker образа
2. Запуск всех production контейнеров
3. Перезапуск Caddy (для обновления конфигурации)
4. Очистку старых images

#### 4. Деплой вручную

```bash
# Сборка production образа
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml build web

# Запуск production контейнеров
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

# Применение миграций
docker compose exec web python backend/manage.py migrate

# Создание суперпользователя (если отсутствует)
docker compose exec web python backend/manage.py createsuperuser

# Сборка статических файлов
docker compose exec web python backend/manage.py collectstatic --no-input
```

### Автоматический деплой (CI/CD)

**GitHub Actions** автоматически деплоит при пуше в `develop`:

```yaml
# .github/workflows/deploy_develop.yaml
on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        # Деплой настроен через SSH-action
        # Подробнее: .github/workflows/deploy_develop.yaml
```

### Мониторинг деплоя

```bash
# Проверка статуса контейнеров
docker compose ps

# Просмотр логов
docker compose logs -f web

# Проверка здоровья сервиса
curl https://yourdomain.com/api/v1/init/

# Проверка БД подключения
docker compose exec web python backend/manage.py check --database default
```

### Откат деплоя

```bash
# Откат к предыдущей версии
git checkout <previous_commit_hash>
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

# Или откат через Docker
docker compose down
docker compose up -d --force-recreate
```
---

## ✅ Чеклист перед коммитом

Перед созданием коммита убедитесь, что:

- [ ] **Код проходит линтинг**: `docker compose run --rm web ruff check`
- [ ] **Код отформатирован**: `docker compose run --rm web ruff format --check`
- [ ] **Тесты проходят**: `docker compose run --rm web pytest`
- [ ] **Миграции не модифицированы** (CI проверит это автоматически)
- [ ] **Сообщение коммита понятное** (описывает WHAT и WHY)

---

## 👥 Команда проекта

<details>
<summary><b>👥 Нажмите для просмотра команды</b></summary>

### Project Management

- **Оксана Шубина** — Менеджер Мастерской ЯП (@oksshubina)
- **Юлия Воложина** — Project Manager (@Yulia_Volozhina) — GitHub: https://github.com/YuliyaVo

### DevOps команда

- **Александр Рассоха** — DevOps Engineer (@rassoalex) — GitHub: https://github.com/proboard

### Backend команда

- **Валерий Щепак** — Наставник Python (@kmvpw)	— GitHub: https://github.com/kmvpw
- **Дмитрий Радюк** — Team Lead (@DzzmitryR) — GitHub: https://github.com/Dzmitry-Radziuk
- **Валерия Луговина** — Backend Developer (@rjts4) — GitHub: https://github.com/Va-agh
- **Андрей Головушкин** — Backend Developer (@Frenky_19) — GitHub: https://github.com/Frenky19
- **Марат Ахметов** — Backend Developer (@makhmetcat) — GitHub: https://github.com/MaratAkhmetov
- **Людмила Баукова** — Backend Developer (@pupilPy) — GitHub: https://github.com/bauklu
- **Игорь Могилин** — Backend Developer (@UltraBack) — GitHub: https://github.com/IgorMogilin
- **Игорь Моисеев** — Backend Developer (@Igormaximich) — GitHub: https://github.com/MoiseevIgorPython
- **Сергей Липатов** — Backend Developer (@serg231178) — GitHub: https://github.com/SergLipatov

### Frontend команда

- **Татьяна Шадрина** — Наставник Web (@ta_nett) — GitHub: https://github.com/tanett
- **Дмитрий Лошаков** — Team Lead (@rost_bear) — GitHub: https://github.com/Rostbear61
- **Лидия Липкина** — Frontend Developer (@Lidylip) — GitHub: https://github.com/LidiaLil
- **Александр Леонтьев** — Frontend Developer (@leo14hulk) — GitHub: https://github.com/Alex14hulk
- **Максим Котюков** — Frontend Developer (@maksim_k_ak) — GitHub: https://github.com/maksim533
- **Егор Пузырев** — Frontend Developer (@egorpuzyr) — GitHub: https://github.com/egorpuz
- **Александр Зиньков** — Frontend Developer (@zinkov_27) — GitHub: https://github.com/h3L1x1
- **Елена Ишмухаметова** — Frontend Developer (@renbiw) — GitHub: https://github.com/renbiw

### QA команда

- **Василий Беляков** — Наставник QA (@burzumba)
- **Денис Костомаркин** — QA Engineer (@DenisK_qa) — GitHub: https://github.com/Denis-Kostomarkin
- **Владислав Бердников** — QA Engineer (@BugReaper) — GitHub: https://github.com/vlad-berd
- **Елизавета Макарова** — QA Engineer (@cradlesound) — GitHub: https://github.com/elizavetamakarovavn-netizen
- **Артем Корниец** — QA Engineer (@chuchunj) — GitHub: https://github.com/artemkorniets
- **Юлия Дивенко** — QA Engineer (@Julie_Schattlich) — GitHub: https://github.com/JulieSchattlich
- **Дмитрий Кузьмичев** — QA Engineer (@Dima_nch) — GitHub: https://github.com/DimkaKy

</details>

### Контакты команды

Для вопросов по разработке и интеграции:
- **GitHub**: https://github.com/Masterskaya-Ambasada/Ambasada-backend
- **Issues**: https://github.com/Masterskaya-Ambasada/Ambasada-backend/issues


---

## 📝 Дополнительная документация

- **docker/django/** — Docker конфигурация и скрипты
- **.github/workflows/** — CI/CD процессы
- **backend/api/schemas/** — OpenAPI схемы эндпоинтов

---

**Версия**: 1.0.0  
**Последнее обновление**: 2026-07-12  
**Python**: 3.12+  
**Django**: 6.0+  
**License**: Private  
**Команда**: Masterskaya Ambasada
