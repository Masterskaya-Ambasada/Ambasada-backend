import os
from functools import partial

from core.validators import MediaFileValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from home.constants import (
    BUTTON_LABEL_MAX_LENGTH,
    DEFAULT_ABOUT_TEXT,
    DEFAULT_ABOUT_TITLE,
    DEFAULT_HERO_BUTTON_LABEL,
    DEFAULT_HERO_BUTTON_LINK,
    DEFAULT_HERO_SUBTITLE,
    DEFAULT_HERO_TITLE,
    DEFAULT_PROJECTS_BUTTON_LABEL,
    DEFAULT_PROJECTS_LINK,
    DEFAULT_PROJECTS_TITLE,
    FIELD_ABOUT_IMG_HELP,
    FIELD_ABOUT_TEXT_HELP,
    FIELD_ABOUT_TITLE_HELP,
    FIELD_HERO_BTN_LABEL_HELP,
    FIELD_HERO_BTN_LINK_HELP,
    FIELD_HERO_IMG_LEFT_HELP,
    FIELD_HERO_IMG_RIGHT_HELP,
    FIELD_HERO_SUBTITLE_HELP,
    FIELD_HERO_TITLE_HELP,
    FIELD_PROJECTS_BTN_LABEL_HELP,
    FIELD_PROJECTS_BTN_LINK_HELP,
    FIELD_PROJECTS_TITLE_HELP,
    HOME_PAGE_SINGLETON_PK,
    LINK_MAX_LENGTH,
    SUBTITLE_MAX_LENGTH,
    TEXT_PREVIEW_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    UPLOAD_HOME_ABOUT,
    UPLOAD_HOME_HERO,
    VALIDATION_DELETE_ERROR,
)


def home_hero_path(instance, filename):
    """Временный fallback для старой миграции 0001_initial."""
    return f'home/{filename}'


def get_upload_path(upload_path, instance, filename):
    """Возвращает путь для загрузки медиа контента."""
    return os.path.join(upload_path, filename)


class HomePageContent(models.Model):
    """Контент главной страницы сайта (Singleton)."""

    # --- СЕКЦИЯ 1: HERO (ГЛАВНЫЙ ЭКРАН) ---
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        default=DEFAULT_HERO_TITLE,
        verbose_name=_('Hero: Главный заголовок'),
        help_text=FIELD_HERO_TITLE_HELP,
    )
    subtitle = models.CharField(
        max_length=SUBTITLE_MAX_LENGTH,
        default=DEFAULT_HERO_SUBTITLE,
        verbose_name=_('Hero: Подзаголовок (Описание)'),
        help_text=FIELD_HERO_SUBTITLE_HELP,
    )
    image_left = models.ImageField(
        upload_to=partial(get_upload_path, UPLOAD_HOME_HERO),
        validators=[MediaFileValidator()],
        verbose_name=_('Hero: Изображение (Левое)'),
        help_text=FIELD_HERO_IMG_LEFT_HELP,
    )
    image_right = models.ImageField(
        upload_to=partial(get_upload_path, UPLOAD_HOME_HERO),
        validators=[MediaFileValidator()],
        verbose_name=_('Hero: Изображение (Правое)'),
        help_text=FIELD_HERO_IMG_RIGHT_HELP,
    )
    hero_button_label = models.CharField(
        max_length=BUTTON_LABEL_MAX_LENGTH,
        default=DEFAULT_HERO_BUTTON_LABEL,
        verbose_name=_('Hero: Текст на кнопке'),
        help_text=FIELD_HERO_BTN_LABEL_HELP,
    )
    hero_button_link = models.CharField(
        max_length=LINK_MAX_LENGTH,
        default=DEFAULT_HERO_BUTTON_LINK,
        verbose_name=_('Hero: Ссылка с кнопки'),
        help_text=FIELD_HERO_BTN_LINK_HELP,
    )

    # --- СЕКЦИЯ 2: ABOUT PREVIEW (О НАС) ---
    about_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        default=DEFAULT_ABOUT_TITLE,
        verbose_name=_('О нас: Заголовок секции'),
        help_text=FIELD_ABOUT_TITLE_HELP,
    )
    about_text = models.TextField(
        max_length=TEXT_PREVIEW_MAX_LENGTH,
        default=DEFAULT_ABOUT_TEXT,
        verbose_name=_('О нас: Краткий текст превью'),
        help_text=FIELD_ABOUT_TEXT_HELP,
    )
    about_image = models.ImageField(
        upload_to=partial(get_upload_path, UPLOAD_HOME_ABOUT),
        validators=[MediaFileValidator()],
        verbose_name=_('О нас: Изображение секции'),
        help_text=FIELD_ABOUT_IMG_HELP,
    )

    # --- СЕКЦИЯ 3: PROJECTS PREVIEW (ПРОЕКТЫ) ---
    projects_title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        default=DEFAULT_PROJECTS_TITLE,
        verbose_name=_('Проекты: Заголовок секции'),
        help_text=FIELD_PROJECTS_TITLE_HELP,
    )
    projects_button_label = models.CharField(
        max_length=BUTTON_LABEL_MAX_LENGTH,
        default=DEFAULT_PROJECTS_BUTTON_LABEL,
        verbose_name=_('Проекты: Текст на кнопке'),
        help_text=FIELD_PROJECTS_BTN_LABEL_HELP,
    )
    projects_button_link = models.CharField(
        max_length=LINK_MAX_LENGTH,
        default=DEFAULT_PROJECTS_LINK,
        verbose_name=_('Проекты: Ссылка с кнопки'),
        help_text=FIELD_PROJECTS_BTN_LINK_HELP,
    )

    class Meta:
        verbose_name = _('Контент главной страницы')
        verbose_name_plural = _('Контент главной страницы')

    def save(self, *args, **kwargs):
        """Принудительно сохраняет запись с фиксированным PK (Singleton)."""
        self.pk = HOME_PAGE_SINGLETON_PK
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Блокирует удаление единственной конфигурационной записи."""
        if self.pk == HOME_PAGE_SINGLETON_PK:
            raise ValidationError(VALIDATION_DELETE_ERROR)
        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self._meta.verbose_name)


class HomePageProject(models.Model):
    """Проект, выбранный для показа в блоке проектов на главной странице."""

    home_page = models.ForeignKey(
        HomePageContent,
        on_delete=models.CASCADE,
        related_name='project_items',
        verbose_name=_('Контент главной страницы'),
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='home_page_items',
        verbose_name=_('Проект'),
    )
    order = models.PositiveSmallIntegerField(
        _('Порядок отображения'),
        default=0,
        help_text=_('Меньшее число показывает проект выше в блоке на главной странице.'),
    )

    class Meta:
        verbose_name = _('Проект на главной странице')
        verbose_name_plural = _('Проекты на главной странице')
        ordering = ('order', 'pk')
        constraints = [
            models.UniqueConstraint(
                fields=('home_page', 'project'),
                name='unique_home_page_project',
            ),
        ]

    def __str__(self):
        return f'{self.order}: {self.project}'
