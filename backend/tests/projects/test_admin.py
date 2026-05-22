from base64 import b64decode

import pytest
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.models import inlineformset_factory
from projects.admin import ProjectAdmin
from projects.admin_forms import ProjectContentBlockInlineFormSet
from projects.models import Project, ProjectContentBlock

TINY_PNG = b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgAAAABAAB9hc4VQAAAABJRU5ErkKC')


def _image_file(name: str) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, TINY_PNG, content_type='image/png')


def _content_block_form_data(index: int, order: int, title: str) -> dict[str, str]:
    prefix = f'content_blocks-{index}'
    return {
        f'{prefix}-variant': ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        f'{prefix}-order': str(order),
        f'{prefix}-title_ru': title,
        f'{prefix}-image': f'https://example.com/{title}.jpg',
        f'{prefix}-left_image': '',
        f'{prefix}-text_ru': '<p>Block text</p>',
        f'{prefix}-accented_text_ru': '',
        f'{prefix}-string_list_ru': '["One"]',
    }


@pytest.mark.django_db
def test_project_content_block_inline_rejects_duplicate_order(published_project):
    """Проверяет, что inline в админке отклоняет дубли order контентных блоков."""
    formset_class = inlineformset_factory(
        Project,
        ProjectContentBlock,
        fields=(
            'variant',
            'order',
            'title_ru',
            'image',
            'left_image',
            'text_ru',
            'accented_text_ru',
            'string_list_ru',
        ),
        formset=ProjectContentBlockInlineFormSet,
        extra=0,
        can_delete=True,
    )
    form_data = {
        'content_blocks-TOTAL_FORMS': '2',
        'content_blocks-INITIAL_FORMS': '0',
        'content_blocks-MIN_NUM_FORMS': '0',
        'content_blocks-MAX_NUM_FORMS': '1000',
        **_content_block_form_data(0, 10, 'first-block'),
        **_content_block_form_data(1, 10, 'second-block'),
    }
    formset = formset_class(data=form_data, instance=published_project, prefix='content_blocks')
    assert not formset.is_valid()
    assert 'Порядок контентных блоков' in str(formset.non_form_errors())


@pytest.mark.django_db
def test_project_content_block_inline_shows_translated_field_errors(published_project):
    """Проверяет, что ошибки translated-полей не падают в админке как ValueError."""
    formset_class = inlineformset_factory(
        Project,
        ProjectContentBlock,
        fields=(
            'variant',
            'order',
            'title_ru',
            'image',
            'left_image',
            'text_ru',
            'accented_text_ru',
            'string_list_ru',
        ),
        formset=ProjectContentBlockInlineFormSet,
        extra=0,
        can_delete=True,
    )
    form_data = {
        'content_blocks-TOTAL_FORMS': '1',
        'content_blocks-INITIAL_FORMS': '0',
        'content_blocks-MIN_NUM_FORMS': '0',
        'content_blocks-MAX_NUM_FORMS': '1000',
        **_content_block_form_data(0, 10, 'missing-text-block'),
        'content_blocks-0-text_ru': '',
    }
    formset = formset_class(data=form_data, instance=published_project, prefix='content_blocks')

    assert not formset.is_valid()
    assert 'text_ru' in formset.forms[0].errors


@pytest.mark.django_db
def test_project_admin_add_renders_content_block_translated_field_error(
    client,
    admin_user,
    project_type_architecture,
):
    """Проверяет, что admin add не падает при ошибке translated-поля контентного блока."""
    client.force_login(admin_user)
    slug = 'admin-invalid-content-block'
    response = client.post(
        '/admin/projects/project/add/',
        data={
            'slug': slug,
            'year': '2026',
            'project_type': str(project_type_architecture.pk),
            'is_published': 'on',
            'title_ru': 'Admin invalid project',
            'description_ru': 'Admin invalid project description',
            'title_en': '',
            'description_en': '',
            'title_sr_latn': '',
            'description_sr_latn': '',
            'title_sr_cyrl': '',
            'description_sr_cyrl': '',
            'cover_image': _image_file('cover.png'),
            'gallery_images-TOTAL_FORMS': '0',
            'gallery_images-INITIAL_FORMS': '0',
            'gallery_images-MIN_NUM_FORMS': '0',
            'gallery_images-MAX_NUM_FORMS': '1000',
            'content_blocks-TOTAL_FORMS': '1',
            'content_blocks-INITIAL_FORMS': '0',
            'content_blocks-MIN_NUM_FORMS': '0',
            'content_blocks-MAX_NUM_FORMS': '1000',
            'content_blocks-0-variant': ProjectContentBlock.Variant.IMAGE_WITH_LIST,
            'content_blocks-0-order': '1',
            'content_blocks-0-title_ru': 'Invalid block',
            'content_blocks-0-image': _image_file('block.png'),
            'content_blocks-0-left_image': '',
            'content_blocks-0-text_ru': '',
            'content_blocks-0-accented_text_ru': '',
            'content_blocks-0-string_list_ru': '["One"]',
            'content_blocks-0-title_en': '',
            'content_blocks-0-text_en': '',
            'content_blocks-0-accented_text_en': '',
            'content_blocks-0-string_list_en': '[]',
            'content_blocks-0-title_sr_latn': '',
            'content_blocks-0-text_sr_latn': '',
            'content_blocks-0-accented_text_sr_latn': '',
            'content_blocks-0-string_list_sr_latn': '[]',
            'content_blocks-0-title_sr_cyrl': '',
            'content_blocks-0-text_sr_cyrl': '',
            'content_blocks-0-accented_text_sr_cyrl': '',
            'content_blocks-0-string_list_sr_cyrl': '[]',
            'content_blocks-0-id': '',
            'content_blocks-0-project': '',
            'content_blocks-0-buttons-TOTAL_FORMS': '0',
            'content_blocks-0-buttons-INITIAL_FORMS': '0',
            'content_blocks-0-buttons-MIN_NUM_FORMS': '0',
            'content_blocks-0-buttons-MAX_NUM_FORMS': '1000',
            '_save': 'Сохранить',
        },
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert not Project.objects.filter(slug=slug).exists()
    assert 'ValueError' not in content
    assert 'name="content_blocks-0-text_ru"' in content
    assert 'Заполните основной текст для выбранного варианта блока.' in content


@pytest.mark.django_db
def test_project_admin_makes_slug_readonly_after_creation(published_project):
    """Проверяет, что контент-менеджер не может изменить slug после создания проекта."""
    project_admin = ProjectAdmin(Project, admin.site)
    assert 'slug' not in project_admin.get_readonly_fields(request=None, obj=None)
    assert 'slug' in project_admin.get_readonly_fields(request=None, obj=published_project)
