from django.db import migrations


def normalize_email_social_links(apps, schema_editor):
    """Убирает mailto: из сохраненных email-ссылок для удобного редактирования в админке."""
    ContactSocialLink = apps.get_model('contacts', 'ContactSocialLink')
    for social_link in ContactSocialLink.objects.filter(social_type='email', url__startswith='mailto:'):
        social_link.url = social_link.url.removeprefix('mailto:')
        social_link.save(update_fields=['url'])


class Migration(migrations.Migration):
    dependencies = [
        ('contacts', '0023_alter_contactsociallink_url'),
    ]

    operations = [
        migrations.RunPython(normalize_email_social_links, migrations.RunPython.noop),
    ]
