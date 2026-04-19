import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_projects_tags_returns_only_tags_of_published_projects(
    api_client,
    published_project,
    second_published_project,
    unpublished_project,
):
    """Проверяет, что ручка тегов возвращает только теги опубликованных проектов."""
    url = reverse('api:projects-tags')
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data == ['Social', 'Urban']


@pytest.mark.django_db
def test_projects_types_returns_only_types_of_published_projects(
    api_client,
    published_project,
    second_published_project,
    unpublished_project,
):
    """Проверяет, что ручка типов проектов возвращает только типы, связанные с опубликованными проектами."""
    url = reverse('api:projects-types')
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'types': [
            {'id': 'architecture', 'label': 'Architecture'},
            {'id': 'research', 'label': 'Research'},
        ]
    }
