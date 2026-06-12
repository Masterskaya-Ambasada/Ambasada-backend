from django.contrib.auth import get_user_model
from django.utils import translation
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserLoginResponseSerializer(serializers.ModelSerializer):
    """Схема данных пользователя для логина и документации."""

    name = serializers.CharField(source='full_name', read_only=True)
    photo = serializers.ImageField(read_only=True)

    class Meta:
        """Метаданные сериализатора ответа пользователя."""

        model = User
        fields = ('id', 'email', 'name', 'role', 'photo', 'is_staff')
        read_only_fields = fields


class AmbasadaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Расширенный сериализатор токенов, переиспользующий схему пользователя."""

    user = UserLoginResponseSerializer(read_only=True)

    default_error_messages = {
        'no_active_account': _('Неверный логин или пароль. Пожалуйста, проверьте данные и попробуйте снова.')
    }

    def validate(self, attrs):
        """Валидирует учетные данные и дополняет ответ информацией о пользователе."""
        data = super().validate(attrs)

        user_serializer = UserLoginResponseSerializer(self.user, context=self.context)
        data['user'] = user_serializer.data

        return data


class TeamMemberSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных блоков команды на сайте с динамической локализацией."""

    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    photo = serializers.ImageField(read_only=True)

    class Meta:
        """Метаданные сериализатора участника команды."""

        model = User
        fields = ('id', 'name', 'role', 'photo')

    def _get_suffix(self) -> str:
        """Определяет языковой суффикс без изменения глобального состояния локали."""
        suffix = self.context.get('lang_suffix')
        if not suffix:
            request = self.context.get('request')
            lang = 'ru'
            if request:
                lang = request.query_params.get('lang') or get_language_from_request(request) or 'ru'
            suffix = lang.lower().replace('-', '_')
        return suffix

    def get_name(self, obj) -> str:
        """Собирает локализованное имя и фамилию из переведенных базовых полей."""
        suffix = self._get_suffix()

        first_name = getattr(obj, f'first_name_{suffix}', None) or getattr(obj, 'first_name', '')
        last_name = getattr(obj, f'last_name_{suffix}', None) or getattr(obj, 'last_name', '')

        full_name = f'{first_name} {last_name}'.strip()

        return full_name or obj.full_name or obj.username

    def get_role(self, obj) -> str:
        """Возвращает локализованную строку роли участника команды."""
        suffix = self._get_suffix()

        if hasattr(obj, f'role_{suffix}'):
            return getattr(obj, f'role_{suffix}', '') or obj.role or ''

        if hasattr(obj, 'get_role_display'):
            lang_code = suffix.replace('_', '-')
            with translation.override(lang_code):
                return translation.gettext(obj.get_role_display())

        return obj.role or ''
