from __future__ import annotations

from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings

from api.projects.constants import (
    PAGINATION_IS_NEXT_KEY,
    PAGINATION_LIMIT_KEY,
    PAGINATION_OFFSET_KEY,
    PAGINATION_TOTAL_ITEMS_KEY,
    PROJECT_LIST_RESPONSE_ITEMS_KEY,
    PROJECT_LIST_RESPONSE_PAGINATION_KEY,
)


class ProjectLimitOffsetPagination(LimitOffsetPagination):
    """Пагинация проектов с полями offset и limit в ответе API."""

    default_limit = api_settings.PAGE_SIZE
    max_limit = settings.REST_FRAMEWORK.get('MAX_PAGE_SIZE')

    def get_paginated_response(self, data):
        """Возвращает пагинированный ответ."""
        return Response(
            {
                PROJECT_LIST_RESPONSE_ITEMS_KEY: data,
                PROJECT_LIST_RESPONSE_PAGINATION_KEY: {
                    PAGINATION_TOTAL_ITEMS_KEY: self.count,
                    PAGINATION_OFFSET_KEY: self.offset,
                    PAGINATION_LIMIT_KEY: self.limit,
                    PAGINATION_IS_NEXT_KEY: self.get_next_link() is not None,
                },
            }
        )

    def get_paginated_response_schema(self, schema):
        """Возвращает OpenAPI-схему в фактическом формате API."""
        return {
            'type': 'object',
            'properties': {
                PROJECT_LIST_RESPONSE_ITEMS_KEY: schema,
                PROJECT_LIST_RESPONSE_PAGINATION_KEY: {
                    'type': 'object',
                    'properties': {
                        PAGINATION_TOTAL_ITEMS_KEY: {'type': 'integer', 'example': 80},
                        PAGINATION_OFFSET_KEY: {'type': 'integer', 'example': 20},
                        PAGINATION_LIMIT_KEY: {'type': 'integer', 'example': 20},
                        PAGINATION_IS_NEXT_KEY: {'type': 'boolean', 'example': True},
                    },
                    'required': [
                        PAGINATION_TOTAL_ITEMS_KEY,
                        PAGINATION_OFFSET_KEY,
                        PAGINATION_LIMIT_KEY,
                        PAGINATION_IS_NEXT_KEY,
                    ],
                },
            },
            'required': [PROJECT_LIST_RESPONSE_ITEMS_KEY, PROJECT_LIST_RESPONSE_PAGINATION_KEY],
        }
