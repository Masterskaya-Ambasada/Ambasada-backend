import pytest
from django.core.exceptions import ValidationError

from projects.constants import STRING_LIST_ITEM_MAX_LENGTH, STRING_LIST_MAX_ITEMS
from projects.validators import validate_string_list


def test_validate_string_list_accepts_valid_list():
    """Проверяет, что валидный список строк проходит валидацию без ошибок."""
    validate_string_list(['One', 'Two', 'Three'])


def test_validate_string_list_raises_error_when_value_is_not_list():
    """Проверяет, что валидатор отклоняет значение, если передан не список."""
    with pytest.raises(ValidationError) as exc_info:
        validate_string_list('not-a-list')
    assert 'должно быть списком строк' in str(exc_info.value)


def test_validate_string_list_raises_error_when_list_has_too_many_items():
    """Проверяет, что валидатор отклоняет список, если превышено допустимое число элементов."""
    value = ['item'] * (STRING_LIST_MAX_ITEMS + 1)
    with pytest.raises(ValidationError) as exc_info:
        validate_string_list(value)
    assert 'не более' in str(exc_info.value)


def test_validate_string_list_raises_error_when_item_is_not_string():
    """Проверяет, что валидатор отклоняет список, если хотя бы один элемент не является строкой."""
    with pytest.raises(ValidationError) as exc_info:
        validate_string_list(['valid', 123])
    assert 'должен быть строкой' in str(exc_info.value)


def test_validate_string_list_raises_error_when_item_is_too_long():
    """Проверяет, что валидатор отклоняет список, если длина элемента превышает допустимый предел."""
    too_long_item = 'x' * (STRING_LIST_ITEM_MAX_LENGTH + 1)
    with pytest.raises(ValidationError) as exc_info:
        validate_string_list([too_long_item])
    assert 'не должна превышать' in str(exc_info.value)
