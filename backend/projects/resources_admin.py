from django.utils.translation import gettext_lazy as _
from import_export import resources

from .models import Project, ProjectContentBlock, ProjectType, Tag


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
        fields = [
            'slug',
            'label_ru',
            'label_en',
            'label_sr_latn'
            ]


class ProjectTypeResource(TagResource):
    """Ресурс для импорта экстпорта типов проектов."""

    class Meta(TagResource.Meta):
        model = ProjectType


class ProjectResource(BaseResource):
    """Ресурс для импорта/экстпорта проектов."""

    class Meta(BaseResource.Meta):
        model = Project
        import_id_fields = ['slug']
        fields = [
            'slug',
            'title_ru',
            'title_en',
            'title_sr_latn',
            'description_ru',
            'description_en',
            'description_sr_latn',
            'year',
            ]

    def after_init_instance(self, instance, new, row, **kwargs):
        if 'project_type' in kwargs:
            instance.project_type = kwargs['project_type']


class ProjectContentBlockResource(resources.ModelResource):
    """Ресурс для импорта/экспорта контентного блока проектов."""

    class Meta:
        model = ProjectContentBlock
        import_id_fields = ['title_en']
        fields = [
            'order',
            'title_ru',
            'title_en',
            'title_sr_latn',
            'string_list_ru',
            'string_list_en',
            'string_list_sr_latn',
            'text_ru',
            'text_en',
            'text_sr_latn',
            'accented_text_ru',
            'accented_text_en',
            'accented_text_sr_latn',
        ]

    def after_init_instance(self, instance, new, row, **kwargs):
        if "project" in kwargs:
            instance.project = kwargs["project"]
        if "variant" in kwargs:
            instance.variant = kwargs["variant"]
        return instance
