from unittest.mock import patch

import pytest
from contacts.models import ContactPageContent, ContactRequest
from contacts.tasks import send_contact_request_notification_task
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def contact_url():
    """Локальная фикстура для URL контактов, чтобы не зависеть от внешних conftest.py."""
    return reverse('api:contact-create')


class TestContactViewPost:
    """Тесты POST."""

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
        assert 'detail' in response.data
        assert response.data['detail']

        assert ContactRequest.objects.count() == 1

        contact = ContactRequest.objects.first()

        for key, value in contact_payload.items():
            if hasattr(contact, key):
                assert getattr(contact, key) == value
        assert contact.notification_status == ContactRequest.NotificationStatus.PENDING
        assert contact.notification_attempts == 0

    @patch('api.contacts.serializers.send_contact_request_notification_task.delay')
    def test_create_contact_request_schedules_notification(
        self,
        mock_delay,
        api_client,
        contact_url,
        contact_payload,
        django_capture_on_commit_callbacks,
    ):
        """После сохранения реальной заявки ставится задача email-уведомления."""
        with django_capture_on_commit_callbacks(execute=True):
            response = api_client.post(
                contact_url,
                contact_payload,
            )

        contact = ContactRequest.objects.get()

        assert response.status_code == status.HTTP_201_CREATED
        mock_delay.assert_called_once_with(contact.pk)

    @pytest.mark.parametrize(
        'field',
        ['name', 'email', 'message'],
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

    @patch('api.contacts.serializers.send_contact_request_notification_task.delay')
    def test_honeypot_field_blocks_creation(
        self,
        mock_delay,
        api_client,
        contact_url,
        contact_payload,
        django_capture_on_commit_callbacks,
    ):
        """
        Honeypot имитирует успешный ответ без создания объекта.

        Если поле заполнено, сервер возвращает 201 Created, но объект в базе данных НЕ создаёт.
        """
        payload = contact_payload.copy()
        payload['contact_preference'] = 'spam-bot'

        with django_capture_on_commit_callbacks(execute=True):
            response = api_client.post(
                contact_url,
                payload,
            )

        assert response.status_code == status.HTTP_201_CREATED
        assert ContactRequest.objects.count() == 0
        mock_delay.assert_not_called()

    @override_settings(
        DEFAULT_FROM_EMAIL='noreply@example.com',
        ADMIN_EMAIL='admin@example.com',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    )
    def test_contact_request_notification_task_sends_email(
        self,
        mailoutbox,
        contact_payload,
    ):
        """Таска отправляет письмо администратору по id сохранённой заявки."""
        contact = ContactRequest.objects.create(**contact_payload)

        send_contact_request_notification_task(contact.pk)

        assert len(mailoutbox) == 1
        email = mailoutbox[0]

        assert email.subject == f'Новая заявка №{contact.pk}'
        assert email.from_email == 'noreply@example.com'
        assert email.to == ['admin@example.com']
        assert contact.name in email.body
        assert contact.email in email.body
        assert contact.message in email.body

        contact.refresh_from_db()
        assert contact.notification_status == ContactRequest.NotificationStatus.SENT
        assert contact.notification_attempts == 1
        assert contact.notification_sent_at is not None
        assert contact.notification_error == ''

    @override_settings(
        DEFAULT_FROM_EMAIL='noreply@example.com',
        ADMIN_EMAIL='admin@example.com',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    )
    def test_contact_request_notification_task_uses_email_from_site_config(
        self,
        mailoutbox,
        contact_payload,
        default_site_config,
    ):
        """Таска использует адрес получателя из настроек сайта, если он задан в админке."""
        default_site_config.contact_notification_email = 'manager@example.com'
        default_site_config.save(update_fields=['contact_notification_email'])

        contact = ContactRequest.objects.create(**contact_payload)

        send_contact_request_notification_task(contact.pk)

        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == ['manager@example.com']

    def test_contact_request_notification_task_ignores_missing_request(self, mailoutbox):
        """Таска не падает, если заявка была удалена до отправки письма."""
        send_contact_request_notification_task(999999)

        assert mailoutbox == []


class TestContactViewGet:
    """Тесты GET."""

    def test_get_active_contact_page_content(
        self,
        api_client,
        contact_url,
    ):
        """Возвращается активные контактные данные."""
        ContactPageContent.objects.create(
            phone='+381111234567',
            address='Belgrade, Serbia',
            is_active=True,
        )

        response = api_client.get(contact_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone'] == '+381111234567'
        assert response.data['address'] == 'Belgrade, Serbia'

    def test_get_empty_string_when_no_content(
        self,
        api_client,
        contact_url,
    ):
        """Если активного блока нет."""
        response = api_client.get(contact_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone'] == ''
        assert response.data['address'] == ''


class TestContactPageContentModel:
    """Тесты модели ContactPageContent."""

    def test_only_one_active_object_exists(self):
        """
        Новый активный блок деактивирует предыдущий.

        Так в базе остаётся только один активный объект контента контактов.
        """
        first = ContactPageContent.objects.create(
            phone='+111111111',
            address='First address',
            is_active=True,
        )

        second = ContactPageContent.objects.create(
            phone='+222222222',
            address='Second address',
            is_active=True,
        )

        first.refresh_from_db()
        second.refresh_from_db()

        assert first.is_active is False
        assert second.is_active is True
