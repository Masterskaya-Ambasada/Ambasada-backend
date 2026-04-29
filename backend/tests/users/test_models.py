import pytest
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    """Тесты основной логики модели User."""

    def test_create_user_normalizes_email(self, user_factory):
        """Проверка, что email приводится к нижнему регистру."""
        user = user_factory(email='UPPER@Example.com')
        assert user.email == 'upper@example.com'

    def test_full_name_property(self, regular_user):
        """Проверка вычисляемого свойства full_name."""
        assert regular_user.full_name == 'Ivan Ivanov'

    def test_role_to_is_staff_automation(self, user_factory):
        """Проверка автоматического назначения is_staff при сохранении."""
        editor = user_factory(email='e@test.com', role=User.Role.EDITOR)
        assert editor.is_staff is True

        simple_user = user_factory(email='s@test.com', role=User.Role.USER)
        assert simple_user.is_staff is False

    def test_can_edit_content_method(self, editor_user, regular_user, admin_user):
        """Проверка разрешения на редактирование контента."""
        assert editor_user.can_edit_content() is True
        assert admin_user.can_edit_content() is True
        assert regular_user.can_edit_content() is False

    def test_unique_email_case_insensitive(self, user_factory):
        """Проверка UniqueConstraint на уровне БД (регистронезависимость)."""
        user_factory(email='unique@test.com')
        with pytest.raises(IntegrityError):
            user_factory(email='UNIQUE@test.com')


@pytest.mark.django_db
class TestUserManager:
    """Тесты менеджера и QuerySet."""

    def test_public_queryset(self, user_factory):
        """Проверка работы фильтра public()."""
        user_factory(email='pub@test.com', is_public=True, is_active=True)
        user_factory(email='priv@test.com', is_public=False, is_active=True)
        user_factory(email='inactive@test.com', is_public=True, is_active=False)

        public_users = User.objects.public()
        assert public_users.count() == 1
        assert public_users.first().email == 'pub@test.com'

    def test_create_superuser_defaults(self, admin_user):
        """Проверка дефолтных значений суперпользователя."""
        assert admin_user.is_superuser is True
        assert admin_user.is_staff is True
        assert admin_user.role == User.Role.ADMIN

    def test_create_user_no_email_raises_error(self):
        """Проверка валидации обязательного email."""
        with pytest.raises(ValueError, match='Электронная почта обязательна'):
            User.objects.create_user(email=None)


@pytest.mark.django_db
def test_team_photo_path_format(regular_user):
    """Проверка генерации пути для фото."""
    from users.models import team_photo_path
    filename = 'avatar.jpg'
    path = team_photo_path(regular_user, filename)
    assert path == f'team_photos/{regular_user.uuid}/{filename}'