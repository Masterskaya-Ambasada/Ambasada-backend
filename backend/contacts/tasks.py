from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from django.utils import timezone

from contacts.models import ContactRequest

MAX_NOTIFICATION_ERROR_LENGTH = 1000


@shared_task(bind=True, max_retries=3)
def send_contact_request_notification_task(self, contact_request_id: int) -> None:
    """Отправляет администратору email-уведомление о новой заявке обратной связи."""
    try:
        contact_request = ContactRequest.objects.get(pk=contact_request_id)
    except ContactRequest.DoesNotExist:
        return

    ContactRequest.objects.filter(pk=contact_request.pk).update(
        notification_attempts=F('notification_attempts') + 1,
        notification_error='',
    )

    subject = f'Новая заявка №{contact_request.pk}'
    message = (
        f'Имя: {contact_request.name}\n'
        f'Email: {contact_request.email}\n'
        f'Причина обращения: {contact_request.reason}\n\n'
        f'Сообщение:\n{contact_request.message}'
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
    except (SMTPException, OSError) as error:
        is_last_attempt = self.request.retries >= self.max_retries
        ContactRequest.objects.filter(pk=contact_request.pk).update(
            notification_status=ContactRequest.NotificationStatus.FAILED
            if is_last_attempt
            else ContactRequest.NotificationStatus.PENDING,
            notification_error=str(error)[:MAX_NOTIFICATION_ERROR_LENGTH],
        )
        if is_last_attempt:
            raise
        raise self.retry(exc=error, countdown=min(60, 2**self.request.retries)) from error

    ContactRequest.objects.filter(pk=contact_request.pk).update(
        notification_status=ContactRequest.NotificationStatus.SENT,
        notification_sent_at=timezone.now(),
        notification_error='',
    )
