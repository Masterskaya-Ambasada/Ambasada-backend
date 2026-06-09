import uuid
from typing import Any, TypeVar

from core.validators import MediaFileValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from .constants import (
    BIO_MAX_LENGTH,
    NAME_MAX_LENGTH,
    POSITION_MAX_LENGTH,
    ROLE_MAX_LENGTH,
    TEAM_PHOTO_UPLOAD_PATH,
    USER_BIO_HELP_TEXT,
    USER_EMAIL_HELP_TEXT,
    USER_FIRST_NAME_HELP_TEXT,
    USER_IS_PUBLIC_HELP_TEXT,
    USER_LAST_NAME_HELP_TEXT,
    USER_ORDER_HELP_TEXT,
    USER_ORDER_STEP,
    USER_PHOTO_HELP_TEXT,
    USER_POSITION_HELP_TEXT,
    USER_ROLE_HELP_TEXT,
    USER_UUID_HELP_TEXT,
    USERS_DEFAULT_ORDER,
)

TUser = TypeVar('TUser', bound='User')


def team_photo_path(instance: 'User', filename: str) -> str:
    """Путь загрузки фото участника команды."""
    return TEAM_PHOTO_UPLOAD_PATH.format(uuid=instance.uuid, filename=filename)


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
        extra_fields.setdefault('position', User.Position.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True'))

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя (используется как участник команды)."""

    class Position(models.TextChoices):
        USER = 'USER', _('Участник команды')
        EDITOR = 'EDITOR', _('Контент-редактор')
        ADMIN = 'ADMIN', _('Администратор')

    username = None

    email = models.EmailField(
        _('Адрес электронной почты'),
        unique=True,
        db_index=True,
        help_text=USER_EMAIL_HELP_TEXT,
    )

    uuid = models.UUIDField(
        _('Уникальный идентификатор'),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=USER_UUID_HELP_TEXT,
    )

    first_name = models.CharField(
        _('Имя'),
        max_length=NAME_MAX_LENGTH,
        help_text=USER_FIRST_NAME_HELP_TEXT,
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=NAME_MAX_LENGTH,
        help_text=USER_LAST_NAME_HELP_TEXT,
    )

    position = models.CharField(
        _('Роль'),
        max_length=POSITION_MAX_LENGTH,
        choices=Position.choices,
        default=Position.USER,
        db_index=True,
        help_text=USER_POSITION_HELP_TEXT,
    )

    role = models.CharField(
        _('Должность'),
        max_length=ROLE_MAX_LENGTH,
        blank=True,
        help_text=USER_ROLE_HELP_TEXT,
    )

    photo = models.ImageField(
        _('Фотография'),
        upload_to=team_photo_path,
        blank=True,
        null=True,
        validators=[MediaFileValidator()],
        help_text=USER_PHOTO_HELP_TEXT,
    )

    bio = models.TextField(
        _('Биография'),
        blank=True,
        max_length=BIO_MAX_LENGTH,
        validators=[MaxLengthValidator(BIO_MAX_LENGTH)],
        help_text=USER_BIO_HELP_TEXT,
    )

    is_public = models.BooleanField(
        _('Публичный статус'),
        default=False,
        db_index=True,
        help_text=USER_IS_PUBLIC_HELP_TEXT,
    )

    order = models.PositiveIntegerField(
        _('Порядок отображения'),
        default=USERS_DEFAULT_ORDER,
        db_index=True,
        help_text=USER_ORDER_HELP_TEXT,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи и команда')
        ordering = ('order', 'last_name', 'first_name')
        constraints = [
            UniqueConstraint(
                Lower('email'),
                name='unique_user_email_lower',
            )
        ]

    def __str__(self) -> str:
        return f'{self.email} ({self.get_position_display()})'

    def save(self, *args, **kwargs):
        """Автоматический расчет порядка и управление доступом к админке."""
        if not self.pk and self.order == USERS_DEFAULT_ORDER:
            max_order = User.objects.aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + USER_ORDER_STEP

        if self.position in {self.Position.EDITOR, self.Position.ADMIN}:
            self.is_staff = True
        elif not self.is_superuser:
            self.is_staff = False

        super().save(*args, **kwargs)

    @property
    def full_name(self) -> str:
        """Returns the user's full name."""
        name = f'{self.first_name} {self.last_name}'.strip()
        return name or self.email

    @property
    def is_editor(self) -> bool:
        """Проверка, является ли пользователь редактором."""
        return self.position == self.Position.EDITOR

    @property
    def is_admin(self) -> bool:
        """Проверка, является ли пользователь администратором."""
        return self.position == self.Position.ADMIN

    def has_role(self, *positions: str) -> bool:
        """Проверка наличия одной из указанных системных должностей."""
        return self.position in positions

    def can_edit_content(self) -> bool:
        """Проверка прав на редактирование контента."""
        return self.position in {self.Position.ADMIN, self.Position.EDITOR}
