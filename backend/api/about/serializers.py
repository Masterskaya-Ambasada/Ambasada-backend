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
    """Сериализация страницы 'О сообществе'."""

    class Meta:
        model = AboutPage
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')

        values = self.context.get('values', instance.values.all())
        images = self.context.get('images', instance.gallery_images.all())
        members = self.context.get('members', User.objects.public())

        return {
            'hero': {
                'title': instance.hero_title,
                'description': instance.hero_description,
                # Убрали image_left и image_right отсюда
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
            'contacts': {
                'email': instance.email,
                'link': instance.contact_link,
            },
        }
