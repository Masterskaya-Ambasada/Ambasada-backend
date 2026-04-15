"""Сериализаторы для API."""

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
    """Сериализация страницы 'О сообществе' с вложенной структурой согласно ТЗ."""

    def to_representation(self, instance):
        ctx = self.context
        values = ctx.get('values', Value.objects.all())
        members = ctx.get('members', TeamMember.objects.all())
        images = ctx.get('images', GalleryImage.objects.all())

        return {
            'hero': {
                'title': instance.hero_title,
                'description': instance.hero_description,
                'image_left': instance.image_left.url if instance.image_left else None,
                'image_right': instance.image_right.url if instance.image_right else None,
            },
            'about_section': {
                'title': instance.about_title,
                'paragraphs': [instance.paragraph_1, instance.paragraph_2],
                'action_button': {
                    'label': instance.button_label,
                    'link': instance.button_link,
                },
            },
            'values': {
                'title': instance.values_title,
                'items': ValueSerializer(values, many=True).data,
            },
            'team': {
                'title': instance.team_title,
                'members': TeamMemberSerializer(members, many=True).data,
                'action_button': {
                    'label': instance.team_button_label,
                    'link': instance.team_button_link,
                },
            },
            'gallery_carousel': {
                'title': instance.gallery_title,
                'images': [{'id': f'img_{img.id}', 'url': img.image.url, 'alt': img.alt} for img in images],
            },
        }

    class Meta:
        model = AboutPage
        fields = []
