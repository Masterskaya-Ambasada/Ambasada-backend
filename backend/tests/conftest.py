"""Pytest configuration for test environment."""

import pytest
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient

from projects.models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectType,
    Tag,
)


# Test settings with local memory cache instead of Redis
TEST_CACHE_SETTINGS = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


@pytest.fixture(autouse=True)
def configure_cache(settings):
    """Configure local memory cache for tests instead of Redis."""
    with override_settings(CACHES=TEST_CACHE_SETTINGS):
        # Reconfigure cache with new settings
        from django.core.cache import caches
        cache.close()
        caches['default'].close()
        yield
        cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def project_type_architecture():
    return ProjectType.objects.create(
        slug='architecture',
        label='Architecture',
    )


@pytest.fixture
def project_type_research():
    return ProjectType.objects.create(
        slug='research',
        label='Research',
    )


@pytest.fixture
def tag_urban():
    return Tag.objects.create(
        slug='urban',
        label='Urban',
    )


@pytest.fixture
def tag_social():
    return Tag.objects.create(
        slug='social',
        label='Social',
    )


@pytest.fixture
def tag_hidden():
    return Tag.objects.create(
        slug='hidden',
        label='Hidden',
    )


@pytest.fixture
def published_project(project_type_architecture, tag_urban, tag_social):
    project = Project.objects.create(
        slug='central-park',
        title='Central Park',
        description='Public space improvement project.',
        year=2024,
        cover_image='projects/central-park/cover/central-park.jpg',
        project_type=project_type_architecture,
        is_published=True,
    )
    project.tags.set([tag_urban, tag_social])
    return project


@pytest.fixture
def second_published_project(project_type_research, tag_social):
    project = Project.objects.create(
        slug='city-research',
        title='City Research',
        description='Research about city mobility.',
        year=2023,
        cover_image='projects/city-research/cover/city-research.jpg',
        project_type=project_type_research,
        is_published=True,
    )
    project.tags.set([tag_social])
    return project


@pytest.fixture
def unpublished_project(project_type_architecture, tag_hidden):
    project = Project.objects.create(
        slug='secret-project',
        title='Secret Project',
        description='This project must stay hidden.',
        year=2025,
        cover_image='projects/secret-project/cover/secret.jpg',
        project_type=project_type_architecture,
        is_published=False,
    )
    project.tags.set([tag_hidden])
    return project


@pytest.fixture
def list_block(published_project):
    return ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        order=1,
        title='List block',
        image='https://example.com/list-block.jpg',
        string_list=['First point', 'Second point'],
        text='<p>Main text</p>',
        accented_text='<p>Accent text</p>',
    )


@pytest.fixture
def two_images_block(published_project):
    return ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.TWO_IMAGES,
        order=2,
        title='Two images block',
        image='https://example.com/right-image.jpg',
        left_image='https://example.com/left-image.jpg',
        text='<p>Two images text</p>',
        accented_text='',
    )


@pytest.fixture
def buttons_block(published_project):
    block = ProjectContentBlock.objects.create(
        project=published_project,
        variant=ProjectContentBlock.Variant.IMAGE_WITH_BUTTONS,
        order=3,
        title='Buttons block',
        image='https://example.com/buttons-block.jpg',
        text='<p>Buttons text</p>',
        accented_text='<p>Buttons accent</p>',
    )
    ProjectBlockButton.objects.create(
        block=block,
        order=1,
        label='Download PDF',
        type=ProjectBlockButton.ButtonType.DOWNLOAD,
        url='https://example.com/file.pdf',
    )
    ProjectBlockButton.objects.create(
        block=block,
        order=2,
        label='Visit page',
        type=ProjectBlockButton.ButtonType.REDIRECT,
        url='https://example.com/page',
    )
    return block
