from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserLoginResponseSerializer(serializers.ModelSerializer):
    """Схема данных пользователя для логина и документации."""

    name = serializers.CharField(source='full_name', read_only=True)

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

    name = serializers.CharField(source='full_name', read_only=True)
    position = serializers.CharField(read_only=True)
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'position', 'photo')

    def get_photo(self, obj):
        if not obj.photo:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url
