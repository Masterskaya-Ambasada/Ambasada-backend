import pytest
from django.forms.models import inlineformset_factory
from projects.admin_forms import ProjectContentBlockInlineFormSet
from projects.models import Project, ProjectContentBlock


def _content_block_form_data(index: int, order: int, title: str) -> dict[str, str]:
    prefix = f'content_blocks-{index}'
    return {
        f'{prefix}-variant': ProjectContentBlock.Variant.IMAGE_WITH_LIST,
        f'{prefix}-order': str(order),
        f'{prefix}-title': title,
        f'{prefix}-image': f'https://example.com/{title}.jpg',
        f'{prefix}-left_image': '',
        f'{prefix}-text': '',
        f'{prefix}-accented_text': '',
        f'{prefix}-string_list': '["One"]',
    }


@pytest.mark.django_db
def test_project_content_block_inline_rejects_duplicate_order(published_project):
    """Checks that the project admin inline validates duplicate content block order."""
    formset_class = inlineformset_factory(
        Project,
        ProjectContentBlock,
        fields=('variant', 'order', 'title', 'image', 'left_image', 'text', 'accented_text', 'string_list'),
        formset=ProjectContentBlockInlineFormSet,
        extra=0,
        can_delete=True,
    )
    form_data = {
        'content_blocks-TOTAL_FORMS': '2',
        'content_blocks-INITIAL_FORMS': '0',
        'content_blocks-MIN_NUM_FORMS': '0',
        'content_blocks-MAX_NUM_FORMS': '1000',
        **_content_block_form_data(0, 10, 'first-block'),
        **_content_block_form_data(1, 10, 'second-block'),
    }
    formset = formset_class(data=form_data, instance=published_project, prefix='content_blocks')
    assert not formset.is_valid()
    assert 'order' in str(formset.non_form_errors())
