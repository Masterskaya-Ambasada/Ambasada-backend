from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import constants


class AboutPage(models.Model):
    """Сущность страницы 'О нас' (Singleton)."""

    # --- HERO СЕКЦИЯ ---
    hero_title = models.CharField(
        max_length=constants.TITLE_MAX_LENGTH,
        verbose_name=_('Hero: Заголовок'),
        default=constants.DEFAULT_HERO_TITLE,
        help_text=constants.FIELD_HERO_TITLE_HELP,
    )
    hero_description = models.CharField(
        max_length=constants.DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Hero: Описание'),
        default=constants.DEFAULT_HERO_DESCRIPTION,
        blank=True,
        help_text=constants.FIELD_HERO_DESC_HELP,
    )

    # --- СЕКЦИЯ 'О НАС' ---
    about_title = models.CharField(
        max_length=constants.TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок блока "О нас"'),
        default=constants.DEFAULT_ABOUT_TITLE,
        help_text=constants.FIELD_ABOUT_TITLE_HELP,
    )
    button_label = models.CharField(
        max_length=constants.TITLE_MAX_LENGTH,
        verbose_name=_('Главная кнопка (текст)'),
        default=constants.DEFAULT_BUTTON_LABEL,
        help_text=constants.FIELD_BUTTON_LABEL_HELP,
    )
    button_link = models.URLField(
        max_length=constants.DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Главная кнопка (ссылка)'),
        default=constants.DEFAULT_BUTTON_LINK,
        help_text=constants.FIELD_BUTTON_LINK_HELP,
    )
    values_title = models.CharField(
        max_length=constants.TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок "Ценности"'),
        default=constants.DEFAULT_VALUES_TITLE,
        help_text=constants.FIELD_VALUES_TITLE_HELP,
    )
    gallery_title = models.CharField(
        max_length=constants.TITLE_MAX_LENGTH,
        verbose_name=_('Заголовок gallery_title'),
        default=constants.DEFAULT_GALLERY_TITLE,
        help_text=constants.FIELD_GALLERY_TITLE_HELP,
    )

    class Meta:
        verbose_name = _('Страница "О нас"')
        verbose_name_plural = _('Страница "О нас"')

    def save(self, *args, **kwargs):
        if not self.pk and AboutPage.objects.exists():
            raise ValidationError(_('Может существовать только одна страница "О нас".'))
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.about_title) if self.about_title else str(_('Страница "О нас"'))


class AboutParagraph(models.Model):
    """Абзацы детального текстового описания на странице."""

    about = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name='paragraphs',
        verbose_name=_('Страница'),
    )
    first_sentence = models.CharField(
        max_length=constants.DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Акцент'),
        help_text=constants.FIELD_FIRST_SENTENCE_HELP,
    )
    main_text = models.TextField(
        verbose_name=_('Основной текст'),
        help_text=constants.FIELD_MAIN_TEXT_HELP,
    )
    order = models.PositiveIntegerField(
        default=constants.PARAGRAPH_DEFAULT_ORDER,
        verbose_name=_('Порядок'),
        help_text=constants.FIELD_ORDER_HELP,
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('Параграф')
        verbose_name_plural = _('Параграфы контента')
        constraints = [models.UniqueConstraint(fields=['about', 'order'], name='unique_about_paragraph_order')]

    def __str__(self):
        prefix = str(_('Абзац'))
        excerpt = str(self.first_sentence[:30]) if self.first_sentence else ''
        return f'{prefix} #{self.order} ({excerpt}...)'


class Value(models.Model):
    """Ключевые ценности организации/сообщества."""

    about = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name=_('Страница'),
    )
    title = models.CharField(
        max_length=constants.TITLE_MAX_LENGTH,
        verbose_name=_('Название'),
        help_text=constants.FIELD_VALUE_TITLE_HELP,
    )
    text = models.TextField(
        validators=[MaxLengthValidator(constants.TEXT_MAX_LENGTH)],
        verbose_name=_('Текст'),
        help_text=constants.FIELD_VALUE_TEXT_HELP,
    )

    class Meta:
        verbose_name = _('Ценность')
        verbose_name_plural = _('Ценности')
        ordering = ['id']

    def __str__(self):
        return str(self.title)


class GalleryImage(models.Model):
    """Изображения галереи для слайдера или карусели."""

    about = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name=_('Страница'),
    )
    image = models.ImageField(
        upload_to=constants.UPLOAD_GALLERY,
        verbose_name=_('Изображение'),
        help_text=constants.FIELD_IMAGE_HELP,
    )
    alt = models.CharField(
        max_length=constants.DESCRIPTION_MAX_LENGTH,
        verbose_name=_('Alt текст'),
        blank=True,
        help_text=constants.FIELD_ALT_HELP,
    )

    class Meta:
        verbose_name = _('Изображение галереи')
        verbose_name_plural = _('Изображения галереи')

    def __str__(self):
        photo_word = str(_('Фото'))
        obj_id = self.id if self.id else str(_('Новое'))
        short_alt = str(self.alt[:30]) if self.alt else str(_('Без описания'))
        return f'{photo_word} #{obj_id} ({short_alt})'
