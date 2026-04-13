"""Модели для раздела 'О сообществе'."""

from django.db import models
from django.core.validators import MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import Truncator


class Value(models.Model):
    """Сущность ценности."""

    title = models.CharField(max_length=100, verbose_name=_('Title'))
    text = models.TextField(validators=[MaxLengthValidator(250)], verbose_name=_('Text'))

    class Meta:
        verbose_name = _('Value')
        verbose_name_plural = _('Values')

    def __str__(self):
        return Truncator(self.title).chars(50)

class TeamMember(models.Model):
    """Сущность члена команды."""

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    role = models.CharField(max_length=255, verbose_name=_('Role'))
    photo = models.ImageField(upload_to='team/', verbose_name=_('Photo'))

    class Meta:
        verbose_name = _('Team Member')
        verbose_name_plural = _('Team Members')

    def __str__(self):
        return Truncator(self.name).chars(50)


class GalleryImage(models.Model):
    """Сущность изображения для галереи."""

    image = models.ImageField(upload_to='gallery/', verbose_name=_('Image'))
    alt = models.CharField(max_length=255, verbose_name=_('Alt text'))

    class Meta:
        verbose_name = _('Gallery Image')
        verbose_name_plural = _('Gallery Images')

    def __str__(self):
        return Truncator(self.alt).chars(50)
    

class AboutPage(models.Model):
    """Сущность страницы 'О нас'."""

    hero_title = models.CharField(max_length=100, verbose_name=_('Hero title'))
    hero_description = models.CharField(max_length=255, verbose_name=_('Hero description'))

    about_title = models.CharField(max_length=100, verbose_name=_('About title'))
    paragraph_1 = models.TextField(validators=[MaxLengthValidator(250)],
                                   verbose_name=_('Paragraph 1'))
    paragraph_2 = models.TextField(validators=[MaxLengthValidator(250)],
                                   verbose_name=_('Paragraph 2'))
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
    
    button_label = models.CharField(max_length=100, verbose_name=_('Button label'))
    button_link = models.CharField(max_length=255, verbose_name=_('Button link'))
    values_title = models.CharField(max_length=100, verbose_name=_('Values title'))
    team_title = models.CharField(max_length=100, verbose_name=_('Team title'))
    team_button_label = models.CharField(
        max_length=100,
        verbose_name=_('Team button label')
    )
    team_button_link = models.CharField(
        max_length=255,
        verbose_name=_('Team button link')
    )
    gallery_title = models.CharField(
        max_length=100,
        verbose_name=_('Gallery title')
    )

    class Meta:
        verbose_name = _('About Page')
        verbose_name_plural = _('About Pages')

    def __str__(self):
        return Truncator(self.hero_title).chars(50)
