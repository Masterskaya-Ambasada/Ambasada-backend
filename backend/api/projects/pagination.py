"""Кастомная пагинация проектов."""

from __future__ import annotations

from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings


class ProjectLimitOffsetPagination(LimitOffsetPagination):
    """Пагинация проектов с полями offset и limit в ответе API."""

    default_limit = api_settings.PAGE_SIZE
    max_limit = settings.REST_FRAMEWORK.get('MAX_PAGE_SIZE')

    def get_paginated_response(self, data):
        """Возвращает пагинированный ответ."""
        return Response(
            {
                'items': data,
                'pagination': {
                    'totalItems': self.count,
                    'offset': self.offset,
                    'limit': self.limit,
                    'isNext': self.get_next_link() is not None,
                },
            }
        )

    def get_paginated_response_schema(self, schema):
        """Возвращает OpenAPI-схему в фактическом формате API."""
        return {
            'type': 'object',
            'properties': {
                'items': schema,
                'pagination': {
                    'type': 'object',
                    'properties': {
                        'totalItems': {'type': 'integer', 'example': 80},
                        'offset': {'type': 'integer', 'example': 20},
                        'limit': {'type': 'integer', 'example': 20},
                        'isNext': {'type': 'boolean', 'example': True},
                    },
                    'required': ['totalItems', 'offset', 'limit', 'isNext'],
                },
            },
            'required': ['items', 'pagination'],
        }
