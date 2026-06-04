import pytest
from django.core.exceptions import ValidationError
from home.models import HomePageContent


@pytest.mark.django_db
def test_home_page_content_singleton_creation(home_page_content):
    """Проверка, что синглтон успешно создается и возвращает верное имя."""
    assert HomePageContent.objects.count() == 1
    assert str(home_page_content) == 'Контент главной страницы'


@pytest.mark.django_db
def test_home_page_content_integrity_error_on_multiple_instances(
    home_page_content,
):
    """Проверка, что создание второго экземпляра вызывает ошибку валидации."""
    with pytest.raises(ValidationError):
        duplicate_content = HomePageContent(
            title_ru='Второй экземпляр',
            subtitle_ru='Должен вызвать ошибку',
        )
        duplicate_content.full_clean()
        duplicate_content.save()

    assert HomePageContent.objects.count() == 1