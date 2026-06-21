import random

from contacts.models import ContactPageContent, ContactRequest
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

        return super().create(validated_data)


class ContactPageContentSerializer(serializers.ModelSerializer):
    """Сериализатор контактных данных организации."""

    class Meta:
        model = ContactPageContent
        fields = (
            'phone',
            'address',
        )
