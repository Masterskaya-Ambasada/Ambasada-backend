from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import HomePageContent


@receiver(pre_save, sender=HomePageContent)
def delete_old_hero_images_on_change(sender, instance, **kwargs):
    """Удаляет старые файлы изображений при их замене в админке."""
    if not instance.pk:
        return

    try:
        old_instance = HomePageContent.objects.get(pk=instance.pk)
    except HomePageContent.DoesNotExist:
        return

    image_fields = ['image_left', 'image_right']

    for field_name in image_fields:
        old_image = getattr(old_instance, field_name)
        new_image = getattr(instance, field_name)

        if old_image and old_image.name != new_image.name:
            if old_image.storage.exists(old_image.name):
                old_image.storage.delete(old_image.name)
