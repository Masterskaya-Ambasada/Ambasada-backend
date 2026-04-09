"""Модели проектов и связанных сущностей для API."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

from projects.constants import (
    BLOCK_VARIANT_IMAGE_WITH_BUTTONS,
    BLOCK_VARIANT_IMAGE_WITH_LIST,
    BLOCK_VARIANT_TWO_IMAGES,
    BUTTON_TYPE_MAX_LENGTH,
    CONTENT_BLOCK_TITLE_MAX_LENGTH,
    DEFAULT_ORDER,
    DESCRIPTION_MAX_LENGTH,
    LABEL_MAX_LENGTH,
    ORDER_STEP,
    PROJECT_SLUG_MAX_LENGTH,
    REFERENCE_SLUG_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    URL_MAX_LENGTH,
)
from projects.validators import validate_string_list


class ProjectType(models.Model):
    """Справочник типов проектов для карточек и фильтров."""

    slug = models.SlugField(
        _('Идентификатор'),
        max_length=REFERENCE_SLUG_MAX_LENGTH,
        unique=True,
        help_text=_('Уникальный идентификатор типа проекта для API и фильтров.'),
    )
    label = models.CharField(
        _('Название'),
        max_length=LABEL_MAX_LENGTH,
        help_text=_('Отображаемое название типа проекта.'),
    )

    class Meta:
        verbose_name = _('Тип проекта')
        verbose_name_plural = _('Типы проектов')
        ordering = ('label', 'pk')

    def __str__(self) -> str:
        return self.label


class Tag(models.Model):
    """Справочник тегов для фильтрации и маркировки проектов."""

    slug = models.SlugField(
        _('Идентификатор'),
        max_length=REFERENCE_SLUG_MAX_LENGTH,
        unique=True,
        help_text=_('Уникальный идентификатор тега для API и фильтров.'),
    )
    label = models.CharField(
        _('Название'),
        max_length=LABEL_MAX_LENGTH,
        help_text=_('Отображаемое название тега.'),
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('label', 'pk')

    def __str__(self) -> str:
        return self.label


class Project(models.Model):
    """Проект, который показывается в каталоге и на детальной странице."""

    slug = models.SlugField(
        _('Slug'),
        max_length=PROJECT_SLUG_MAX_LENGTH,
        unique=True,
        help_text=_('Уникальный идентификатор проекта для URL.'),
    )
    title = models.CharField(
        _('Название'),
        max_length=TITLE_MAX_LENGTH,
        db_index=True,
        help_text=_('Название проекта для списка и детальной страницы.'),
    )
    description = models.CharField(
        _('Краткое описание'),
        max_length=DESCRIPTION_MAX_LENGTH,
        help_text=_('Описание проекта для карточек и верхнего блока детальной страницы.'),
    )
    year = models.PositiveSmallIntegerField(
        _('Год'),
        help_text=_('Год реализации или публикации проекта.'),
    )
    cover_image = models.URLField(
        _('Обложка'),
        max_length=URL_MAX_LENGTH,
        help_text=_('URL главного изображения проекта.'),
    )
    project_type = models.ForeignKey(
        ProjectType,
        on_delete=models.PROTECT,
        related_name='projects',
        verbose_name=_('Тип проекта'),
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='projects',
        verbose_name=_('Теги'),
        blank=True,
    )
    is_published = models.BooleanField(
        _('Опубликован'),
        default=True,
        db_index=True,
        help_text=_('Неопубликованные проекты не попадают в публичный API.'),
    )

    class Meta:
        verbose_name = _('Проект')
        verbose_name_plural = _('Проекты')
        ordering = ('title', 'pk')
        indexes = [
            models.Index(fields=('is_published', 'slug')),
            models.Index(fields=('is_published', 'title')),
        ]

    def __str__(self) -> str:
        return self.title


class ProjectContentBlock(models.Model):
    """Контентный блок детальной страницы проекта."""

    class Variant(models.IntegerChoices):
        """Поддерживаемые варианты разметки контентного блока."""

        IMAGE_WITH_LIST = BLOCK_VARIANT_IMAGE_WITH_LIST, _('Изображение и список')
        TWO_IMAGES = BLOCK_VARIANT_TWO_IMAGES, _('Два изображения')
        IMAGE_WITH_BUTTONS = BLOCK_VARIANT_IMAGE_WITH_BUTTONS, _('Изображение и кнопки')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='content_blocks',
        verbose_name=_('Проект'),
    )
    variant = models.PositiveSmallIntegerField(
        _('Вариант'),
        choices=Variant.choices,
        help_text=_('Вариант разметки, который использует фронтенд.'),
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=DEFAULT_ORDER,
        db_index=True,
        help_text=_('Порядок блока внутри проекта. Используется для сортировки и генерации index.'),
    )
    title = models.CharField(
        _('Заголовок'),
        max_length=CONTENT_BLOCK_TITLE_MAX_LENGTH,
        help_text=_('Заголовок секции проекта.'),
    )
    image = models.URLField(
        _('Основное изображение'),
        max_length=URL_MAX_LENGTH,
        help_text=_('Основное изображение блока.'),
    )
    left_image = models.URLField(
        _('Дополнительное изображение'),
        max_length=URL_MAX_LENGTH,
        blank=True,
        help_text=_('Второе изображение для варианта с двумя картинками.'),
    )
    string_list = models.JSONField(
        _('Список тезисов'),
        default=list,
        blank=True,
        help_text=_('Список строк для варианта с изображением и списком.'),
    )
    text = models.TextField(
        _('Текст'),
        blank=True,
        help_text=_('Основной HTML-текст блока.'),
    )
    accented_text = models.TextField(
        _('Акцентный текст'),
        blank=True,
        help_text=_('Дополнительный акцентный HTML-текст блока.'),
    )

    class Meta:
        verbose_name = _('Контентный блок проекта')
        verbose_name_plural = _('Контентные блоки проектов')
        ordering = ('order', 'pk')
        indexes = [
            models.Index(fields=('project', 'order')),
        ]

    def __str__(self) -> str:
        return f'{self.project}: {self.title}'

    def clean(self) -> None:
        """Проверяет согласованность полей для выбранного варианта блока."""
        super().clean()
        try:
            validate_string_list(self.string_list)
        except ValidationError as error:
            raise ValidationError({'string_list': error.messages}) from error
        if self.variant == self.Variant.IMAGE_WITH_LIST and not self.string_list:
            raise ValidationError({'string_list': ('Для варианта 1 требуется хотя бы один элемент списка.')})
        if self.variant != self.Variant.IMAGE_WITH_LIST and self.string_list:
            raise ValidationError({'string_list': ('Список тезисов допустим только для варианта 1.')})
        if self.variant == self.Variant.TWO_IMAGES and not self.left_image:
            raise ValidationError({'left_image': 'Для варианта 2 требуется второе изображение.'})
        if self.variant != self.Variant.TWO_IMAGES and self.left_image:
            raise ValidationError({'left_image': ('Второе изображение допустимо только для варианта 2.')})

    def save(self, *args, **kwargs):
        """Автоматически назначает порядок блока в пределах проекта."""
        if not self.order:
            max_order = (
                ProjectContentBlock.objects.filter(project=self.project)
                .aggregate(max_order=Max('order'))
                .get('max_order')
                or DEFAULT_ORDER
            )
            self.order = max_order + ORDER_STEP
        self.full_clean()
        super().save(*args, **kwargs)


class ProjectBlockButton(models.Model):
    """Кнопка действия внутри контентного блока проекта."""

    class ButtonType(models.TextChoices):
        """Поддерживаемые типы кнопок блока."""

        DOWNLOAD = 'download', _('Скачать файл')
        REDIRECT = 'redirect', _('Перейти по ссылке')

    block = models.ForeignKey(
        ProjectContentBlock,
        on_delete=models.CASCADE,
        related_name='buttons',
        verbose_name=_('Контентный блок'),
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=DEFAULT_ORDER,
        db_index=True,
        help_text=_('Порядок кнопки внутри блока.'),
    )
    label = models.CharField(
        _('Подпись'),
        max_length=LABEL_MAX_LENGTH,
        help_text=_('Текст кнопки для фронтенда.'),
    )
    type = models.CharField(
        _('Тип'),
        max_length=BUTTON_TYPE_MAX_LENGTH,
        choices=ButtonType.choices,
        help_text=_('Тип действия кнопки.'),
    )
    url = models.URLField(
        _('URL'),
        max_length=URL_MAX_LENGTH,
        help_text=_('Ссылка для скачивания или перехода.'),
    )

    class Meta:
        verbose_name = _('Кнопка контентного блока')
        verbose_name_plural = _('Кнопки контентных блоков')
        ordering = ('order', 'pk')
        indexes = [models.Index(fields=('block', 'order'))]

    def __str__(self) -> str:
        return self.label

    def save(self, *args, **kwargs):
        """Автоматически назначает порядок кнопки в пределах блока."""
        if not self.order:
            max_order = (
                ProjectBlockButton.objects.filter(block=self.block).aggregate(max_order=Max('order')).get('max_order')
                or DEFAULT_ORDER
            )
            self.order = max_order + ORDER_STEP
        self.full_clean()
        super().save(*args, **kwargs)
