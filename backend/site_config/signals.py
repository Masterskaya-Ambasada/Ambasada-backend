from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .constants import clear_config_cache
from .models import Language


@receiver(post_save, sender=Language)
def language_saved(sender, instance, **kwargs):
    """Очищает кэш конфигурации при изменении языка."""
    clear_config_cache()


@receiver(post_delete, sender=Language)
def language_deleted(sender, instance, **kwargs):
    """Очищает кэш конфигурации при удалении языка."""
    clear_config_cache()
