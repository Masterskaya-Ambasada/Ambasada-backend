from import_export import fields, resources
from .models import Tag, ProjectContentBlock, Project, ProjectType
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from import_export.results import Error, Result


class BaseResource(resources.ModelResource):
    """Базовый класс для импорта/экспорта ресурсов с общими настройками."""
    
    class Meta:
        abstract = True
        report_skipped = True
        use_transactions = True
        skip_rows_with_errors = False
   
    def before_import_row(self, row, **kwargs):
        """Проверка обязательных полей перед импортом."""
        if not row.get('slug'): # добавить проверку всех обязательных полей
            raise ValueError(_("slug: Это поле обязательно для заполнения"))
        return row


class TagResource(BaseResource):
    """Ресурс для импорта/экспорта тегов."""

    class Meta(BaseResource.Meta):
        model = Tag
        import_id_fields = ['slug']
        fields = ['slug',
                  'label_ru',
                  'label_en',
                  'label_sr_latn']


class ProjectTypeResource(TagResource):
    """Ресурс для импорта экстпорта типов проектов."""
    
    class Meta(TagResource.Meta):
        model = ProjectType


class ProjectContentBlockResource(resources.ModelResource):
    """Ресурс для импорта/экспорта контентного блока проектов."""

    class Meta:
        model = ProjectContentBlock


class ProjectResource(resources.ModelResource):
    """Ресурс для импорта экстпорта проектов."""

    class Meta:
        model = Project



