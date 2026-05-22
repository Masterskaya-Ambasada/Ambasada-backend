import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings
from projects import models as project_models
from projects.constants import (
    PROJECT_BLOCKS_DIRECTORY,
    PROJECT_COVER_DIRECTORY,
    PROJECT_GALLERY_DIRECTORY,
    PROJECT_MEDIA_DIRECTORY,
)
from projects.models import Project, ProjectBlockButton, ProjectContentBlock, ProjectGalleryImage


@pytest.mark.django_db
def test_project_type_str_returns_label(project_type_architecture):
    """Проверяет, что строковое представление типа проекта возвращает его label."""
    assert str(project_type_architecture) == 'Architecture'


@pytest.mark.django_db
def test_tag_str_returns_label(tag_urban):
    """Проверяет, что строковое представление тега возвращает его label."""
    assert str(tag_urban) == 'Urban'


@pytest.mark.django_db
def test_project_str_returns_title(published_project):
    """Проверяет, что строковое представление проекта возвращает его title."""
    assert str(published_project) == 'Central Park'


@pytest.mark.django_db
def test_content_block_str_contains_project_title_and_block_title(list_block):
    """Проверяет, что строковое представление контентного блока содержит название проекта и блока."""
    value = str(list_block)
    assert 'Central Park' in value
    assert 'List block' in value


@pytest.mark.django_db
def test_project_block_button_str_returns_label(buttons_block):
    """Проверяет, что строковое представление кнопки блока возвращает её label."""
    button = buttons_block.buttons.first()
    assert str(button) == button.label


@pytest.mark.django_db
def test_content_block_save_auto_sets_order(published_project):
    """Проверяет, что при сохранении контентным блокам автоматически назначается порядок внутри проекта."""
    first_block = ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=0,
        title='First block',
        image='https://example.com/1.jpg',
        string_list=['A'],
        text='<p>First text</p>',
        accented_text='',
    )
    second_block = ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=0,
        title='Second block',
        image='https://example.com/2.jpg',
        string_list=['B'],
        text='<p>Second text</p>',
        accented_text='',
    )
    assert first_block.order == 1
    assert second_block.order == 2


@pytest.mark.django_db
def test_project_block_button_save_auto_sets_order(buttons_block):
    """Проверяет, что при сохранении кнопке автоматически назначается порядок внутри блока."""
    button = ProjectBlockButton.objects.create(
        block=buttons_block,
        order=0,
        label='Extra button',
        type=ProjectBlockButton.ButtonType.REDIRECT,
        url='https://example.com/extra',
    )
    assert button.order == 3


@pytest.mark.django_db
def test_content_block_bulk_create_auto_sets_orders(published_project):
    """Проверяет, что bulk_create автоматически проставляет order контентным блокам без заданного порядка."""
    blocks = ProjectContentBlock.objects.bulk_create(
        [
            ProjectContentBlock(
                project=published_project,
                variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                order=0,
                title='Bulk 1',
                image='https://example.com/bulk1.jpg',
                string_list=['One'],
                text='<p>Bulk 1 text</p>',
                accented_text='',
            ),
            ProjectContentBlock(
                project=published_project,
                variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                order=0,
                title='Bulk 2',
                image='https://example.com/bulk2.jpg',
                string_list=['Two'],
                text='<p>Bulk 2 text</p>',
                accented_text='',
            ),
        ]
    )
    assert blocks[0].order == 1
    assert blocks[1].order == 2


