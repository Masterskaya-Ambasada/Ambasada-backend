import pytest
from contacts.models import ContactSocialLink
from site_config.models import SiteConfig


@pytest.fixture
def site_config(db):
    """Создаёт базовые настройки сайта для ссылок на соцсети."""
    return SiteConfig.objects.create(site_name='Test site', seo_description='SEO text', copyright='2026')


@pytest.mark.django_db
def test_contact_social_link_admin_add_shows_order_error(client, admin_user, site_config):
    """Проверяет, что дубль order в админке показывает ошибку формы, а не IntegrityError."""
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
            'social_type': ContactSocialLink.SocialType.INSTAGRAM,
            'url': 'https://instagram.com/example',
            'order': '1',
            'is_active': 'on',
            '_save': 'Сохранить',
        },
    )

    form = response.context['adminform'].form
    assert response.status_code == 200
    assert 'order' in form.errors
    assert ContactSocialLink.objects.count() == 1


@pytest.mark.django_db
def test_contact_social_link_admin_add_shows_social_type_error(client, admin_user, site_config):
    """Проверяет, что дубль соцсети в админке показывает ошибку формы, а не IntegrityError."""
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
            'social_type': ContactSocialLink.SocialType.TELEGRAM,
            'url': 'https://t.me/another',
            'order': '2',
            'is_active': 'on',
            '_save': 'Сохранить',
        },
    )

    form = response.context['adminform'].form
    assert response.status_code == 200
    assert 'social_type' in form.errors
    assert ContactSocialLink.objects.count() == 1
