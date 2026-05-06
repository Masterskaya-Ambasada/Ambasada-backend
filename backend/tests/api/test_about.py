"""Тесты API страницы 'О нас'."""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_about_page_success(api_client, about_full_setup):
    """
    Проверяет успешное получение страницы 'О нас'.

    Ожидается:
    - статус 200
    - наличие всех секций
    - корректные данные из БД
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
    assert 'detail' in response.json()


@pytest.mark.django_db
def test_about_team_structure(api_client, about_full_setup):
    """
    Проверяет структуру и данные блока команды.

    Ожидается:
    - title присутствует
    - members не пустой
    - данные совпадают с БД
    """
    url = reverse('api:about')
    response = api_client.get(url)

    data = response.json()['team']

    assert 'title' in data
    assert 'members' in data
    assert isinstance(data['members'], list)
    assert len(data['members']) == 2

    emails = [m['email'] for m in data['members']]
    assert 'user1@test.com' in emails
    assert 'user2@test.com' in emails

    assert 'action_button' in data


@pytest.mark.django_db
def test_about_values_structure(api_client, about_full_setup):
    """
    Проверяет структуру и данные блока ценностей.

    Ожидается:
    - title присутствует
    - items содержит реальные данные
    """
    url = reverse('api:about')
    response = api_client.get(url)

    data = response.json()['values']

    assert 'title' in data
    assert 'items' in data
    assert isinstance(data['items'], list)
    assert len(data['items']) == 2

    titles = [v['title'] for v in data['items']]
    assert 'Value 1' in titles
    assert 'Value 2' in titles


@pytest.mark.django_db
def test_about_gallery_structure(api_client, about_full_setup):
    """
    Проверяет структуру и данные галереи.

    Ожидается:
    - title присутствует
    - изображения реально возвращаются из БД
    """
    url = reverse('api:about')
    response = api_client.get(url)

    data = response.json()['gallery_carousel']

    assert 'title' in data
    assert 'images' in data
    assert isinstance(data['images'], list)
    assert len(data['images']) == 2

    alts = [img['alt'] for img in data['images']]
    assert 'Image 1' in alts
    assert 'Image 2' in alts