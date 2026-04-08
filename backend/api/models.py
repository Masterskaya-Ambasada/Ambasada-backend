"""Модели для раздела 'О сообществе'."""

from django.db import models


class Value(models.Model):
    """Сущность ценности."""

    title = models.CharField(max_length=100)
    text = models.TextField(max_length=250)


class TeamMember(models.Model):
    """Сущность члена команды."""

    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    photo = models.URLField()


class GalleryImage(models.Model):
    """Сущность изображения для галереи."""

    url = models.URLField()
    alt = models.CharField(max_length=255)


class AboutPage(models.Model):
    """Сущность страницы 'О нас'."""

    hero_title = models.CharField(max_length=100)
    hero_description = models.CharField(max_length=255)

    about_title = models.CharField(max_length=100)
    paragraph_1 = models.TextField(max_length=250)
    paragraph_2 = models.TextField(max_length=250)

    button_text = models.CharField(max_length=100)
    button_link = models.CharField(max_length=255)

    def __str__(self):
        return 'AboutPage'
