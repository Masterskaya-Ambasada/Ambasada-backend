
# Проект "Ambasada za urbanizam"
Backend на Django DRF для веб-сайта.

## 🛠️ Локальная разработка с Docker

### Настройка окружения:

```bash
cp  .env.example  .env
```

### Запуск сервисов.

*Если локальных `docker images` нет — они будут загружены из DockerHub или собраны автоматически.*
```bash
docker  compose  up  -d
```

### 3. Создать миграции, применить миграции базы данных и создать суперпользователя:

```bash
docker  compose  exec  -it  web  python  backend/manage.py  makemigrations
docker  compose  exec  -it  web  python  backend/manage.py  migrate
docker  compose  exec  -it  web  python  backend/manage.py  createsuperuser
```

### Доступ к приложению

* Откройте http://localhost:8000/api/docs/ в браузере

## API

Документация API доступна по следующим адресам:
*  `/api/docs/` → Swagger UI

*  `/api/redoc/` → ReDoc

*  `/api/schema/` → raw schema (OpenAPI)

### Примечания

Документация генерируется автоматически на основе **DRF views и serializers**.
При добавлении новых endpoints они автоматически появляются в **OpenAPI schema** и документации.

## 🌐 Мультиязычность (i18n & l10n)

Проект поддерживает несколько языков:

* 🇷🇺 Русский (`ru`)
* 🇬🇧 Английский (`en`)
* 🇷🇸 Сербский (латиница) (`sr-latn`)
* 🇷🇸 Сербский (кириллица) (`sr-cyrl`)

Вся инфраструктура уже настроена внутри Docker — ничего дополнительно устанавливать не требуется.

---

## Интерфейсные строки (gettext)

Все строки, которые видит пользователь (заголовки, ошибки, подсказки), **обязательно должны быть обёрнуты в функцию перевода** `_()`.

```python
from django.utils.translation import gettext_lazy as _
```

### Пример в модели

```python
class Project(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
        help_text=_('Enter the project name.')
    )
```

* `verbose_name` — название поля в Django Admin
* `help_text` — подсказка пользователю
* `_()` — помечает строку для перевода

### Использование в `apps.py`

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ProjectsConfig(AppConfig):
    name = "projects"
    verbose_name = _('Projects')
```

### Пример валидации

```python
from django.core.exceptions import ValidationError

raise ValidationError(_('Invalid value'))
```

❌ Нельзя хардкодить строки без `_()`.

---

## Перевод данных в базе (django-modeltranslation)

Для полей, которые должны иметь разные значения на разных языках (например название или описание проекта), используется **django-modeltranslation**.

### Пример модели

```python
class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
```

### `translation.py`

```python
from modeltranslation.translator import register, TranslationOptions
from .models import Project

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = ('ru', 'en') # уточнят у заказчика
```

После этого библиотека создаёт дополнительные поля в базе:

```
title_ru
title_en
title_sr_latn
title_sr_cyrl
```

⚠️ В коде **всегда используется только базовое поле**:

```python
project.title
```

Нельзя использовать `title_en`, `title_ru` и т.д. — Django автоматически подставляет перевод в зависимости от активного языка.

После добавления переводов необходимо создать миграции:

```bash
docker compose exec web python backend/manage.py makemigrations
```

---

## Работа с API

Язык ответа определяется через `LocaleMiddleware` и заголовок:

```
Accept-Language
```

### Пример сериализатора

```python
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'description')
```

Используются обычные поля (`title`, `description`). DRF автоматически вернёт перевод для выбранного языка.

### Пример запроса

```
GET /api/projects/
Accept-Language: en
```

Ответ API будет на английском.

---

## Workflow обновления переводов

Если добавлены новые строки с `_()`, необходимо обновить файлы переводов.

### 1. Сбор строк

```bash
docker compose exec web python backend/manage.py makemessages -a
```

### 2. Добавление переводов

Файлы переводов находятся в:

```
backend/locale/<lang>/LC_MESSAGES/django.po
```

Пример:

```
msgid "Название"
msgstr "Title"
```

⚠️ Если есть строка `#, fuzzy`, её нужно удалить — иначе перевод не применится.

### 3. Компиляция переводов

```bash
docker compose exec web python backend/manage.py compilemessages
```

---

## Важные примечания

* В репозиторий должны коммититься **оба файла**: `.po` и `.mo`
* URL автоматически получают языковой префикс:

```
/en/admin/
/ru/admin/
/sr-latn/admin/
/sr-cyrl/admin/
```

* Docker уже содержит `gettext`, поэтому на Windows ничего дополнительно устанавливать не нужно.

---

## Чек‑лист перед коммитом

* Все пользовательские строки обёрнуты в `_()`
* Для моделей с текстовыми полями создан `translation.py`
* В коде нет `*_en`, `*_ru` и других языковых полей
* Обновлены `.po` файлы
* Скомпилированы `.mo` файлы
* Проверен заголовок `Accept-Language` в API

  
## ✅ Проверка качества и форматирования кода

Форматирование кода:

```bash
docker  compose  run  --rm  -it  web  ruff  format
```

Запуск всех проверок и тестов так же, как при production-деплое:

```bash
docker  compose  run  --rm  -it  web  bash  ./docker/django/ci.sh
```
Команда для исправления ошибок:
```bash
docker compose exec web ruff check . --fix
```

## 🔄 Команды обслуживания

Пересборка контейнера (если изменились зависимости или возникли проблемы):

```bash
docker  compose  build  web
docker  compose  up  -d
```

Очистка проекта (удаляет volumes, включая базу данных):

```bash
docker  compose  down  -v
```