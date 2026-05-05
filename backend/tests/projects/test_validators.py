import pytest
from django.core.exceptions import ValidationError

from projects.constants import STRING_LIST_ITEM_MAX_LENGTH, STRING_LIST_MAX_ITEMS
from projects.validators import validate_string_list


def test_validate_string_list_accepts_valid_list():
    validate_string_list(['One', 'Two', 'Three'])


def test_validate_string_list_raises_error_when_value_is_not_list():
    with pytest.raises(ValidationError) as exc_info:
        validate_string_list('not-a-list')
    assert 'должно содержать список строк' in str(exc_info.value).lower()


def test_validate_string_list_raises_error_when_list_has_too_many_items():
    value = ['item'] * (STRING_LIST_MAX_ITEMS + 1)
    with pytest.raises(ValidationError) as exc_info:
        validate_string_list(value)
    assert 'максимальное количество элементов списка: 20' in str(exc_info.value).lower()


def test_validate_string_list_raises_error_when_item_is_not_string():
    with pytest.raises(ValidationError) as exc_info:
        validate_string_list(['valid', 123])
    assert 'строк' in str(exc_info.value).lower()


def test_validate_string_list_raises_error_when_item_is_too_long():
    too_long_item = 'x' * (STRING_LIST_ITEM_MAX_LENGTH + 1)
    with pytest.raises(ValidationError) as exc_info:
        validate_string_list([too_long_item])
    assert 'длина' in str(exc_info.value).lower() or 'превышать' in str(exc_info.value).lower()