@pytest.mark.django_db
def test_content_block_bulk_create_gets_max_orders_in_single_batch(
    published_project,
    second_published_project,
    monkeypatch,
):
    """Проверяет, что bulk_create не делает отдельный запрос max(order) для каждого объекта."""
    calls = []
    original_get_max_orders = project_models._get_max_orders

    def spy_get_max_orders(queryset, related_field_name, related_ids):
        calls.append((related_field_name, set(related_ids)))
        return original_get_max_orders(queryset, related_field_name, related_ids)

    monkeypatch.setattr(project_models, '_get_max_orders', spy_get_max_orders)
    blocks = ProjectContentBlock.objects.bulk_create(
        [
            ProjectContentBlock(
                project=published_project,
                variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                order=0,
                title='First project bulk 1',
                image='https://example.com/first-project-bulk-1.jpg',
                string_list=['One'],
                text='<p>Bulk text</p>',
                accented_text='',
            ),
            ProjectContentBlock(
                project=published_project,
                variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                order=0,
                title='First project bulk 2',
                image='https://example.com/first-project-bulk-2.jpg',
                string_list=['Two'],
                text='<p>Bulk text</p>',
                accented_text='',
            ),
            ProjectContentBlock(
                project=second_published_project,
                variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                order=0,
                title='Second project bulk 1',
                image='https://example.com/second-project-bulk-1.jpg',
                string_list=['One'],
                text='<p>Bulk text</p>',
                accented_text='',
            ),
        ]
    )
    assert calls == [('project', {published_project.pk, second_published_project.pk})]
    assert [block.order for block in blocks] == [1, 2, 1]


@pytest.mark.django_db
def test_content_block_save_locks_project_before_auto_order(published_project, monkeypatch):
    """Проверяет, что автоназначение order блокирует проект от параллельного расчета."""
    calls = []

    def spy_lock_related_rows(model, related_field_name, related_ids):
        calls.append((model, related_field_name, set(related_ids)))

    monkeypatch.setattr(project_models, '_lock_related_rows', spy_lock_related_rows)
    ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=0,
        title='Locked auto order block',
        image='https://example.com/locked-auto-order.jpg',
        string_list=['One'],
        text='<p>Locked text</p>',
        accented_text='',
    )
    assert calls == [(ProjectContentBlock, 'project', {published_project.pk})]


@pytest.mark.django_db
def test_content_block_save_without_title_does_not_raise_validation_error(published_project):
    """Проверяет, что save не вызывает full_clean и не ломает сохранение из nested admin."""
    block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=0,
        image='https://example.com/no-title.jpg',
        string_list=['One'],
        text='<p>Text without title</p>',
        accented_text='',
    )
    block.save()
    assert block.pk is not None
    assert block.order == 1


@pytest.mark.django_db
def test_content_block_order_must_be_unique_within_project(published_project):
    """Проверяет, что порядок контентных блоков уникален внутри одного проекта."""
    ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=10,
        title='First ordered block',
        image='https://example.com/first.jpg',
        string_list=['One'],
        text='<p>First text</p>',
        accented_text='',
    )
    duplicate_block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=10,
        title='Duplicate ordered block',
        image='https://example.com/duplicate.jpg',
        string_list=['Two'],
        text='<p>Duplicate text</p>',
        accented_text='',
    )
    with pytest.raises(ValidationError) as exc_info:
        duplicate_block.full_clean()
    assert 'order' in exc_info.value.message_dict


@pytest.mark.django_db
def test_content_block_order_can_repeat_for_different_projects(published_project, second_published_project):
    """Проверяет, что одинаковый порядок разрешен для блоков разных проектов."""
    ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=10,
        title='First project block',
        image='https://example.com/first-project.jpg',
        string_list=['One'],
        text='<p>First project text</p>',
        accented_text='',
    )
    second_project_block = ProjectContentBlock(
        project=second_published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=10,
        title='Second project block',
        image='https://example.com/second-project.jpg',
        string_list=['Two'],
        text='<p>Second project text</p>',
        accented_text='',
    )
    second_project_block.full_clean()


@pytest.mark.django_db
def test_content_block_bulk_create_rejects_duplicate_order_in_same_project(published_project):
    """Проверяет, что bulk_create не сохраняет дубли порядка внутри одного проекта."""
    with pytest.raises(ValidationError) as exc_info:
        ProjectContentBlock.objects.bulk_create(
            [
                ProjectContentBlock(
                    project=published_project,
                    variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                    order=10,
                    title='Bulk duplicate 1',
                    image='https://example.com/bulk-duplicate-1.jpg',
                    string_list=['One'],
                    text='<p>Bulk duplicate 1 text</p>',
                    accented_text='',
                ),
                ProjectContentBlock(
                    project=published_project,
                    variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                    order=10,
                    title='Bulk duplicate 2',
                    image='https://example.com/bulk-duplicate-2.jpg',
                    string_list=['Two'],
                    text='<p>Bulk duplicate 2 text</p>',
                    accented_text='',
                ),
            ]
        )
    assert 'order' in exc_info.value.message_dict


