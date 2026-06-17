import random

from contacts.models import ContactPageContent, ContactRequest
from contacts.tasks import send_contact_request_notification_task
from django.db import transaction
from django.utils.translation import get_language_from_request
from rest_framework import serializers


class ContactRequestSerializer(serializers.ModelSerializer):
    """Сериализатор для формы обратной связи со встроенным антиспамом (Honeypot)."""

    contact_preference = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    class Meta:
        model = ContactRequest
        fields = [
            'name',
            'email',
            'message',
            'reason',
            'contact_preference',
        ]

    def validate(self, attrs):
        """Проверяет хонейпот и маркирует внутреннее состояние."""
        honeypot = attrs.pop('contact_preference', None)

        if honeypot and honeypot.strip():
            attrs['_is_spam'] = True
        else:
            attrs['_is_spam'] = False

        return attrs

    def create(self, validated_data):
        """Создает запись в БД только для людей. Для ботов эмулирует успешный ответ."""
        is_spam = validated_data.pop('_is_spam', False)

        if is_spam:
            fake_instance = ContactRequest(**validated_data)
            fake_instance.pk = random.randint(10000, 99999)

            return fake_instance

        contact_request = super().create(validated_data)
        transaction.on_commit(lambda: send_contact_request_notification_task.delay(contact_request.pk))

        return contact_request


class ContactPageContentSerializer(serializers.ModelSerializer):
    """Сериализатор для страницы контактов с безопасной локализацией."""

    donation_text = serializers.SerializerMethodField()

    class Meta:
        model = ContactPageContent
        fields = ('donation_text',)

    def get_donation_text(self, obj):
        suffix = self.context.get('lang_suffix')

        if not suffix:
            request = self.context.get('request')
            lang = 'ru'
            if request:
                lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
            suffix = lang.lower().replace('-', '_')

        return getattr(obj, f'donation_text_{suffix}', '') or obj.donation_text or ''
