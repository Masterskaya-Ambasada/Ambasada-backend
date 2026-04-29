# Тесты проекта

## Что покрыто

- API тесты: `backend/tests/api/`
- Тесты моделей и валидаторов `projects`: `backend/tests/projects/`
- Тесты моделей, менеджеров, QuerySet, пути сохранения фото `users`: `backend/tests/users/`
- Общие фикстуры: `backend/tests/conftest.py`

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