@pytest.mark.django_db
def test_project_block_button_bulk_create_auto_sets_orders(buttons_block):
    """Проверяет, что bulk_create автоматически проставляет order кнопкам без заданного порядка."""
    buttons = ProjectBlockButton.objects.bulk_create(
        [
            ProjectBlockButton(
                block=buttons_block,
                order=0,
                label='Bulk button 1',
                type=ProjectBlockButton.ButtonType.DOWNLOAD,
                url='https://example.com/a.pdf',
            ),
            ProjectBlockButton(
                block=buttons_block,
                order=0,
                label='Bulk button 2',
                type=ProjectBlockButton.ButtonType.REDIRECT,
                url='https://example.com/b',
            ),
        ]
    )
    assert buttons[0].order == 3
    assert buttons[1].order == 4


@pytest.mark.django_db
def test_content_block_with_list_variant_requires_string_list(published_project):
    """Проверяет, что вариант IMAGE_WITH_LIST требует список тезисов."""
    block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=1,
        title='Invalid list block',
        image='https://example.com/list.jpg',
        string_list=[],
        text='<p>List text</p>',
        accented_text='',
    )
    with pytest.raises(ValidationError) as exc_info:
        block.full_clean()
    assert 'string_list_ru' in exc_info.value.message_dict


@pytest.mark.django_db
def test_content_block_non_list_variant_allows_string_list(published_project):
    """Проверяет, что нерелевантный список тезисов можно сохранить для другого варианта."""
    block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.TWO_IMAGES,
        order=1,
        title='Invalid two images block',
        image='https://example.com/main.jpg',
        left_image='https://example.com/left.jpg',
        string_list=['Should not be here'],
        text='<p>Two images text</p>',
        accented_text='',
    )
    block.full_clean()


@pytest.mark.django_db
def test_two_images_variant_requires_left_image(published_project):
    """Проверяет, что вариант TWO_IMAGES требует второе изображение."""
    block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.TWO_IMAGES,
        order=1,
        title='Invalid missing left image',
        image='https://example.com/main.jpg',
        left_image='',
        string_list=[],
        text='<p>Two images text</p>',
        accented_text='',
    )
    with pytest.raises(ValidationError) as exc_info:
        block.full_clean()
    assert 'left_image' in exc_info.value.message_dict


@pytest.mark.django_db
def test_non_two_images_variant_allows_left_image(published_project):
    """Проверяет, что нерелевантное второе изображение можно сохранить для другого варианта."""
    block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_BUTTONS,
        order=1,
        title='Invalid extra left image',
        image='https://example.com/main.jpg',
        left_image='https://example.com/left.jpg',
        string_list=[],
        text='<p>Buttons text</p>',
        accented_text='',
    )
    block.full_clean()


@pytest.mark.django_db
def test_content_block_requires_common_image_and_text(published_project):
    """Проверяет, что для любого варианта нужны основное изображение и текст."""
    block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_BUTTONS,
        order=1,
        title='Invalid common fields block',
        image='',
        left_image='',
        string_list=[],
        text='',
        accented_text='',
    )
    with pytest.raises(ValidationError) as exc_info:
        block.full_clean()
    assert {'image', 'text_ru'} <= set(exc_info.value.message_dict)


@pytest.mark.django_db(transaction=True)
def test_project_queryset_delete_removes_project_media_directory(published_project, tmp_path):
    """Проверяет, что папка проекта удаляется при любом удалении Project через queryset."""
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        project_dir = tmp_path / PROJECT_MEDIA_DIRECTORY / published_project.slug
        cover_dir = project_dir / PROJECT_COVER_DIRECTORY
        cover_dir.mkdir(parents=True)
        (cover_dir / 'cover.jpg').write_text('cover')
        Project.objects.filter(pk=published_project.pk).delete()
        assert not project_dir.exists()


