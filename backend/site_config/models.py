from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Код'))
    label = models.CharField(max_length=50, unique=True, verbose_name=_('Название'))

    class Meta:
        verbose_name = _('Язык')
        verbose_name_plural = _('Языки')
        ordering = ['label']

    def __str__(self):
        return self.label


class Social(models.Model):
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
    site_name = models.CharField(max_length=100, verbose_name=_('Название сайта'), help_text=_('Максимум 100 символов'))
    seo_description = models.CharField(
        max_length=250, verbose_name=_('SEO описание'), help_text=_('Максимум 250 символов')
    )
    privacy_policy = models.TextField(
        max_length=250, verbose_name=_('Политика конфиденциальности'), help_text=_('Максимум 250 символов'), default=''
    )
    copyright = models.CharField(max_length=150, verbose_name=_('Копирайт'), help_text=_('Максимум 150 символов'))
    languages = models.ManyToManyField('Language', blank=True, related_name='site_configs', verbose_name=_('Языки'))

    socials = models.ManyToManyField('Social', blank=True, related_name='site_configs', verbose_name=_('Соцсети'))

    def save(self, *args, **kwargs):
        if not self.pk and SiteConfig.objects.exists():
            raise ValidationError(_('Может существовать только один объект настроек сайта'))
        result = super().save(*args, **kwargs)
        cache.delete('site_config_init')
        return result

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete('site_config_init')
        return result

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')
