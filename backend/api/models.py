from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    code = models.CharField(max_length=10)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class Social(models.Model):
    class SocialType(models.TextChoices):
        TELEGRAM = 'telegram', 'Telegram'
        INSTAGRAM = 'instagram', 'Instagram'

    type = models.CharField(max_length=20, choices=SocialType.choices, verbose_name='Тип соцсети')
    url = models.URLField()

    def __str__(self):
        return self.get_type_display()


class SiteConfig(models.Model):
    site_name = models.CharField(max_length=100, verbose_name=_('Название сайта'), help_text=_('Максимум 100 символов'))
    seo_description = models.CharField(
        max_length=250, verbose_name=_('SEO описание'), help_text=_('Максимум 250 символов')
    )
    copyright = models.CharField(max_length=150, verbose_name=_('Копирайт'), help_text=_('Максимум 150 символов'))
    languages = models.ManyToManyField('Language', blank=True, verbose_name=_('Языки'))
    socials = models.ManyToManyField('Social', blank=True, verbose_name=_('Соцсети'))

    def save(self, *args, **kwargs):
        if not self.pk and SiteConfig.objects.exists():
            raise ValidationError('Может быть только один SiteConfig')
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')
