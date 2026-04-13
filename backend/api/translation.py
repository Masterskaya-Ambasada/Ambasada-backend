from modeltranslation.translator import register, TranslationOptions
from .models import AboutPage, Value, TeamMember, GalleryImage


@register(AboutPage)
class AboutPageTranslationOptions(TranslationOptions):
    fields = (
        'hero_title',
        'hero_description',
        'about_title',
        'paragraph_1',
        'paragraph_2',
        'button_label',
        'values_title',
        'team_title',
        'team_button_label',
        'gallery_title',
    )


@register(Value)
class ValueTranslationOptions(TranslationOptions):
    fields = ('title', 'text')


@register(TeamMember)
class TeamMemberTranslationOptions(TranslationOptions):
    fields = ('name', 'role')


@register(GalleryImage)
class GalleryImageTranslationOptions(TranslationOptions):
    fields = ('alt',)
