"""
Core validators for text fields and media file uploads.

Usage
-----

Text validators — connect in serializer fields:

    from core.validators import validate_no_html, validate_no_urls

    class ArticleSerializer(serializers.Serializer):
        title = serializers.CharField(
            validators=[validate_no_html],
        )
        message = serializers.CharField(
            validators=[validate_no_html, validate_no_urls],
        )

Media validator — connect in model fields:

    from core.validators import MediaFileValidator

    class Project(BaseModel):
        image = models.ImageField(
            upload_to=upload_to_projects,
            validators=[MediaFileValidator()],           # default: IMAGE_TYPES, 10 MB
        )

    # Custom MIME types or size limit:
    from core.validators import MediaFileValidator, DOCUMENT_TYPES

    class Report(BaseModel):
        file = models.FileField(
            upload_to=upload_to_reports,
            validators=[MediaFileValidator(
                allowed_types=DOCUMENT_TYPES,
                max_size_mb=20,
            )],
        )

Predefined MIME type sets:

    IMAGE_TYPES          = ['image/jpeg', 'image/png', 'image/webp']
    IMAGE_TYPES_EXTENDED = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml']
    DOCUMENT_TYPES       = ['application/pdf']

Anti-spam for public forms — Honeypot pattern:

    Honeypot is a hidden field (display: none via CSS, NOT type="hidden").
    Legitimate users never see it. Bots fill all fields automatically — we reject them.

    class ContactSerializer(serializers.Serializer):
        # ... regular fields ...

        website = serializers.CharField(
            required=False,
            allow_blank=True,
            write_only=True,     # never returned in response
        )

        def validate_website(self, value):
            if value and value.strip():
                # Deliberately vague — bots should not learn what triggered rejection
                raise serializers.ValidationError('Invalid submission.')
            return value

    Frontend markup (React / Vue / vanilla):
        <input
            name="website"
            style="display:none"
            tabindex="-1"
            autocomplete="off"
        />
        # Important: never fill this field programmatically — it must arrive empty.
"""

import re

import magic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# ---------------------------------------------------------------------------
# Predefined MIME type sets
# ---------------------------------------------------------------------------

#: Standard web image formats. Use as default for ImageField validators.
IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

#: Extended image set including GIF and SVG.
IMAGE_TYPES_EXTENDED = [*IMAGE_TYPES, 'image/gif', 'image/svg+xml']

#: PDF documents only.
DOCUMENT_TYPES = ['application/pdf']


# ---------------------------------------------------------------------------
# Text validators
# ---------------------------------------------------------------------------


def validate_no_html(value: str) -> None:
    """
    Reject values containing HTML tags.

    Protects against XSS when user input ends up in emails,
    logs, or is rendered without escaping.

    Example blocked input: <script>alert(1)</script>, <b>bold</b>
    """
    if re.search(r'<[^>]+>', value):
        raise ValidationError(_('HTML tags are not allowed.'))


def validate_no_urls(value: str) -> None:
    """
    Reject values containing HTTP/HTTPS links or bare www. addresses.

    Filters out the majority of spam messages that contain
    advertising or phishing links.

    Example blocked input: https://spam.com, www.ads.net/promo
    """
    if re.search(r'(https?://|www\.)\S+', value, re.IGNORECASE):
        raise ValidationError(_('Links in messages are not allowed.'))


# ---------------------------------------------------------------------------
# Media file validator
# ---------------------------------------------------------------------------


class MediaFileValidator:
    """
    Validate uploaded files by real MIME type (magic bytes) and size.

    Reads the first 2048 bytes of the file to detect its true type —
    independent of the file extension. This prevents MIME spoofing,
    e.g. a PHP script renamed to photo.webp will be detected and rejected.

    Implements __eq__ and deconstruct so Django can serialize
    this validator into migrations without errors.

    Args:
        allowed_types:  List of accepted MIME type strings.
                        Defaults to IMAGE_TYPES (jpeg, png, webp).
        max_size_mb:    Maximum allowed file size in megabytes.
                        Defaults to 10 MB.

    Raises:
        ValidationError: if the file's MIME type is not in allowed_types,
                         or if the file size exceeds max_size_mb.
    """

    def __init__(
        self,
        allowed_types: list[str] | None = None,
        max_size_mb: int = 10,
    ) -> None:
        """Initialize validator with allowed MIME types and maximum file size."""
        self.allowed_types = allowed_types or IMAGE_TYPES
        self.max_size_mb = max_size_mb
        self._max_size_bytes = max_size_mb * 1024 * 1024

    def __call__(self, file) -> None:
        self._validate_size(file)
        self._validate_mime(file)

    def _validate_size(self, file) -> None:
        if file.size > self._max_size_bytes:
            raise ValidationError(
                _('File size %(size).1f MB exceeds the limit of %(max)d MB.')
                % {
                    'size': file.size / (1024 * 1024),
                    'max': self.max_size_mb,
                }
            )

    def _validate_mime(self, file) -> None:
        file.seek(0)
        mime = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)  # reset pointer so Django can continue saving the file

        if mime not in self.allowed_types:
            raise ValidationError(
                _('File type "%(mime)s" is not allowed. Accepted: %(allowed)s.')
                % {
                    'mime': mime,
                    'allowed': ', '.join(self.allowed_types),
                }
            )

    def __eq__(self, other: object) -> bool:
        """Required for stable migration comparison."""
        return (
            isinstance(other, MediaFileValidator)
            and self.allowed_types == other.allowed_types
            and self.max_size_mb == other.max_size_mb
        )

    def deconstruct(self) -> tuple:
        """Required for Django to serialize this validator into migrations."""
        return (
            'core.validators.MediaFileValidator',
            [],
            {
                'allowed_types': self.allowed_types,
                'max_size_mb': self.max_size_mb,
            },
        )
