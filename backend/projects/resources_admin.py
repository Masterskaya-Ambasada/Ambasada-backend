"""Классы ресурсов для импорта csv."""

from django.utils.translation import gettext_lazy as _
from import_export import resources

from .models import ProjectType, Tag


class BaseResource(resources.ModelResource):
    """Базовый класс для импорта/экспорта ресурсов с общими настройками."""

    class Meta:
        abstract = True
        report_skipped = True
        use_transactions = True
        skip_rows_with_errors = False

    def before_import_row(self, row, **kwargs):
        """Проверка обязательных полей перед импортом."""
        if not row.get('slug'):  # добавить проверку всех обязательных полей
            raise ValueError(_('slug: Это поле обязательно для заполнения'))
        return row


class TagResource(BaseResource):
    """Ресурс для импорта/экспорта тегов."""

    class Meta(BaseResource.Meta):
        model = Tag
        import_id_fields = ['slug']
        fields = ['slug', 'label_ru', 'label_en', 'label_sr_latn']


class ProjectTypeResource(TagResource):
    """Ресурс для импорта экстпорта типов проектов."""

    class Meta(TagResource.Meta):
        model = ProjectType
