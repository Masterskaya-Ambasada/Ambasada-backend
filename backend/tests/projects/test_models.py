import pytest
from django.core.exceptions import ValidationError

from projects.models import ProjectBlockButton, ProjectContentBlock


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
        text='',
        accented_text='',
    )
    second_block = ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=0,
        title='Second block',
        image='https://example.com/2.jpg',
        string_list=['B'],
        text='',
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
                text='',
                accented_text='',
            ),
            ProjectContentBlock(
                project=published_project,
                variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
                order=0,
                title='Bulk 2',
                image='https://example.com/bulk2.jpg',
                string_list=['Two'],
                text='',
                accented_text='',
            ),
        ]
    )
    assert blocks[0].order == 1
    assert blocks[1].order == 2


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
def test_content_block_with_list_variant_allows_empty_string_list(published_project):
    """Проверяет, что вариант IMAGE_WITH_LIST можно сохранить без списка тезисов."""
    block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=1,
        title='Invalid list block',
        image='https://example.com/list.jpg',
        string_list=[],
        text='',
        accented_text='',
    )
    block.full_clean()


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
        text='',
        accented_text='',
    )
    block.full_clean()


@pytest.mark.django_db
def test_two_images_variant_allows_empty_left_image(published_project):
    """Проверяет, что вариант TWO_IMAGES можно сохранить без второго изображения."""
    block = ProjectContentBlock(
        project=published_project,
        variant=ProjectContentBlock.Variant.TWO_IMAGES,
        order=1,
        title='Invalid missing left image',
        image='https://example.com/main.jpg',
        left_image='',
        string_list=[],
        text='',
        accented_text='',
    )
    block.full_clean()


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
        text='',
        accented_text='',
    )
    block.full_clean()


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
                    text='',
                    accented_text='',
                )
            ]
        )
