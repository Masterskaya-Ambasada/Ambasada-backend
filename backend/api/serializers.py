from rest_framework import serializers
from .models import SiteConfig, Language, Social


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["code", "label"]


class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = ["type", "url"]


class SiteConfigSerializer(serializers.ModelSerializer):
    languages = LanguageSerializer(many=True)
    socials = SocialSerializer(many=True)

    class Meta:
        model = SiteConfig
        fields = [
            "site_name",
            "seo_description",
            "languages",
            "socials",
            "copyright",
        ]
