import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestTeamApi:
    """Тесты для TeamListView (Список команды)."""

    URL = reverse('api:team_list')

    def test_get_team_list_structure(self, api_client, user_factory):
        """Проверка маппинга полей и пагинации."""
        first_name = 'Дмитрий'
        last_name = 'Кодров'
        user_factory(
            email='member@test.com', 
            first_name=first_name, 
            last_name=last_name,
            is_public=True,
            is_active=True
        )
        
        response = api_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK

        results = response.data['results']
        member = results[0]
        
        assert member['name'] == f'{first_name} {last_name}'
        assert 'position' in member
        assert 'photo' in member
        assert 'email' not in member
        assert 'role' not in member

    def test_team_list_ordering(self, api_client, user_factory):
        """Проверка сортировки по id."""
        u1 = user_factory(email='1@test.com', is_public=True, is_active=True)
        u2 = user_factory(email='2@test.com', is_public=True, is_active=True)

        response = api_client.get(self.URL)
        results = response.data['results']
        
        assert results[0]['id'] < results[1]['id']
        assert results[0]['name'] == u1.full_name

    def test_team_list_filters_private_and_inactive_users(self, api_client, user_factory):
        """Проверка, что API скрывает непубличных и неактивных пользователей."""
        user_factory(
            email='visible@test.com', 
            is_public=True, 
            is_active=True
        )
        user_factory(
            email='hidden@test.com', 
            is_public=False, 
            is_active=True
        )
        user_factory(
            email='inactive@test.com', 
            is_public=True, 
            is_active=False
        )

        response = api_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        
        results = response.data['results']
        
        assert len(results) == 1
        assert results[0]['name'] == 'visible@test.com' or 'visible' in results[0]['name'].lower()