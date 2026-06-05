# Ambasada za urbanizam — Backend API

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![CI](https://github.com/Masterskaya-Ambasada/Ambasada-backend/actions/workflows/codecheck.yaml/badge.svg)
![License](https://img.shields.io/badge/License-Private-red)
![Coverage](https://img.shields.io/badge/coverage-in%20progress-yellow)

**Backend система на Django DRF для веб-сайта Ambasada za urbanizam**

## 📋 Общее описание проекта

Ambasada za urbanizam — это комплексная веб-платформа для управления проектами в сфере урбанистики. Backend система обеспечивает REST API для работы с проектами, командой, контактами и контентом сайта.

### 🎯 Ключевые возможности

- **Управление проектами**: Полный CRUD для проектов с категоризациями, тегами и публикацией
- **Мультиязычность**: Поддержка 4 языков (русский, английский, сербский латиница/кириллица)
- **API документация**: Автоматическая генерация OpenAPI/Swagger документации
- **Безопасность**: JWT авторизация, rate limiting, CSP защита
- **Контент-менеджмент**: Динамические страницы (О нас, Контакты) с админ-панелью
- **Медиа-ресурсы**: Управление изображениями и файлами с валидацией

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
└─────────────┘            │
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │PostgreSQL│  │  Redis   │  │  Media   │
        │          │  │          │  │  Files   │
        └──────────┘  └──────────┘  └──────────┘
```

### Компоненты системы
- **Caddy**: Reverse proxy, HTTPS termination, rate limiting
- **Django/Gunicorn**: Application server, business logic
- **PostgreSQL**: Primary database storage
- **Redis**: Caching, sessions
- **Media files**: User uploaded content (images, documents)

---

## 🛠️ Стек технологий

### Backend Core
- **Django 6.0** — основной веб-фреймворк
- **Django REST Framework 3.16** — API слой
- **Python 3.12** — язык программирования
- **Gunicorn** — production сервер
- **PostgreSQL 17** — основная БД (опционально SQLite для разработки)

### API & Документация
- **drf-spectacular** — OpenAPI 3.0 схема
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

---

## 🌿 Git Workflow

### Ветки и деплой

```
main     → production (ручной деплой)
develop  → dev-сервер (авто-деплой через CI/CD)
feature/* → PR в develop
```

### CI/CD процесс

1. **PR в `main` или `develop`** → запускаются проверки:
   - Линтинг и форматирование (ruff)
   - Тесты (pytest)
   - Django checks
   - Проверка миграций (не модифицированы)

2. **Merge в `develop`** → автоматический деплой на dev-сервер

3. **Merge в `main`** → production деплой (вручную)

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
│   │   ├── projects/          # CRUD проектов
│   │   ├── schemas/           # OpenAPI схемы
│   │   ├── site_config/       # Инициализация API
│   │   ├── users/             # Команда проекта
│   │   ├── urls.py            # Маршруты API v1
│   │   ├── serializers.py     # DRF сериализаторы
│   │   └── views.py           # API представления
│   ├── backend/               # Основные настройки Django
│   │   ├── settings.py        # Конфигурация (ENV переменные)
│   │   ├── urls.py            # Главный routes файл
│   │   └── wsgi.py            # WSGI приложение
│   ├── contacts/              # Приложение контактов
│   │   ├── models.py          # Модели: Contact, ContactSocialLink
│   │   └── admin.py           # Кастомная админка
│   ├── core/                  # Общие утилиты проекта
│   │   ├── middleware.py      # Кастомный middleware (throttle)
│   │   └── validators.py      # Валидаторы файлов, текста
│   ├── locale/                # Файлы переводов (i18n)
│   │   ├── ru/LC_MESSAGES/    # Русский
│   │   ├── en/LC_MESSAGES/    # Английский
│   │   ├── sr_Latn/LC_MESSAGES/  # Сербский (латиница)
│   │   └── sr_Cyrl/LC_MESSAGES/  # Сербский (кириллица)
│   ├── projects/              # Приложение проектов
│   │   ├── models.py          # Модели: Project, ProjectTag, ProjectType
│   │   ├── validators.py      # Валидаторы slug, полей
│   │   └── admin.py           # Кастомная админка
│   ├── site_config/           # Конфигурация сайта
│   │   ├── models.py          # Модели: SiteConfig
│   │   └── views.py           # Init endpoint
│   ├── tests/                 # Тесты проекта
│   │   ├── api/               # API тесты
│   │   ├── projects/          # Тесты проектов
│   │   ├── users/             # Тесты пользователей
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
├── pyproject.toml            # Poetry зависимости
└── README.md                 # Этот файл
```

### Описание модулей

| Модуль | Назначение | Ключевые функции |
|--------|------------|-----------------|
| **about** | Страница "О нас" | Галерея, контент, SEO |
| **api** | REST API слой | Эндпоинты, сериализаторы, схемы |
| **contacts** | Обратная связь | Форма контактов, социальные ссылки |
| **projects** | Управление проектами | CRUD, категории, публикация |
| **users** | Пользователи | Профили, команда проекта |
| **site_config** | Настройки сайта | Инициализация, конфигурация |
| **core** | Общие утилиты | Middleware, валидаторы |
| **backend** | Django конфигурация | Settings, URLs, WSGI |

---

## 🚀 Инструкция по установке и развёртыванию

### Требования

- **Docker** 20.10+ и **Docker Compose** 2.0+
- **Git** для клонирования репозитория
- **Порт** 8000 (Django) должен быть свободен

### 1. Клонирование и базовая настройка

```bash
# Клонирование репозитория
git clone https://github.com/Masterskaya-Ambasada/Ambasada-backend.git
cd Ambasada-backend

# Копирование примера переменных окружения
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте файл `.env` согласно вашим требованиям. Минимальные изменения:

```bash
# Редактирование основных настроек
nano .env  # или используйте ваш редактор
```

**Обязательные переменные для локальной разработки:**

```env
# Основные настройки
DEBUG=True
APP_ENV=development
SECRET_KEY=your-local-development-secret-key
DJANGO_SETTINGS_MODULE=backend.settings

# База данных (опционально, по умолчанию SQLite)
ENABLE_POSTGRES_DB=True  # False для SQLite
POSTGRES_DB=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# CORS (разрешите ваш фронтенд)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Запуск контейнеров

```bash
# Сборка и запуск всех сервисов
docker compose up -d

# Проверка статуса
docker compose ps
```

**При первом запуске** подождите 1-2 минуты пока:
- PostgreSQL инициализируется
- Redis запустится
- Django применит миграции

### 4. Инициализация проекта

```bash
# Применение миграций базы данных
docker compose exec -it web python backend/manage.py migrate

# Создание суперпользователя для админ-панели
docker compose exec -it web python backend/manage.py createsuperuser

# (Опционально) Загрузка начальных данных
docker compose exec -it web python backend/manage.py loaddata initial_data
```

### 5. Проверка работы

```bash
# Проверка логов
docker compose logs web

# Доступ к приложению
# API документация: http://localhost:8000/api/docs/
# Админ-панель:    http://localhost:8000/admin/
# API schema:       http://localhost:8000/api/schema/
```

---

## 🌍 Переменные окружения

### Структура `.env` файла

```env
# ====================
# DJANGO CORE SETTINGS
# ====================
DEBUG=True                              # Режим отладки (True/False)
APP_ENV=development                     # Окружение (development/production)
SECRET_KEY=your-secret-key-here         # Секретный ключ Django
DJANGO_SETTINGS_MODULE=backend.settings # Модуль настроек

# Хосты и CORS
ALLOWED_HOSTS=localhost,127.0.0.1      # Разрешённые хосты
CSRF_TRUSTED_ORIGINS=http://localhost:8000  # Trusted origins для CSRF
CORS_ALLOWED_ORIGINS=http://localhost:3000   # CORS для фронтенда

# ====================
# DATABASE
# ====================
ENABLE_POSTGRES_DB=True                 # Использовать PostgreSQL (True/False)
POSTGRES_DB=db                         # Имя БД
POSTGRES_USER=postgres                 # Пользователь БД
POSTGRES_PASSWORD=postgres              # Пароль БД
POSTGRES_HOST=db                       # Хост БД (в docker: 'db')
POSTGRES_PORT=5432                     # Порт БД

# ====================
# REDIS & CACHE
# ====================
REDIS_URL=redis://redis:6379/0          # URL для подключения к Redis
CACHE_LOCATION=redis://redis:6379/      # Локация кэша

# ====================
# SECURITY SETTINGS
# ====================
# JWT токены
JWT_ACCESS_TOKEN_MINUTES=60            # Время жизни access токена (минуты)
JWT_REFRESH_TOKEN_DAYS=1                # Время жизни refresh токена (дни)

# ====================
# THROTTLING RATES
# ====================
# Лимиты API (формат: число/период)
THROTTLE_RATE_ANON=120/hour            # Анонимные пользователи
THROTTLE_RATE_USER=600/hour            # Авторизованные пользователи
THROTTLE_RATE_CONTACT=5/hour          # Форма контактов (anti-spam)
THROTTLE_RATE_AUTH=10/minute          # Вход в админку (anti-brute-force)

# ====================
# GUNICORN SETTINGS
# ====================
GUNICORN_MAX_REQUESTS=2000             # Макс. запросов перед рестартом worker
GUNICORN_MAX_REQUESTS_JITTER=400       # Рандомизация рестарта

# ====================
# ADMIN LOGIN THROTTLE
# ====================
ADMIN_LOGIN_MAX_ATTEMPTS=10            # Макс. попыток входа
ADMIN_LOGIN_WINDOW_SECONDS=60         # Окно наблюдения (секунды)
ADMIN_LOGIN_BLOCK_SECONDS=300          # Время блокировки (секунды)

# ====================
# COOKIE NAMES
# ====================
SESSION_COOKIE_NAME=ambasada_sessionid  # Имя сессионной куки
CSRF_COOKIE_NAME=ambasada_csrftoken    # Имя CSRF куки
```

### Продукционные переменные

Для production окружения дополнительно required:

```env
# ====================
# PRODUCTION SETTINGS
# ====================
DEBUG=False
APP_ENV=production
SECRET_KEY=<generate-strong-secret-key>

# CORS (только продакшн домены)
CORS_ALLOWED_ORIGINS=https://ambasada.rs,https://www.ambasada.rs
```

---

## 💾 Работа с базой данных

### Применение миграций

```bash
# Создание новых миграций (после изменений моделей)
docker compose exec -it web python backend/manage.py makemigrations

# Просмотр SQL для миграции (без применения)
docker compose exec -it web python backend/manage.py sqlmigrate <app_name> <migration_number>

# Применение миграций
docker compose exec -it web python backend/manage.py migrate

# Проверка статуса миграций
docker compose exec -it web python backend/manage.py showmigrations
```

### Управление данными

Запуск Django shell:

```bash
docker compose exec -it web python backend/manage.py shell
```

Примеры операций в Django shell:

```python
from projects.models import Project
from users.models import User

# Создание проекта
project = Project.objects.create(
    title_ru="Новый проект",
    title_en="New Project",
    is_published=True
)

# Создание пользователя
user = User.objects.create_user(
    email='user@example.com',
    password='secure_password',
    first_name='Иван',
    last_name='Иванов'
)
```

### Резервное копирование

```bash
# Резервное копирование PostgreSQL
docker compose exec db pg_dump -U postgres db > backup.sql

# Восстановление из резервной копии
docker compose exec -T db psql -U postgres db < backup.sql

# Резервное копирование SQLite (dev окружение)
# Только для development с SQLite
docker compose cp web:/code/db.sqlite3 ./backup.sqlite3
```

---

## ▶️ Запуск проекта

### Режимы запуска

#### 1. Локальная разработка (Development)

```bash
# Запуск с hot-reload (django server)
docker compose up

# Или в фоновом режиме
docker compose up -d

# Просмотр логов в реальном времени
docker compose logs -f web
```

#### 2. Production режим

```bash
# Использование production конфигурации
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

# Или через скрипт деплоя
bash docker/deploy_dev_server.sh
```

#### 3. Тестовый режим

```bash
# Запуск тестов
docker compose run --rm web pytest

# С coverage отчётом
docker compose run --rm web pytest --cov=backend --cov-report=html
```

### Управление контейнерами

```bash
# Остановка всех сервисов
docker compose down

# Остановка с удалением volumes (включая БД!)
docker compose down -v

# Перезапуск конкретного сервиса
docker compose restart web

# Ресборка контейнера (после изменений зависимостей)
docker compose build web
docker compose up -d
```

---

## 📡 Работа с API

### Доступ к документации

| Документация | URL | Описание |
|--------------|-----|----------|
| **Swagger UI** | `http://localhost:8000/api/docs/` | Интерактивная документация |
| **ReDoc** | `http://localhost:8000/api/redoc/` | Статическая документация |
| **OpenAPI Schema** | `http://localhost:8000/api/schema/` | RAW JSON схема |

### Основные эндпоинты API

#### Авторизация `/api/v1/auth/`

```bash
# Получение токенов
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

# Ответ
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Обновление access токена
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Проекты `/api/v1/projects/`

```bash
# Список проектов
GET /api/v1/projects/

# Детали проекта
GET /api/v1/projects/{slug}/

# Теги проектов
GET /api/v1/projects/tags/

# Типы проектов
GET /api/v1/projects/types/
```

#### Пользователи `/api/v1/users/`

```bash
# Список команды
GET /api/v1/users/team/
```

#### Контакты `/api/v1/contact/`

```bash
# Создание контакта (anti-spam защита)
POST /api/v1/contact/
Content-Type: application/json

{
  "name": "Иван Петров",
  "email": "ivan@example.com",
  "message": "Здравствуйте, хочу задать вопрос..."
}
```

#### О нас `/api/v1/about/`

```bash
# Получение данных страницы "О нас"
GET /api/v1/about/
```

### Использование API с мультиязычностью

```bash
# Запрос с определённым языком
GET /api/v1/projects/
Accept-Language: ru

# Ответ будет на русском языке

# Смена языка
Accept-Language: en  # Ответ на английском
Accept-Language: sr-latn  # Сербский (латиница)
```

---

## 🛡️ Авторизация

### Статус авторизации

**Авторизация реализована, но НЕ подключена к эндпоинтам.**

Текущее состояние:
- ✅ JWT токены реализованы через `SimpleJWT`
- ✅ Эндпоинты авторизации работают (`/api/v1/auth/login/`)
- ✅ Модель пользователя `User` расширяет `AbstractUser`
- ❌ Защита эндпоинтов через `IsAuthenticated` НЕ применена

### JWT авторизация

```bash
# Получение токена
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Использование токена для запросов
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer <access_token>"
```

---

## 🌐 Локализация

### Поддерживаемые языки

- 🇷🇺 **Русский** (`ru`) — основной язык
- 🇬🇧 **Английский** (`en`) — международный
- 🇷🇸 **Сербский (латиница)** (`sr-latn`) — для Сербии
- 🇷🇸 **Сербский (кириллица)** (`sr-cyrl`) — альтернативная форма

### Fallback цепочка

```
sr-latn → sr-cyrl → ru → en
```

Если перевод отсутствует на запрошенном языке, система использует следующий в цепочке.

### Работа с переводами

#### 1. Переводы интерфейса (gettext)

Все строки, видимые пользователю, должны быть обёрнуты в `_()`:

```python
from django.utils.translation import gettext_lazy as _

class Project(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название'),
        help_text=_('Введите название проекта')
    )
```

#### 2. Переводы данных в БД (modeltranslation)

Для полей, требующих перевода:

```python
# models.py
class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

# translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Project

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = ('ru', 'en', 'sr-latn')
```

После этого автоматически создаются поля: `title_ru`, `title_en`, `title_sr_latn`, `title_sr_cyrl`.

#### 3. Обновление переводов

```bash
# Сбор новых строк для перевода
docker compose exec web python backend/manage.py makemessages -a

# Редактирование переводов
# backend/locale/<lang>/LC_MESSAGES/django.po

# Компиляция переводов
docker compose exec web python backend/manage.py compilemessages
```

#### 4. Использование в API

```python
# serializers.py - используем только базовые поля
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'description')  # НЕ title_en!
```

Язык ответа определяется заголовком `Accept-Language`:

```bash
GET /api/v1/projects/
Accept-Language: en

# Ответ будет на английском
```

---

## 🧪 Тестирование

### Покрытие тестами

| Модуль | Покрытие | Типы тестов | Статус |
|--------|----------|-------------|---------|
| **projects** | ✅ Частично | Unit, Integration | Базовые CRUD |
| **users** | ✅ Частично | Unit | Модели User |
| **site_config** | ✅ Частично | Unit | Инициализация |
| **api** | ✅ Частично | Integration | Эндпоинты |
| **about** | ❌ Нет | — | Отсутствует |
| **contacts** | ❌ Нет | — | Отсутствует |
| **auth** | ✅ Частично | Unit | JWT авторизация |

### Запуск тестов

#### Все тесты

```bash
# Запуск всех тестов
docker compose exec web pytest

# С подробным выводом
docker compose exec web pytest -v

# С coverage отчётом
docker compose exec web pytest --cov=backend --cov-report=html --cov-report=term
```

#### По модулям

```bash
# Тесты проектов
docker compose exec web pytest backend/tests/projects/

# Тесты API
docker compose exec web pytest backend/tests/api/

# Тесты авторизации
docker compose exec web pytest backend/tests/api/test_auth.py
```

#### Отдельный тест

```bash
# Запуск конкретного теста
docker compose exec web pytest backend/tests/projects/test_models.py::test_project_slug_generation

# С Marker (если используется)
docker compose exec web pytest -m "not slow"
```

### Структура тестов

```
backend/tests/
├── conftest.py                # Общие pytest fixtures
├── api/
│   ├── test_auth.py          # Тесты JWT авторизации
│   ├── test_projects_list.py # Тесты списка проектов
│   ├── test_projects_detail.py # Тесты деталей проектов
│   ├── test_projects_meta.py # Тесты метаданных проектов
│   └── test_team_list.py     # Тесты команды
├── projects/
│   ├── test_models.py        # Тесты моделей проектов
│   └── test_validators.py    # Тесты валидаторов
├── users/
│   └── test_models.py        # Тесты моделей пользователей
├── site_config/
│   └── test_init.py          # Тесты инициализации
└── test_admin_login_throttle.py # Тесты throttle middleware
```

### Покрытие кода

Текущее покрытие кода находится в процессе развития. Основные модули, покрытые тестами:
- **projects**: базовые CRUD операции
- **users**: модели и валидация
- **api**: эндпоинты и сериализаторы
- **site_config**: инициализация

Для получения актуальных показателей coverage запустите:
```bash
docker compose exec web pytest --cov=backend --cov-report=term
```

---

## 🚨 Troubleshooting

### Частые ошибки и решения

#### 1. Проблемы с Docker

**Ошибка**: `Cannot connect to the Docker daemon`

**Решение**:
```bash
# Проверка статуса Docker
docker info

# Запуск Docker Desktop (Windows/Mac)
# или службы Docker (Linux)
sudo systemctl start docker
```

#### 2. Проблемы с портом 8000

**Ошибка**: `port is already allocated`

**Решение**:
```bash
# Поиск процесса на порту 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac

# Изменение порта в docker-compose.override.yml
services:
  web:
    ports:
      - "8001:8000"  # Используйте 8001
```

#### 3. Проблемы с БД

**Ошибка**: `FATAL: database "db" does not exist`

**Решение**:
```bash
# Пересоздание volumes (удаляет БД!)
docker compose down -v
docker compose up -d

# Применение миграций
docker compose exec web python backend/manage.py migrate
```

#### 4. Проблемы с миграциями

**Ошибка**: `AttributeError: module 'backend.projects.models' has no attribute 'ModelName'`

**Решение**:
```bash
# Проверка миграций
docker compose exec web python backend/manage.py showmigrations

# Откат проблемной миграции
docker compose exec web python backend/manage.py migrate <app_name> <previous_migration>

# Пересоздание миграции
docker compose exec web python backend/manage.py makemigrations <app_name> --empty
```

#### 5. Проблемы с переводами

**Ошибка**: Переводы не применяются

**Решение**:
```bash
# Проверка .po файлов на fuzzy строки
grep "#, fuzzy" backend/locale/*/LC_MESSAGES/django.po

# Удалить строку "#, fuzzy" вручную в .po файле

# Перекомпиляция
docker compose exec web python backend/manage.py compilemessages
```

#### 6. Проблемы с памятью

**Ошибка**: `Cannot allocate memory`

**Решение**:
```bash
# Очистка Docker ресурсов
docker system prune -a

# Увеличение памяти в Docker Desktop
# Settings → Resources → Memory
```

#### 7. Проблемы с доступом к API

**Ошибка**: `CSRF token missing` или `CORS blocked`

**Решение**:
```bash
# Проверка настроек CORS в .env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Проверка CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Для API запросов используйте правильные заголовки
curl -X POST http://localhost:8000/api/v1/contact/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Test"}'
```

---

## 🚀 Процесс деплоя

### Деплой на Production сервер

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
        # ... скрипт деплоя
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

## 📞 Поддержка и контакты

### Разработка

- **GitHub**: https://github.com/Masterskaya-Ambasada/Ambasada-backend
- **Issues**: https://github.com/Masterskaya-Ambasada/Ambasada-backend/issues

### Контакты команды

Для вопросов по разработке и интеграции:
- **Email**: develop@ambasada.rs (пример)
- **Telegram**: @ambasada_dev (пример)

---

## 📝 Дополнительная документация

- **docker/django/** — Docker конфигурация и скрипты
- **.github/workflows/** — CI/CD процессы
- **backend/api/schemas/** — OpenAPI схемы эндпоинтов

---

**Версия**: 1.0.0  
**Последнее обновление**: 2026-06-05  
**Python**: 3.12+  
**Django**: 6.0+  
**License**: Private
