from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from site_config.cache import clear_config_cache

from .models import ContactSocialLink


@receiver([post_save, post_delete], sender=ContactSocialLink)
def invalidate_site_config_on_social_change(sender, **kwargs):
    """Сбрасывает кэш настроек сайта при изменении, добавлении или удалении социальных ссылок."""
    clear_config_cache()
