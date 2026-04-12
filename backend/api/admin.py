from django.contrib import admin  # type: ignore

from .models import Language, SiteConfig, Social

admin.site.register(SiteConfig)
admin.site.register(Language)
admin.site.register(Social)
