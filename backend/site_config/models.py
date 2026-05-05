from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    """Модель доступных языков на основе настроек проекта."""

    code = models.CharField(max_length=10, unique=True, choices=settings.LANGUAGES, verbose_name=_('Код'))

    class Meta:
        verbose_name = _('Язык')
        verbose_name_plural = _('Языки')
        ordering = ['code']

    @property
    def label(self):
        """Возвращает название языка из настроек проекта."""
        return self.get_code_display()

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

    def __str__(self):
        return f'{self.get_social_type_display()}: {self.url}'


class SiteConfig(models.Model):
    """Глобальные настройки сайта (Singleton)."""

    site_name = models.CharField(max_length=100, verbose_name=_('Название сайта'), help_text=_('Максимум 100 символов'))
    seo_description = models.CharField(
        max_length=250, verbose_name=_('SEO описание'), help_text=_('Максимум 250 символов')
    )
    copyright = models.CharField(max_length=150, verbose_name=_('Копирайт'), help_text=_('Максимум 150 символов'))
    languages = models.ManyToManyField('Language', blank=True, related_name='site_configs', verbose_name=_('Языки'))
    socials = models.ManyToManyField('Social', blank=True, related_name='site_configs', verbose_name=_('Соцсети'))

    def save(self, *args, **kwargs):
        """Проверяет существование объекта и очищает кэш при сохранении."""
        if not self.pk and SiteConfig.objects.exists():
            raise ValidationError(_('Может существовать только один объект настроек сайта'))
        result = super().save(*args, **kwargs)
        cache.delete('site_config_init')
        return result

    def delete(self, *args, **kwargs):
        """Очищает кэш при удалении объекта."""
        result = super().delete(*args, **kwargs)
        cache.delete('site_config_init')
        return result

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')
