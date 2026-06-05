import re

import magic
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
IMAGE_TYPES_EXTENDED = [*IMAGE_TYPES, 'image/gif', 'image/svg+xml']
DOCUMENT_TYPES = ['application/pdf']


# ---------------------------------------------------------------------------
# Валидаторы текста
# ---------------------------------------------------------------------------


def validate_no_html(value: str) -> None:
    """Запрещает использование HTML-тегов для предотвращения XSS-атак."""
    if re.search(r'<[^>]+>', value):
        raise ValidationError(_('Использование HTML-тегов запрещено.'))


def validate_no_urls(value: str) -> None:
    """Запрещает публикацию ссылок (http/https/www) для защиты от спама."""
    if re.search(r'(https?://|www\.)\S+', value, re.IGNORECASE):
        raise ValidationError(_('Добавление ссылок в текст запрещено.'))


# ---------------------------------------------------------------------------
# Валидатор медиафайлов
# ---------------------------------------------------------------------------


class MediaFileValidator:
    """Валидация файла по реальному MIME-типу (через magic bytes) и размеру."""

    def __init__(
        self,
        allowed_types: list[str] | None = None,
        max_size_mb: int = 20,
    ) -> None:
        """Инициализация: разрешенные типы (MIME) и макс. размер в МБ."""
        self.allowed_types = allowed_types or IMAGE_TYPES
        self.max_size_mb = max_size_mb
        self._max_size_bytes = max_size_mb * 1024 * 1024

    def __call__(self, file) -> None:
        uploaded_file = self._get_uploaded_file(file)
        if uploaded_file is None:
            return

        self._validate_size(uploaded_file)
        self._validate_mime(uploaded_file)

    def _get_uploaded_file(self, file) -> UploadedFile | None:
        """Возвращает загружаемый файл и пропускает уже сохраненные пути."""
        if isinstance(file, UploadedFile):
            return file

        wrapped_file = getattr(file, '_file', None)
        if isinstance(wrapped_file, UploadedFile):
            return wrapped_file

        return None

    def _validate_size(self, file) -> None:
        if file.size > self._max_size_bytes:
            raise ValidationError(
                _('Размер файла (%(size).1f МБ) превышает лимит в %(max)d МБ.')
                % {
                    'size': file.size / (1024 * 1024),
                    'max': self.max_size_mb,
                }
            )

    def _validate_mime(self, file) -> None:
        file.seek(0)
        mime = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)

        if mime not in self.allowed_types:
            raise ValidationError(
                _('Файл типа "%(mime)s" запрещен. Допустимые: %(allowed)s.')
                % {
                    'mime': mime,
                    'allowed': ', '.join(self.allowed_types),
                }
            )

    def __eq__(self, other: object) -> bool:
        """Сравнение для корректной работы миграций."""
        return (
            isinstance(other, MediaFileValidator)
            and self.allowed_types == other.allowed_types
            and self.max_size_mb == other.max_size_mb
        )

    def deconstruct(self) -> tuple:
        """Сериализация для миграций Django."""
        return (
            'core.validators.MediaFileValidator',
            [],
            {
                'allowed_types': self.allowed_types,
                'max_size_mb': self.max_size_mb,
            },
        )
