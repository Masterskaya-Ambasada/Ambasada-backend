from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class AmbasadaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Расширенный сериализатор токенов с данными пользователя и понятными ошибками."""

    default_error_messages = {
        'no_active_account': _('Неверный логин или пароль. Пожалуйста, проверьте данные и попробуйте снова.')
    }

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        request = self.context.get('request')

        photo_url = None
        if user.photo:
            photo_url = request.build_absolute_uri(user.photo.url) if request else user.photo.url

        data['user'] = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'photo': photo_url,
            'is_staff': user.is_staff,
        }

        return data


class TeamMemberSerializer(serializers.ModelSerializer):
    """Для блоков команды на главной и странице 'О нас'."""

    name = serializers.CharField(source='full_name', read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'role', 'photo')
