from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from contacts.constants import MAX_MESSAGE_LENGTH, MAX_NAME_LENGTH, MAX_REASON_LENGTH


class ContactRequest(models.Model):
    """Модель для формы обратной связи."""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name=_('Имя'),
    )
    email = models.EmailField(
        verbose_name=_('Email'),
    )
    message = models.TextField(
        max_length=MAX_MESSAGE_LENGTH,
        verbose_name=_('Сообщение'),
        validators=[MaxLengthValidator(MAX_MESSAGE_LENGTH)],
        help_text=_('Введите сообщение'),
    )
    reason = models.CharField(
        max_length=MAX_REASON_LENGTH,
        verbose_name=_('Причина обращения'),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Запрос обратной связи')
        verbose_name_plural = _('Запросы обратной связи')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.name} <{self.email}> - {self.reason}'
