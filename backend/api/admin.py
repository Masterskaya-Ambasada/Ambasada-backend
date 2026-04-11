from django.contrib import admin
from .models import SiteConfig, Language, Social


admin.site.register(SiteConfig)
admin.site.register(Language)
admin.site.register(Social)

