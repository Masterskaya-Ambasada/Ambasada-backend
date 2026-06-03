from core.base_admin import BaseAdmin
from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import HomePageContent


class HomePageContentAdminForm(forms.ModelForm):
    """Кастомная форма для предзаполнения языковых полей контента."""

    class Meta:
        model = HomePageContent
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Инициализация полей формы дефолтными значениями."""
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            # === 1. РУССКИЙ ЯЗЫК (RU) ===
            if 'title_ru' in self.fields:
                self.fields['title_ru'].initial = 'Амбасада за урбанизам'
            if 'subtitle_ru' in self.fields:
                self.fields['subtitle_ru'].initial = 'Исследуем, проектируем и меняем городскую среду Белграда'
            if 'hero_button_label_ru' in self.fields:
                self.fields['hero_button_label_ru'].initial = 'Смотреть проекты'
            if 'about_title_ru' in self.fields:
                self.fields['about_title_ru'].initial = 'О сообществе'
            if 'about_text_ru' in self.fields:
                self.fields[
                    'about_text_ru'
                ].initial = 'Мы объединяем урбанистов, архитекторов и жителей для создания комфортного города.'
            if 'projects_title_ru' in self.fields:
                self.fields['projects_title_ru'].initial = 'Наши проекты'
            if 'projects_button_label_ru' in self.fields:
                self.fields['projects_button_label_ru'].initial = 'Все проекты'

            # === 2. АНГЛИЙСКИЙ ЯЗЫК (EN) ===
            if 'title_en' in self.fields:
                self.fields['title_en'].initial = 'Ambasada za Urbanizam'
            if 'subtitle_en' in self.fields:
                self.fields[
                    'subtitle_en'
                ].initial = 'Exploring, designing and changing the urban environment of Belgrade'
            if 'hero_button_label_en' in self.fields:
                self.fields['hero_button_label_en'].initial = 'View Projects'
            if 'about_title_en' in self.fields:
                self.fields['about_title_en'].initial = 'About community'
            if 'about_text_en' in self.fields:
                self.fields[
                    'about_text_en'
                ].initial = 'We bring together urbanists, architects, and citizens to create a liveable city.'
            if 'projects_title_en' in self.fields:
                self.fields['projects_title_en'].initial = 'Our Projects'
            if 'projects_button_label_en' in self.fields:
                self.fields['projects_button_label_en'].initial = 'All projects'

            # === 3. СЕРБСКИЙ (ЛАТИНИЦА - SR_LATN) ===
            if 'title_sr_latn' in self.fields:
                self.fields['title_sr_latn'].initial = 'Ambasada za urbanizam'
            if 'subtitle_sr_latn' in self.fields:
                self.fields['subtitle_sr_latn'].initial = 'Istražujemo, projektujemo i menjamo urbanu sredinu Beograda'
            if 'hero_button_label_sr_latn' in self.fields:
                self.fields['hero_button_label_sr_latn'].initial = 'Pogledaj projekte'
            if 'about_title_sr_latn' in self.fields:
                self.fields['about_title_sr_latn'].initial = 'O zajednici'
            if 'about_text_sr_latn' in self.fields:
                self.fields[
                    'about_text_sr_latn'
                ].initial = 'Spajamo urbaniste, arhitekte i građane radi stvaranja udobnog grada.'
            if 'projects_title_sr_latn' in self.fields:
                self.fields['projects_title_sr_latn'].initial = 'Naši projekti'
            if 'projects_button_label_sr_latn' in self.fields:
                self.fields['projects_button_label_sr_latn'].initial = 'Svi projekti'

            # === 4. СЕРБСКИЙ (КИРИЛЛИЦА - SR_CYRL) ===
            if 'title_sr_cyrl' in self.fields:
                self.fields['title_sr_cyrl'].initial = 'Амбасада за урбанизам'
            if 'subtitle_sr_cyrl' in self.fields:
                self.fields['subtitle_sr_cyrl'].initial = 'Истражујемо, пројектујемо и мењамо урбану среду Београда'
            if 'hero_button_label_sr_cyrl' in self.fields:
                self.fields['hero_button_label_sr_cyrl'].initial = 'Погледај пројекте'
            if 'about_title_sr_cyrl' in self.fields:
                self.fields['about_title_sr_cyrl'].initial = 'О заједници'
            if 'about_text_sr_cyrl' in self.fields:
                self.fields[
                    'about_text_sr_cyrl'
                ].initial = 'Спајамо урбанисте, архитекте и грађане ради стварања удобног града.'
            if 'projects_title_sr_cyrl' in self.fields:
                self.fields['projects_title_sr_cyrl'].initial = 'Наши пројекти'
            if 'projects_button_label_sr_cyrl' in self.fields:
                self.fields['projects_button_label_sr_cyrl'].initial = 'Сви пројекти'


@admin.register(HomePageContent)
class HomePageContentAdmin(BaseAdmin):
    """Администрирование контента главной страницы (Singleton)."""

    form = HomePageContentAdminForm
    ordering = ('id',)
    list_display = ['__str__']
    tinymce_fields = []
    readonly_fields = ('image_left_preview', 'image_right_preview')

    fieldsets = (
        (
            _('1. Общие медиафайлы и ссылки'),
            {
                'fields': (
                    'image_left',
                    'image_left_preview',
                    'image_right',
                    'image_right_preview',
                    'hero_button_link',
                    'projects_button_link',
                ),
                'description': _('Изображения и целевые ссылки, общие для всех языковых версий.'),
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
                'description': _('Контент и заголовки главного экрана на русском языке.'),
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
                'description': _('Контент и заголовки главного экрана на английском языке.'),
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
                'description': _('Контент и заголовки главного экрана на сербской латинице.'),
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
                'description': _('Контент и заголовки главного экрана на сербской кириллице.'),
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

    def has_add_permission(self, request):
        """Запрет на создание более одного экземпляра контента."""
        if HomePageContent.objects.exists():
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context=None):
        """Перенаправление со списка на редактирование единственной записи."""
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
