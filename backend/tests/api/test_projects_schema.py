import pytest
import yaml
from django.urls import reverse


def _load_openapi_schema(api_client):
    """Загружает и парсит OpenAPI-схему проекта."""
    response = api_client.get(reverse('api:schema'))
    assert response.status_code == 200
    return yaml.safe_load(response.content)


@pytest.mark.django_db
def test_projects_schema_documents_filters_and_language_header(api_client):
    """Проверяет, что схема списка проектов описывает фильтры и заголовок языка."""
    schema = _load_openapi_schema(api_client)
    project_list_operation = schema['paths']['/api/v1/projects/']['get']
    parameter_names = {parameter['name'] for parameter in project_list_operation['parameters']}
    assert project_list_operation['summary'] == 'Список проектов'
    assert 'Accept-Language' in parameter_names
    assert 'project_type' in parameter_names
    assert 'tag' in parameter_names
    assert 'search' in parameter_names


@pytest.mark.django_db
def test_projects_schema_documents_action_button_and_pagination(api_client):
    """Проверяет, что схема списка проектов описывает action_button и пагинацию."""
    schema = _load_openapi_schema(api_client)
    action_button_schema = schema['components']['schemas']['ProjectActionButton']
    paginated_schema = schema['components']['schemas']['PaginatedProjectCardList']
    assert set(action_button_schema['properties']) == {'label', 'link'}
    assert set(paginated_schema['properties']) == {'items', 'pagination'}
    assert set(paginated_schema['properties']['pagination']['properties']) == {
        'totalItems',
        'offset',
        'limit',
        'isNext',
    }


@pytest.mark.django_db
def test_projects_schema_documents_meta_endpoints(api_client):
    """Проверяет, что схема описывает endpoints тегов, типов и деталки проекта."""
    schema = _load_openapi_schema(api_client)
    project_tags_operation = schema['paths']['/api/v1/projects/tags/']['get']
    project_types_operation = schema['paths']['/api/v1/projects/categories/']['get']
    project_detail_operation = schema['paths']['/api/v1/projects/{project_slug}/']['get']
    assert project_tags_operation['summary'] == 'Список тегов проектов'
    assert project_types_operation['summary'] == 'Список типов проектов'
    assert project_detail_operation['summary'] == 'Детальная страница проекта'
    assert any(parameter['name'] == 'project_slug' for parameter in project_detail_operation['parameters'])
