import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from projects.models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectType,
    Tag,
)

User = get_user_model()


# =========================================================
# USERS
# =========================================================

@pytest.fixture
def user_factory(db):
    """Фабрика для создания пользователей с произвольными параметрами."""
    def create_user(email='test@example.com', password='password', **kwargs):
        return User.objects.create_user(email=email, password=password, **kwargs)
    return create_user


@pytest.fixture
def regular_user(user_factory):
    """Обычный пользователь (роль USER, без прав staff)."""
    return user_factory(
        email='user@test.com',
        first_name='Ivan',
        last_name='Ivanov',
        role=User.Role.USER
    )


@pytest.fixture
def editor_user(user_factory):
    """Пользователь-редактор контента."""
    return user_factory(email='editor@test.com', role=User.Role.EDITOR)


@pytest.fixture
def admin_user(db):
    """Суперпользователь."""
    return User.objects.create_superuser(
        email='admin@test.com',
        password='adminpassword',
        first_name='Admin',
        last_name='Adminov'
    )


# =========================================================
# API
# =========================================================

@pytest.fixture
def api_client():
    """DRF тестовый клиент."""
    return APIClient()


# =========================================================
# ROJECT TYPES
# =========================================================

@pytest.fixture
def project_type_architecture():
    """Тип проекта: архитектура."""
    return ProjectType.objects.create(
        slug='architecture',
        label='Architecture',
    )


@pytest.fixture
def project_type_research():
    """Тип проекта: исследование."""
    return ProjectType.objects.create(
        slug='research',
        label='Research',
    )


# =========================================================
# TAGS
# =========================================================

@pytest.fixture
def tag_urban():
    """Тег: urban."""
    return Tag.objects.create(
        slug='urban',
        label='Urban',
    )


@pytest.fixture
def tag_social():
    """Тег: social."""
    return Tag.objects.create(
        slug='social',
        label='Social',
    )


@pytest.fixture
def tag_hidden():
    """Тег: скрытый (для непубличных проектов)."""
    return Tag.objects.create(
        slug='hidden',
        label='Hidden',
    )


# =========================================================
# PROJECTS
# =========================================================

@pytest.fixture
def published_project(project_type_architecture, tag_urban, tag_social):
    """Опубликованный проект с тегами urban и social."""
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
    """Второй опубликованный проект."""
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
    """Неопубликованный проект (используется для проверки доступа)."""
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


# =========================================================
# CONTENT BLOCKS
# =========================================================

@pytest.fixture
def list_block(published_project):
    """Контент-блок с изображением и списком."""
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
    """Контент-блок с двумя изображениями."""
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


# =========================================================
# BUTTONS BLOCK
# =========================================================

@pytest.fixture
def buttons_block(published_project):
    """Контент-блок с кнопками действий."""
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