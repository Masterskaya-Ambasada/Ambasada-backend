from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from nested_admin.formsets import NestedInlineFormSet

from projects.constants import DEFAULT_ORDER


class ProjectContentBlockInlineFormSet(NestedInlineFormSet):
    """Проверяет уникальность порядка блоков в рамках формы проекта."""

    def clean(self):
        super().clean()
        seen_orders = set()
        for form in self.forms:
            if not hasattr(form, 'cleaned_data') or form.cleaned_data.get('DELETE'):
                continue
            order = form.cleaned_data.get('order')
            if order is None or order == DEFAULT_ORDER:
                continue
            if order in seen_orders:
                raise ValidationError(_('Порядок контентных блоков внутри одного проекта не должен повторяться.'))
            seen_orders.add(order)
