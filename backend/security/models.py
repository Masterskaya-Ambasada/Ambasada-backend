from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import TEXT_HELP_TEXT


class SecurityPolicy(models.Model):
    text = models.TextField(verbose_name=_('Текст политики'), help_text=TEXT_HELP_TEXT)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата последнего обновления'))

    class Meta:
        verbose_name = _('Политика конфиденциальности')
        verbose_name_plural = _('Политики конфиденциальности')

    def __str__(self):
        return str(self._meta.verbose_name)

    def clean(self):
        """Запрещаем создание второй записи на уровне валидации Django."""
        if SecurityPolicy.objects.exclude(pk=self.pk).exists():
            raise ValidationError(_('Может существовать только одна запись политики конфиденциальности.'))
        super().clean()

    def save(self, *args, **kwargs):
        """Гарантируем, что у записи всегда будет id=1 (жесткий Singleton)."""
        self.pk = 1
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Удобный метод для получения синглтона в коде или сериализаторах."""
        obj, created = cls.objects.get_or_create(pk=1, defaults={'text': _('Текст политики...')})
        return obj
