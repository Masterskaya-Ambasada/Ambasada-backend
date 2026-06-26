import pytest
from contacts.models import ContactSocialLink
from django.db.utils import IntegrityError
from site_config.models import SiteConfig


@pytest.fixture
def site_config(db):
    """Создаёт базовые настройки сайта для ссылок на соцсети."""
    config, _ = SiteConfig.objects.get_or_create(
        pk=1,
        defaults={
            'site_name': 'Test site',
            'seo_description': 'SEO text',
            'copyright': '2026',
        },
    )
    return config


@pytest.mark.django_db
def test_contact_social_link_admin_add_shows_order_error(client, admin_user, site_config):
    """Проверяет, что дубль order в базе вызывает IntegrityError."""
    ContactSocialLink.objects.create(
        site_config=site_config,
        social_type=ContactSocialLink.SocialType.TELEGRAM,
        url='https://t.me/example',
        order=1,
    )
    client.force_login(admin_user)

    # Ожидаем, что база выбросит ошибку уникальности order
    with pytest.raises(IntegrityError) as exc_info:
        client.post(
            '/admin/contacts/contactsociallink/add/',
            data={
                'site_config': site_config.pk,
                'social_type': ContactSocialLink.SocialType.INSTAGRAM,
                'url': 'https://instagram.com/example',
                'order': '1',
                'is_active': 'on',
                '_save': 'Сохранить',
            },
        )

    assert 'unique_site_config_social_order' in str(exc_info.value)
    assert ContactSocialLink.objects.count() == 1


@pytest.mark.django_db
def test_contact_social_link_admin_add_shows_social_type_error(client, admin_user, site_config):
    """Проверяет, что дубль соцсети в базе вызывает IntegrityError."""
    ContactSocialLink.objects.create(
        site_config=site_config,
        social_type=ContactSocialLink.SocialType.TELEGRAM,
        url='https://t.me/example',
        order=1,
    )
    client.force_login(admin_user)

    # Ожидаем, что база выбросит ошибку уникальности social_type
    with pytest.raises(IntegrityError) as exc_info:
        client.post(
            '/admin/contacts/contactsociallink/add/',
            data={
                'site_config': site_config.pk,
                'social_type': ContactSocialLink.SocialType.TELEGRAM,
                'url': 'https://t.me/another',
                'order': '2',
                'is_active': 'on',
                '_save': 'Сохранить',
            },
        )

    assert 'unique_site_config_social_type' in str(exc_info.value)
    assert ContactSocialLink.objects.count() == 1


@pytest.mark.django_db
def test_contact_social_link_admin_accepts_plain_email(client, admin_user, site_config):
    """В админке для типа Email можно сохранить обычный адрес без mailto-префикса."""
    client.force_login(admin_user)

    response = client.post(
        '/admin/contacts/contactsociallink/add/',
        data={
            'site_config': site_config.pk,
            'social_type': ContactSocialLink.SocialType.EMAIL,
            'url': 'hello@example.com',
            'order': '3',
            'is_active': 'on',
            '_save': 'Сохранить',
        },
    )

    assert response.status_code == 302
    saved_link = ContactSocialLink.objects.get(social_type=ContactSocialLink.SocialType.EMAIL)
    assert saved_link.url == 'hello@example.com'
