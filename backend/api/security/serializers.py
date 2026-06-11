from rest_framework import serializers
from security.models import SecurityPolicy


class SecurityPolicySerializer(serializers.ModelSerializer):
    """Сериализация политики конфиденциальности с явным указанием языка."""

    text = serializers.SerializerMethodField()

    class Meta:
        model = SecurityPolicy
        fields = ['text']

    def get_text(self, obj):
        suffix = self.context.get('lang_suffix', 'ru')
        return getattr(obj, f'text_{suffix}', '') or obj.text or ''
