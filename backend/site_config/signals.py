from contacts.models import ContactSocialLink
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from site_config.cache import clear_config_cache
from site_config.models import SiteConfig


@receiver([post_save, post_delete], sender=SiteConfig)
@receiver([post_save, post_delete], sender=ContactSocialLink)
def invalidate_site_config_cache(sender, instance, **kwargs):
    """Сбрасывает кеш при изменении настроек или социальных ссылок."""
    clear_config_cache()
