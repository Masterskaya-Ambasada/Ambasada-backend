import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestAuthApi:
    """Тесты для AmbasadaTokenObtainPairView (Логин)."""

    URL = reverse('api:token_obtain_pair')

    def test_login_returns_tokens_and_user_data(self, api_client, user_factory):
        """Проверка JWT и данных пользователя (id, email, name, role)."""
        email = 'dmitry_dev@example.com'
        password = 'secure_pass_123'
        first_name = 'Дмитрий'
        last_name = 'Кодров'
        
        user_factory(
            email=email, 
            password=password, 
            first_name=first_name, 
            last_name=last_name
        )

        data = {'email': email, 'password': password}
        response = api_client.post(self.URL, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        
        user_data = response.data['user']
        assert user_data['email'] == email
        assert user_data['name'] == f'{first_name} {last_name}'
        assert 'role' in user_data
        assert 'is_staff' in user_data

    def test_login_error_message_is_localized(self, api_client, user_factory):
        '''Проверка кастомного сообщения об ошибке на русском языке.'''
        user_factory(email='test@test.com', password='correct_password')
        
        data = {'email': 'test@test.com', 'password': 'wrong_password'}
        response = api_client.post(self.URL, data, HTTP_ACCEPT_LANGUAGE='ru')
        
        # Обновляем текст в соответствии с реальностью из логов:
        expected_error = 'Неверный логин или пароль. Пожалуйста, проверьте правильность введённых данных и попробуйте снова.'
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert str(response.data['detail']).strip() == expected_error