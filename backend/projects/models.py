"""Модели проектов и связанных сущностей для API."""

from __future__ import annotations

import shutil
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Max
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_jsonform.models.fields import JSONField

from projects.constants import (
    BLOCK_VARIANT_IMAGE_WITH_BUTTONS,
    BLOCK_VARIANT_IMAGE_WITH_LIST,
    BLOCK_VARIANT_TWO_IMAGES,
    BUTTON_TYPE_DOWNLOAD,
    BUTTON_TYPE_MAX_LENGTH,
    BUTTON_TYPE_REDIRECT,
    CONTENT_BLOCK_TITLE_MAX_LENGTH,
    DEFAULT_ORDER,
    DESCRIPTION_MAX_LENGTH,
    JSONFORM_TEXTAREA_ROWS,
    LABEL_MAX_LENGTH,
    ORDER_STEP,
    PROJECT_BLOCK_FALLBACK_SLUG,
    PROJECT_BLOCKS_DIRECTORY,
    PROJECT_COVER_DIRECTORY,
    PROJECT_GALLERY_DIRECTORY,
    PROJECT_MEDIA_DIRECTORY,
    PROJECT_SLUG_MAX_LENGTH,
    REFERENCE_SLUG_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    URL_MAX_LENGTH,
)

from .validators import validate_string_list


def _get_max_order(queryset: models.QuerySet, related_field_name: str, related_id: int) -> int:
    """Возвращает максимальный order в пределах связанного объекта."""
    return (
        queryset.filter(**{f'{related_field_name}_id': related_id}).aggregate(max_order=Max('order')).get('max_order')
        or DEFAULT_ORDER
    )


def _assign_next_order(instance: models.Model, queryset: models.QuerySet, related_field_name: str) -> None:
    """Назначает следующий order, если он не задан явно."""
    if instance.order:
        return
    related_id = getattr(instance, f'{related_field_name}_id')
    if related_id is None:
        return
    instance.order = _get_max_order(queryset, related_field_name, related_id) + ORDER_STEP


def _project_media_path(slug: str) -> Path:
    """Возвращает безопасный путь к медиа-папке проекта."""
    media_root = Path(settings.MEDIA_ROOT).resolve()
    project_dir = (media_root / PROJECT_MEDIA_DIRECTORY / slug).resolve()
    if not project_dir.is_relative_to(media_root):
        raise ValidationError(_('Некорректный путь к медиа-папке проекта.'))
    return project_dir


def _delete_project_media_directory(slug: str) -> None:
    """Удаляет папку проекта из MEDIA_ROOT."""
    project_dir = _project_media_path(slug)
    if project_dir.exists():
        shutil.rmtree(project_dir)


def _merge_directories(source: Path, destination: Path) -> None:
    """Перемещает содержимое source в destination, сохраняя уже существующие новые файлы."""
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        target = destination / child.name
        if child.is_dir() and target.is_dir():
            _merge_directories(child, target)
            child.rmdir()
            continue
        if target.exists():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
            continue
        shutil.move(str(child), str(target))
    source.rmdir()


def _move_project_media_directory(old_slug: str, new_slug: str) -> None:
    """Переименовывает медиа папку проекта при изменении slug."""
    old_dir = _project_media_path(old_slug)
    if not old_dir.exists():
        return
    new_dir = _project_media_path(new_slug)
    if old_dir == new_dir:
        return
    if new_dir.exists():
        _merge_directories(old_dir, new_dir)
        return
    new_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(old_dir), str(new_dir))


def _replace_project_media_slug(file_name: str | None, old_slug: str, new_slug: str) -> str | None:
    """Обновляет slug в сохраненном пути файла проекта."""
    if not file_name:
        return file_name
    old_prefix = f'{PROJECT_MEDIA_DIRECTORY}/{old_slug}/'
    if not file_name.startswith(old_prefix):
        return file_name
    return f'{PROJECT_MEDIA_DIRECTORY}/{new_slug}/{file_name[len(old_prefix):]}'


def project_cover_image_path(instance: 'Project', filename: str) -> str:
    """Путь загрузки обложки проекта."""
    return f'{PROJECT_MEDIA_DIRECTORY}/{instance.slug}/{PROJECT_COVER_DIRECTORY}/{filename}'


def project_gallery_image_path(instance: 'ProjectGalleryImage', filename: str) -> str:
    """Путь загрузки изображений галереи проекта."""
    return f'{PROJECT_MEDIA_DIRECTORY}/{instance.project.slug}/{PROJECT_GALLERY_DIRECTORY}/{filename}'


def project_block_image_path(instance: 'ProjectContentBlock', filename: str) -> str:
    """Путь загрузки изображений контентных блоков проекта."""
    project_slug = instance.project.slug if instance.project_id else PROJECT_BLOCK_FALLBACK_SLUG
    return f'{PROJECT_MEDIA_DIRECTORY}/{project_slug}/{PROJECT_BLOCKS_DIRECTORY}/{filename}'


