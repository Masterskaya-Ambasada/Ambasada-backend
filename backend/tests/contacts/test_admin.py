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
    """Проверяет, что дубль order отображается как ошибка формы."""
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

    assert response.status_code == 200
    assert ContactSocialLink.objects.count() == 1
    errors = response.content.decode()
    assert 'уже занят' in errors


@pytest.mark.django_db
def test_contact_social_link_admin_add_shows_social_type_error(client, admin_user, site_config):
    """Проверяет, что дубль social_type отображается как ошибка формы."""
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

    assert response.status_code == 200
    assert ContactSocialLink.objects.count() == 1
    errors = response.content.decode()
    assert 'уже существует' in errors


@pytest.mark.django_db
def test_contact_social_link_admin_accepts_plain_email(client, admin_user, site_config):
    """В админке для типа Email можно сохранить обычный адрес без mailto-префикса."""
    client.force_login(admin_user)

    response = client.post(
        '/admin/contacts/contactsociallink/add/',
        data={
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


@pytest.mark.django_db
def test_contact_social_link_order_range_validation(client, admin_user, site_config):
    """Проверяет, что order за пределами 1-5 отклоняется формой."""
    client.force_login(admin_user)

    response = client.post(
        '/admin/contacts/contactsociallink/add/',
        data={
            'social_type': ContactSocialLink.SocialType.FACEBOOK,
            'url': 'https://facebook.com/example',
            'order': '0',
            'is_active': 'on',
            '_save': 'Сохранить',
        },
    )

    assert response.status_code == 200
    assert ContactSocialLink.objects.count() == 0

    response = client.post(
        '/admin/contacts/contactsociallink/add/',
        data={
            'social_type': ContactSocialLink.SocialType.FACEBOOK,
            'url': 'https://facebook.com/example',
            'order': '6',
            'is_active': 'on',
            '_save': 'Сохранить',
        },
    )

    assert response.status_code == 200
    assert ContactSocialLink.objects.count() == 0


@pytest.mark.django_db
def test_contact_social_link_admin_add_success(client, admin_user, site_config):
    """Проверяет успешное добавление новой записи соцсети."""
    client.force_login(admin_user)

    response = client.post(
        '/admin/contacts/contactsociallink/add/',
        data={
            'social_type': ContactSocialLink.SocialType.LINKEDIN,
            'url': 'https://linkedin.com/company/example',
            'order': '1',
            'is_active': 'on',
            '_save': 'Сохранить',
        },
    )

    assert response.status_code == 302
    assert ContactSocialLink.objects.count() == 1
    link = ContactSocialLink.objects.first()
    assert link.social_type == ContactSocialLink.SocialType.LINKEDIN
    assert link.site_config == site_config


@pytest.mark.django_db
def test_contact_social_link_admin_swap_orders(client, admin_user, site_config):
    """Проверяет, что обмен порядков между записями работает без ошибок."""
    link1 = ContactSocialLink.objects.create(
        site_config=site_config,
        social_type=ContactSocialLink.SocialType.TELEGRAM,
        url='https://t.me/example',
        order=1,
    )
    link2 = ContactSocialLink.objects.create(
        site_config=site_config,
        social_type=ContactSocialLink.SocialType.INSTAGRAM,
        url='https://instagram.com/example',
        order=2,
    )

    client.force_login(admin_user)

    response = client.post(
        '/admin/contacts/contactsociallink/',
        data={
            'form-0-id': str(link1.pk),
            'form-0-social_type': ContactSocialLink.SocialType.TELEGRAM,
            'form-0-url': 'https://t.me/example',
            'form-0-order': '2',
            'form-0-is_active': 'on',
            'form-1-id': str(link2.pk),
            'form-1-social_type': ContactSocialLink.SocialType.INSTAGRAM,
            'form-1-url': 'https://instagram.com/example',
            'form-1-order': '1',
            'form-1-is_active': 'on',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            '_save': 'Сохранить',
        },
    )

    assert response.status_code == 302
    link1.refresh_from_db()
    link2.refresh_from_db()
    assert link1.order == 2
    assert link2.order == 1
