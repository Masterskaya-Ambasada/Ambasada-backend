from rest_framework import serializers
from site_config.models import Language, SiteConfig, Social


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['code', 'label']


class SocialSerializer(serializers.ModelSerializer):
    social_type = serializers.CharField(source='get_social_type_display', read_only=True)

    class Meta:
        model = Social
        fields = ['social_type', 'url']


class SiteConfigSerializer(serializers.ModelSerializer):
    languages = LanguageSerializer(many=True, read_only=True)
    socials = SocialSerializer(many=True, read_only=True)

    class Meta:
        model = SiteConfig

        fields = [
            'site_name',
            'seo_description',
            'languages',
            'socials',
            'copyright',
        ]


class ErrorSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    code = serializers.CharField()
    message = serializers.CharField()
