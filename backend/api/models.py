from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=10)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class Social(models.Model):
    type = models.CharField(max_length=50)
    url = models.URLField()

    def __str__(self):
        return self.type


class SiteConfig(models.Model):
    site_name = models.CharField(max_length=100)
    seo_description = models.CharField(max_length=250)
    copyright = models.CharField(max_length=150)

    languages = models.ManyToManyField("Language", blank=True)
    socials = models.ManyToManyField("Social", blank=True)

    def __str__(self):
        return self.site_name
