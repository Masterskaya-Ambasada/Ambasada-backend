from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from .constants import (
    DESCRIPTION_MAX_LENGTH,
    PARAGRAPH_DEFAULT_ORDER,
    TEXT_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    TRUNCATE_LENGTH,
    UPLOAD_ABOUT,
    UPLOAD_GALLERY,
)


class Value(models.Model):
    """Сущность ценности."""

    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Название'),
    )
    text = models.TextField(
        validators=[MaxLengthValidator(TEXT_MAX_LENGTH)],
        verbose_name=_('Текст'),
    )

    class Meta:
        verbose_name = _('Ценность')
        verbose_name_plural = _('Ценности')
        ordering = ['id']

    def __str__(self):
        return Truncator(self.title).chars(TRUNCATE_LENGTH)


class GalleryImage(models.Model):
    """Сущность изображения для галереи."""

    image = models.ImageField(
        upload_to=UPLOAD_GALLERY,
        verbose_name=_('Изображение'),
        blank=True,
        null=True,
    )
    alt = models.CharField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Alt текст'),
        blank=True,
        default='',
    )

    class Meta:
        verbose_name = _('Изображение галереи')
        verbose_name_plural = _('Галерея изображений')
        ordering = ['id']

    def __str__(self):
        return Truncator(self.alt).chars(TRUNCATE_LENGTH)


class AboutPage(models.Model):
    """Сущность страницы 'О нас' (Singleton)."""

    hero_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок hero'),
    )
    hero_description = models.CharField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Описание hero'),
    )
    about_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок блока "О нас"'),
    )
    image_left = models.ImageField(
        upload_to=UPLOAD_ABOUT,
        verbose_name=_('Левое изображение hero'),
        blank=True,
        null=True,
    )
    image_right = models.ImageField(
        upload_to=UPLOAD_ABOUT,
        verbose_name=_('Правое изображение hero'),
        blank=True,
        null=True,
    )
    button_label = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Текст кнопки'),
    )
    button_link = models.CharField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Ссылка кнопки'),
    )
    values_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок "Ценности"'),
    )
    team_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок "Команда"'),
    )
    team_button_label = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Кнопка команды (текст)'),
    )
    team_button_link = models.CharField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Кнопка команды (ссылка)'),
    )
    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True,
        default='',
    )
    contact_link = models.CharField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Ссылка для связи'),
        blank=True,
        default='',
    )
    gallery_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок галереи'),
    )

    class Meta:
        verbose_name = _('Страница "О нас"')
        verbose_name_plural = _('Страница "О нас"')

    def clean(self):
        if not self.pk and AboutPage.objects.exists():
            raise ValidationError(_('Может существовать только одна страница "О нас".'))

    def save(self, *args, **kwargs):
        """Жесткая защита от создания дубликатов на уровне сохранения."""
        if not self.pk and AboutPage.objects.exists():
            raise ValidationError(_('Может существовать только одна страница "О нас".'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.hero_title or 'Страница "О нас"'


class AboutParagraph(models.Model):
    """Параграф страницы 'О нас' (разделён на акцент и основной текст)."""

    about = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name='paragraphs',
        verbose_name=_('Страница "О нас"'),
    )
    first_sentence = models.CharField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Акцент (первое предложение)'),
    )
    main_text = models.TextField(
        verbose_name=_('Основной текст'),
    )
    order = models.PositiveIntegerField(
        default=PARAGRAPH_DEFAULT_ORDER,
        verbose_name=_('Порядок'),
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('Параграф')
        verbose_name_plural = _('Параграфы')

        constraints = [models.UniqueConstraint(fields=['about', 'order'], name='unique_about_paragraph_order')]

    def __str__(self):
        return Truncator(self.first_sentence).chars(TRUNCATE_LENGTH)
