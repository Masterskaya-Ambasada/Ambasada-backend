from about.models import AboutPage, AboutParagraph, GalleryImage, Value
from api.users.serializers import TeamMemberSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AboutParagraphSerializer(serializers.ModelSerializer):
    """Сериализация параграфов страницы."""

    class Meta:
        model = AboutParagraph
        fields = ['first_sentence', 'main_text']


class ValueSerializer(serializers.ModelSerializer):
    """Сериализация ценностей."""

    class Meta:
        model = Value
        fields = ['id', 'title', 'text']


class GalleryImageSerializer(serializers.ModelSerializer):
    """Сериализация изображений галереи."""

    url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = GalleryImage
        fields = ['id', 'url', 'alt']


class AboutPageSerializer(serializers.ModelSerializer):
    """Сериализация страницы 'О сообществе' с вложенной структурой согласно ТЗ."""

    image_left = serializers.ImageField(read_only=True)
    image_right = serializers.ImageField(read_only=True)

    class Meta:
        model = AboutPage
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')

        values = self.context.get('values') or Value.objects.all()
        images = self.context.get('images') or GalleryImage.objects.all()
        members = self.context.get('members') or User.objects.public()

        image_left_url = (
            self.fields['image_left'].to_representation(instance.image_left) if instance.image_left else None
        )
        image_right_url = (
            self.fields['image_right'].to_representation(instance.image_right) if instance.image_right else None
        )

        return {
            'hero': {
                'title': instance.hero_title,
                'description': instance.hero_description,
                'image_left': image_left_url,
                'image_right': image_right_url,
            },
            'about_section': {
                'title': instance.about_title,
                'paragraphs': AboutParagraphSerializer(
                    instance.paragraphs.all(), many=True, context={'request': request}
                ).data,
                'action_button': {
                    'text': instance.button_label,
                    'link': instance.button_link,
                },
            },
            'values': {
                'title': instance.values_title,
                'items': ValueSerializer(values, many=True, context={'request': request}).data,
            },
            'team': {
                'title': instance.team_title,
                'members': TeamMemberSerializer(members, many=True, context={'request': request}).data,
                'action_button': {
                    'label': instance.team_button_label,
                    'link': instance.team_button_link,
                },
            },
            'gallery_carousel': {
                'title': instance.gallery_title,
                'images': GalleryImageSerializer(images, many=True, context={'request': request}).data,
            },
        }