class OrderedValidationQuerySet(models.QuerySet):
    """QuerySet с валидацией и автонумерацией при массовом создании."""

    related_field_name: str | None = None

    def _set_missing_orders(self, objs: list[models.Model]) -> None:
        """Заполняет пропущенные порядковые номера в пределах связанного объекта."""
        if not self.related_field_name:
            return
        pending_orders: defaultdict[int, int] = defaultdict(int)
        max_orders: dict[int, int] = {}
        related_field_name = self.related_field_name
        for obj in objs:
            if obj.order:
                continue
            related_id = getattr(obj, f'{related_field_name}_id')
            if related_id is None:
                continue
            if related_id not in max_orders:
                max_orders[related_id] = _get_max_order(self, related_field_name, related_id)
            pending_orders[related_id] += ORDER_STEP
            obj.order = max_orders[related_id] + pending_orders[related_id]

    def _validate_prepared_objects(self, objs: list[models.Model]) -> None:
        """Выполняет дополнительные проверки после автозаполнения order."""

    def bulk_create(
        self,
        objs,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
    ):
        """Проверяет и подготавливает объекты перед массовым созданием."""
        objs = list(objs)
        self._set_missing_orders(objs)
        self._validate_prepared_objects(objs)
        for obj in objs:
            obj.full_clean()
        return super().bulk_create(
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
        )


class ProjectContentBlockQuerySet(OrderedValidationQuerySet):
    """QuerySet для контентных блоков проекта."""

    related_field_name = 'project'

    def _validate_prepared_objects(self, objs: list[models.Model]) -> None:
        super()._validate_prepared_objects(objs)
        seen_orders = set()
        for obj in objs:
            if not obj.project_id or not obj.order:
                continue
            order_key = (obj.project_id, obj.order)
            if order_key in seen_orders:
                raise ValidationError(
                    {'order': _('Контентные блоки одного проекта не должны иметь одинаковый порядок.')}
                )
            seen_orders.add(order_key)


