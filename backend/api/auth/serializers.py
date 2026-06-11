from django.contrib.auth import get_user_model
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserLoginResponseSerializer(serializers.ModelSerializer):
    """Схема данных пользователя для логина и документации с безопасной локализацией."""

    name = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'position', 'photo', 'is_staff')
        read_only_fields = fields

    def _get_suffix(self) -> str:
        """Определяем языковой суффикс из контекста или запроса."""
        suffix = self.context.get('lang_suffix')
        if not suffix:
            request = self.context.get('request')
            lang = 'ru'
            if request:
                lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
            suffix = lang.lower().replace('-', '_')
        return suffix

    def get_name(self, obj) -> str:
        suffix = self._get_suffix()
        return getattr(obj, f'full_name_{suffix}', '') or obj.full_name or ''

    def get_position(self, obj) -> str:
        suffix = self._get_suffix()
        if hasattr(obj, f'position_{suffix}'):
            return getattr(obj, f'position_{suffix}', '') or obj.position or ''
        return obj.position or ''


class AmbasadaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Расширенный сериализатор токенов, переиспользующий схему пользователя."""

    user = UserLoginResponseSerializer(read_only=True)

    default_error_messages = {
        'no_active_account': _('Неверный логин или пароль. Пожалуйста, проверьте данные и попробуйте снова.')
    }

    def validate(self, attrs):
        data = super().validate(attrs)

        request = self.context.get('request')

        lang = 'ru'
        if request:
            lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
        lang_suffix = lang.lower().replace('-', '_')

        custom_context = {'request': request, 'lang_suffix': lang_suffix}

        user_serializer = UserLoginResponseSerializer(self.user, context=custom_context)
        data['user'] = user_serializer.data

        return data
