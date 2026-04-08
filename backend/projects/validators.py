"""Переиспользуемые валидаторы приложения проектов."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError

from projects.constants import STRING_LIST_ITEM_MAX_LENGTH, STRING_LIST_MAX_ITEMS


def validate_string_list(value: Any) -> None:
    """Проверяет структуру и ограничения поля string_list."""
    if not isinstance(value, list):
        raise ValidationError('Поле string_list должно быть списком строк.')
    if len(value) > STRING_LIST_MAX_ITEMS:
        raise ValidationError(f'Допускается не более {STRING_LIST_MAX_ITEMS} элементов списка.')
    for item in value:
        if not isinstance(item, str):
            raise ValidationError('Каждый элемент списка должен быть строкой.')
        if len(item) > STRING_LIST_ITEM_MAX_LENGTH:
            raise ValidationError(
                'Длина каждого элемента списка не должна ' f'превышать {STRING_LIST_ITEM_MAX_LENGTH} символов.'
            )
