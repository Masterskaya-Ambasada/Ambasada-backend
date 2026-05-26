from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    DESCRIPTION_MAX_LENGTH,
    PARAGRAPH_DEFAULT_ORDER,
    TEXT_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    UPLOAD_GALLERY,
)


class AboutPage(models.Model):
    """Сущность страницы 'О нас' (Singleton)."""

    about_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок блока "О нас"'),
        help_text=_('Заголовок для текстового раздела с описанием деятельности.'),
    )
    button_label = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Главная кнопка (текст)'),
        help_text=_('Надпись на кнопке в блоке "О нас" (например, "Подробнее").'),
    )
    button_link = models.URLField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Главная кнопка (ссылка)'),
        help_text=_('URL-адрес, на который ведет главная кнопка (включая https://).'),
    )

    values_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок "Ценности"'),
        help_text=_('Заголовок для блока с перечислением ценностей сообщества.'),
    )
    team_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок "Команда"'),
        help_text=_('Заголовок для секции с участниками команды.'),
    )
    team_button_label = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Кнопка команды (текст)'),
        help_text=_('Надпись на кнопке для перехода к списку всей команды.'),
    )
    team_button_link = models.URLField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Кнопка команды (ссылка)'),
        help_text=_('URL-адрес для кнопки команды.'),
    )
    email = models.EmailField(
        verbose_name=_('Email'), blank=True, default='', help_text=_('Контактный email для связи.')
    )
    contact_link = models.URLField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Ссылка для связи'),
        blank=True,
        help_text=_('Прямая ссылка для связи (например, Telegram-бот или форма).'),
    )
    gallery_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок галереи'),
        help_text=_('Заголовок для фотогалереи сообщества.'),
    )

    class Meta:
        verbose_name = _('Страница "О нас"')
        verbose_name_plural = _('Страница "О нас"')

    def save(self, *args, **kwargs):
        if not self.pk and AboutPage.objects.exists():
            raise ValidationError(_('Может существовать только одна страница "О нас".'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.about_title or _('Страница "О нас"')


class AboutParagraph(models.Model):
    about = models.ForeignKey(
        AboutPage, on_delete=models.CASCADE, related_name='paragraphs', verbose_name=_('Страница')
    )
    first_sentence = models.CharField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Акцент'),
        help_text=_('Первое предложение абзаца, которое выделяется жирным или цветом.'),
    )
    main_text = models.TextField(
        verbose_name=_('Основной текст'), help_text=_('Развернутое описание основного содержания абзаца.')
    )
    order = models.PositiveIntegerField(
        default=PARAGRAPH_DEFAULT_ORDER,
        verbose_name=_('Порядок'),
        help_text=_('Числовой индекс для сортировки абзацев (чем меньше число, тем выше блок).'),
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('Параграф')
        constraints = [models.UniqueConstraint(fields=['about', 'order'], name='unique_about_paragraph_order')]


class Value(models.Model):
    about = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='values', verbose_name=_('Страница'))
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH, verbose_name=_('Название'), help_text=_('Краткий заголовок ценности.')
    )
    text = models.TextField(
        validators=[MaxLengthValidator(TEXT_MAX_LENGTH)],
        verbose_name=_('Текст'),
        help_text=_('Подробное описание сути ценности.'),
    )

    class Meta:
        verbose_name = _('Ценность')
        ordering = ['id']


class GalleryImage(models.Model):
    about = models.ForeignKey(
        AboutPage, on_delete=models.CASCADE, related_name='gallery_images', verbose_name=_('Страница')
    )
    image = models.ImageField(
        upload_to=UPLOAD_GALLERY,
        verbose_name=_('Изображение'),
        help_text=_('Загрузите фото для галереи. Оптимально в высоком качестве.'),
    )
    alt = models.CharField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Alt текст'),
        blank=True,
        help_text=_('Описание изображения для людей с нарушениями зрения и SEO.'),
    )

    class Meta:
        verbose_name = _('Изображение галереи')
