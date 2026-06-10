from django.contrib.auth import get_user_model
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
        data = super().validate(attrs)

        user_serializer = UserLoginResponseSerializer(self.user, context=self.context)
        data['user'] = user_serializer.data

        return data


class TeamMemberSerializer(serializers.ModelSerializer):
    """Для публичных блоков команды на сайте."""

    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    photo = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'role', 'photo')

    def _get_suffix(self) -> str:
        """Определяем суффикс языка без изменения глобального состояния."""
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

    def get_role(self, obj) -> str:
        suffix = self._get_suffix()

        if hasattr(obj, f'role_{suffix}'):
            return getattr(obj, f'role_{suffix}', '') or obj.role or ''

        if hasattr(obj, 'get_role_display'):
            return _(obj.get_role_display())

        return obj.role or ''
