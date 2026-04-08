from modeltranslation.translator import TranslationOptions, register

from .models import User


@register(User)
class UserTranslationOptions(TranslationOptions):
    """Translation options for the User model."""

    fields = (
        'first_name',
        'last_name',
    )  # Fields of the User model that should be translated
