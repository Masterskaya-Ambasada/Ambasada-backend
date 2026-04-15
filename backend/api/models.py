"""Модели для раздела 'О сообществе'."""

from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _


class Value(models.Model):
    """Сущность ценности."""

    title = models.CharField(max_length=100, verbose_name=_('Title'), default='')
    text = models.TextField(validators=[MaxLengthValidator(250)], verbose_name=_('Text'), default='')

    class Meta:
        verbose_name = _('Value')
        verbose_name_plural = _('Values')
        ordering = ['id']

    def __str__(self):
        return Truncator(self.title).chars(50)


class TeamMember(models.Model):
    """Сущность члена команды."""

    name = models.CharField(max_length=255, verbose_name=_('Name'), default='')
    role = models.CharField(max_length=255, verbose_name=_('Role'), default='')
    photo = models.ImageField(
        upload_to='team/',
        verbose_name=_('Photo'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Team Member')
        verbose_name_plural = _('Team Members')
        ordering = ['id']

    def __str__(self):
        return Truncator(self.name).chars(50)


class GalleryImage(models.Model):
    """Сущность изображения для галереи."""

    image = models.ImageField(
        upload_to='gallery/',
        verbose_name=_('Image'),
        blank=True,
        null=True,
    )
    alt = models.CharField(max_length=255, verbose_name=_('Alt text'), default='')

    class Meta:
        verbose_name = _('Gallery Image')
        verbose_name_plural = _('Gallery Images')
        ordering = ['id']

    def __str__(self):
        return Truncator(self.alt).chars(50)


class AboutPage(models.Model):
    """Сущность страницы 'О нас'."""

    hero_title = models.CharField(max_length=100, verbose_name=_('Hero title'), default='')
    hero_description = models.CharField(max_length=255, verbose_name=_('Hero description'), default='')

    about_title = models.CharField(max_length=100, verbose_name=_('About title'), default='')
    paragraph_1 = models.TextField(validators=[MaxLengthValidator(250)], verbose_name=_('Paragraph 1'), default='')
    paragraph_2 = models.TextField(validators=[MaxLengthValidator(250)], verbose_name=_('Paragraph 2'), default='')

    image_left = models.ImageField(
        upload_to='about/',
        verbose_name=_('Hero left image'),
        blank=True,
        null=True,
    )
    image_right = models.ImageField(
        upload_to='about/',
        verbose_name=_('Hero right image'),
        blank=True,
        null=True,
    )

    button_label = models.CharField(max_length=100, verbose_name=_('Button label'), default='')
    button_link = models.CharField(max_length=255, verbose_name=_('Button link'), default='')

    values_title = models.CharField(max_length=100, verbose_name=_('Values title'), default='')
    team_title = models.CharField(max_length=100, verbose_name=_('Team title'), default='')

    team_button_label = models.CharField(max_length=100, verbose_name=_('Team button label'), default='')
    team_button_link = models.CharField(max_length=255, verbose_name=_('Team button link'), default='')

    gallery_title = models.CharField(max_length=100, verbose_name=_('Gallery title'), default='')

    class Meta:
        verbose_name = _('About Page')
        verbose_name_plural = _('About Pages')

    def __str__(self):
        return self.hero_title or 'About Page'
