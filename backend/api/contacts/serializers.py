from contacts.models import ContactPageContent, ContactRequest
from rest_framework import serializers


class ContactRequestSerializer(serializers.ModelSerializer):
    """Сериалайзер для формы обратной связи со встроенным антиспамом."""

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

    def create(self, validated_data):
        validated_data.pop('contact_preference', None)
        return super().create(validated_data)


class ContactPageContentSerializer(serializers.ModelSerializer):
    """Сериалайзер для редактируемой ссылки на пожертвования."""

    class Meta:
        model = ContactPageContent
        fields = ('donation_text',)
