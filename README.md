# Ambasada za urbanizam — Backend API

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![CI](https://github.com/Masterskaya-Ambasada/Ambasada-backend/actions/workflows/codecheck.yaml/badge.svg)
![License](https://img.shields.io/badge/License-Private-red)

**Backend система на Django REST Framework для веб-сайта Ambasada za urbanizam — комплексной платформы для управления проектами в сфере урбанистики**

## 📋 Общее описание

Backend обеспечивает REST API для работы с проектами, командой, контактами и контентом сайта. Система поддерживает 4 языка, реализует кэширование через Redis и обеспечивает безопасность через JWT авторизацию, rate limiting и CSP защиту.

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
- **Redis**: Кэширование данных эндпоинтов init/home с автоматической инвалидацией через сигналы
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
- Порт 8000 должен быть свободен

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

#### Разработка (Development)

```bash
# Запуск с hot-reload
docker compose up

# Или в фоновом режиме
docker compose up -d

# Просмотр логов
docker compose logs -f web

# Запуск тестов
docker compose run --rm web pytest

# С coverage отчётом
docker compose run --rm web pytest --cov=backend --cov-report=html
```

#### Production Деплой

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
│   │   └── admin.py           # Кастомная админка
│   ├── site_config/           # Конфигурация сайта
│   │   ├── models.py          # Модели: SiteConfig
│   │   ├── cache.py           # Функции кэширования init/home
│   │   └── signals.py         # Сигналы для инвалидации кэша
│   ├── tests/                 # Тесты проекта
│   │   ├── api/               # API тесты
│   │   ├── about/             # Тесты about
│   │   ├── contacts/          # Тесты контактов
│   │   ├── home/              # Тесты home
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
| **api** | REST API слой | Эндпоинты, сериализаторы, явные OpenAPI схемы |
| **contacts** | Обратная связь | Форма контактов, социальные ссылки |
| **home** | Главная страница | Контент, кэширование, сигналы |
| **projects** | Управление проектами | CRUD, категории, публикация |
| **users** | Пользователи | Профили, команда проекта |
| **site_config** | Настройки сайта | Init endpoint, Redis-кэширование |
| **core** | Общие утилиты | Middleware, валидаторы |
| **backend** | Django конфигурация | Settings, URLs, WSGI |

---

## 🌍 Переменные окружения

### Ключевые переменные

```env
# Основные настройки
DEBUG=True
APP_ENV=development
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=backend.settings

# База данных
ENABLE_POSTGRES_DB=True  # False для SQLite
POSTGRES_DB=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db

# CORS (разрешите ваш фронтенд)
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Полный список переменных

📖 **Полный список всех переменных окружения с комментариями находится в `.env.example`**

<details>
<summary><b>📋 Дополнительные переменные для production</b></summary>

Для production окружения дополнительно required:

```env
# Production settings
DEBUG=False
APP_ENV=production
SECRET_KEY=<strong-secret-key>

# Production hosts
ALLOWED_HOSTS=ambasada.rs,www.ambasada.rs
CSRF_TRUSTED_ORIGINS=https://ambasada.rs,https://www.ambasada.rs
CORS_ALLOWED_ORIGINS=https://ambasada.rs,https://www.ambasada.rs

# Production logging
LOG_LEVEL=WARNING
LOG_OUTPUT=file
LOG_FILE_PATH=/code/logs/django.log

# Production cache
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

| Документация | URL | Описание |
|--------------|-----|----------|
| **Swagger UI** | `http://localhost:8000/api/docs/` | Интерактивная документация |
| **ReDoc** | `http://localhost:8000/api/redoc/` | Статическая документация |
| **OpenAPI Schema** | `http://localhost:8000/api/schema/` | RAW JSON схема |

### Основные эндпоинты API

<details>
<summary><b>🔗 Список доступных эндпоинтов</b></summary>

#### Инициализация и главные страницы
- `GET /api/v1/init/` — Инициализация фронтенда (кэшируется в Redis)
- `GET /api/v1/home/` — Главная страница (кэшируется в Redis)

#### Контент
- `GET /api/v1/about/` — Страница "О нас"
- `POST /api/v1/contact/` — Форма обратной связи (anti-spam защита)

#### Проекты
- `GET /api/v1/projects/` — Список проектов
- `GET /api/v1/projects/{slug}/` — Детали проекта
- `GET /api/v1/projects/tags/` — Теги проектов
- `GET /api/v1/projects/types/` — Типы проектов

#### Пользователи
- `GET /api/v1/users/team/` — Список команды

#### Авторизация (JWT)
- `POST /api/v1/auth/login/` — Получение токенов
- `POST /api/v1/auth/token/refresh/` — Обновление access токена

### Явные OpenAPI схемы

Для всех эндпоинтов явно прописаны схемы в `backend/api/schemas/`:
- `init_schemas.py`, `home_shemas.py` (опечатка в имени файла - legacy), `about_schemas.py`
- `contact_schemas.py`, `project_schemas.py`
- `auth_schemas.py`, `users_schemas.py`

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

- **Юлия Воложина** — Project Manager (@Yulia_Volozhina) — GitHub: https://github.com/YuliyaVo

### Backend команда

- **Дмитрий Радюк** — Team Lead (@DzzmitryR) — GitHub: https://github.com/Dzmitry-Radziuk
- **Валерия Луговина** — Backend Developer (@rjts4) — GitHub: https://github.com/Va-agh
- **Андрей Головушкин** — Backend Developer (@Frenky_19) — GitHub: https://github.com/Frenky19
- **Марат Ахметов** — Backend Developer (@makhmetcat) — GitHub: https://github.com/MaratAkhmetov
- **Людмила Баукова** — Backend Developer (@pupilPy) — GitHub: https://github.com/bauklu
- **Игорь Могилин** — Backend Developer (@UltraBack) — GitHub: https://github.com/IgorMogilin
- **Игорь Моисеев** — Backend Developer (@Igormaximich) — GitHub: https://github.com/MoiseevIgorPython
- **Сергей Липатов** — Backend Developer (@serg231178) — GitHub: https://github.com/SergLipatov

### DevOps команда

- **Александр Рассоха** — DevOps Engineer (@rassoalex) — GitHub: https://github.com/proboard

### QA команда

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
**Последнее обновление**: 2026-06-05  
**Python**: 3.12+  
**Django**: 6.0+  
**License**: Private  
**Команда**: Masterskaya Ambasada
