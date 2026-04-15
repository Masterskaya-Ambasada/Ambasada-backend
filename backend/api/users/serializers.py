from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class AmbasadaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Расширенный сериализатор токенов c объектом user ."""

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


""" # Ниже написал некоторые примеры сериализаторов, можно изменять под свой код.
class TeamMemberSerializer(serializers.ModelSerializer):
    \"""
    Сериализатор для краткого отображения члена команды.
    Используется в HomeView и AboutView.
    \"""
    name = serializers.CharField(source='full_name', read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True) 

    class Meta:
        model = User
        fields = (
            'id', 
            'name', 
            'role', 
            'photo'
        )


class UserDetailSerializer(serializers.ModelSerializer):
    \"""Детальный вывод участника команды.\"""
    name = serializers.CharField(source='full_name', read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 
            'name', 
            'role', 
            'position', 
            'bio', 
            'photo'
        ) """
