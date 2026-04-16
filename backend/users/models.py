from typing import Any, TypeVar

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from .constants import BIO_MAX_LENGTH, NAME_MAX_LENGTH, POSITION_MAX_LENGTH, ROLE_MAX_LENGTH

TUser = TypeVar('TUser', bound='User')


def team_photo_path(instance: 'User', filename: str) -> str:
    """Путь загрузки фото участника команды."""
    folder_name = instance.email.replace('@', '_at_')
    return f'team_photos/{folder_name}/{filename}'


class UserQuerySet(models.QuerySet):
    def public(self):
        """Возвращает только тех, кто отмечен для показа на сайте."""
        return self.filter(is_public=True, is_active=True)


class UserManager(BaseUserManager):
    """Менеджер пользователей (создание user/superuser)."""

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_queryset().public()

    def _create_user(self, email: str, password: str | None, **extra_fields: Any) -> TUser:
        """Базовая логика создания пользователя."""
        if not email:
            raise ValueError(_('Электронная почта обязательна'))

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)

        user.set_password(password) if password else user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> TUser:
        """Создание обычного пользователя."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> TUser:
        """Создание суперпользователя."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True'))

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя (используется как участник команды)."""

    class Role(models.TextChoices):
        USER = 'USER', _('Пользователь')
        EDITOR = 'EDITOR', _('Контент-редактор')
        ADMIN = 'ADMIN', _('Администратор')

    username = None

    email = models.EmailField(
        _('адрес электронной почты'),
        unique=True,
        db_index=True,
    )

    first_name = models.CharField(_('имя'), max_length=NAME_MAX_LENGTH)
    last_name = models.CharField(_('фамилия'), max_length=NAME_MAX_LENGTH)

    role = models.CharField(
        _('роль'),
        max_length=ROLE_MAX_LENGTH,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
    )

    position = models.CharField(
        _('должность'),
        max_length=POSITION_MAX_LENGTH,
        blank=True,
        help_text=_('Роль в команде (например: архитектор, дизайнер и т.д.)'),
    )

    photo = models.ImageField(
        _('фотография'),
        upload_to=team_photo_path,
        blank=True,
        null=True,
    )

    bio = models.TextField(
        _('биография'),
        blank=True,
        max_length=BIO_MAX_LENGTH,
        validators=[MaxLengthValidator(BIO_MAX_LENGTH)],
        help_text=_('Краткое описание участника команды'),
    )

    is_public = models.BooleanField(
        _('публичный статус'),
        default=False,
        db_index=True,
        help_text=_('Отображать в блоке команды на сайте'),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ('email',)
        constraints = [
            UniqueConstraint(
                Lower('email'),
                name='unique_user_email_lower',
            )
        ]

    def __str__(self) -> str:
        return f'{self.email} ({self.get_role_display()})'

    def save(self, *args, **kwargs):
        """Автоматическое управление доступом к админке в зависимости от роли."""
        if self.role in {self.Role.EDITOR, self.Role.ADMIN}:
            self.is_staff = True
        elif not self.is_superuser:
            self.is_staff = False
        super().save(*args, **kwargs)

    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя."""
        name = f'{self.first_name} {self.last_name}'.strip()
        return name or self.email

    @property
    def is_editor(self) -> bool:
        """Проверка, является ли пользователь редактором."""
        return self.role == self.Role.EDITOR

    @property
    def is_admin(self) -> bool:
        """Проверка, является ли пользователь администратором."""
        return self.role == self.Role.ADMIN

    def has_role(self, *roles: str) -> bool:
        """Проверка наличия одной из указанных ролей."""
        return self.role in roles

    def can_edit_content(self) -> bool:
        """Проверка прав на редактирование контента."""
        return self.role in {self.Role.ADMIN, self.Role.EDITOR}
