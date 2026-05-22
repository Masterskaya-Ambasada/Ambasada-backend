from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .constants import STRING_LIST_ITEM_MAX_LENGTH, STRING_LIST_MAX_ITEMS


def validate_string_list(value: Any) -> None:
    """Проверяет структуру и ограничения поля string_list."""
    if not isinstance(value, list):
        raise ValidationError(_('Поле string_list должно быть списком строк.'))
    if len(value) > STRING_LIST_MAX_ITEMS:
        raise ValidationError(
            _('Допускается не более %(max_items)s элементов списка.'),
            params={'max_items': STRING_LIST_MAX_ITEMS},
        )
    for item in value:
        if not isinstance(item, str):
            raise ValidationError(_('Каждый элемент списка должен быть строкой.'))
        if len(item) > STRING_LIST_ITEM_MAX_LENGTH:
            raise ValidationError(
                _('Длина каждого элемента списка не должна превышать %(max_length)s символов.'),
                params={'max_length': STRING_LIST_ITEM_MAX_LENGTH},
            )
