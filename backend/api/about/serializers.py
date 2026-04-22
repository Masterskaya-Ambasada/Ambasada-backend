"""Сериализаторы для API."""

from about.models import AboutPage, GalleryImage, Value
from api.users.serializers import TeamMemberSerializer
from rest_framework import serializers
from users.models import User


class ValueSerializer(serializers.ModelSerializer):
    """Сериализация ценностей."""

    class Meta:
        model = Value
        fields = ['id', 'title', 'text']


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
        members = ctx.get('members', User.objects.public())
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
                'paragraphs': [
                    {
                        'first_sentence': p.first_sentence,
                        'main_text': p.main_text,
                    }
                    for p in instance.paragraphs.order_by('order')
                ],
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
                'images': [
                    {'id': f'img_{img.id}', 'url': img.image.url if img.image else None, 'alt': img.alt}
                    for img in images
                ],
            },
        }

    class Meta:
        model = AboutPage
        fields = []
