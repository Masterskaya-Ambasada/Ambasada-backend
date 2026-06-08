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

    def validate(self, attrs):
        """Проверка хонейпота перед сохранением."""
        honeypot = attrs.get('contact_preference')

        if honeypot is not None and honeypot.strip() != '':
            attrs['is_spam'] = True
        else:
            attrs['is_spam'] = False

        attrs.pop('contact_preference', None)
        return attrs

    def create(self, validated_data):
        is_spam = validated_data.pop('is_spam', False)

        if is_spam:
            return ContactRequest(**validated_data)

        return super().create(validated_data)


class ContactPageContentSerializer(serializers.ModelSerializer):
    """Сериалайзер для редактируемой ссылки на пожертвования."""

    class Meta:
        model = ContactPageContent
        fields = ('donation_text',)
