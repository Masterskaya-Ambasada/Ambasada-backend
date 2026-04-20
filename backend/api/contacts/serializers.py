from contacts.models import ContactRequest
from rest_framework import serializers


class ContactRequestSerializer(serializers.ModelSerializer):
    """Сериалайзер для формы обратной связи со встроенным антиспамом."""

    contact_preference = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ContactRequest
        fields = ['name', 'email', 'message', 'reason', 'contact_preference']
