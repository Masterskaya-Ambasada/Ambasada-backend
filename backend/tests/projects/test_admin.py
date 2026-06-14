from base64 import b64decode
from pathlib import Path

import pytest
from django.contrib import admin
from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.models import inlineformset_factory
from django.test import override_settings
from projects.admin import (
    ProjectAdmin,
    ProjectBlockButtonInline,
    ProjectContentBlockInline,
    ProjectTypeAdmin,
    TagAdmin,
)
from projects.admin_forms import ProjectContentBlockInlineFormSet
from projects.constants import REFERENCE_TRANSLATED_FIELDS
from projects.models import Project, ProjectBlockButton, ProjectContentBlock, ProjectType, Tag
from projects.resources_admin import ProjectTypeResource, TagResource

TINY_PNG = b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC')


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
    assert 'order' in str(formset.non_form_errors())


@pytest.mark.django_db
def test_project_content_block_inline_shows_translated_field_errors(published_project):
    """Проверяет, что ошибки переводных полей не падают в админке как ValueError."""
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
    """Проверяет, что форма создания проекта не падает при ошибке переводного поля контентного блока."""
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


@pytest.mark.django_db
def test_project_admin_prepopulates_slug_from_russian_title_only_on_create(published_project):
    """Проверяет автозаполнение slug из русского названия только при создании проекта."""
    project_admin = ProjectAdmin(Project, admin.site)

    assert project_admin.get_prepopulated_fields(request=None, obj=None) == {'slug': ('title_ru',)}
    assert project_admin.get_prepopulated_fields(request=None, obj=published_project) == {}


def test_project_admin_uses_filter_horizontal_for_tags():
    """Проверяет, что теги выбираются через удобный many-to-many виджет."""
    project_admin = ProjectAdmin(Project, admin.site)

    assert project_admin.filter_horizontal == ('tags',)


def test_project_admin_hides_jsonform_source_textarea():
    """Проверяет, что техническое textarea django-jsonform скрыто от редактора."""
    css_path = finders.find('projects/css/admin_custom.css')
    css = Path(css_path).read_text(encoding='utf-8')

    assert 'textarea[data-django-jsonform]' in css
    assert 'display: none !important' in css


def test_project_block_button_inline_uses_translated_label_fields():
    """Проверяет, что подписи кнопок контентного блока редактируются на всех языках."""
    assert ProjectBlockButtonInline.fields == (
        'order',
        'label_ru',
        'label_en',
        'label_sr_latn',
        'label_sr_cyrl',
        'type',
        'url',
    )
    assert 'label' not in ProjectBlockButtonInline.fields


def test_project_reference_admins_use_translated_label_fields():
    """Проверяет, что теги и типы проектов редактируются на всех языках."""
    assert TagAdmin(Tag, admin.site).fields == REFERENCE_TRANSLATED_FIELDS
    assert ProjectTypeAdmin(ProjectType, admin.site).fields == REFERENCE_TRANSLATED_FIELDS


def test_project_reference_resources_include_all_translated_label_fields():
    """Проверяет, что импорт и экспорт справочников поддерживает все языки."""
    assert TagResource.Meta.fields == REFERENCE_TRANSLATED_FIELDS
    assert ProjectTypeResource.Meta.fields == REFERENCE_TRANSLATED_FIELDS


def test_project_admin_shows_detailed_manager_help_texts():
    """Проверяет, что в админке есть подробные подсказки с ограничениями для менеджера."""
    project_admin = ProjectAdmin(Project, admin.site)
    tag_admin = TagAdmin(Tag, admin.site)
    content_block_inline = ProjectContentBlockInline(Project, admin.site)
    button_inline = ProjectBlockButtonInline(ProjectContentBlock, admin.site)

    project_slug_help = project_admin.formfield_for_dbfield(Project._meta.get_field('slug'), request=None).help_text
    tag_label_help = tag_admin.formfield_for_dbfield(Tag._meta.get_field('label_sr_latn'), request=None).help_text
    block_image_help = content_block_inline.formfield_for_dbfield(
        ProjectContentBlock._meta.get_field('image'),
        request=None,
    ).help_text
    button_url_help = button_inline.formfield_for_dbfield(
        ProjectBlockButton._meta.get_field('url'),
        request=None,
    ).help_text

    assert 'сгенерируется из русского названия' in project_slug_help
    assert 'fallback' in tag_label_help
    assert 'Необязательное основное изображение' in block_image_help
    assert 'Google Drive' in button_url_help


@pytest.mark.django_db
@override_settings(FRONTEND_URL='https://ambasada.example/')
def test_project_admin_view_on_site_uses_frontend_url_from_settings(published_project):
    """Проверяет, что ссылка на проект в админке строится от настроенного домена фронтенда."""
    project_admin = ProjectAdmin(Project, admin.site)

    link = str(project_admin.get_view_on_site(published_project))

    assert f'https://ambasada.example/projects/{published_project.slug}/' in link
    assert 'localhost:3000' not in link


@pytest.mark.django_db
def test_project_admin_add_generates_slug_from_russian_title(
    client,
    admin_user,
    project_type_architecture,
):
    """Проверяет, что проект создаётся с пустым slug и русским названием с первого submit."""
    client.force_login(admin_user)
    response = client.post(
        '/admin/projects/project/add/',
        data={
            'slug': '',
            'year': '2026',
            'project_type': str(project_type_architecture.pk),
            'is_published': 'on',
            'title_ru': 'Парк Победы',
            'description_ru': 'Описание проекта',
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
            'content_blocks-TOTAL_FORMS': '0',
            'content_blocks-INITIAL_FORMS': '0',
            'content_blocks-MIN_NUM_FORMS': '0',
            'content_blocks-MAX_NUM_FORMS': '1000',
            '_save': 'Сохранить',
        },
    )
    assert response.status_code == 302
    assert Project.objects.filter(slug='park-pobedy', title_ru='Парк Победы').exists()
