import pytest
from django.core.cache import cache
from django.urls import reverse
from home.models import HomePageProject
from rest_framework import status


def get_available_languages(model_instance):
    """Динамически находит все языковые коды, настроенные в полях тестовой модели."""
    languages = set()
    for field in model_instance._meta.fields:
        if field.name.startswith('title_'):
            lang = field.name.split('title_')[1]
            languages.add(lang)
    return list(languages)


@pytest.mark.django_db
def test_home_endpoint_returns_empty_config_when_no_config(api_client):
    """Проверяет fallback-ответ главной страницы без настроенного контента."""
    cache.clear()
    url = reverse('api:home')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['hero']['title'] == ''
    assert response.data['hero']['subtitle'] == ''


@pytest.mark.django_db
def test_home_endpoint_all_configured_languages_and_structure(
    api_client,
    home_page_content,
    published_project,
    second_published_project,
    team_members,
):
    """Проверяет структуру главной страницы для всех настроенных языков."""
    for member in team_members:
        member.is_public = True
        member.save()

    languages = get_available_languages(home_page_content)
    assert len(languages) > 0, 'В фикстуре модели должен быть настроен хотя бы один язык'

    url = reverse('api:home')

    for lang_code in languages:
        response = api_client.get(url, {'lang': lang_code})
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        assert all(key in data for key in ['hero', 'about_preview', 'team_preview', 'projects_preview'])

        translatable_fields = [
            ('hero', 'title'),
            ('hero', 'subtitle'),
            ('about_preview', 'title'),
            ('about_preview', 'text'),
        ]

        for section, field in translatable_fields:
            value = data[section][field]
            string_value = str(value)
            assert len(string_value) > 0, f'Поле {section}.{field} не должно быть пустым'

        assert 'about.webp' in data['about_preview']['image']
        assert data['hero']['action_button']['link'] == home_page_content.hero_button_link

        items = data['projects_preview']['items']
        assert len(items) == 2

        assert items[0]['id'] == published_project.slug
        assert items[0]['isFirst'] is True
        assert items[1]['id'] == second_published_project.slug
        assert items[1]['isFirst'] is False


@pytest.mark.django_db
def test_home_endpoint_returns_projects_in_admin_configured_order(
    api_client,
    home_page_content,
    published_project,
    second_published_project,
):
    """Проверяет, что главная отдает проекты в порядке, заданном в админке."""
    HomePageProject.objects.create(home_page=home_page_content, project=published_project, order=20)
    HomePageProject.objects.create(home_page=home_page_content, project=second_published_project, order=10)

    url = reverse('api:home')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    items = response.data['projects_preview']['items']
    assert [item['id'] for item in items] == [second_published_project.slug, published_project.slug]
    assert items[0]['isFirst'] is True
    assert items[1]['isFirst'] is False
