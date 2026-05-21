from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from contacts.constants import MAX_MESSAGE_LENGTH, MAX_NAME_LENGTH, MAX_REASON_LENGTH, SOCIAL_TYPE_MAX_LENGTH


class ContactRequest(models.Model):
    """Модель для формы обратной связи."""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name=_('Имя'),
    )
    email = models.EmailField(
        verbose_name=_('Email'),
    )
    message = models.TextField(
        max_length=MAX_MESSAGE_LENGTH,
        verbose_name=_('Сообщение'),
        validators=[MaxLengthValidator(MAX_MESSAGE_LENGTH)],
        help_text=_('Введите сообщение'),
    )
    reason = models.CharField(
        max_length=MAX_REASON_LENGTH,
        verbose_name=_('Причина обращения'),
    )
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_('Обработано'),
        help_text=_('Показывает, обработано ли обращение.'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Запрос обратной связи')
        verbose_name_plural = _('Запросы обратной связи')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.name} <{self.email}> - {self.reason}'


class ContactPageContent(models.Model):
    """Ссылка на пожертвования с возможностью редактирования в админке."""

    donation_text = models.TextField(
        blank=True,
        verbose_name=_('Текстовый блок для пожертвований'),
        help_text=_('Редактируемый текст с возможностью добавить внешнюю ссылку.'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активно'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления'),
    )

    class Meta:
        verbose_name = _('Редактируемая ссылка на пожертвования')
        verbose_name_plural = _('Редактируемые ссылки на пожертвования')
        ordering = ('-updated_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['is_active'],
                condition=Q(is_active=True),
                name='only_one_active_contact_page_content',
            )
        ]

    def __str__(self):
        return str(self._meta.verbose_name)

    def save(self, *args, **kwargs):
        if self.is_active:
            from django.db import transaction

            with transaction.atomic():
                ContactPageContent.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class ContactSocialLink(models.Model):
    """Ссылки на соцсети и мессенджеры проекта."""

    class SocialType(models.TextChoices):
        TELEGRAM = 'telegram', _('Telegram')
        INSTAGRAM = 'instagram', _('Instagram')
        FACEBOOK = 'facebook', _('Facebook')
        LINKEDIN = 'linkedin', _('LinkedIn')

    site_config = models.ForeignKey(
        'site_config.SiteConfig',
        on_delete=models.CASCADE,
        related_name='socials',
        verbose_name='Настройки сайта',
    )
    social_type = models.CharField(
        max_length=SOCIAL_TYPE_MAX_LENGTH,
        choices=SocialType.choices,
        verbose_name=_('Тип соцсети / мессенджера'),
        help_text=_('Выбор соцсети.'),
    )
    url = models.URLField(
        verbose_name=_('Ссылка'),
        help_text=_('Например: https://t.me/tme'),
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Порядок отображения'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Показывать на сайте'),
        help_text=_(
            'Если галочка включена — ссылка отображается на странице контактов. '
            'Если выключена — ссылка скрыта, но не удаляется.'
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания'),
    )

    def clean(self):
        super().clean()
        if not hasattr(self, 'site_config') or self.site_config is None:
            from site_config.models import SiteConfig

            self.site_config = SiteConfig.objects.first()

        if self.site_config:
            qs = ContactSocialLink.objects.filter(site_config=self.site_config, social_type=self.social_type)

            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError(
                    {
                        'social_type': _(
                            'Ссылка для этого типа соцсети уже добавлена. Вы можете отредактировать существующую запись'
                        )
                    }
                )

    class Meta:
        verbose_name = _('Ссылка на соцсеть / мессенджер')
        verbose_name_plural = _('Ссылки на соцсети / мессенджеры')
        ordering = ('order', 'id')

        constraints = [
            models.UniqueConstraint(
                fields=['site_config', 'social_type'],
                name='unique_site_config_social_type',
                violation_error_message=_('Ссылка для этого типа соцсети уже добавлена.'),
            ),
            models.UniqueConstraint(
                fields=['order'],
                name='unique_contact_social_link_order',
                violation_error_message=_('Этот порядок отображения уже занят. Укажите другое число.'),
            ),
        ]

    def __str__(self):
        return f'{self.get_social_type_display()} - {self.url}'
