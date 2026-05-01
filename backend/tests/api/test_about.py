"""Тесты API страницы 'О нас'."""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_about_page_success(api_client, about_page, values, gallery_images):
    """
    Проверяет успешное получение страницы 'О нас'.

    Ожидается:
    - статус 200
    - наличие всех основных секций
    """
    url = reverse('api:about')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert 'hero' in data
    assert 'about_section' in data
    assert 'values' in data
    assert 'team' in data
    assert 'gallery_carousel' in data


@pytest.mark.django_db
def test_about_page_not_found(api_client):
    """
    Проверяет поведение API, когда страница 'О нас' отсутствует.

    Ожидается:
    - статус 404
    - корректное сообщение об ошибке
    """
    url = reverse('api:about')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] is not None


@pytest.mark.django_db
def test_about_team_structure(api_client, about_page, team_members):
    """
    Проверяет корректность структуры блока команды.

    Ожидается:
    - наличие title
    - список участников
    - наличие action_button
    """
    url = reverse('api:about')
    response = api_client.get(url)

    data = response.json()['team']

    assert 'title' in data
    assert 'members' in data
    assert isinstance(data['members'], list)
    assert 'action_button' in data


@pytest.mark.django_db
def test_about_values_structure(api_client, about_page, values):
    """
    Проверяет корректность структуры блока ценностей.

    Ожидается:
    - наличие title
    - список items
    """
    url = reverse('api:about')
    response = api_client.get(url)

    data = response.json()['values']

    assert 'title' in data
    assert 'items' in data
    assert isinstance(data['items'], list)


@pytest.mark.django_db
def test_about_gallery_structure(api_client, about_page, gallery_images):
    """
    Проверяет корректность структуры галереи.

    Ожидается:
    - наличие title
    - список изображений
    """
    url = reverse('api:about')
    response = api_client.get(url)

    data = response.json()['gallery_carousel']

    assert 'title' in data
    assert 'images' in data
    assert isinstance(data['images'], list)