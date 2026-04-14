
# Проект "Ambasada za urbanizam"
Backend на Django DRF для веб-сайта.

## 🛠️ Локальная разработка с Docker

### Настройка окружения:

```shell
cp  .env.example  .env
```

### Запуск сервисов.

*Если локальных `docker images` нет — они будут загружены из DockerHub или собраны автоматически.*
```shell
docker  compose  up  -d
```

### 3. Применить миграции базы данных и создать суперпользователя:

```shell
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

### Поддержка многоязычности

При добавлении нового функционала необходимо учитывать поддержку многоязычности.
* Используйте `gettext_lazy` для строк, которые должны поддерживать перевод:

```python
from django.utils.translation import gettext_lazy as _
```

* Язык определяется через HTTP-заголовок `Accept-Language`.
* Руководство по мультиязычности - https://disk.yandex.ru/i/2c5tOXhtRHoKUQ
  
## ✅ Проверка качества и форматирования кода

Форматирование кода:

```shell
docker  compose  run  --rm  -it  web  ruff  format
```

Запуск всех проверок и тестов так же, как при production-деплое:

```shell
docker  compose  run  --rm  -it  web  bash  ./docker/django/ci.sh
```

## 🔄 Команды обслуживания

Пересборка контейнера (если изменились зависимости или возникли проблемы):

```shell
docker  compose  build  web
docker  compose  up  -d
```

Очистка проекта (удаляет volumes, включая базу данных):

```shell
docker  compose  down  -v
```