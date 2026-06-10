from about.models import AboutPage, AboutParagraph, GalleryImage, Value
from api.users.serializers import TeamMemberSerializer
from django.contrib.auth import get_user_model
from django.utils.translation import get_language_from_request
from rest_framework import serializers
from site_config.cache import get_site_config_cached

User = get_user_model()


class AboutParagraphSerializer(serializers.ModelSerializer):
    """Сериализация параграфов страницы с явным указанием языка."""

    first_sentence = serializers.SerializerMethodField()
    main_text = serializers.SerializerMethodField()

    class Meta:
        model = AboutParagraph
        fields = ['first_sentence', 'main_text']

    def get_first_sentence(self, obj):
        suffix = self.context.get('lang_suffix', 'ru')
        return getattr(obj, f'first_sentence_{suffix}', '') or obj.first_sentence or ''

    def get_main_text(self, obj):
        suffix = self.context.get('lang_suffix', 'ru')
        return getattr(obj, f'main_text_{suffix}', '') or obj.main_text or ''


class ValueSerializer(serializers.ModelSerializer):
    """Сериализация ценностей с явным указанием языка."""

    title = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    class Meta:
        model = Value
        fields = ['id', 'title', 'text']

    def get_title(self, obj):
        suffix = self.context.get('lang_suffix', 'ru')
        return getattr(obj, f'title_{suffix}', '') or obj.title or ''

    def get_text(self, obj):
        suffix = self.context.get('lang_suffix', 'ru')
        return getattr(obj, f'text_{suffix}', '') or obj.text or ''


class GalleryImageSerializer(serializers.ModelSerializer):
    """Сериализация изображений галереи."""

    url = serializers.ImageField(source='image', read_only=True)
    alt = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ['id', 'url', 'alt']

    def get_alt(self, obj):
        suffix = self.context.get('lang_suffix', 'ru')
        return getattr(obj, f'alt_{suffix}', '') or obj.alt or ''


class AboutPageSerializer(serializers.ModelSerializer):
    """Сериализация страницы 'О сообществе' под строгий JSON-контракт."""

    class Meta:
        model = AboutPage
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')

        lang = 'ru'
        if request:
            lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        lang = lang.lower()

        lang_suffix = lang.replace('-', '_')
        child_context = {'request': request, 'lang_suffix': lang_suffix}

        cached_config = get_site_config_cached(language=lang) or {}

        values = self.context.get('values', list(instance.values.all()))[:4]
        images = self.context.get('images', instance.gallery_images.all())
        members = self.context.get('members', User.objects.public())

        return {
            'about_section': {
                'title': getattr(instance, f'about_title_{lang_suffix}', '') or instance.about_title or '',
                'paragraphs': AboutParagraphSerializer(
                    instance.paragraphs.all(), many=True, context=child_context
                ).data,
                'action_button': {
                    'text': getattr(instance, f'button_label_{lang_suffix}', '') or instance.button_label or '',
                    'link': instance.button_link or '',
                },
            },
            'values': {
                'title': getattr(instance, f'values_title_{lang_suffix}', '') or instance.values_title or '',
                'items': ValueSerializer(values, many=True, context=child_context).data,
            },
            'team': {
                'title': cached_config.get('team_title') or 'Наша команда',
                'members': TeamMemberSerializer(members, many=True, context=child_context).data,
                'action_button': {
                    'label': cached_config.get('about_team_button_label') or 'Присоединиться',
                    'link': cached_config.get('team_button_link') or '/contacts',
                },
            },
            'gallery_carousel': {
                'title': getattr(instance, f'gallery_title_{lang_suffix}', '') or instance.gallery_title or '',
                'images': GalleryImageSerializer(images, many=True, context=child_context).data,
            },
        }