class ProjectBlockButtonQuerySet(OrderedValidationQuerySet):
    """QuerySet для кнопок контентного блока."""

    related_field_name = 'block'


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
    # По контракту description - короткое описание верхнего блока, оно не подразумевает html.
    # Предлагаю оставить CharField, пока не будет известно обратное
    description = models.CharField(
        _('Краткое описание'),
        max_length=DESCRIPTION_MAX_LENGTH,
        help_text=_('Описание проекта для карточек и верхнего блока детальной страницы.'),
    )
    year = models.PositiveSmallIntegerField(
        _('Год'),
        db_index=True,
        help_text=_('Год реализации или публикации проекта.'),
    )
    cover_image = models.ImageField(
        _('Обложка'),
        upload_to=project_cover_image_path,
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
            models.Index(
                fields=('is_published', 'slug'),
                name='prj_pub_slug_idx',
            ),
            models.Index(
                fields=('is_published', 'title'),
                name='prj_pub_title_idx',
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def _get_persisted_slug(self) -> str | None:
        """Возвращает slug проекта из БД до текущего сохранения."""
        if self._state.adding or not self.pk:
            return None
        return Project.objects.filter(pk=self.pk).values_list('slug', flat=True).first()

    def _sync_media_paths_after_slug_change(self, old_slug: str) -> None:
        """Обновляет сохраненные пути файлов при переименовании slug проекта."""
        if old_slug == self.slug:
            return
        new_cover_image_name = _replace_project_media_slug(self.cover_image.name, old_slug, self.slug)
        if new_cover_image_name != self.cover_image.name:
            self.cover_image.name = new_cover_image_name
            Project.objects.filter(pk=self.pk).update(cover_image=new_cover_image_name)
        for gallery_image in self.gallery_images.all():
            new_image_name = _replace_project_media_slug(gallery_image.image.name, old_slug, self.slug)
            if new_image_name != gallery_image.image.name:
                gallery_image.image.name = new_image_name
                ProjectGalleryImage.objects.filter(pk=gallery_image.pk).update(image=new_image_name)
        for content_block in self.content_blocks.all():
            update_fields = {}
            new_image_name = _replace_project_media_slug(content_block.image.name, old_slug, self.slug)
            if new_image_name != content_block.image.name:
                content_block.image.name = new_image_name
                update_fields['image'] = new_image_name
            new_left_image_name = _replace_project_media_slug(content_block.left_image.name, old_slug, self.slug)
            if new_left_image_name != content_block.left_image.name:
                content_block.left_image.name = new_left_image_name
                update_fields['left_image'] = new_left_image_name
            if update_fields:
                ProjectContentBlock.objects.filter(pk=content_block.pk).update(**update_fields)

    def save(self, *args, **kwargs):
        """Синхронизирует медиа пути при изменении slug проекта."""
        old_slug = self._get_persisted_slug()
        super().save(*args, **kwargs)
        if old_slug and old_slug != self.slug:
            self._sync_media_paths_after_slug_change(old_slug)
            transaction.on_commit(lambda: _move_project_media_directory(old_slug, self.slug))


class ProjectGalleryImage(models.Model):
    """Изображение для карусели в верхнем блоке детальной страницы проекта."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name=_('Проект'),
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to=project_gallery_image_path,
        max_length=URL_MAX_LENGTH,
        help_text=_('Изображение для карусели проекта.'),
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=DEFAULT_ORDER,
        db_index=True,
        help_text=_('Порядок изображения в карусели проекта.'),
    )

    class Meta:
        verbose_name = _('Изображение карусели проекта')
        verbose_name_plural = _('Изображения карусели проекта')
        ordering = ('order', 'pk')
        indexes = [models.Index(fields=('project', 'order'))]

    def __str__(self) -> str:
        return f'{self.project}: {self.order}'

    def save(self, *args, **kwargs):
        """Автоматически назначает порядок изображения в пределах проекта."""
        _assign_next_order(self, ProjectGalleryImage.objects, 'project')
        self.full_clean()
        super().save(*args, **kwargs)


class ProjectContentBlock(models.Model):
    """Контентный блок детальной страницы проекта."""

    objects = ProjectContentBlockQuerySet.as_manager()

    LIST_SCHEMA = {
        'type': 'array',
        'items': {
            'type': 'string',
            'rows': JSONFORM_TEXTAREA_ROWS,
            'widget': 'textarea',
        },
    }

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
    image = models.ImageField(
        _('Основное изображение'),
        upload_to=project_block_image_path,
        max_length=URL_MAX_LENGTH,
        blank=True,  # добавил из-за проблем с импортом
        help_text=_('Основное изображение блока.'),
    )
    left_image = models.ImageField(
        _('Дополнительное изображение'),
        upload_to=project_block_image_path,
        max_length=URL_MAX_LENGTH,
        blank=True,
        help_text=_('Второе изображение для варианта с двумя картинками.'),
    )
    string_list = JSONField(
        _('Список тезисов'),
        schema=LIST_SCHEMA,
        default=list,
        blank=True,
        help_text=_(
            'Слева вводите тезисы, а справа отображается технический JSON-код для системы. Его можно не трогать.'
        ),
    )
    text = models.TextField(
        _('Текст'),
        blank=True,
        help_text=_('Основной текст блока. Обязателен для всех вариантов, поддерживает HTML через редактор.'),
    )
    accented_text = models.TextField(
        _('Акцентный текст'),
        blank=True,
        help_text=_(
            'Дополнительный выделенный текст или подпись. Используйте, если в макете нужен акцентный текст; '
            'иначе поле можно оставить пустым.'
        ),
    )

    class Meta:
        verbose_name = _('Контентный блок проекта')
        verbose_name_plural = _('Контентные блоки проектов')
        ordering = ('order', 'pk')
        constraints = [
            models.UniqueConstraint(
                fields=('project', 'order'),
                name='unique_project_content_block_order',
            ),
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
        self._validate_variant_required_fields()
        if self.project_id and self.order:
            duplicate_order_exists = (
                ProjectContentBlock.objects.filter(project_id=self.project_id, order=self.order)
                .exclude(pk=self.pk)
                .exists()
            )
            if duplicate_order_exists:
                raise ValidationError({'order': _('Контентный блок с таким порядком уже существует в этом проекте.')})

    def _validate_variant_required_fields(self) -> None:
        """Проверяет обязательные поля для выбранного варианта блока."""
        errors = {}
        if not self.image:
            errors['image'] = _('Добавьте основное изображение для выбранного варианта блока.')
        if not self.text:
            errors['text'] = _('Заполните основной текст для выбранного варианта блока.')
        if self.variant == self.Variant.IMAGE_WITH_LIST and not self.string_list:
            errors['string_list'] = _('Добавьте хотя бы один тезис для варианта "Изображение и список".')
        if self.variant == self.Variant.TWO_IMAGES and not self.left_image:
            errors['left_image'] = _('Добавьте второе изображение для варианта "Два изображения".')
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Автоматически назначает порядок блока в пределах проекта."""
        _assign_next_order(self, ProjectContentBlock.objects, 'project')
        self.full_clean()
        super().save(*args, **kwargs)


class ProjectBlockButton(models.Model):
    """Кнопка действия внутри контентного блока проекта."""

    objects = ProjectBlockButtonQuerySet.as_manager()

    class ButtonType(models.TextChoices):
        """Поддерживаемые типы кнопок блока."""

        DOWNLOAD = BUTTON_TYPE_DOWNLOAD, _('Скачать файл')
        REDIRECT = BUTTON_TYPE_REDIRECT, _('Перейти по ссылке')

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
        _assign_next_order(self, ProjectBlockButton.objects, 'block')
        self.full_clean()
        super().save(*args, **kwargs)


@receiver(post_delete, sender=Project)
def delete_project_media_directory_on_project_delete(sender, instance: Project, **kwargs) -> None:
    """Удаляет медиа папку проекта после удаления объекта Project."""
    transaction.on_commit(lambda: _delete_project_media_directory(instance.slug))
