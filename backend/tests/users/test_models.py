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

    def test_full_name_with_missing_parts(self, user_factory):
        """Проверка full_name, если одно из полей пустое (граничный случай)."""
        user_only_first = user_factory(email='first@test.com', first_name='Дмитрий', last_name='')
        assert user_only_first.full_name == 'Дмитрий'
        
        user_empty = user_factory(email='empty@test.com', first_name='', last_name='')
        assert user_empty.full_name == 'empty@test.com'

    def test_role_to_is_staff_automation(self, user_factory):
        """Проверка автоматического назначения is_staff при сохранении в зависимости от роли."""
        editor = user_factory(email='e@test.com', role=User.Role.EDITOR)
        assert editor.is_staff is True

        simple_user = user_factory(email='s@test.com', role=User.Role.USER)
        assert simple_user.is_staff is False

    def test_role_check_properties_and_methods(self, admin_user, editor_user, regular_user):
        """Тесты свойств быстрого доступа к ролям и метода has_role."""
        assert admin_user.is_admin is True
        assert admin_user.is_editor is False
        assert admin_user.has_role(User.Role.ADMIN) is True

        assert editor_user.is_editor is True
        assert editor_user.is_admin is False
        assert editor_user.has_role(User.Role.EDITOR) is True
        assert editor_user.has_role(User.Role.ADMIN, User.Role.EDITOR) is True

        assert regular_user.is_admin is False
        assert regular_user.is_editor is False
        assert regular_user.has_role(User.Role.USER) is True

    def test_can_edit_content_method(self, editor_user, regular_user, admin_user):
        """Проверка бизнес-логики: кто может управлять контентом."""
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

    def test_create_superuser_invalid_flags_raises_error(self):
        """Негативные кейсы для create_superuser: проверка обязательных флагов."""
        with pytest.raises(ValueError, match='is_staff'):
            User.objects.create_superuser(
                email='bad_staff@test.com',
                password='password',
                is_staff=False
            )

        with pytest.raises(ValueError, match='is_superuser'):
            User.objects.create_superuser(
                email='bad_super@test.com',
                password='password',
                is_superuser=False
            )

    def test_create_user_no_email_raises_error(self):
        """Проверка валидации обязательного email в менеджере."""
        with pytest.raises(ValueError, match='почты'):
            User.objects.create_user(email=None)


@pytest.mark.django_db
def test_team_photo_path_format(regular_user):
    """Проверка генерации пути для фото участника."""
    from users.models import team_photo_path
    filename = 'avatar.jpg'
    path = team_photo_path(regular_user, filename)
    assert path == f'team_photos/{regular_user.uuid}/{filename}'