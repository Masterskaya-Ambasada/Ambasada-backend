from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    CONTACT_BUTTON_LABEL_MAX_LENGTH,
    CONTACT_LINK_MAX_LENGTH,
    COOKIE_BUTTON_TEXT_MAX_LENGTH,
    COPYRIGHT_MAX_LENGTH,
    DEFAULT_ABOUT_TEAM_BUTTON_LABEL,
    DEFAULT_COOKIE_BUTTON_TEXT,
    DEFAULT_COOKIE_MESSAGE,
    DEFAULT_COPYRIGHT_TEXT,
    DEFAULT_MAIN_TEAM_BUTTON_LABEL,
    DEFAULT_TEAM_BUTTON_LINK,
    DEFAULT_TEAM_TITLE,
    HELP_ABOUT_TEAM_BUTTON,
    HELP_COOKIE_BUTTON_TEXT,
    HELP_COOKIE_MESSAGE,
    HELP_COPYRIGHT,
    HELP_MAIN_TEAM_BUTTON,
    HELP_PRIVACY_POLICY,
    HELP_SEO_DESCRIPTION,
    HELP_SITE_NAME,
    HELP_TEAM_BUTTON_LINK,
    HELP_TEAM_TITLE,
    SEO_DESCRIPTION_MAX_LENGTH,
    SITE_CONFIG_SINGLETON_PK,
    SITE_NAME_MAX_LENGTH,
    TEAM_TITLE_MAX_LENGTH,
    VALIDATION_SITE_DELETE_ERROR,
)


class SiteConfig(models.Model):
    """Глобальные настройки сайта (True Singleton для продакшена)."""

    # --- ОСНОВНЫЕ НАСТРОЙКИ И SEO ---
    site_name = models.CharField(
        max_length=SITE_NAME_MAX_LENGTH,
        verbose_name=_('Название сайта'),
        help_text=HELP_SITE_NAME,
    )
    seo_description = models.CharField(
        max_length=SEO_DESCRIPTION_MAX_LENGTH,
        verbose_name=_('SEO описание'),
        help_text=HELP_SEO_DESCRIPTION,
    )
    privacy_policy = models.TextField(
        verbose_name=_('Согласие на обработку персональных данных'),
        default='',
        help_text=HELP_PRIVACY_POLICY,
    )

    # --- COOKIES И ПОДВАЛ (FOOTER) ---
    cookie_message = models.TextField(
        verbose_name=_('Текст cookie-сообщения'),
        default=DEFAULT_COOKIE_MESSAGE,
        help_text=HELP_COOKIE_MESSAGE,
    )
    cookie_button_text = models.CharField(
        max_length=COOKIE_BUTTON_TEXT_MAX_LENGTH,
        verbose_name=_('Текст кнопки cookie'),
        default=DEFAULT_COOKIE_BUTTON_TEXT,
        help_text=HELP_COOKIE_BUTTON_TEXT,
    )
    copyright = models.CharField(
        max_length=COPYRIGHT_MAX_LENGTH,
        default=DEFAULT_COPYRIGHT_TEXT,
        verbose_name=_('Копирайт'),
        help_text=HELP_COPYRIGHT,
    )

    # --- СЕКЦИЯ КОМАНДЫ (TEAM) ---
    team_title = models.CharField(
        max_length=TEAM_TITLE_MAX_LENGTH,
        default=DEFAULT_TEAM_TITLE,
        verbose_name=_('Заголовок секции "Команда"'),
        help_text=HELP_TEAM_TITLE,
    )
    main_team_button_label = models.CharField(
        max_length=CONTACT_BUTTON_LABEL_MAX_LENGTH,
        default=DEFAULT_MAIN_TEAM_BUTTON_LABEL,
        verbose_name=_('Главная: Кнопка команды (текст)'),
        help_text=HELP_MAIN_TEAM_BUTTON,
    )
    about_team_button_label = models.CharField(
        max_length=CONTACT_BUTTON_LABEL_MAX_LENGTH,
        default=DEFAULT_ABOUT_TEAM_BUTTON_LABEL,
        verbose_name=_('О нас: Кнопка команды (текст)'),
        help_text=HELP_ABOUT_TEAM_BUTTON,
    )
    team_button_link = models.CharField(
        max_length=CONTACT_LINK_MAX_LENGTH,
        default=DEFAULT_TEAM_BUTTON_LINK,
        verbose_name=_('Кнопка команды (ссылка)'),
        help_text=HELP_TEAM_BUTTON_LINK,
    )

    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')

    def save(self, *args, **kwargs):
        """Гарантирует уникальность записи на уровне PK и сбрасывает кэш."""
        self.pk = SITE_CONFIG_SINGLETON_PK
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Запрещает удаление только основной системной записи."""
        if self.pk == SITE_CONFIG_SINGLETON_PK:
            raise ValidationError(VALIDATION_SITE_DELETE_ERROR)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.site_name
