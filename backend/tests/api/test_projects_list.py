import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_projects_list_returns_only_published_projects(
    api_client,
    published_project,
    second_published_project,
    unpublished_project,
):
    """Проверяет, что список проектов возвращает только опубликованные проекты."""
    url = reverse('api:projects-list')
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    returned_ids = [item['id'] for item in data['items']]
    assert published_project.slug in returned_ids
    assert second_published_project.slug in returned_ids
    assert unpublished_project.slug not in returned_ids


@pytest.mark.django_db
def test_projects_list_filters_by_project_type(
    api_client,
    published_project,
    second_published_project,
):
    """Проверяет фильтрацию списка проектов по slug типа проекта."""
    url = reverse('api:projects-list')
    response = api_client.get(url, {'project_type': 'architecture'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['items']) == 1
    assert data['items'][0]['id'] == published_project.slug


@pytest.mark.django_db
def test_projects_list_filters_by_single_tag(
    api_client,
    published_project,
    second_published_project,
):
    """Проверяет фильтрацию списка проектов по одному тегу."""
    url = reverse('api:projects-list')
    response = api_client.get(url, {'tag': 'urban'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['items']) == 1
    assert data['items'][0]['id'] == published_project.slug


@pytest.mark.django_db
def test_projects_list_filters_by_multiple_tags(
    api_client,
    published_project,
    second_published_project,
):
    """Проверяет фильтрацию списка проектов по нескольким тегам, переданным в query params."""
    url = reverse('api:projects-list')
    response = api_client.get(url + '?tag=urban&tag=social')
    assert response.status_code == 200
    data = response.json()
    returned_ids = [item['id'] for item in data['items']]
    assert published_project.slug in returned_ids
    assert second_published_project.slug in returned_ids


@pytest.mark.django_db
def test_projects_list_filters_by_search_with_strip(
    api_client,
    published_project,
    second_published_project,
):
    """Проверяет, что поиск по названию работает корректно и учитывает обрезку пробелов по краям строки."""
    url = reverse('api:projects-list')
    response = api_client.get(url, {'search': '  Central  '})
    assert response.status_code == 200
    data = response.json()
    assert len(data['items']) == 1
    assert data['items'][0]['id'] == published_project.slug


@pytest.mark.django_db
def test_projects_list_returns_expected_card_fields(api_client, published_project):
    """Проверяет, что API списка проектов возвращает карточку проекта в ожидаемом формате."""
    url = reverse('api:projects-list')
    response = api_client.get(url)
    assert response.status_code == 200
    item = response.json()['items'][0]
    assert item['id'] == published_project.slug
    assert item['title'] == published_project.title
    assert item['description'] == published_project.description
    assert item['project_type'] == published_project.project_type.label
    assert item['tags'] == ['Social', 'Urban']
    assert item['year'] == str(published_project.year)
    assert item['image'] == published_project.cover_image


@pytest.mark.django_db
def test_projects_list_returns_custom_pagination_payload(
    api_client,
    published_project,
    second_published_project,
):
    """Проверяет, что список проектов возвращает кастомную структуру пагинации."""
    url = reverse('api:projects-list')
    response = api_client.get(url, {'limit': 1, 'offset': 0})
    assert response.status_code == 200
    data = response.json()
    assert 'items' in data
    assert 'pagination' in data
    assert data['pagination']['totalItems'] == 2
    assert data['pagination']['offset'] == 0
    assert data['pagination']['limit'] == 1
    assert data['pagination']['isNext'] is True
    assert len(data['items']) == 1
