from about.models import AboutPage, AboutParagraph, GalleryImage, Value
from api.users.serializers import TeamMemberSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from site_config.cache import get_site_config_cached

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
    """Сериализация страницы 'О сообществе' под строгий JSON-контракт."""

    class Meta:
        model = AboutPage
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')

        lang = request.query_params.get('lang', 'ru') if request else 'ru'
        cached_config = get_site_config_cached(language=lang) or {}

        values = self.context.get('values', instance.values.all())[:4]
        images = self.context.get('images', instance.gallery_images.all())
        members = self.context.get('members', User.objects.public())

        return {
            'hero': {
                'title': instance.hero_title,
                'description': instance.hero_description,
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
                'title': cached_config.get('about_team_title') or cached_config.get('team_title') or 'Наша команда',
                'members': TeamMemberSerializer(members, many=True, context={'request': request}).data,
                'action_button': {
                    'label': cached_config.get('about_team_button_label') or 'Присоединиться',
                    'link': cached_config.get('team_button_link') or '/contacts',
                },
            },
            'gallery_carousel': {
                'title': instance.gallery_title,
                'images': GalleryImageSerializer(images, many=True, context={'request': request}).data,
            },
        }
