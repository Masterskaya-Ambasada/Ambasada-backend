import pytest
from contacts.models import ContactSocialLink
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
    """Проверяет, что дубль order показывает ошибку формы без желтой страницы."""
    ContactSocialLink.objects.create(
        site_config=site_config,
        social_type=ContactSocialLink.SocialType.TELEGRAM,
        url='https://t.me/example',
        order=1,
    )
    client.force_login(admin_user)

    response = client.post(
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

    assert response.status_code == 200
    assert 'Этот порядок отображения уже занят для данного сайта' in response.content.decode()
    assert ContactSocialLink.objects.count() == 1


@pytest.mark.django_db
def test_contact_social_link_admin_add_shows_social_type_error(client, admin_user, site_config):
    """Проверяет, что дубль типа ссылки показывает ошибку формы без желтой страницы."""
    ContactSocialLink.objects.create(
        site_config=site_config,
        social_type=ContactSocialLink.SocialType.TELEGRAM,
        url='https://t.me/example',
        order=1,
    )
    client.force_login(admin_user)
    response = client.post(
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
    assert response.status_code == 200
    assert 'Для данного сайта уже добавлена ссылка этого типа соцсети' in response.content.decode()
    assert ContactSocialLink.objects.count() == 1


@pytest.mark.django_db
def test_contact_social_link_admin_adds_email_link(client, admin_user, site_config):
    """Проверяет, что в админке можно добавить email как ссылку для связи."""
    client.force_login(admin_user)
    response = client.post(
        '/admin/contacts/contactsociallink/add/',
        data={
            'social_type': ContactSocialLink.SocialType.EMAIL,
            'url': 'hello@example.com',
            'order': '10',
            'is_active': 'on',
            '_save': 'Сохранить',
        },
    )
    assert response.status_code == 302
    social_link = ContactSocialLink.objects.get(social_type=ContactSocialLink.SocialType.EMAIL)
    assert social_link.site_config == site_config
    assert social_link.url == 'hello@example.com'


def test_contact_social_link_social_type_has_email_choice():
    """Проверяет, что Email доступен в выборе типа соцсети / мессенджера."""
    assert (ContactSocialLink.SocialType.EMAIL, 'Email') in ContactSocialLink.SocialType.choices
