# Тесты проекта

## Что покрыто

- API тесты: `backend/tests/api/`
- Тесты моделей и валидаторов `projects`: `backend/tests/projects/`
- Общие фикстуры: `backend/tests/conftest.py`
- Тесты `site_config`: `backend/tests/site_config/`

## Site Config (InitView)

Покрытие тестами эндпоинта `/api/init/`:

- Успешный сценарий (возвращает данные конфигурации)
- Отсутствие конфигурации (возвращает 404 и код `NOT_FOUND`)
- Корректная структура ответа
- Работа с пустыми связями (languages, socials)
- Работа со связанными объектами (languages, socials)

Тесты используют кэширование, поэтому перед каждым тестом кэш очищается.
В тестовой среде используется `LocMemCache` (см. настройки в `settings.py`).

## Базовый запуск

Для API-тестов нужны `db` и `redis`.

```bash
docker compose up -d db redis
docker compose run --rm web pytest
```

## Точечный запуск

Только тесты `projects`:

```bash
docker compose run --rm web pytest backend/tests/projects
```

Один файл:

```bash
docker compose run --rm web pytest backend/tests/api/test_projects_list.py
```

Один тест:

```bash
docker compose run --rm web pytest backend/tests/api/test_projects_list.py::test_projects_list_returns_only_published_projects
```

## Какие могут быть проблемы

### `Redis ConnectionError` в API-тестах

Причина: сервис `redis` не поднят.

Решение:

```bash
docker compose up -d redis
```
