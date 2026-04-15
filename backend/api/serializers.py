"""
Сериализаторы для API.

Anti-spam techniques (for public forms):

Honeypot field — hidden via CSS (display: none), NOT type="hidden".
Bots fill all visible fields automatically; humans never touch it.
If the field arrives non-empty — silently reject the submission.
"""

from rest_framework import serializers

from .models import AboutPage, GalleryImage, TeamMember, Value


class ValueSerializer(serializers.ModelSerializer):
    """Сериализация ценностей."""

    class Meta:
        model = Value
        fields = ['id', 'title', 'text']


class TeamMemberSerializer(serializers.ModelSerializer):
    """Сериализация членов команды."""

    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'photo']


class GalleryImageSerializer(serializers.ModelSerializer):
    """Сериализация изображений галереи."""

    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'alt']


class AboutPageSerializer(serializers.ModelSerializer):
    """Сериализация основной страницы 'О сообществе'."""

    def to_representation(self, instance):
        return {
            "hero": {
                "title": instance.hero_title,
                "description": instance.hero_description,
                "image_left": (
                    instance.image_left.url if instance.image_left else None
                ),
                "image_right": (
                    instance.image_right.url if instance.image_right else None
                ),
            },
            "about_section": {
                "title": instance.about_title,
                "paragraphs": [
                    instance.paragraph_1,
                    instance.paragraph_2,
                ],
                "action_button": {
                    "label": instance.button_label,
                    "link": instance.button_link,
                },
            },
            "values": {
                "title": instance.values_title,
                "items": ValueSerializer(
                    Value.objects.all(), many=True
                ).data,
            },
            "team": {
                "title": instance.team_title,
                "members": TeamMemberSerializer(
                    TeamMember.objects.all(), many=True
                ).data,
                "action_button": {
                    "label": instance.team_button_label,
                    "link": instance.team_button_link,
                },
            },
            "gallery_carousel": {
                "title": instance.gallery_title,
                "images": [
                    {
                        "id": f"img_{img.id}",
                        "url": img.image.url,
                        "alt": img.alt,
                    }
                    for img in GalleryImage.objects.all()
                ],
            },
        }

    class Meta:
        model = AboutPage
        fields = []