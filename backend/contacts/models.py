from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from . import constants


class ContactRequest(models.Model):
    """Модель для формы обратной связи."""

    name = models.CharField(
        max_length=constants.MAX_NAME_LENGTH,
        verbose_name=_('Имя'),
    )
    email = models.EmailField(
        verbose_name=_('Email'),
    )
    message = models.TextField(
        max_length=constants.MAX_MESSAGE_LENGTH,
        verbose_name=_('Сообщение'),
        help_text=constants.HELP_REQUEST_MESSAGE,
    )

    message = models.TextField(
        verbose_name=_('Сообщение'),
        help_text=constants.HELP_REQUEST_MESSAGE,
        validators=[
            MinLengthValidator(
                limit_value=constants.MIN_MESSAGE_LENGTH,
                message=constants.ERROR_MESSAGE_MIN_LENGTH,
            ),
            MaxLengthValidator(
                limit_value=constants.MAX_MESSAGE_LENGTH,
                message=constants.ERROR_MESSAGE_MAX_LENGTH,
            ),
        ],
    )
    reason = models.CharField(
        max_length=constants.MAX_REASON_LENGTH,
        verbose_name=_('Причина обращения'),
    )
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_('Обработано'),
        help_text=constants.HELP_REQUEST_IS_PROCESSED,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания'),
    )

    class Meta:
        verbose_name = _('Запрос обратной связи')
        verbose_name_plural = _('Запросы обратной связи')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.name} от <{self.email}>'


class ContactPageContent(models.Model):
    """Сингл активный блок пожертвований."""

    donation_text = models.TextField(
        blank=True,
        verbose_name=_('Текстовый блок для пожертвований'),
        help_text=constants.HELP_CONTENT_DONATION_TEXT,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активно'),
        help_text=constants.HELP_CONTENT_IS_ACTIVE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления'),
    )

    def save(self, *args, **kwargs):
        """Автопереключение активного блока."""
        if self.is_active:
            with transaction.atomic():
                ContactPageContent.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Редактируемая ссылка на пожертвования')
        verbose_name_plural = _('Редактируемые ссылки на пожертвования')
        ordering = ('-updated_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['is_active'],
                condition=Q(is_active=True),
                name='unique_active_contact_page_content',
                violation_error_message=constants.ERROR_MULTIPLE_ACTIVE_DONATIONS,
            )
        ]

    def __str__(self):
        return (
            self.donation_text[: constants.DONATION_TEXT_PREVIEW_LENGTH]
            if self.donation_text
            else str(self._meta.verbose_name)
        )


def get_default_site_config():
    """Возвращает единственный доступный объект SiteConfig."""
    from site_config.models import SiteConfig

    return SiteConfig.objects.first()


class ContactSocialLink(models.Model):
    """Ссылки на соцсети и мессенджеры проекта."""

    class SocialType(models.TextChoices):
        TELEGRAM = 'telegram', _('Telegram')
        INSTAGRAM = 'instagram', _('Instagram')
        FACEBOOK = 'facebook', _('Facebook')
        LINKEDIN = 'linkedin', _('LinkedIn')
        EMAIL = 'email', _('Email')

    site_config = models.ForeignKey(
        'site_config.SiteConfig',
        on_delete=models.CASCADE,
        related_name='socials',
        verbose_name=_('Настройки сайта'),
        default=get_default_site_config,
    )
    social_type = models.CharField(
        max_length=constants.SOCIAL_TYPE_MAX_LENGTH,
        choices=SocialType.choices,
        verbose_name=_('Тип соцсети / мессенджера'),
        help_text=constants.HELP_SOCIAL_TYPE,
    )
    url = models.URLField(
        verbose_name=_('Ссылка'),
        help_text=constants.HELP_SOCIAL_URL,
    )
    order = models.PositiveSmallIntegerField(
        default=constants.DEFAULT_ORDER_VALUE_CONTACT_SOCIAL_LINK,
        verbose_name=_('Порядок отображения'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Показывать на сайте'),
        help_text=constants.HELP_SOCIAL_IS_ACTIVE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания'),
    )

    class Meta:
        verbose_name = _('Ссылка на соцсеть / мессенджер')
        verbose_name_plural = _('Ссылки на соцсети / мессенджеры')
        ordering = ('order', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=['site_config', 'social_type'],
                name='unique_site_config_social_type',
                violation_error_message=constants.ERROR_DUPLICATE_SOCIAL_TYPE,
            ),
            models.UniqueConstraint(
                fields=['site_config', 'order'],
                name='unique_site_config_social_order',
                violation_error_message=constants.ERROR_DUPLICATE_SOCIAL_ORDER,
            ),
        ]

    def clean(self):
        """Гарантирует привязку к дефолтному конфигу, если запись создается напрямую."""
        super().clean()

        if not self.site_config_id:
            site_config = get_default_site_config()
            if not site_config:
                raise ValidationError({NON_FIELD_ERRORS: constants.ERROR_MISSING_SITE_CONFIG})
            self.site_config = site_config

    def __str__(self):
        return f'{self.get_social_type_display()} - {self.url}'
