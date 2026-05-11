from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    COOKIE_BUTTON_TEXT_MAX_LENGTH,
    COPYRIGHT_MAX_LENGTH,
    DEFAULT_COOKIE_BUTTON_TEXT,
    DEFAULT_COOKIE_MESSAGE,
    SEO_DESCRIPTION_MAX_LENGTH,
    SITE_CONFIG_SINGLETON_PK,
    SITE_NAME_MAX_LENGTH,
)


class SiteConfig(models.Model):
    """Глобальные настройки сайта (True Singleton для продакшена)."""

    site_name = models.CharField(
        max_length=SITE_NAME_MAX_LENGTH, verbose_name=_('Название сайта'), help_text=_('Максимум 100 символов')
    )
    seo_description = models.CharField(
        max_length=SEO_DESCRIPTION_MAX_LENGTH, verbose_name=_('SEO описание'), help_text=_('Максимум 250 символов')
    )
    privacy_policy = models.TextField(verbose_name=_('Политика конфиденциальности'), default='')

    cookie_message = models.TextField(
        verbose_name=_('Текст cookie-сообщения'),
        default=DEFAULT_COOKIE_MESSAGE,
    )

    cookie_button_text = models.CharField(
        max_length=COOKIE_BUTTON_TEXT_MAX_LENGTH,
        verbose_name=_('Текст кнопки cookie'),
        default=DEFAULT_COOKIE_BUTTON_TEXT,
    )

    copyright = models.CharField(
        max_length=COPYRIGHT_MAX_LENGTH, verbose_name=_('Копирайт'), help_text=_('Максимум 150 символов')
    )

    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')

    def save(self, *args, **kwargs):
        """Гарантирует уникальность записи на уровне PK и сбрасывает кэш."""
        self.pk = SITE_CONFIG_SINGLETON_PK
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Запрещает удаление только основной системной записи."""
        if self.pk == SITE_CONFIG_SINGLETON_PK:
            raise ValidationError(_('Удаление системных настроек сайта запрещено.'))
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.site_name
