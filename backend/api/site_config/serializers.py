from contacts.models import ContactSocialLink
from rest_framework import serializers
from site_config.models import Language, SiteConfig


class LanguageSerializer(serializers.ModelSerializer):
    """Сериализатор для модели языков."""

    label = serializers.CharField(read_only=True)

    class Meta:
        model = Language
        fields = ['code', 'label']


class SiteConfigSocialSerializer(serializers.ModelSerializer):
    """Сериализатор для модели социальных сетей."""

    social_type = serializers.CharField(source='get_social_type_display', read_only=True)

    class Meta:
        model = ContactSocialLink
        fields = ['social_type', 'url']


class SiteConfigSerializer(serializers.ModelSerializer):
    """Сериализатор для конфигурации сайта."""

    languages = LanguageSerializer(many=True, read_only=True)
    socials = SiteConfigSocialSerializer(many=True, read_only=True)

    class Meta:
        model = SiteConfig
        fields = [
            'site_name',
            'seo_description',
            'privacy_policy',
            'cookie_message',
            'cookie_button_text',
            'languages',
            'socials',
            'copyright',
        ]


class ErrorSerializer(serializers.Serializer):
    """Сериализатор для стандартных ответов об ошибках."""

    status = serializers.IntegerField()
    code = serializers.CharField()
    message = serializers.CharField()