@pytest.mark.django_db(transaction=True)
def test_project_slug_change_moves_media_directory_and_updates_file_paths(published_project, tmp_path):
    """Проверяет, что смена slug переносит медиа-папку и обновляет пути файлов."""
    old_slug = published_project.slug
    new_slug = 'central-park-renamed'
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        old_project_dir = tmp_path / PROJECT_MEDIA_DIRECTORY / old_slug
        old_cover_dir = old_project_dir / PROJECT_COVER_DIRECTORY
        old_gallery_dir = old_project_dir / PROJECT_GALLERY_DIRECTORY
        old_blocks_dir = old_project_dir / PROJECT_BLOCKS_DIRECTORY
        for directory in (old_cover_dir, old_gallery_dir, old_blocks_dir):
            directory.mkdir(parents=True)
        (old_cover_dir / 'cover.jpg').write_text('cover')
        (old_gallery_dir / 'gallery.jpg').write_text('gallery')
        (old_blocks_dir / 'main.jpg').write_text('main')
        (old_blocks_dir / 'left.jpg').write_text('left')
        published_project.cover_image = f'{PROJECT_MEDIA_DIRECTORY}/{old_slug}/{PROJECT_COVER_DIRECTORY}/cover.jpg'
        published_project.save()
        gallery_image = ProjectGalleryImage.objects.create(
            project=published_project,
            image=f'{PROJECT_MEDIA_DIRECTORY}/{old_slug}/{PROJECT_GALLERY_DIRECTORY}/gallery.jpg',
            order=1,
        )
        content_block = ProjectContentBlock.objects.create(
            project=published_project,
            variant=ProjectContentBlock.Variant.TWO_IMAGES,
            order=1,
            title='Two images block',
            image=f'{PROJECT_MEDIA_DIRECTORY}/{old_slug}/{PROJECT_BLOCKS_DIRECTORY}/main.jpg',
            left_image=f'{PROJECT_MEDIA_DIRECTORY}/{old_slug}/{PROJECT_BLOCKS_DIRECTORY}/left.jpg',
            string_list=[],
            text='<p>Two images text</p>',
            accented_text='',
        )
        published_project.slug = new_slug
        published_project.save()
        published_project.refresh_from_db()
        gallery_image.refresh_from_db()
        content_block.refresh_from_db()
        assert not old_project_dir.exists()
        assert (tmp_path / PROJECT_MEDIA_DIRECTORY / new_slug / PROJECT_COVER_DIRECTORY / 'cover.jpg').exists()
        assert published_project.cover_image.name == (
            f'{PROJECT_MEDIA_DIRECTORY}/{new_slug}/{PROJECT_COVER_DIRECTORY}/cover.jpg'
        )
        assert gallery_image.image.name == (
            f'{PROJECT_MEDIA_DIRECTORY}/{new_slug}/{PROJECT_GALLERY_DIRECTORY}/gallery.jpg'
        )
        assert content_block.image.name == f'{PROJECT_MEDIA_DIRECTORY}/{new_slug}/{PROJECT_BLOCKS_DIRECTORY}/main.jpg'
        assert content_block.left_image.name == (
            f'{PROJECT_MEDIA_DIRECTORY}/{new_slug}/{PROJECT_BLOCKS_DIRECTORY}/left.jpg'
        )


@pytest.mark.django_db
def test_content_block_bulk_create_validates_objects(published_project):
    """Проверяет, что bulk_create выполняет валидацию объектов и не сохраняет невалидный контентный блок."""
    with pytest.raises(ValidationError):
        ProjectContentBlock.objects.bulk_create(
            [
                ProjectContentBlock(
                    project=published_project,
                    variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                    order=0,
                    title='Broken block',
                    image='https://example.com/broken.jpg',
                    string_list='not-a-list',
                    text='<p>Broken text</p>',
                    accented_text='',
                )
            ]
        )
