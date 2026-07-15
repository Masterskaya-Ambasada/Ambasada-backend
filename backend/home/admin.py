from core.base_admin import BaseAdmin
from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .constants import HOME_PROJECTS_PREVIEW_LIMIT
from .models import HomePageContent, HomePageProject

HOME_IMAGE_PREVIEW_FIELDS = ('image_left', 'image_right', 'about_image')


class HomePageContentAdminForm(forms.ModelForm):
    """Кастомная форма для гарантированного предзаполнения языковых полей контента."""

    class Meta:
        model = HomePageContent
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Инициализация полей формы дефолтными значениями, если они пусты."""
        super().__init__(*args, **kwargs)

        for field_name in HOME_IMAGE_PREVIEW_FIELDS:
            if field_name in self.fields:
                widget_classes = self.fields[field_name].widget.attrs.get('class', '').split()
                if BaseAdmin.image_preview_input_class not in widget_classes:
                    widget_classes.append(BaseAdmin.image_preview_input_class)
                self.fields[field_name].widget.attrs['class'] = ' '.join(widget_classes)

        defaults = {
            # === 1. РУССКИЙ ЯЗЫК (RU) ===
            'title_ru': 'Амбасада за урбанизам',
            'subtitle_ru': 'Исследуем, проектируем и меняем городскую среду Белграда',
            'hero_button_label_ru': 'Смотреть проекты',
            'about_title_ru': 'О сообществе',
            'about_text_ru': 'Мы объединяем урбанистов, архитекторов и жителей для создания комфортного города.',
            'projects_title_ru': 'Наши проекты',
            'projects_button_label_ru': 'Все проекты',
            # === 2. АНГЛИЙСКИЙ ЯЗЫК (EN) ===
            'title_en': 'Ambasada za Urbanizam',
            'subtitle_en': 'Exploring, designing and changing the urban environment of Belgrade',
            'hero_button_label_en': 'View Projects',
            'about_title_en': 'About community',
            'about_text_en': 'We bring together urbanists, architects, and citizens to create a liveable city.',
            'projects_title_en': 'Our Projects',
            'projects_button_label_en': 'All projects',
            # === 3. СЕРБСКИЙ (ЛАТИНИЦА - SR_LATN) ===
            'title_sr_latn': 'Ambasada za urbanizam',
            'subtitle_sr_latn': 'Istražujemo, projektujemo i menjamo urbanu sredinu Beograda',
            'hero_button_label_sr_latn': 'Pogledaj projekte',
            'about_title_sr_latn': 'O zajednici',
            'about_text_sr_latn': 'Spajamo urbaniste, arhitekte i građane radi stvaranja udobnog grada.',
            'projects_title_sr_latn': 'Naši projekti',
            'projects_button_label_sr_latn': 'Svi projekti',
            # === 4. СЕРБСКИЙ (КИРИЛЛИЦА - SR_CYRL) ===
            'title_sr_cyrl': 'Амбасада за урбанизам',
            'subtitle_sr_cyrl': 'Истражујемо, пројектујемо и мењамо урбану среду Београда',
            'hero_button_label_sr_cyrl': 'Погледај пројекте',
            'about_title_sr_cyrl': 'О заједници',
            'about_text_sr_cyrl': 'Спајамо урбанисте, архитекте и грађане ради стварања удобног града.',
            'projects_title_sr_cyrl': 'Наши пројекти',
            'projects_button_label_sr_cyrl': 'Сви пројекти',
        }

        for field_name, default_value in defaults.items():
            if field_name in self.fields:
                is_empty = not self.instance.pk or not getattr(self.instance, field_name, None)
                if is_empty:
                    self.fields[field_name].initial = default_value


class HomePageProjectInline(admin.TabularInline):
    """Инлайн для ручной сортировки проектов на главной странице."""

    model = HomePageProject
    extra = 0
    max_num = HOME_PROJECTS_PREVIEW_LIMIT
    fields = ('order', 'project')
    ordering = ('order', 'pk')
    autocomplete_fields = ('project',)


@admin.register(HomePageContent)
class HomePageContentAdmin(BaseAdmin):
    """Администрирование контента главной страницы (Singleton)."""

    form = HomePageContentAdminForm
    ordering = ('id',)
    list_display = ['__str__']
    tinymce_fields = []
    readonly_fields = (
        'image_left_preview',
        'image_right_preview',
        'about_image_preview',
    )
    inlines = (HomePageProjectInline,)

    fieldsets = (
        (
            _('1. Общие медиафайлы и ссылки'),
            {
                'fields': (
                    'image_left',
                    'image_left_preview',
                    'image_right',
                    'image_right_preview',
                    'about_image',
                    'about_image_preview',
                    'hero_button_link',
                    'projects_button_link',
                ),
                'description': _('Изображения и целевые ссылки, общие для всех версий.'),
            },
        ),
        (
            _('2. Локализация: Русский (RU)'),
            {
                'fields': (
                    'title_ru',
                    'subtitle_ru',
                    'hero_button_label_ru',
                    'about_title_ru',
                    'about_text_ru',
                    'projects_title_ru',
                    'projects_button_label_ru',
                ),
                'classes': ('collapse',),
                'description': _('Контент экрана на русском языке.'),
            },
        ),
        (
            _('3. Локализация: Английский (EN)'),
            {
                'fields': (
                    'title_en',
                    'subtitle_en',
                    'hero_button_label_en',
                    'about_title_en',
                    'about_text_en',
                    'projects_title_en',
                    'projects_button_label_en',
                ),
                'classes': ('collapse',),
                'description': _('Контент экрана на английском языке.'),
            },
        ),
        (
            _('4. Локализация: Сербский Латиница (SR-Latn)'),
            {
                'fields': (
                    'title_sr_latn',
                    'subtitle_sr_latn',
                    'hero_button_label_sr_latn',
                    'about_title_sr_latn',
                    'about_text_sr_latn',
                    'projects_title_sr_latn',
                    'projects_button_label_sr_latn',
                ),
                'classes': ('collapse',),
                'description': _('Контент экрана на сербской латинице.'),
            },
        ),
        (
            _('5. Локализация: Сербский Кириллица (SR-Cyrl)'),
            {
                'fields': (
                    'title_sr_cyrl',
                    'subtitle_sr_cyrl',
                    'hero_button_label_sr_cyrl',
                    'about_title_sr_cyrl',
                    'about_text_sr_cyrl',
                    'projects_title_sr_cyrl',
                    'projects_button_label_sr_cyrl',
                ),
                'classes': ('collapse',),
                'description': _('Контент экрана на сербской кириллице.'),
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Интеграция классов виджетов для JS-превью картинок."""
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        return self.add_image_preview_widget_class(db_field, formfield)

    @admin.display(description=_('Превью левого изображения'))
    def image_left_preview(self, obj):
        """Рендеринг превью левого изображения."""
        return self.get_admin_image_preview(obj, 'image_left', width=220, height=220)

    @admin.display(description=_('Превью правого изображения'))
    def image_right_preview(self, obj):
        """Рендеринг превью правого изображения."""
        return self.get_admin_image_preview(obj, 'image_right', width=220, height=220)

    @admin.display(description=_('Превью изображения секции О Нас'))
    def about_image_preview(self, obj):
        """Рендеринг превью изображения секции О Нас."""
        return self.get_admin_image_preview(obj, 'about_image', width=220, height=220)

    def has_add_permission(self, request):
        """Запрет на создание более одного экземпляра контента."""
        if HomePageContent.objects.exists():
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context=None):
        """Перенаправление со списка на редактирование синглтона."""
        existing_instance = HomePageContent.objects.only('pk').first()
        if existing_instance:
            return redirect(
                reverse(
                    'admin:home_homepagecontent_change',
                    args=[existing_instance.pk],
                )
            )
        return super().changelist_view(request, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        """Перенаправление с формы добавления на редактирование синглтона."""
        existing_instance = HomePageContent.objects.only('pk').first()
        if existing_instance:
            return redirect(
                reverse(
                    'admin:home_homepagecontent_change',
                    args=[existing_instance.pk],
                )
            )
        return super().add_view(request, form_url, extra_context)

    def has_delete_permission(self, request, obj=None):
        """Полный запрет удаления конфигурации контента."""
        return False

    def get_actions(self, request):
        """Исключение массового удаления из доступных экшенов."""
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    class Media:
        """Подключение скриптов и стилей визуального оформления превью."""

        js = ('core/js/admin_image_preview_inline.js',)
        css = {
            'all': ('core/css/admin_image_preview.css',),
        }
