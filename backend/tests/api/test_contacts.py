import pytest
from django.utils.translation import gettext as _
from rest_framework import status

from contacts.models import ContactPageContent, ContactRequest

pytestmark = pytest.mark.django_db


class TestContactViewPost:
    """Тесты POST"""

    def test_create_contact_request_success(
        self,
        api_client,
        contact_url,
        contact_payload,
    ):
        """Успешное создание обращения."""
        response = api_client.post(
            contact_url,
            contact_payload,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['detail'] == _('Получено')

        assert ContactRequest.objects.count() == 1

        contact = ContactRequest.objects.first()

        for key, value in contact_payload.items():
            if hasattr(contact, key):
                assert getattr(contact, key) == value

    @pytest.mark.parametrize(
        'field',
        ['name', 'email', 'message', 'reason'],
    )
    def test_required_fields(
        self,
        api_client,
        contact_url,
        contact_payload,
        field,
    ):
        """Проверка обязательных полей."""
        payload = contact_payload.copy()
        payload.pop(field)

        response = api_client.post(
            contact_url,
            payload,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert field in response.data

    def test_honeypot_field_blocks_creation(
        self,
        api_client,
        contact_url,
        contact_payload,
    ):
        """
        Если заполнено honeypot-поле,
        объект не создаётся.
        """
        payload = contact_payload.copy()
        payload['contact_preference'] = 'spam-bot'

        response = api_client.post(
            contact_url,
            payload,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['detail'] == _('Получено')

        assert ContactRequest.objects.count() == 0


class TestContactViewGet:
    """Тесты GET"""

    def test_get_active_donation_text(
        self,
        api_client,
        contact_url,
    ):
        """Возвращается активный donation_text."""
        ContactPageContent.objects.create(
            donation_text='Поддержите проект',
            is_active=True,
        )

        response = api_client.get(contact_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['donation_text'] == 'Поддержите проект'

    def test_get_empty_string_when_no_content(
        self,
        api_client,
        contact_url,
    ):
        """Если активного блока нет."""
        response = api_client.get(contact_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['donation_text'] == ''


class TestContactPageContentModel:
    """Тесты модели ContactPageContent."""

    def test_only_one_active_object_exists(self):
        """
        При создании нового активного блока
        предыдущий автоматически деактивируется.
        """
        first = ContactPageContent(
            donation_text='Первый блок',
            is_active=True,
        )
        first.save()

        second = ContactPageContent(
            donation_text='Второй блок',
            is_active=True,
        )
        second.save()

        first.refresh_from_db()
        second.refresh_from_db()

        assert first.is_active is False
        assert second.is_active is True