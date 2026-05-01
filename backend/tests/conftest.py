import pytest
from rest_framework.test import APIClient

from projects.models import (
    Project,
    ProjectBlockButton,
    ProjectContentBlock,
    ProjectType,
    Tag,
)


@pytest.fixture(autouse=True)
def disable_rest_framework_throttling(settings):
    """Отключает throttling в тестах, чтобы они не зависели от Redis."""
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }


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


# Для ABOUT (новые фикстуры)
@pytest.fixture
def about_page(db):
    """Создает страницу 'О нас'."""
    from about.models import AboutPage

    return AboutPage.objects.create(
        hero_title="Hero",
        hero_description="Hero description",
        about_title="About",
        button_label="Button",
        button_link="/projects",
        values_title="Values",
        team_title="Team",
        team_button_label="Join",
        team_button_link="/join",
        gallery_title="Gallery",
    )


@pytest.fixture
def values(db):
    """Создает список ценностей."""
    from about.models import Value

    return Value.objects.bulk_create([
        Value(title="Value 1", text="Text 1"),
        Value(title="Value 2", text="Text 2"),
    ])


@pytest.fixture
def gallery_images(db):
    """Создает изображения галереи."""
    from about.models import GalleryImage

    return GalleryImage.objects.bulk_create([
        GalleryImage(alt="Image 1"),
        GalleryImage(alt="Image 2"),
    ])


@pytest.fixture
def team_members(db, django_user_model):
    """Создает участников команды."""
    return [
        django_user_model.objects.create(
            email="user1@test.com",
            first_name="User",
            last_name="One",
        ),
        django_user_model.objects.create(
            email="user2@test.com",
            first_name="User",
            last_name="Two",
        ),
    ]


@pytest.fixture
def about_full_setup(about_page, values, gallery_images, team_members):
    """
    Полная подготовка данных для About API:
    - страница
    - ценности
    - участники команды
    - галерея
    """
    about_page.team_members.set(team_members)
    return {
        "page": about_page,
        "values": values,
        "members": team_members,
        "images": gallery_images,
    }