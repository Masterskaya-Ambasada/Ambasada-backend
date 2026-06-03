from about.admin import AboutPageAdmin, GalleryImageInline
from about.models import AboutPage, GalleryImage
from django.contrib import admin


def _flatten_admin_fields(fieldsets):
    fields = []
    for _, options in fieldsets:
        for field in options['fields']:
            if isinstance(field, tuple):
                fields.extend(field)
            else:
                fields.append(field)
    return fields


def test_about_admin_does_not_include_removed_hero_fields():
    """Проверяет корректность полей в настройках админки страницы 'О нас'."""
    about_admin = AboutPageAdmin(AboutPage, admin.site)
    fields = _flatten_admin_fields(about_admin.fieldsets)

    assert list(about_admin.list_display) == ['id', 'about_title']
    assert list(about_admin.list_display_links) == ['id', 'about_title']
    assert any(field.startswith('hero_title') for field in fields)


def test_about_gallery_inline_uses_bounded_image_preview():
    """Проверяет, что галерея выводит ограниченное превью изображения."""
    inline = GalleryImageInline(AboutPage, admin.site)
    gallery_image = GalleryImage(image='about/gallery/test.jpg')
    preview = str(inline.image_preview_field(gallery_image))
    assert 'admin-image-preview' in preview
    assert 'width: 240px' in preview
    assert 'height: 160px' in preview
    assert 'max-width: 100%' in preview
    assert '<img' in preview
    assert 'width="240"' in preview
    assert 'height="160"' in preview
    assert 'width: 240px !important' in preview
    assert 'max-height: 160px' in preview
    assert 'about/gallery/test.jpg' in preview