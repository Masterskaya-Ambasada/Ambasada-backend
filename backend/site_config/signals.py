import logging

from about.models import AboutPage
from contacts.models import ContactPageContent, ContactSocialLink
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from home.models import HomePageContent
from projects.models import Project
from security.models import SecurityPolicy

from site_config.cache import clear_config_cache
from site_config.models import SiteConfig

from .middleware import get_current_user

logger = logging.getLogger('admin')

User = get_user_model()


def get_action_name(kwargs):
    """Возвращает тип действия: создан, удален или изменен."""
    if kwargs.get('created'):
        return 'создан'
    if kwargs.get('signal') == post_delete:
        return 'удален'
    return 'изменен'


@receiver([post_save, post_delete], sender=HomePageContent)
@receiver([post_save, post_delete], sender=SiteConfig)
@receiver([post_save, post_delete], sender=ContactSocialLink)
def invalidate_site_config_cache(sender, instance, **kwargs):
    """Сбрасывает кеш при изменении настроек или социальных ссылок."""
    action = get_action_name(kwargs)
    obj_id = getattr(instance, 'id', None)
    obj_name = sender.__name__

    logger.info(f'Сброс кэша: {obj_name} (ID: {obj_id}) - {action}')
    clear_config_cache()


@receiver([post_save, post_delete], sender=AboutPage)
@receiver([post_save, post_delete], sender=Project)
@receiver([post_save, post_delete], sender=User)
@receiver([post_save, post_delete], sender=ContactPageContent)
@receiver([post_save, post_delete], sender=SecurityPolicy)
def log_model_change(sender, instance, **kwargs):
    """Логгирование действий администратора (создание/изменение/удаление)."""
    current_user = get_current_user()
    action = get_action_name(kwargs)
    target_info = ''
    if sender.__name__ == 'User':
        target_info = f'{instance.full_name} ({instance.email})'
    elif sender.__name__ == 'Project':
        target_info = instance.slug
    logger.info(f'Объект {sender.__name__} {target_info} {action} администратором {current_user}')
