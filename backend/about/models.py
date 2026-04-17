"""Модели для раздела 'О сообществе'."""

from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _


class Value(models.Model):
    """Сущность ценности."""

    title = models.CharField(
        max_length=100,
        verbose_name=_('Название'),
        default='',
    )
    text = models.TextField(
        validators=[MaxLengthValidator(250)],
        verbose_name=_('Текст'),
        default='',
    )

    class Meta:
        verbose_name = _('Ценность')
        verbose_name_plural = _('Ценности')
        ordering = ['id']

    def __str__(self):
        return Truncator(self.title).chars(50)


class TeamMember(models.Model):
    """Сущность члена команды."""

    name = models.CharField(
        max_length=255,
        verbose_name=_('Имя'),
        default='',
    )
    role = models.CharField(
        max_length=255,
        verbose_name=_('Роль'),
        default='',
    )
    photo = models.ImageField(
        upload_to='team/',
        verbose_name=_('Фото'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Участник команды')
        verbose_name_plural = _('Участники команды')
        ordering = ['id']

    def __str__(self):
        return Truncator(self.name).chars(50)


class GalleryImage(models.Model):
    """Сущность изображения для галереи."""

    image = models.ImageField(
        upload_to='gallery/',
        verbose_name=_('Изображение'),
        blank=True,
        null=True,
    )
    alt = models.CharField(
        max_length=255,
        verbose_name=_('Alt текст'),
        default='',
    )

    class Meta:
        verbose_name = _('Изображение галереи')
        verbose_name_plural = _('Галерея изображений')
        ordering = ['id']

    def __str__(self):
        return Truncator(self.alt).chars(50)


class AboutPage(models.Model):
    """Сущность страницы 'О нас'."""

    hero_title = models.CharField(
        max_length=100,
        verbose_name=_('Заголовок hero'),
        default='',
    )
    hero_description = models.CharField(
        max_length=255,
        verbose_name=_('Описание hero'),
        default='',
    )

    about_title = models.CharField(
        max_length=100,
        verbose_name=_('Заголовок блока "О нас"'),
        default='',
    )
    paragraph_1 = models.TextField(
        validators=[MaxLengthValidator(250)],
        verbose_name=_('Параграф 1'),
        default='',
    )
    paragraph_2 = models.TextField(
        validators=[MaxLengthValidator(250)],
        verbose_name=_('Параграф 2'),
        default='',
    )

    image_left = models.ImageField(
        upload_to='about/',
        verbose_name=_('Левое изображение hero'),
        blank=True,
        null=True,
    )
    image_right = models.ImageField(
        upload_to='about/',
        verbose_name=_('Правое изображение hero'),
        blank=True,
        null=True,
    )

    button_label = models.CharField(
        max_length=100,
        verbose_name=_('Текст кнопки'),
        default='',
    )
    button_link = models.CharField(
        max_length=255,
        verbose_name=_('Ссылка кнопки'),
        default='',
    )

    values_title = models.CharField(
        max_length=100,
        verbose_name=_('Заголовок "Ценности"'),
        default='',
    )
    team_title = models.CharField(
        max_length=100,
        verbose_name=_('Заголовок "Команда"'),
        default='',
    )

    team_button_label = models.CharField(
        max_length=100,
        verbose_name=_('Кнопка команды (текст)'),
        default='',
    )
    team_button_link = models.CharField(
        max_length=255,
        verbose_name=_('Кнопка команды (ссылка)'),
        default='',
    )

    gallery_title = models.CharField(
        max_length=100,
        verbose_name=_('Заголовок галереи'),
        default='',
    )

    class Meta:
        verbose_name = _('Страница "О нас"')
        verbose_name_plural = _('Страницы "О нас"')

    def __str__(self):
        return self.hero_title or 'Страница "О нас"'