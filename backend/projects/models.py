"""Модели проектов и связанных сущностей для API."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max

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
        'Идентификатор',
        max_length=REFERENCE_SLUG_MAX_LENGTH,
        unique=True,
        help_text='Уникальный идентификатор типа проекта для API и фильтров.',
    )
    label = models.CharField(
        'Название',
        max_length=LABEL_MAX_LENGTH,
        help_text='Отображаемое название типа проекта.',
    )

    class Meta:
        verbose_name = 'Тип проекта'
        verbose_name_plural = 'Типы проектов'
        ordering = ('label', 'pk')

    def __str__(self) -> str:
        return self.label


class Tag(models.Model):
    """Справочник тегов для фильтрации и маркировки проектов."""

    slug = models.SlugField(
        'Идентификатор',
        max_length=REFERENCE_SLUG_MAX_LENGTH,
        unique=True,
        help_text='Уникальный идентификатор тега для API и фильтров.',
    )
    label = models.CharField(
        'Название',
        max_length=LABEL_MAX_LENGTH,
        help_text='Отображаемое название тега.',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('label', 'pk')

    def __str__(self) -> str:
        return self.label


class Project(models.Model):
    """Проект, который показывается в каталоге и на детальной странице."""

    slug = models.SlugField(
        'Slug',
        max_length=PROJECT_SLUG_MAX_LENGTH,
        unique=True,
        help_text='Уникальный идентификатор проекта для URL.',
    )
    title = models.CharField(
        'Название',
        max_length=TITLE_MAX_LENGTH,
        db_index=True,
        help_text='Название проекта для списка и детальной страницы.',
    )
    description = models.CharField(
        'Краткое описание',
        max_length=DESCRIPTION_MAX_LENGTH,
        help_text=('Описание проекта для карточек и верхнего блока детальной страницы.'),
    )
    year = models.PositiveSmallIntegerField(
        'Год',
        help_text='Год реализации или публикации проекта.',
    )
    cover_image = models.URLField(
        'Обложка',
        max_length=URL_MAX_LENGTH,
        help_text='URL главного изображения проекта.',
    )
    project_type = models.ForeignKey(
        ProjectType,
        on_delete=models.PROTECT,
        related_name='projects',
        verbose_name='Тип проекта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='projects',
        verbose_name='Теги',
        blank=True,
    )
    is_published = models.BooleanField(
        'Опубликован',
        default=True,
        db_index=True,
        help_text='Неопубликованные проекты не попадают в публичный API.',
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
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

        IMAGE_WITH_LIST = BLOCK_VARIANT_IMAGE_WITH_LIST, 'Изображение и список'
        TWO_IMAGES = BLOCK_VARIANT_TWO_IMAGES, 'Два изображения'
        IMAGE_WITH_BUTTONS = BLOCK_VARIANT_IMAGE_WITH_BUTTONS, 'Изображение и кнопки'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='content_blocks',
        verbose_name='Проект',
    )
    variant = models.PositiveSmallIntegerField(
        'Вариант',
        choices=Variant.choices,
        help_text='Вариант разметки, который использует фронтенд.',
    )
    order = models.PositiveIntegerField(
        'Порядок',
        default=DEFAULT_ORDER,
        db_index=True,
        help_text=('Порядок блока внутри проекта. Используется для сортировки и генерации index.'),
    )
    title = models.CharField(
        'Заголовок',
        max_length=CONTENT_BLOCK_TITLE_MAX_LENGTH,
        help_text='Заголовок секции проекта.',
    )
    image = models.URLField(
        'Основное изображение',
        max_length=URL_MAX_LENGTH,
        help_text='Основное изображение блока.',
    )
    left_image = models.URLField(
        'Дополнительное изображение',
        max_length=URL_MAX_LENGTH,
        blank=True,
        help_text='Второе изображение для варианта с двумя картинками.',
    )
    string_list = models.JSONField(
        'Список тезисов',
        default=list,
        blank=True,
        help_text='Список строк для варианта с изображением и списком.',
    )
    text = models.TextField(
        'Текст',
        blank=True,
        help_text='Основной HTML-текст блока.',
    )
    accented_text = models.TextField(
        'Акцентный текст',
        blank=True,
        help_text='Дополнительный акцентный HTML-текст блока.',
    )

    class Meta:
        verbose_name = 'Контентный блок проекта'
        verbose_name_plural = 'Контентные блоки проектов'
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

        DOWNLOAD = 'download', 'Скачать файл'
        REDIRECT = 'redirect', 'Перейти по ссылке'

    block = models.ForeignKey(
        ProjectContentBlock,
        on_delete=models.CASCADE,
        related_name='buttons',
        verbose_name='Контентный блок',
    )
    order = models.PositiveIntegerField(
        'Порядок',
        default=DEFAULT_ORDER,
        db_index=True,
        help_text='Порядок кнопки внутри блока.',
    )
    label = models.CharField(
        'Подпись',
        max_length=LABEL_MAX_LENGTH,
        help_text='Текст кнопки для фронтенда.',
    )
    type = models.CharField(
        'Тип',
        max_length=BUTTON_TYPE_MAX_LENGTH,
        choices=ButtonType.choices,
        help_text='Тип действия кнопки.',
    )
    url = models.URLField(
        'URL',
        max_length=URL_MAX_LENGTH,
        help_text='Ссылка для скачивания или перехода.',
    )

    class Meta:
        verbose_name = 'Кнопка контентного блока'
        verbose_name_plural = 'Кнопки контентных блоков'
        ordering = ('order', 'pk')
        indexes = [models.Index(fields=('block', 'order')),]

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
