from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    COOKIE_BUTTON_TEXT_MAX_LENGTH,
    DEFAULT_COOKIE_BUTTON_TEXT,
    DEFAULT_COOKIE_MESSAGE,
    get_config_cache_key,
)


def clear_config_cache():
    """Единая функция очистки кэша конфигурации."""
    keys = [get_config_cache_key(language_code) for language_code, _ in settings.LANGUAGES]
    cache.delete_many(keys)


class Language(models.Model):
    """Модель доступных языков на основе настроек проекта."""

    code = models.CharField(max_length=10, unique=True, choices=settings.LANGUAGES, verbose_name=_('Код'))

    class Meta:
        verbose_name = _('Язык')
        verbose_name_plural = _('Языки')
        ordering = ['code']

    def label(self):
        """Возвращает название языка из настроек проекта."""
        return self.get_code_display()

    label.short_description = _('Название языка')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        clear_config_cache()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        clear_config_cache()

    def __str__(self):
        return f'{self.get_code_display()} ({self.code})'


class Social(models.Model):
    """Модель ссылок на социальные сети."""

    class SocialType(models.TextChoices):
        TELEGRAM = 'telegram', _('Telegram')
        INSTAGRAM = 'instagram', _('Instagram')
        FACEBOOK = 'facebook', _('Facebook')
        LINKEDIN = 'linkedin', _('LinkedIn')

    social_type = models.CharField(
        max_length=20, choices=SocialType.choices, verbose_name=_('Тип соцсети'), db_index=True
    )
    url = models.URLField(verbose_name=_('URL'))

    class Meta:
        verbose_name = _('Социальная сеть')
        verbose_name_plural = _('Социальные сети')
        constraints = [models.UniqueConstraint(fields=['social_type', 'url'], name='unique_social_type_url')]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        clear_config_cache()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        clear_config_cache()

    def __str__(self):
        return f'{self.get_social_type_display()}: {self.url}'


class SiteConfig(models.Model):
    """Глобальные настройки сайта (True Singleton для продакшена)."""

    site_name = models.CharField(max_length=100, verbose_name=_('Название сайта'), help_text=_('Максимум 100 символов'))
    seo_description = models.CharField(
        max_length=250, verbose_name=_('SEO описание'), help_text=_('Максимум 250 символов')
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

    copyright = models.CharField(max_length=150, verbose_name=_('Копирайт'), help_text=_('Максимум 150 символов'))
    languages = models.ManyToManyField('Language', blank=True, related_name='site_configs', verbose_name=_('Языки'))
    socials = models.ManyToManyField('Social', blank=True, related_name='site_configs', verbose_name=_('Соцсети'))

    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')

    def save(self, *args, **kwargs):
        """Гарантирует уникальность записи на уровне PK и сбрасывает кэш."""
        self.pk = 1
        super().save(*args, **kwargs)
        clear_config_cache()

    def delete(self, *args, **kwargs):
        """Запрещает удаление системных настроек."""
        raise ValidationError(_('Удаление системных настроек сайта запрещено.'))

    def __str__(self):
        return self.site_name
