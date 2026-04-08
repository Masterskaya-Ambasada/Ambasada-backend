from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['username']

    def __str__(self):
        return self.username
