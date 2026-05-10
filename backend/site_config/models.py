from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    COOKIE_BUTTON_TEXT_MAX_LENGTH,
    COPYRIGHT_MAX_LENGTH,
    DEFAULT_COOKIE_BUTTON_TEXT,
    DEFAULT_COOKIE_MESSAGE,
    LANGUAGE_CODE_MAX_LENGTH,
    SEO_DESCRIPTION_MAX_LENGTH,
    SITE_CONFIG_SINGLETON_PK,
    SITE_NAME_MAX_LENGTH,
    clear_config_cache,
)


class Language(models.Model):
    """Модель доступных языков на основе настроек проекта."""

    code = models.CharField(max_length=LANGUAGE_CODE_MAX_LENGTH, unique=True, verbose_name=_('Код'))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Язык')
        verbose_name_plural = _('Языки')
        ordering = ['code']

    def label(self):
        """Возвращает название языка из настроек проекта."""
        # return self.get_code_display()
        return dict(settings.LANGUAGES).get(self.code, self.code)

    label.short_description = _('Название языка')

    def __str__(self):
        return f'{self.label()} ({self.code})'


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
    socials = models.ManyToManyField(
        'contacts.ContactSocialLink', blank=True, related_name='site_configs', verbose_name=_('Соцсети')
    )

    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')

    def save(self, *args, **kwargs):
        """Гарантирует уникальность записи на уровне PK и сбрасывает кэш."""
        self.pk = SITE_CONFIG_SINGLETON_PK
        super().save(*args, **kwargs)
        clear_config_cache()

    def delete(self, *args, **kwargs):
        """Запрещает удаление системных настроек."""
        raise ValidationError(_('Удаление системных настроек сайта запрещено.'))

    def __str__(self):
        return self.site_name
