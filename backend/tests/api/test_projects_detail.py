import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_project_detail_returns_only_published_project(
    api_client,
    published_project,
    unpublished_project,
):
    """Проверяет, что детальная ручка доступна только для опубликованного проекта."""
    published_url = reverse('api:projects-detail', kwargs={'project_id': published_project.slug})
    unpublished_url = reverse('api:projects-detail', kwargs={'project_id': unpublished_project.slug})
    published_response = api_client.get(published_url)
    unpublished_response = api_client.get(unpublished_url)
    assert published_response.status_code == 200
    assert unpublished_response.status_code == 404


@pytest.mark.django_db
def test_project_detail_returns_info_and_content_blocks(
    api_client,
    published_project,
    list_block,
    two_images_block,
    buttons_block,
):
    """Проверяет, что детальная ручка проекта возвращает блок info и список content_blocks."""
    url = reverse('api:projects-detail', kwargs={'project_id': published_project.slug})
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert 'info' in data
    assert 'content_blocks' in data
    assert data['info']['id'] == published_project.slug
    assert len(data['content_blocks']) == 3


@pytest.mark.django_db
def test_project_detail_formats_content_block_indexes(
    api_client,
    published_project,
    list_block,
    two_images_block,
    buttons_block,
):
    """Проверяет, что индексы контентных блоков сериализуются в строковом формате с ведущими нулями."""
    url = reverse('api:projects-detail', kwargs={'project_id': published_project.slug})
    response = api_client.get(url)
    assert response.status_code == 200
    blocks = response.json()['content_blocks']
    assert blocks[0]['index'] == '001'
    assert blocks[1]['index'] == '002'
    assert blocks[2]['index'] == '003'


@pytest.mark.django_db
def test_project_detail_hides_variant_specific_fields_for_list_block(
    api_client,
    published_project,
    list_block,
):
    """Проверяет, что для блока варианта IMAGE_WITH_LIST в ответе остаются только допустимые для него поля."""
    list_block.left_image = 'https://example.com/hidden-left-image.jpg'
    list_block.save()
    url = reverse('api:projects-detail', kwargs={'project_id': published_project.slug})
    response = api_client.get(url)
    assert response.status_code == 200
    block = response.json()['content_blocks'][0]
    assert block['variant'] == 1
    assert 'string_list' in block
    assert 'left_image' not in block
    assert 'buttons' not in block


@pytest.mark.django_db
def test_project_detail_hides_variant_specific_fields_for_two_images_block(
    api_client,
    published_project,
    list_block,
    two_images_block,
):
    """Проверяет, что для блока варианта TWO_IMAGES в ответе остаются только допустимые для него поля."""
    two_images_block.string_list = ['Hidden list item']
    two_images_block.save()
    url = reverse('api:projects-detail', kwargs={'project_id': published_project.slug})
    response = api_client.get(url)
    assert response.status_code == 200
    block = response.json()['content_blocks'][1]
    assert block['variant'] == 2
    assert 'left_image' in block
    assert 'string_list' not in block
    assert 'buttons' not in block


@pytest.mark.django_db
def test_project_detail_hides_variant_specific_fields_for_buttons_block(
    api_client,
    published_project,
    list_block,
    two_images_block,
    buttons_block,
):
    """Проверяет, что для блока варианта IMAGE_WITH_BUTTONS в ответе остаются только допустимые для него поля."""
    buttons_block.left_image = 'https://example.com/hidden-left-image.jpg'
    buttons_block.string_list = ['Hidden list item']
    buttons_block.save()
    url = reverse('api:projects-detail', kwargs={'project_id': published_project.slug})
    response = api_client.get(url)
    assert response.status_code == 200
    block = response.json()['content_blocks'][2]
    assert block['variant'] == 3
    assert 'buttons' in block
    assert len(block['buttons']) == 2
    assert 'string_list' not in block
    assert 'left_image' not in block


@pytest.mark.django_db
def test_project_detail_returns_buttons_in_expected_order(
    api_client,
    published_project,
    list_block,
    two_images_block,
    buttons_block,
):
    """Проверяет, что кнопки в блоке проекта возвращаются в ожидаемом порядке."""
    url = reverse('api:projects-detail', kwargs={'project_id': published_project.slug})
    response = api_client.get(url)
    assert response.status_code == 200
    buttons = response.json()['content_blocks'][2]['buttons']
    assert [button['label'] for button in buttons] == ['Download PDF', 'Visit page']
    assert [button['type'] for button in buttons] == ['download', 'redirect']
